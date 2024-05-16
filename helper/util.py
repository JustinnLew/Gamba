from data import save, load, log
import discord

async def balance_helper(ctx, data, usr):
    log('------\nbalance', name, data)
    if usr:
        id = str(usr.id)
        name = usr.global_name or usr.name
    else:
        id = str(ctx.author.id)
        name = ctx.author.global_name or ctx.author.name
    await ctx.send(f'**{name}** has **${data[id]["balance"]:.2f}**')
    log('balance(success)', name, data)

async def poor_helper(ctx, data, default_balance):
    log('------\npoor', name, data)
    id = str(ctx.author.id)
    name = ctx.author.global_name
    if data[id]['balance'] < default_balance:
        data[id]['balance'] = default_balance
        await ctx.send(f'{ctx.author.mention} has been reset to **${default_balance:.2f}**')
    log('poor(success)', name, data)

async def shutdown_helper(ctx, bot, MAGIC_ID):
    if ctx.author.id != MAGIC_ID:
            await ctx.send('You do not have permission to do that.')
            return
    await ctx.send('Shutting down...')
    await bot.close()

async def give_helper(ctx, data, user, amount):
    log('give', name, data)
    id = str(ctx.author.id)
    name = ctx.author.global_name
    if data[id]['balance'] < amount:
        await ctx.send(f'**{ctx.author.mention}** does not have enough coins to give that amount!')
        return
    if amount < 0:
        await ctx.send(f'**{ctx.author.mention}** cannot give a negative amount of coins!')
        return
    data[id]['balance'] -= amount
    data[str(user.id)]['balance'] += amount
    await ctx.send(f'{ctx.author.mention} has given {user.mention} **${amount:.2f}**')
    log('give(success)', name, data)

async def leaderboard_helper(ctx, data):
    leaderboard = sorted([(value['name'], value['balance']) for value in data.values()], key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title="Leaderboard", color=discord.Color.gold())
    for i, (name, balance) in enumerate(leaderboard):
        embed.add_field(value=f'{i+1}.  **{name}**:  ${balance:.2f}\n', name="\u200b", inline=False)
    await ctx.send(embed=embed)