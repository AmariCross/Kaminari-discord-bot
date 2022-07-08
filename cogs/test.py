import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from views import Next
import math
import re


class Suggestion(discord.ui.Modal, title="Suggestion"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    suggest = discord.ui.TextInput(
        label="What do you suggest for the server",
        style=discord.TextStyle.long,
        placeholder="Type what you want to be updated in the server here...",
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your feedback, {interaction.user.mention}', ephemeral=True)
        suggestion_c = self.bot.get_channel(992487850077589525)
        embed = discord.Embed(colour=discord.Colour.from_rgb(148, 150, 255))
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name=f"User {interaction.user.name}'s suggestion", value=f"`{self.suggest.value}`")
        await suggestion_c.send(embed=embed)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(
        first_value='The first value you want to add something to',
        second_value='The value you want to add to the first value',
    )
    async def addd(self, interaction: discord.Interaction, first_value: int, second_value: int):
        """Adds two numbers together."""
        await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')

    @app_commands.command(name="modal")
    async def modal_test(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Suggestion(self.bot))

    @app_commands.command(name="user_info", description="Get info about your self or an another account in the guild")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        def format_time(time):
            return time.strftime("%d-%B-%Y at %I:%M %p")

        if member is None:
            member = interaction.user
        roleList = [r.name for r in member.roles]
        roleList.remove("@everyone")
        roles = ", ".join(roleList)
        embed = discord.Embed(title="User info", color=discord.Colour.from_rgb(148, 150, 255))
        answer = ""
        if member.bot is False:
            answer += "No"
        else:
            answer += "Yes"
        nickname = ""
        if member.display_name is interaction.user.name:
            nickname += "No Nickname"
        else:
            nickname += member.display_name

        fields = [("Username", f"```{member}```", True),
                  ("User Id", f"```{member.id}```", True),
                  (f"Roles[{len(roleList)}]", f"```{roles}```", False),
                  ("Nickname", f'```{nickname}```', True),
                  ("Is a bot", f'```{answer}```', True),
                  ('Joined this server on', f"```{format_time(member.joined_at)}```", False),
                  ('Account created on', f"```{format_time(member.created_at)}```", False)
                  ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))
