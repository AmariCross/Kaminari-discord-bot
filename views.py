import discord

main_color = discord.Colour.from_rgb(148, 150, 255)


class Next(discord.ui.View):
    def __init__(self, func, author):
        super().__init__()
        self.func = func
        self.author = author

    @discord.ui.button(label='Next', style=discord.ButtonStyle.green)
    async def next_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author.id:
            val = await self.func()
            await interaction.response.edit_message(embed=val)
        else:
            await interaction.response.send_message("This command isn't for you!", ephemeral=True)

    @discord.ui.button(label='Stop Interaction', style=discord.ButtonStyle.grey)
    async def stop_interaction_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Interaction ended (╯▔皿▔)╯", ephemeral=True)
        await interaction.response.edit_message(view=self)
        self.stop()


class Url_Button(discord.ui.View):
    def __init__(self, link: str, text: str):
        super().__init__()
        self.add_item(discord.ui.Button(label=text, url=link))


class HelpDropDown(discord.ui.Select):
    def __init__(self, author, bot):
        self.author = author
        self.bot = bot
        cogs = [c for c in self.bot.cogs.keys()]
        options = [discord.SelectOption(label=cog,
                                        description=f"/help {str(cog.lower())}",
                                        value=f"{cog.title()}") for cog in cogs]
        super().__init__(placeholder='Chose a category', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            em = discord.Embed(
                title="Nope",
                description="This command is not for you",
                color=main_color
            )
            return await interaction.response.send_message(embed=em, ephemeral=True)
        embed = discord.Embed(title=f"{self.values[0]} Commands", color=main_color)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        for command in self.bot.get_cog(self.values[0]).__cog_app_commands__:
            description = command.description
            embed.add_field(name=f"/`{command.name}`", value=description, inline=False)
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, author, bot):
        self.author = author
        self.bot = bot

        super().__init__()
        self.add_item(HelpDropDown(author, bot))
        self.add_item(
            discord.ui.Button(label='Invite',
                              url="https://discord.com/api/oauth2/authorize?client_id=992285824840372245&permissions=8&"
                                  "scope=bot%20applications.commands")
        )
