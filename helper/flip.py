from data import save, load, check_usr, log
import random

async def flip_helper(ctx, data, amount):
    id = str(ctx.author.id)
    name = ctx.author.global_name
    log('------\nflip', name, data)
    check_usr(data, ctx)
    if data[id]['balance'] < amount:
        await ctx.send(f'**{ctx.author.mention}** does not have enough coins to bet that amount!')
        return

    if random.randint(0, 1) == 0:
        multiplier = determine_cashout()
        cashout = multiplier * amount
        if multiplier == 66:
            await ctx.send(f'**JACKPOT**\n **+ ${cashout:.2f}**: {ctx.author.mention} now has **${data[id]["balance"] + cashout:.2f}**')
        else:
            await ctx.send(f'Heads! **+ ${cashout:.2f}**: {ctx.author.mention} now has **${data[id]["balance"] + cashout:.2f}**')
        data[id]['balance'] += cashout
    else:
        cashout = min(determine_loss() * amount, data[id]['balance'])
        await ctx.send(f'Tails! **- ${cashout:.2f}**: {ctx.author.mention} now has **${data[id]["balance"] - cashout:.2f}**')
        data[id]['balance'] -= cashout
    save(data)
    log('flip(success)', name, data)

def determine_cashout():
    roll = random.randint(0, 100)
    if roll == 66:
        return 100
    elif int(roll % 2) == 1:
        return 2
    else:
        return 2.5

def determine_loss():
    return random.uniform(1, 1.5)