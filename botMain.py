import os
import discord
from dotenv import load_dotenv
from cthulu import Cthulu
from dice_roller import Roller

bot = discord.Bot()


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")


# Add cogs
bot.add_cog(Roller(bot))
bot.add_cog(Cthulu(bot))

load_dotenv()
bot.run(os.environ["token"])
