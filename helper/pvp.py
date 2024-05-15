from data import save, load, check_usr, log
import random
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv()

BOT_ID = int(os.getenv('BOT_ID'))
STEAL_MULT = float(os.getenv('STEAL_MULT'))
STEAL_CHANCE = float(os.getenv('STEAL_CHANCE'))
BATTLE_INIT_HP = int(os.getenv('BATTLE_INIT_HP'))

async def battle_helper(ctx, data, opponent, amount, bot):
    check_usr(data, ctx)
    challenger = ctx.author
    challenger_id = str(challenger.id)
    opponent_id = str(opponent.id)
    if opponent == challenger:
        await ctx.send("You cannot battle yourself!")
        return
    if amount < 0:
        await ctx.send("You must bet a positive amount!")
        return
    if opponent_id not in data:
        await ctx.send("Opponent has not registered!")
        return
    if data[challenger_id]['balance'] < amount:
        await ctx.send(f"{challenger.mention} does not have enough money!")
        return
    if data[opponent_id]['balance'] < amount:
        await ctx.send(f"{opponent.mention} does not have enough money!")
        return

    message = await ctx.send(f"{challenger.mention} challenges {opponent.mention} to a battle!\nReact with ✅ to accept the challenge")
    await message.add_reaction('✅')
    def check(reaction, user):
        return user == opponent and str(reaction.emoji) == '✅'

    try:
        if await bot.wait_for('reaction_add', timeout=20.0, check=check):
            await ctx.send(f"{opponent.mention} has accepted the challenge!")
            result = await battle_loop(challenger, opponent, ctx)
            if result:
                data[challenger_id]['balance'] += amount
                data[opponent_id]['balance'] -= amount
                await ctx.send(f"{challenger.mention} has won the battle and received **{amount}**!\n{opponent.mention} has lost **{amount}**!")
            else:
                data[challenger_id]['balance'] -= amount
                data[opponent_id]['balance'] += amount
                await ctx.send(f"{opponent.mention} has won the battle and received **{amount}**!\n{challenger.mention} has lost **{amount}**!")
    except:
        await ctx.send(f"{opponent.mention} has declined the challenge!")
        return
    save()

async def battle_loop(challenger, opponent, ctx):
    challenger_hp = BATTLE_INIT_HP
    opponent_hp = BATTLE_INIT_HP
    turn = random.randint(0, 1)
    while challenger_hp > 0 and opponent_hp > 0:
        damage = random.randint(5, 45)
        if turn == 0:
            opponent_hp = max(opponent_hp - damage, 0)
            string = f"{challenger.mention} attacks for **{damage}** damage! {opponent.mention} has **{opponent_hp}** HP left!"
        else:
            challenger_hp = max(challenger_hp - damage, 0)
            string = f"{opponent.mention} attacks for **{damage}** damage! {challenger.mention} has **{challenger_hp}** HP left!"
        turn = 1 - turn
        sleep(1)
        await ctx.send(string)
    return challenger_hp > 0

async def steal_helper(ctx, data):
    log('------\nsteal', ctx.author.global_name, data)
    check_usr(data, ctx)
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

