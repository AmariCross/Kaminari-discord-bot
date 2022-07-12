import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from views import StartAkiView
import dateutil.parser
from easy_pil import Editor, Font, load_image, Canvas
from PIL import Image
import requests
import os
from views import SpotifyView, SpotifyTrack


async def get_track(search: str):
    search = search.replace(" ", "+")
    AUTH_URL = 'https://accounts.spotify.com/api/token'

    # POST, don't mind the requests just don't mind
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
    url = f"https://api.spotify.com/v1/search?q={search}&type=track&limit=25"
    async with aiohttp.request("GET", url=url, headers=headers) as response:
        data = await response.json()
        track_id = []
        track_name = []
        artist_name = []

        for i, t in enumerate(data['tracks']['items']):
            track_id.append(t['id'])
            track_name.append(t['name'])
            artist_name.append(t['artists'][0]['name'])

    return track_id, track_name, artist_name


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__class__.__name__} Cog has been loaded")

    @app_commands.command(name="akinator",
                          description="An akinator command aki asks some questions he has to guess the "
                                      "character you want him to guess")
    async def akinator(self, interaction):
        embed = discord.Embed(title="Start the quiz")
        view = StartAkiView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_message()

    @app_commands.command(name="spotify",
                          description="Get what is now being played by the a user you mention or yourself")
    @app_commands.describe(user="The person you want to check to see what they are playing in spotify")
    async def spotify(self, interaction, user: discord.Member = None):
        user = user or interaction.user
        member = discord.Guild.get_member(interaction.guild, user.id)
        spotify_result = next((activity for activity in member.activities if isinstance(activity, discord.Spotify)),
                              None)

        if spotify_result is None:
            return await interaction.response.send_message(f'{member.name} is not listening to Spotify.')
        track_background_image = Editor("spotify_template.png")
        album_image = Editor(load_image(str(spotify_result.album_cover_url)))

        title_font = Font.montserrat(variant="bold", size=16)
        artist_font = Font.montserrat(variant="bold", size=14)
        album_font = Font.montserrat(variant="bold", size=14)
        start_duration_font = Font.montserrat(variant="bold", size=12)
        end_duration_font = Font.montserrat(variant="bold", size=12)

        # Positions
        title_text_position = (150, 30)
        artist_text_position = (150, 60)
        album_text_position = (150, 80)
        start_duration_text_position = (150, 122)
        end_duration_text_position = (515, 122)

        track_background_image.text(title_text_position, spotify_result.title, font=title_font, color="white")
        track_background_image.text(artist_text_position, f'by {spotify_result.artist}', font=artist_font,
                                    color="white")
        track_background_image.text(album_text_position, spotify_result.album, font=album_font, color="white")
        track_background_image.text(start_duration_text_position, '0:00', font=start_duration_font, color="white")
        track_background_image.text(end_duration_text_position,
                                    f"{dateutil.parser.parse(str(spotify_result.duration)).strftime('%M:%S')}",
                                    font=end_duration_font, color="white")

        # background color stuff
        temp_image = Image.open(fp=album_image.image_bytes)
        temp_image_rgb = temp_image.convert("RGB")

        album_color = temp_image_rgb.getpixel((250, 100))

        background_image_color = Editor(Canvas((571, 156), color=album_color))
        background_image_color.paste(track_background_image, (0, 0))

        # Resize
        album_image_resize = album_image.resize((140, 160))
        background_image_color.paste(album_image_resize, (0, 0))

        file = discord.File(fp=background_image_color.image_bytes, filename="track.png")
        view = SpotifyTrack(member)

        await interaction.response.send_message(
            f"<:spotify:995745517348859914> {interaction.user}, listening to **{spotify_result.title}** by "
            f"**{spotify_result.artist}**", file=file, view=view)

    @app_commands.command(name="track", description="Using this command you search for a song in spotify within my bot")
    @app_commands.describe(search="The song your searching for")
    async def track(self, interaction, search: str):
        ids, name, artist = await get_track(search)
        view = SpotifyView(interaction.user, search)
        await interaction.response.send_message(f"https://open.spotify.com/track/{ids[0]}", view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
