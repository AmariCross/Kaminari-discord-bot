import discord
from discord.ext import commands
import time as t
import os
from views import Url_Button
import motor.motor_asyncio
import asyncio

intents = discord.Intents.all()
start_time = t.time()


class MyBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=";",
            intents=intents,
            application_id=992285824840372245
        )

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()


bot = MyBot()
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to discord.")
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("/help"))


@bot.tree.command(name="invite", description="Sends an invite for the bot!")
async def invite(interaction: discord.Interaction):
    url = "https://discord.com/api/oauth2/authorize?client_id=992285824840372245&permissions=8&scope=bot%20" \
          "applications.commands"
    embed = discord.Embed(title="Invite", colour=discord.Colour.from_rgb(148, 150, 255),
                          description=f"[Like invite me]({url})", url=url)
    await interaction.response.send_message(embed=embed, view=Url_Button(url, "Invite"))


async def main():
    async with bot:
        bot.mongoConnect = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URI"])
        await bot.start(os.environ['TOKEN'])


asyncio.run(main())
