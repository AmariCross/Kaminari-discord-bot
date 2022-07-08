import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from views import Next
from discord.app_commands import Choice


class Api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__class__.__name__} Cog has been loaded")

    @app_commands.command(name="meme", description="Sends random memes")
    async def meme(self, interaction) -> None:
        meme_url = "https://meme-api.herokuapp.com/gimme"

        async def meme_opt():
            async with aiohttp.request('GET', meme_url, headers={}) as response:
                res = await response.json()
                title = res["title"]
                link = res["postLink"]
                memes = discord.Embed(title=f"{title}", url=link, colour=discord.Colour.from_rgb(148, 150, 255))
                memes.set_image(url=res["url"])
                return memes

        embed = await meme_opt()
        view = Next(meme_opt, interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="animal",
                          description="Send a random pic of an animal with any of the choices provided!")
    @app_commands.describe(animal="The animal you want to get random pics of!")
    @app_commands.choices(animal=[
        Choice(name="cat", value="cat"),
        Choice(name="dog", value="dog"),
        Choice(name="panda", value="panda"),
        Choice(name="fox", value="fox"),
        Choice(name="red panda", value="red_panda"),
        Choice(name="koala", value="koala"),
        Choice(name="bird", value="birb"),
        Choice(name="raccoon", value="raccoon"),
        Choice(name="kangaroo", value="kangaroo")
    ])
    async def ani(self, interaction, animal: str):
        url = f"https://some-random-api.ml/animal/{animal}"

        async def animal_opt():
            async with aiohttp.request('GET', url, headers={}) as response:
                data = await response.json()
                image = data['image']
                embed = discord.Embed(title='YES YES YES YES 😎')
                embed.set_image(url=image)
                return embed

        em = await animal_opt()
        view = Next(animal_opt, interaction.user)
        await interaction.response.send_message(embed=em, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Api(bot))
