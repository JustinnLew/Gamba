#!/usr/bin/env python3

import discord
from dotenv import load_dotenv
import os
import random
from discord.ext import commands
import pprint
from data import save, load, check_usr, log
from importlib import import_module
from helper.util import balance_helper, poor_helper
from helper.flip import flip_helper

TOKEN = os.getenv('TOKEN')
DEFAULT_BALANCE = 1000.00

load_dotenv()

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=help_command)

data = {}

@bot.event
async def on_ready():
    global data
    data = load()
    print('Ready!')

@bot.command(help='!flip <amount> to bet on a coin. Default amount is 0.')
async def flip(ctx, amount: float = 0):
    await flip_helper(ctx, data, amount)

@bot.command(help='Check your balance')
async def balance(ctx):
    await balance_helper(ctx, data)

@bot.command(help='Out of money?')
async def poor(ctx):
    await poor_helper(ctx, data, DEFAULT_BALANCE)

@bot.command(help='Shutdown bot')
async def shutdown(ctx):
    save(data)
    await ctx.send('Shutting down...')
    await bot.close()

bot.run(os.getenv('TOKEN'))

