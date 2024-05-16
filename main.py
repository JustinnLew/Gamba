#!/usr/bin/env python3

import discord
from dotenv import load_dotenv
import os
import random
from discord.ext import commands
import pprint
from data import save, load, check_usr, log
from importlib import import_module
from helper.util import balance_helper, poor_helper, shutdown_helper, leaderboard_helper, give_helper
from helper.flip import flip_helper
from helper.pvp import battle_helper, steal_helper
import datetime
import re
from time import sleep

load_dotenv()

TOKEN = os.getenv('TOKEN')
DEFAULT_BALANCE = float(os.getenv('DEFAULT_BALANCE'))
MAGIC_ID = int(os.getenv('MAGIC_ID'))
BOT_ID = int(os.getenv('BOT_ID'))
BATTLE_INIT_HP= int(os.getenv('BATTLE_INIT_HP'))

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=help_command)

data = {}

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

@bot.command(name='flip', aliases=['f', 'coin'], help='flip <amount> to bet on a coin. Default amount is 0.')
async def flip(ctx, amount: float = 0):
    await flip_helper(ctx, data["users"], amount)

@bot.command(name='balance', aliases=['b'], help='Check your balance')
async def balance(ctx, usr: discord.Member = None):
    await balance_helper(ctx, data["users"], usr)

@bot.command(name='poor', aliases=['p'], help='Out of money?')
async def poor(ctx):
    await poor_helper(ctx, data["users"], DEFAULT_BALANCE)

@bot.command(help='leaderboard')
async def leaderboard(ctx):
    await leaderboard_helper(ctx, data["users"])

@commands.cooldown(1, 60, commands.BucketType.user)
@bot.command(name='battle', aliases=['fight'], help='battle <user> <amount> to battle another user. Default amount is 0.')
async def battle(ctx, opponent: discord.Member, amount: float = 0):
    await battle_helper(ctx, data["users"], opponent, amount, bot)

@commands.cooldown(1, 3600, commands.BucketType.user)
@bot.command(help='chance to steal a portion of another user\'s balance')
async def steal(ctx):
    await steal_helper(ctx, data["users"])

@bot.command(help='give <user> <amount> to give another user coins')
async def give(ctx, user: discord.Member, amount: float):
    await give_helper(ctx, data["users"], user, amount)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        time = str(datetime.timedelta(seconds=error.retry_after))
        time = re.sub(r'.\d*$', '', time)
        await ctx.send(f'This command is on cooldown, you can use it in {time}')

bot.run(os.getenv('TOKEN'))

