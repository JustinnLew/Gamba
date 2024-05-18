#!/usr/bin/env python3

import discord
from dotenv import load_dotenv
import os
import random
from discord.ext import commands
import pprint
from data import save, load, check_usr, log
from helper.util import balance_helper, poor_helper, leaderboard_helper, give_helper
from helper.flip import flip_helper
from helper.pvp import battle_helper, steal_helper
import datetime
import re
from asyncio import sleep

load_dotenv()

TOKEN = os.getenv('TOKEN')
DEFAULT_BALANCE = float(os.getenv('DEFAULT_BALANCE'))
MAGIC_ID = int(os.getenv('MAGIC_ID'))
BOT_ID = int(os.getenv('BOT_ID'))
BATTLE_INIT_HP= int(os.getenv('BATTLE_INIT_HP'))

# GLOBAL KILL FLAG
ENABLED = True

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=help_command)

data = {}

# -------------------------------------------- BOT SETUP --------------------------------------------

@bot.event
async def on_ready():
    global data
    data = load()
    print('Ready!')

@bot.before_invoke
async def before_all(ctx):
    check_usr(data, ctx)

@bot.after_invoke
async def after_all(ctx):
    log(f'{ctx.author.name}: Invoked {ctx.message.content} on {datetime.datetime.now()}', data)
    save(data)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        time = str(datetime.timedelta(seconds=error.retry_after))
        time = re.sub(r'.\d*$', '', time)
        await ctx.send(f'This command is on cooldown, you can use it in {time}')
    if isinstance(error, commands.DisabledCommand):
        await ctx.send('Watch the game')

# -------------------------------------------- COMMANDS --------------------------------------------

@bot.command(name='gamba-create', help='Create a gamba', enabled = ENABLED)
async def gamba_create(ctx, duration: int, *args):
    name = ' '.join(args)
    if data["gamba"]:
        await ctx.send('Gamba already in progress')
        return
    data["gamba"] = {
        "state": "betting",
        "owner": {
            "id": ctx.author.id,
            "name": ctx.author.global_name or ctx.author.name
        },
        "name": name,
        "votes": [],
    }
    save(data)
    await ctx.send(f'```fix\nGamba Created: {name}```')
    await ctx.send(f"```yaml\n!gamba-yes <amount> to vote yes\n```")
    await ctx.send(f"```yaml\n!gamba-no <amount> to vote no\n```")
    await ctx.send(f"```md\n> Betting ends in {duration} seconds\n```")
    await sleep(duration)
    data["gamba"]["state"] = "closed"
    await ctx.send(f"```md\n> Betting closed\n```")

@bot.command(name='gamba-delete', help='Delete a gamba', enabled = ENABLED)
async def delete_gamba(ctx):
    if not data["gamba"]["owner"]:
        await ctx.send('No gamba in progress')
        return
    if data["gamba"]["owner"]["id"] != ctx.author.id:
        await ctx.send('You do not own the gamba')
        return
    data["gamba"] = None
    await ctx.send('```fix\nGamba Deleted```')

@bot.command(name='gamba-view', help='View current gamba', enabled = ENABLED)
async def view_gamba(ctx):
    embed = discord.Embed(title='Gamba', color=discord.Color.pink())
    embed.add_field(name='Owner', value=data["gamba"]["owner"]["name"])
    embed.add_field(name='Name', value=data["gamba"]["name"])
    embed.add_field(name='State', value=data["gamba"]["state"])
    yes = ""
    no = ""
    for v in data["gamba"]["votes"]:
        if v["choice"] == "yes":
            yes += f'{v["name"]}: {v["amount"]}\n'
        else:
            no += f'{v["name"]}: {v["amount"]}\n'
    embed.add_field(name='Yes', value=yes)
    embed.add_field(name='No', value=no)
    await ctx.send(embed=embed)

@bot.command(name='gamba-yes', help='Bet on yes', enabled = ENABLED)
async def gamba_yes(ctx, amount):
    name = ctx.author.global_name or ctx.author.name
    if data["gamba"]["state"] != "betting":
        await ctx.send('Betting is closed')
        return
    if amount == 'all' or amount == 'ALL':
        amount = float(data["users"][str(ctx.author.id)]['balance'])
    else:
        amount = float(amount)
    if data["users"][str(ctx.author.id)]['balance'] < amount:
        await ctx.send('Not enough coins')
        return
    for v in data["gamba"]["votes"]:
        if v["name"] == name:
            data["users"][str(ctx.author.id)]['balance'] += v["amount"]
            v["amount"] = amount
            data["users"][str(ctx.author.id)]['balance'] -= amount
            v["choice"] = "yes"
            return
    data["gamba"]["votes"].append({
        "id": str(ctx.author.id),
        "name": name,
        "amount": amount,
        "choice": "yes",
    })
    data["users"][str(ctx.author.id)]['balance'] -= amount
    await ctx.send(f'```fix\nbet place by {name} for {amount} on yes```')

