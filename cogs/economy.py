import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime

main_color = discord.Colour.from_rgb(148, 150, 255)


async def fetchData(bot, _id):
    collection = bot.mongoConnect.ecom.ecom
    if await collection.find_one({"_id": _id}) is None:
        newData = {
            "_id": _id,
            "wallet": 0,
            "bank": 0
        }
        await collection.insert_one(newData)
    return await collection.find_one({"_id": _id}), collection


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__class__.__name__} Cog has been loaded")

    @app_commands.command(name="balance", description="Use this command to find the balance of a user")
    @app_commands.describe(member="You can try to find the balance of an another user using this if you would like to")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user
        userData, collection = await fetchData(self.bot, str(member.id))
        embed = discord.Embed(color=discord.Colour.from_rgb(148, 150, 255), timestamp=datetime.datetime.utcnow())
        embed.add_field(name=f"{member.display_name}'s balance", value=f"""
        Bank: ${"{:,}".format(userData['bank'])}
        Wallet: ${"{:,}".format(userData['wallet'])}
        """)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="beg", description="This command is for coins and you get a random chance of getting "
                                                  "between $500 and $1000")
    async def beg(self, interaction: discord.Interaction):

        moneyReceived = random.randint(500, 1000)

        userData, collection = await fetchData(self.bot, str(interaction.user.id))

        await collection.update_one({"_id": str(interaction.user.id)}, {"$inc": {"wallet": moneyReceived}})

        await interaction.response.send_message(f"You've received {moneyReceived} coins")

    @app_commands.command(name="deposit", description="Deposit money from your wallet to your bank account")
    async def deposit(self, interaction: discord.Interaction, money: str):
        userData, collection = await fetchData(self.bot, str(interaction.user.id))
        embed = discord.Embed(colour=discord.Colour.from_rgb(148, 150, 255))

        if userData['wallet'] >= int(money):
            await collection.update_one({"_id": str(interaction.user.id)}, {"$inc": {"bank": int(money)}})
            await collection.update_one({"_id": str(interaction.user.id)}, {"$inc": {"wallet": -int(money)}})
            embed.add_field(name='Deposited', value=f"`${money}`", inline=False)
            embed.add_field(name="Current Wallet Balance", value=f"`${userData['wallet'] - int(money)}`", inline=True)
            embed.add_field(name="Current Bank Balance", value=f"`${userData['bank'] + int(money)}`", inline=True)
        else:
            embed.add_field(name="Depositing Error",
                            value=f"This is over the amount you have in your wallet({userData['wallet']})")
            embed.colour = discord.Colour.red()
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="withdraw", description="Withdraw some money from your bank account to your wallet")
    async def withdraw(self, interaction: discord.Interaction, money: str):
        userData, collection = await fetchData(self.bot, str(interaction.user.id))
        embed = discord.Embed(colour=discord.Colour.from_rgb(148, 150, 255))

        if userData['bank'] >= int(money):
            await collection.update_one({"_id": str(interaction.user.id)}, {"$inc": {"wallet": int(money)}})
            await collection.update_one({"_id": str(interaction.user.id)}, {"$inc": {"bank": -int(money)}})
            embed.add_field(name='Withdrew', value=f"`${money}`", inline=False)
            embed.add_field(name="Current Wallet Balance", value=f"`${userData['wallet'] + int(money)}`", inline=True)
            embed.add_field(name="Current Bank Balance", value=f"`${userData['bank'] - int(money)}`", inline=True)
        else:
            embed.add_field(name="Withdrawing Error",
                            value=f"This is over the amount you have in your bank(${userData['bank']})")
            embed.colour = discord.Colour.red()
        await interaction.response.edit_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
