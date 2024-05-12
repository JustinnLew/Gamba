from data import save, load, check_usr, log
import random

async def flip_helper(ctx, data):
    id = str(ctx.author.id)
    name = ctx.author.global_name
    log('------\nflip', name, data)
    check_usr(data, id)
    if data[id]['balance'] < 1:
        await ctx.send(f'{name} you have no coins to flip!')
        return
    if random.randint(0, 1) == 0:
        cashout = determine_cashout()
        if cashout == 66:
            await ctx.send(f'**JACKPOT**\nHeads! *{name}* has **{data[id]["balance"]*cashout:.2f}** coins!')
        else:
            await ctx.send(f'Heads! *{name}* has **{data[id]["balance"]*cashout:.2f}** coins!')
        data[id]['balance'] *= cashout
    else:
        data[id]['balance'] /= determine_loss()
        await ctx.send(f'Tails! *{name}* has **{data[id]["balance"]:.2f}** coins!')
    save(data)
    log('flip(success)', name, data)

def determine_cashout():
    roll = random.randint(0, 100)
    if roll == 66:
        return 66
    elif int(roll / 10) == 9:
        return 3
    elif int(roll % 2) == 1:
        return 1.5
    else:
        return 2

def determine_loss():
    return random.uniform(1.5, 2)