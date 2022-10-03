
import discord
from discord.ext import commands

from core import checks
from core.checks import PermissionLevel


class ClaimThread(commands.Cog):
    """Allows supporters to claim thread by sending claim in the thread channel"""
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.plugin_db.get_partition(self)
        check_reply.fail_msg = 'This thread has been claimed by another user.'
        self.bot.get_command('close').add_check(check_reply)
        self.bot.get_command('areply').add_check(check_reply)

    @checks.has_permissions(PermissionLevel.OWNER)
    @checks.thread_only()
    @commands.command()
    async def claim(self, ctx):
        if any(str(role) == 'Corporate Permissions' for role in ctx.author.roles):
            thread = await self.db.find_one({'thread_id': str(ctx.thread.channel.id)})
            if thread is None:
                await self.db.insert_one({'thread_id': str(ctx.thread.channel.id), 'claimers': [str(ctx.author.id)]})
                await ctx.send('Claimed')
            else:
                await ctx.send('Thread is already claimed')

    @checks.has_permissions(PermissionLevel.OWNER)
    @checks.thread_only()
    @commands.command()
    async def addclaim(self, ctx, *, member: discord.Member):
        """Adds another user to the thread claimers"""
        thread = await self.db.find_one({'thread_id': str(ctx.thread.channel.id)})
        if thread and any(str(role) == 'Corporate Permissions' for role in ctx.author.roles):
            await self.db.find_one_and_update({'thread_id': str(ctx.thread.channel.id)}, {'$addToSet': {'claimers': str(member.id)}})
            await ctx.send('Added to claimers')

    @checks.has_permissions(PermissionLevel.OWNER)
    @checks.thread_only()
    @commands.command()
    async def removeclaim(self, ctx, *, member: discord.Member):
        """Removes a user from the thread claimers"""
        thread = await self.db.find_one({'thread_id': str(ctx.thread.channel.id)})
        if thread and any(str(role) == 'Corporate Permissions' for role in ctx.author.roles):
            await self.db.find_one_and_update({'thread_id': str(ctx.thread.channel.id)}, {'$pull': {'claimers': str(member.id)}})
            await ctx.send('Removed from claimers')

    @checks.has_permissions(PermissionLevel.OWNER)
    @checks.thread_only()
    @commands.command()
    async def unclaim(self, ctx):
        """Remove claim on ticket"""
        thread = await self.db.find_one({'thread_id': str(ctx.thread.channel.id)})
        if thread and any(str(role) == 'Corporate Permissions' for role in ctx.author.roles):
            await self.db.delete_one({ 'thread_id': str(ctx.thread.channel.id) })
            await ctx.send('Claim removed')

async def check_reply(ctx):
    thread = await ctx.bot.get_cog('ClaimThread').db.find_one({'thread_id': str(ctx.thread.channel.id)})
    print(ctx.author.roles)
    if thread:
        return ctx.author.bot or (any(str(role) == 'Corporate Permissions' for role in ctx.author.roles)) # (str(ctx.author.id) in thread['claimers']) or 
    return True


async def setup(bot):
    await bot.add_cog(ClaimThread(bot))
