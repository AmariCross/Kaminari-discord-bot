import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from views import HelpView


invite = "https://discord.com/api/oauth2/authorize?client_id=992285824840372245&permissions=8&scope=bot%20" \
         "applications.commands"

main_color = discord.Colour.from_rgb(148, 150, 255)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cogs = [c for c in self.bot.cogs.keys()]
        self.options = [Choice(name=cog, value=cog) for cog in self.cogs]

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__class__.__name__} Cog has been loaded")

    @app_commands.command(name="help", description="List of all the commands on this bot")
    @app_commands.describe(search="The specific category you want info on")
    async def help(self, interaction, search: str = None):
        coms = []
        for command in self.bot.tree.walk_commands():
            coms.append(str(command.name).lower())
        em = discord.Embed(title="Help",
                           description=f"Invite: [Click here!]({invite}) || `/help [category]` or "
                                       f"`/help [command]` for more info", color=main_color)
        em.set_thumbnail(url=self.bot.user.avatar.url)
        cogs = [c for c in self.bot.cogs.keys()]
        if search is None:
            for cog in cogs:
                em.add_field(name=cog, value=f"`/help {str(cog).lower()}`", inline=False)
            await interaction.response.send_message(embed=em, view=HelpView(interaction.user, self.bot))
        else:
            if str(search).title() in cogs:
                for command in self.bot.get_cog(str(search.title())).__cog_app_commands__:
                    em.title = f"{search.title()} Commands"
                    em.add_field(name=f"`/{command.name}`", value=command.description, inline=False)
                await interaction.response.send_message(embed=em, view=HelpView(interaction.user, self.bot))
            elif search.lower() in coms:
                com = self.bot.tree.get_command(search.lower())
                em.title = f"`/{search}` info"
                em.description = ""
                em.add_field(name="Description:", value=com.description)
                await interaction.response.send_message(embed=em)
            else:
                em.title = "Error"
                em.description = f'```fix\ncommand "{search}" is not found pls use a valid category or ' \
                                 f'command in the bot. ```'
                await interaction.response.send_message(embed=em)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
