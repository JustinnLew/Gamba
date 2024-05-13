from data import save, load, check_usr, log
import discord

async def balance_helper(ctx, data):
    id = str(ctx.author.id)
    name = ctx.author.global_name
    log('------\nbalance', name, data)
    check_usr(data, ctx)
    await ctx.send(f'{name} has **{data[id]["balance"]:.2f}** coins!')
    log('balance(success)', name, data)

async def poor_helper(ctx, data, default_balance):
    id = str(ctx.author.id)
    name = ctx.author.global_name
    log('------\npoor', name, data)
    check_usr(data, ctx)
    if data[id]['balance'] < default_balance:
        data[id]['balance'] = default_balance
        await ctx.send(f'{name} has been reset to **{default_balance:.2f}** coins!')
        save(data)
    log('poor(success)', name, data)

async def shutdown_helper(ctx, bot, MAGIC_ID, data):
    if ctx.author.id != MAGIC_ID:
            await ctx.send('You do not have permission to do that.')
            return
    save(data)
    await ctx.send('Shutting down...')
    await bot.close()

async def leaderboard_helper(ctx, data):
    data = load()
    leaderboard = sorted([(value['name'], value['balance']) for value in data.values()], key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title="Leaderboard", color=discord.Color.gold())
    for i, (name, balance) in enumerate(leaderboard):
        embed.add_field(value=f'{i+1}.  **{name}**:  ${balance:.2f}\n', name="\u200b", inline=False)
    await ctx.send(embed=embed)