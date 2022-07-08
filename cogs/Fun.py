import aiohttp
import discord
from discord.ext import commands
from discord import app_commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__class__.__name__} Cog has been loaded")


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