@bot.command(name='gamba-no', help='Bet on no', enabled = ENABLED)
async def gamba_no(ctx, amount):
    name = ctx.author.global_name or ctx.author.name
    if data["gamba"]["state"] != "betting":
        await ctx.send('Betting is closed')
        return
    if amount == 'all' or amount == 'ALL':
        amount = float(data["users"][str(ctx.author.id)]['balance'])
    else:
        amount = float(amount)
    if data["users"][str(ctx.author.id)]['balance'] < amount:
        await ctx.send('Not enough coins')
        return
    for v in data["gamba"]["votes"]:
        if v["name"] == name:
            data["users"][str(ctx.author.id)]['balance'] += v["amount"]
            v["amount"] = amount
            data["users"][str(ctx.author.id)]['balance'] -= amount
            v["choice"] = "no"
            return
    data["gamba"]["votes"].append({
        "id": str(ctx.author.id),
        "name": name,
        "amount": amount,
        "choice": "no",
    })
    data["users"][str(ctx.author.id)]['balance'] -= amount
    await ctx.send(f'```fix\nbet place by {name} for {amount} on no```')

@bot.command(name='mygamba', help='View your gamba', enabled = ENABLED)
async def mygamba(ctx):
    name = ctx.author.global_name or ctx.author.name
    for v in data["gamba"]["votes"]:
        if v["name"] == name:
            await ctx.send(f'```fix\nYou have bet {v["amount"]} on {v["choice"]}```')
            return

@bot.command(name='gamba-end', help='End gamba', enabled = ENABLED)
async def end_gamba(ctx, result):
    if result != "yes" and result != "no":
        await ctx.send('Invalid result')
        return
    if not data["gamba"]:
        await ctx.send('No gamba in progress')
        return
    if data["gamba"]["state"] != "closed":
        await ctx.send('Betting is still open')
        return
    if data["gamba"]["owner"]["id"] != ctx.author.id:
        await ctx.send('You do not own the gamba')
        return
    yes_total = 0
    no_total = 0
    for v in data["gamba"]["votes"]:
        if v["choice"] == "yes":
            yes_total += v["amount"]
        else:
            no_total += v["amount"]
    if result == "yes":
        for v in data["gamba"]["votes"]:
            if v["choice"] == "yes":
                winnings = ((yes_total / v["amount"]) * no_total)
                data["users"][v["id"]]['balance'] += v["amount"] + winnings
                await ctx.send(f'```fix\n{v["name"]} won {winnings}```')
    else:
        for v in data["gamba"]["votes"]:
            if v["choice"] == "no":
                winnings = ((no_total / v["amount"]) * yes_total)
                data["users"][v["id"]]['balance'] += v["amount"] + winnings
                await ctx.send(f'```fix\n{v["name"]} won {winnings}```')

@commands.cooldown(1, 1, commands.BucketType.user)
@bot.command(name='flip', aliases=['f', 'coin'], help='flip <amount> to bet on a coin. Default amount is 0.', enabled = ENABLED)
async def flip(ctx, amount):
    if amount == 'all' or amount == 'ALL':
        amount = float(data["users"][str(ctx.author.id)]['balance'])
    else:
        amount = float(amount)
    await flip_helper(ctx, data["users"], amount)

@bot.command(name='balance', aliases=['b'], help='Check your balance', enabled = ENABLED)
async def balance(ctx, usr: discord.Member = None):
    await balance_helper(ctx, data["users"], usr)

@bot.command(name='poor', aliases=['p'], help='Out of money?', enabled = ENABLED)
async def poor(ctx):
    await poor_helper(ctx, data["users"], DEFAULT_BALANCE)

@bot.command(name='leaderboard', aliases=['l'], help='money leaderboard', enabled = ENABLED)
async def leaderboard(ctx):
    await leaderboard_helper(ctx, data["users"])

@commands.cooldown(1, 60, commands.BucketType.user)
@bot.command(name='battle', aliases=['fight'], help='battle <user> <amount> to battle another user. Default amount is 0.', enabled = ENABLED)
async def battle(ctx, opponent: discord.Member, amount: float = 0):
    await battle_helper(ctx, data["users"], opponent, amount, bot)

@commands.cooldown(1, 3600, commands.BucketType.user)
@bot.command(name='steal', aliases=['s'], help='chance to steal a portion of another user\'s balance', enabled = ENABLED)
async def steal(ctx):
    await steal_helper(ctx, data["users"])

@bot.command(help='give <user> <amount> to give another user coins', enabled = ENABLED)
async def give(ctx, user: discord.Member, amount: float):
    await give_helper(ctx, data["users"], user, amount)

# ----------------------------------------------------------------------------------------------

bot.run(os.getenv('TOKEN'))

