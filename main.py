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

@bot.command(help='flip <amount> to bet on a coin. Default amount is 0.')
async def flip(ctx, amount: float = 0):
    check_usr(data, ctx)
    await flip_helper(ctx, data["users"], amount)
    save(data)

@bot.command(help='Check your balance')
async def balance(ctx, usr: discord.Member = None):
    check_usr(data, ctx)
    await balance_helper(ctx, data["users"], usr)

@bot.command(help='Out of money?')
async def poor(ctx):
    check_usr(data, ctx)
    await poor_helper(ctx, data["users"], DEFAULT_BALANCE)
    save(data)

@bot.command(help='Shutdown bot')
async def shutdown(ctx):
    await shutdown_helper(ctx, bot, MAGIC_ID, data)

@bot.command(help='leaderboard')
async def leaderboard(ctx):
    await leaderboard_helper(ctx, data["users"])

@commands.cooldown(1, 60, commands.BucketType.user)
@bot.command(help='battle <user> <amount> to battle another user. Default amount is 0.')
async def battle(ctx, opponent: discord.Member, amount: float = 0):
    check_usr(data, ctx)
    await battle_helper(ctx, data["users"], opponent, amount, bot)
    save(data)

@commands.cooldown(1, 3600, commands.BucketType.user)
@bot.command(help='chance to steal a portion of another user\'s balance')
async def steal(ctx):
    check_usr(data, ctx)
    await steal_helper(ctx, data["users"])
    save(data)

@bot.command(help='give <user> <amount> to give another user coins')
async def give(ctx, user: discord.Member, amount: float):
    check_usr(data, ctx)
    await give_helper(ctx, data["users"], user, amount)
    save(data)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        time = str(datetime.timedelta(seconds=error.retry_after))
        time = re.sub(r'.\d*$', '', time)
        await ctx.send(f'This command is on cooldown, you can use it in {time}')

bot.run(os.getenv('TOKEN'))

