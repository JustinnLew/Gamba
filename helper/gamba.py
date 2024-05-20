from dotenv import load_dotenv
import discord
from asyncio import sleep
from data import save

load_dotenv()

async def gamba_delete_helper(ctx, data):
    if not data["gamba"]["owner"]:
        await ctx.send('No gamba in progress')
        return
    if data["gamba"]["owner"]["id"] != ctx.author.id:
        await ctx.send('You do not own the gamba')
        return
    for v in data["gamba"]["votes"]:
        data["users"][v["id"]]['balance'] += v["amount"]
    data["gamba"] = None
    await ctx.send('```fix\nGamba Deleted```')

async def gamba_create_helper(ctx, data, duration, name):
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

async def gamba_view_helper(ctx, data):
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

async def gamba_choice_helper(ctx, data, choice, amount):
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
            v["choice"] = choice
            return
    data["gamba"]["votes"].append({
        "id": str(ctx.author.id),
        "name": name,
        "amount": amount,
        "choice": choice,
    })
    data["users"][str(ctx.author.id)]['balance'] -= amount
    await ctx.send(f'```fix\nbet place by {name} for {amount} on {choice}```')

async def my_gamba_helper(ctx, data):
    name = ctx.author.global_name or ctx.author.name
    for v in data["gamba"]["votes"]:
        if v["name"] == name:
            await ctx.send(f'```fix\nYou have bet {v["amount"]} on {v["choice"]}```')
            return

async def gamba_end_helper(ctx, data, result):
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
                winnings = ((v["amount"] / yes_total) * no_total)
                data["users"][v["id"]]['balance'] += v["amount"] + winnings
                await ctx.send(f'```fix\n{v["name"]} won {winnings}```')
    else:
        for v in data["gamba"]["votes"]:
            if v["choice"] == "no":
                winnings = ((v["amount"] / no_total) * yes_total)
                data["users"][v["id"]]['balance'] += v["amount"] + winnings
                await ctx.send(f'```fix\n{v["name"]} won {winnings}```')
    data["gamba"] = None