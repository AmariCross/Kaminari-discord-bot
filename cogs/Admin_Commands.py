import discord
from discord.ext import commands


class Adminstration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__class__.__name__} Cog has been loaded")

    @commands.command()
    async def purge(self, ctx: commands.Context, limit: int, member: discord.Member = None):
        if ctx.author.id != 892881382479638548:
            await ctx.reply("no")
        else:
            await ctx.message.delete()
            msg = []
            try:
                limit = int(limit)
            except:
                return await ctx.send("Please pass in an integer as limit")
            if not member:
                await ctx.channel.purge(limit=limit)
                return await ctx.send(f"Purged {limit} messages", delete_after=3)
            async for m in ctx.channel.history():
                if len(msg) == limit:
                    break
                if m.author == member:
                    msg.append(m)
            await ctx.channel.delete_messages(msg)
            await ctx.send(f"Purged {member.mention} messages", delete_after=3)


async def setup(bot: commands.Bot):
    await bot.add_cog(Adminstration(bot))
