import discord
from dice_roller import Roller

bot = discord.Bot()

@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")

# Add cogs
bot.add_cog(Roller(bot))

bot.run("OTk5NDk4NzQzNTU0NTE1MDY0.GCm5bc.59cElP3XLBBnun_A9Qp5d37m2Vk-QUlCPGkDqo")
