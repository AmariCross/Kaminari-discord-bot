import discord
from akinator.async_aki import Akinator
import requests
import os


def get_track(search: str):
    search = search.replace(" ", "+")
    AUTH_URL = 'https://accounts.spotify.com/api/token'

    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': os.environ['SPOTIFY_ID'],
        'client_secret': os.environ['SPOTIFY_SECRET'],
    })

    # convert the response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data['access_token']

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    url = f"https://api.spotify.com/v1/search?q={search}&type=track&limit=10"
    r = requests.request("GET", url, headers=headers)
    hi = r.json()
    track_id = []
    track_name = []
    artist_name = []

    for i, t in enumerate(hi['tracks']['items']):
        track_id.append(t['id'])
        track_name.append(t['name'])
        artist_name.append(t['artists'][0]['name'])

    return track_id, track_name, artist_name


aki = Akinator()

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
        for c in self.children:
            c.disabled = True
        try:
            await interaction.response.edit_message(view=self)
        except (discord.NotFound, AttributeError):
            pass


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
        super().__init__(placeholder='Choose a category', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            em = discord.Embed(
                title="Nope",
                description="This command is not for you",
                color=main_color
            )
            return await interaction.response.send_message(embed=em, ephemeral=True)
        self.placeholder = f"{self.values[0]} Help Page"
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

        
class StartAkiView(discord.ui.View):
    def __init__(self, author):
        super().__init__()
        self.author = author
        self.questions = None
        self.message = None

    @discord.ui.button(
        emoji="\N{BLACK RIGHTWARDS ARROW}",
        label="Start",
        style=discord.ButtonStyle.green,
    )
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This isn't for you", ephemeral=True)
        self.questions = aki.question
        view = MainQuizView(questions=await aki.start())
        select = AkiAnsSelect(self.author)
        view.add_item(select)
        view.add_item(AkiAnsSubmit(view, select, interaction.user))
        await interaction.response.edit_message(embed=await view.embed(), view=view)

    @discord.ui.button(
        style=discord.ButtonStyle.danger, emoji="\N{CROSS MARK}"
    )
    async def close(self, inter: discord.Interaction, button):
        for c in self.children:
            c.disabled = True
        try:
            await inter.response.edit_message(view=self)
            await aki.close()
        except (discord.NotFound, AttributeError):
            pass


class MainQuizView(discord.ui.View):
    def __init__(
            self,
            questions):
        super().__init__()
        self.questions = questions

    async def embed(self):
        q = self.questions
        em = discord.Embed(color=discord.Color.blurple())
        em.description = f"**Question {aki.step + 1}\n{q}**"
        return em


class AkiAnsSelect(discord.ui.Select):
    def __init__(self, author):
        self.author = author
        options = [discord.SelectOption(label=answer,
                                        description="Is this your answer?",
                                        value=answer) for answer in ['yes', 'no', 'idk']]
        super().__init__(placeholder='Choose an answer', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This isn't for you", ephemeral=True)
        try:
            await interaction.response.send_message()
        except BaseException as i:
            print(i)
            pass


class AkiAnsSubmit(discord.ui.Button):
    def __init__(self, view: MainQuizView, select: discord.ui.Select, author):
        self._view = view
        self.select = select
        self.author = author
        super().__init__(
            style=discord.ButtonStyle.green,
            emoji="\N{BLACK RIGHTWARDS ARROW}",
            label="Submit",
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This isn't for you", ephemeral=True)
        if not self.select.values[0]:
            return
        while aki.progression <= 80:
            await aki.answer(self.select.values[0])
            view = MainQuizView(aki.question)
            s = AkiAnsSelect(interaction.user)
            view.add_item(s)
            view.add_item(AkiAnsSubmit(view, s, interaction.user))
            return await interaction.response.edit_message(embed=await view.embed(), view=view)
        await aki.win()
        embed2 = discord.Embed(title="Is this your character?", color=discord.Color.blurple())
        embed2.add_field(name=aki.first_guess['name'], value=f"{aki.first_guess['description']}"
                                                             f"\nRanking as **#{aki.first_guess['ranking']}**"
                                                             f"\n\n[yes (y) / no (n)]")
        embed2.set_image(url=aki.first_guess['absolute_picture_path'])
        await interaction.response.edit_message(embed=embed2, view=EndAkiView(interaction.user))
        await aki.close()


class EndAkiView(discord.ui.View):
    def __init__(self, author):
        super().__init__()
        self.author = author

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, emoji="👍")
    async def yes_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This isn't for you", ephemeral=True)
        url = "https://cdn.discordapp.com/attachments/937139620368511029/" \
              "995222789973872740/image_2022-07-09_015946256-removebg-preview.png"
        embed = discord.Embed(title="Damn right I won")
        embed.set_image(url=url)
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red, emoji="👎")
    async def no_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This isn't for you", ephemeral=True)
        url = "https://cdn.discordapp.com/attachments/937139620368511029/995228082036285520/unknown.png"
        embed = discord.Embed(title="Well Damn", color=discord.Color.blurple())
        embed.set_image(url=url)
        await interaction.response.edit_message(embed=embed, view=None)


class SpotifyTrack(discord.ui.View):
    def __init__(self, author):
        super().__init__()
        spotify_result = next((activity for activity in author.activities if isinstance(activity, discord.Spotify)),
                              None)
        self.add_item(discord.ui.Button(label="" + "Spotify".ljust(38, "\u2800"),
                                        url=str(spotify_result.track_url),
                                        emoji="<:spotify:995745517348859914>"))


class SpotifySelect(discord.ui.Select):
    def __init__(self, author, search):
        self.author = author
        ids, name, artists = get_track(search)
        options = [discord.SelectOption(label=f"{n}",
                                        description=a,
                                        emoji="<:spotify:995745517348859914>",
                                        value=i) for i, n, a in zip(ids, name, artists)]
        options[0].default = True
        super().__init__(options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This ain't for you", ephemeral=True)
        await interaction.response.edit_message(content=f"https://open.spotify.com/track/{self.values[0]}")


class SpotifyView(discord.ui.View):
    def __init__(self, author, search):
        super().__init__()
        self.author = author
        self.search = search

        self.add_item(SpotifySelect(self.author, search))
