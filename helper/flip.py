import random

async def flip_helper(ctx, data, amount):
    if amount == 'all' or amount == 'ALL':
        amount = float(data["users"][str(ctx.author.id)]['balance'])
    else:
        amount = float(amount)
    id = str(ctx.author.id)
    if data[id]['balance'] < amount:
        await ctx.send(f'**{ctx.author.mention}** does not have enough coins to bet that amount!')
        return

    if random.randint(0, 1) == 0:
        multiplier = determine_cashout()
        cashout = multiplier * amount
        if multiplier == 100:
            await ctx.send(f'**JACKPOT**\n **+ ${cashout:,.2f}**: {ctx.author.mention} now has **${data[id]["balance"] + cashout:,.2f}**')
        else:
            await ctx.send(f'Heads! **+ ${cashout:,.2f}**: {ctx.author.mention} now has **${data[id]["balance"] + cashout:,.2f}**')
        data[id]['balance'] += cashout
    else:
        cashout = min(1 * amount, data[id]['balance'])
        await ctx.send(f'Tails! **- ${cashout:,.2f}**: {ctx.author.mention} now has **${data[id]["balance"] - cashout:,.2f}**')
        data[id]['balance'] -= cashout

def determine_cashout():
    roll = random.randint(0, 100)
    if roll == 66:
        return 100
    else:
        return 1

def determine_loss():
    return random.uniform(1, 1.5)