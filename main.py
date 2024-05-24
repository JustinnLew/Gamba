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
from helper.gamba import gamba_end_helper, my_gamba_helper, gamba_choice_helper, gamba_view_helper, gamba_create_helper, gamba_delete_helper
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
        await ctx.send('This command is currently disabled')

# -------------------------------------------- COMMANDS --------------------------------------------

@bot.command(name='gamba-create', help='!gamba-create <voting duration (seconds)> <*name>', description="create a gamba", enabled = ENABLED)
async def gamba_create(ctx, duration: int, *args):
    await gamba_create_helper(ctx, data, duration, ' '.join(args))

@bot.command(name='gamba-delete', help='!gamba-delete', description='Delete a gamba', enabled = ENABLED)
async def delete_gamba(ctx):
    await gamba_delete_helper(ctx, data)

@bot.command(name='gamba-view', help='!gamba-view', description='View current gamba', enabled = ENABLED)
async def view_gamba(ctx):
    await gamba_view_helper(ctx, data)

@bot.command(name='gamba-yes', help='!gamba-yes <amount>', description='Bet on yes', enabled = ENABLED)
async def gamba_yes(ctx, amount):
    await gamba_choice_helper(ctx, data, "yes", amount)

@bot.command(name='gamba-no', help='!gamba-no <amount>', description='Bet on no', enabled = ENABLED)
async def gamba_no(ctx, amount):
    await gamba_choice_helper(ctx, data, "no", amount)

@bot.command(name='mygamba', help='!mygamba', description='View your gamba', enabled = ENABLED)
async def mygamba(ctx):
    await my_gamba_helper(ctx, data)

@bot.command(name='gamba-end', help='!gamba-end', description='End gamba', enabled = ENABLED)
async def end_gamba(ctx, result):
    await gamba_end_helper(ctx, data, result)

@commands.cooldown(1, 1, commands.BucketType.user)
@bot.command(name='flip', aliases=['f', 'coin'], help='!flip <amount>',description='flip <amount> to bet on a coin', enabled = ENABLED)
async def flip(ctx, amount):
    await flip_helper(ctx, data["users"], amount)

@bot.command(name='balance', aliases=['b'], help='!balance <usr (optional)>', description='Check your balance', enabled = ENABLED)
async def balance(ctx, usr: discord.Member = None):
    await balance_helper(ctx, data["users"], usr)

@bot.command(name='poor', aliases=['p'], help='Out of money?', enabled = ENABLED)
async def poor(ctx):
    await poor_helper(ctx, data["users"], DEFAULT_BALANCE)

@bot.command(name='leaderboard', aliases=['l'], help='money leaderboard', enabled = ENABLED)
async def leaderboard(ctx):
    await leaderboard_helper(ctx, data["users"])

@commands.cooldown(1, 60, commands.BucketType.user)
@bot.command(name='battle', aliases=['fight'], help='!battle <user> <amount> to battle another user. Default amount is 0.', enabled = ENABLED)
async def battle(ctx, opponent: discord.Member, amount: float = 0):
    await battle_helper(ctx, data["users"], opponent, amount, bot)

@commands.cooldown(1, 3600, commands.BucketType.user)
@bot.command(name='steal', aliases=['s'], help='chance to steal a portion of another user\'s balance', enabled = ENABLED)
async def steal(ctx):
    await steal_helper(ctx, data["users"])

@bot.command(help='!give <user> <amount> to give another user coins', enabled = ENABLED)
async def give(ctx, user: discord.Member, amount: float):
    await give_helper(ctx, data["users"], user, amount)

@commands.cooldown(1, 86400, commands.BucketType.user)
@bot.command(name='daily', aliases=['d'], help='daily free money', enabled = ENABLED)
async def daily(ctx):
    id = str(ctx.author.id)
    amount = random.randint(1, 1000000)
    data["users"][id]['balance'] += amount
    await ctx.send(f'**+ ${amount:,.2f}**: {ctx.author.mention} now has **${data["users"][id]["balance"]:,.2f}**')

# ----------------------------------------------------------------------------------------------

bot.run(TOKEN)

