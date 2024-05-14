from data import save, load, check_usr, log
import random
import os
from dotenv import load_dotenv

load_dotenv()

BOT_ID = int(os.getenv('BOT_ID'))
STEAL_MULT = float(os.getenv('STEAL_MULT'))
STEAL_CHANCE = float(os.getenv('STEAL_CHANCE'))

async def battle_helper(ctx, data, user, amount):
    pass

async def steal_helper(ctx, data):
    log('------\nsteal', ctx.author.global_name, data)
    chosen = randomly_choose_user_in_guild(data, ctx)
    if random.random() < STEAL_CHANCE and chosen != str(ctx.author.id):
        chosen_name = data[chosen]['name']
        user_name = data[str(ctx.author.id)]['name']
        amount_to_steal = STEAL_MULT * data[chosen]['balance']
        data[chosen]['balance'] -= amount_to_steal
        data[str(ctx.author.id)]['balance'] += amount_to_steal
        await ctx.send(f'You stole ${amount_to_steal:.2f} from **{chosen_name}**\n ~ **{user_name}** now has ${data[str(ctx.author.id)]["balance"]:.2f}\n ~ **{chosen_name}** now has ${data[chosen]["balance"]:.2f}')
    else:
        await ctx.send('You failed to steal from anyone')
    save(data)
    log('------\nsteal(success)', ctx.author.global_name, data)

def randomly_choose_user_in_guild(data, ctx):
    member_ids = [member.id for member in ctx.guild.members]
    member_ids.remove(BOT_ID)
    chosen = str(random.choice(member_ids))
    while chosen not in data or data[chosen]['balance'] == 0:
        chosen = str(random.choice(member_ids))
    return chosen
