from data import save, load, check_usr, log

async def balance_helper(ctx, data):
    id = str(ctx.author.id)
    name = ctx.author.global_name
    log('------\nbalance', name, data)
    check_usr(data, id)
    await ctx.send(f'{name} has **{data[id]["balance"]:.2f}** coins!')
    log('balance(success)', name, data)

async def poor_helper(ctx, data, default_balance):
    id = str(ctx.author.id)
    name = ctx.author.global_name
    log('------\npoor', name, data)
    check_usr(data, id)
    if data[id]['balance'] < default_balance:
        data[id]['balance'] = default_balance
        await ctx.send(f'{name} has been reset to **{default_balance:.2f}** coins!')
        save(data)
    log('poor(success)', name, data)
