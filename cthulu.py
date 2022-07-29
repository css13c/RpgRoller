import math
import re
from types import FunctionType
from typing import Callable, List, Optional
import discord
from discord import Button, Interaction, commands, Bot, Option, Embed, Cog
from discord.ui import View, Item
from discord.commands.context import ApplicationContext

from constants import TEST_GUILD
from dice_roller import DiceResult, Roller

class CSkillResult:
    threshold: int = 0
    tens: DiceResult
    ones: DiceResult
    hardThresh: int = math.floor(threshold / 2)
    expertThresh: int = math.floor(threshold / 5)

    def __init__(self, threshold: int) -> None:
        self.threshold = threshold

    def getEmbed() -> Embed:
        return discord.Embed()

PushFunc = Callable[[str], CSkillResult]
class Cthulu(Cog):
    bot: Bot

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    class PushRoll(View):
        onPush: PushFunc
        rollStr: str

        def __init__(self, *items: Item, timeout: Optional[float] = 180, onPush: PushFunc, rollStr: str):
            super().__init__(*items, timeout=timeout)
            self.onPush = onPush
            self.rollStr = rollStr

        @discord.ui.button(label="Push Roll", style=discord.ButtonStyle.primary)
        async def button_callback(self, button: Button, interaction: Interaction):
            result = self.onPush(self.rollStr)
            interaction.message.reply(embed=result.getEmbed())

    HELP = """```
/croll [diceCount=1][p|b][skillThreshold]

Dice Types:
    p - Penalty Dice
    b - Bonus Dice

You can't use both penalty and bonus dice in the same roll

Examples:
    /croll 50
    Success = 44

    /croll b50
    Success = 30/60 + 4

    /croll p30
    Failure = 10/60 + 7
```
"""

    async def handleRoll(self, pbDie: int, penalty: bool, thresh: int) -> CSkillResult:
        result = CSkillResult()
        roller: Roller = self.bot.get_cog("Roller")
        tensRolls = roller.roll_die(pbDie + 1, 10)

    async def parseRoll(self, dice: str) -> CSkillResult:
        if dice.__contains__("p") and dice.__contains__("b"):
            return None

        match = re.search("(\d*?)([pb]*)(\d+)")
        if match == None:
            return None

        [pbDice, pb, threshold] = match.groups()
        if pbDice == "":
            pbDice = 1

        return self.handleRoll(pbDice, pb == "p", threshold)

    @commands.command(guild_ids=[TEST_GUILD], description="")
    async def croll(
        self,
        ctx: ApplicationContext,
        dice: Option(str, description="Dice to roll. Enter 'help' for more details", required=True)
    ) -> None:
        print(f"\nCthulu check for {ctx.author}: {dice}")
        if dice == "help" or dice.strip() == "":
            print("Got help")
            await ctx.respond(self.HELP)
            return

        result = self.parseRoll(dice)
        if result == None:
            print("ID10T Error, got help")
            await ctx.respond("Cannot understand dice string. Have some help: " + self.HELP)
            return