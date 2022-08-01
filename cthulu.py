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
    # Success thresholds
    threshold: int = 0
    hard_thresh: int = math.floor(threshold / 2)
    extreme_thresh: int = math.floor(threshold / 5)

    # Roll values
    tens: DiceResult
    ones: DiceResult
    has_bonus: bool
    pushed: bool

    # Dice string rolled
    roll_str: str

    def __init__(
        self,
        query: str,
        threshold: int,
        tens: DiceResult,
        ones: DiceResult,
        has_bonus: bool = False,
        pushed: bool = False,
    ) -> None:
        self.threshold = threshold
        self.tens = tens
        self.ones = ones
        self.has_bonus = has_bonus
        self.roll_str = query
        self.pushed = pushed

    def get_tens_val(self) -> int:
        return self.tens.max() if self.has_bonus else self.tens.min()

    def get_roll(self) -> int:
        ten_val = self.get_tens_val()
        one_val = self.ones.max()
        return ten_val + one_val

    def get_embed(self) -> Embed:
        em = Embed(title=self.get_success())

        # Values needed for footer
        tens_vals = "/".join(str(x) for x in self.tens)
        em.footer = f"""Roll: {self.roll_str}
Result: {self.get_tens_val()} ({tens_vals}) + {self.ones.max()} = {self.get_roll()}"""

    # TODO: Add colors (probs return tuple)
    def get_success(self, improvement: bool = False) -> str:
        roll = self.get_roll()
        if improvement:
            return (
                "Improvement Success!" if roll > self.threshold else "Improvment Fail!"
            )

        # Don't want to invert success value since improvement checks can't have criticals
        if roll == 1:
            return "Critical Success!"
        elif roll == 100:
            return "Critical Fail!"
        elif roll <= self.extreme_thresh:
            return "Extreme Success!"
        elif roll <= self.hard_thresh:
            return "Hard Success!"
        elif roll <= self.threshold:
            return "Success"
        else:
            return "Failure"


PushFunc = Callable[[str], CSkillResult]


class Cthulu(Cog):
    bot: Bot

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    class PushRoll(View):
        on_push: PushFunc
        original: CSkillResult

        def __init__(
            self,
            *items: Item,
            timeout: Optional[float] = 180,
            on_push: PushFunc,
            original: CSkillResult,
        ):
            super().__init__(*items, timeout=timeout)
            self.on_push = on_push
            self.original = original

        @discord.ui.button(label="Push Roll", style=discord.ButtonStyle.primary)
        async def button_callback(self, button: Button, interaction: Interaction):
            result = self.on_push(self.original.roll_str)
            interaction.message.reply(embed=result.get_embed())

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

    def parse_roll(self, dice: str) -> CSkillResult:
        if dice.__contains__("p") and dice.__contains__("b"):
            return None

        match = re.search("(\d*?)([pb]*)(\d+)")
        if match == None:
            return None

        [pb_dice, pb, threshold] = match.groups()
        if pb_dice == "":
            pb_dice = 1

        roller: Roller = self.bot.get_cog("Roller")
        tensRolls = roller.roll_die(rolls=pb_dice + 1, die_num=10)
        onesRoll = roller.roll_die(rolls=1, die_num=10)
        bonus = pb == "p"
        result = CSkillResult(
            query=dice,
            has_bonus=bonus,
            pushed=False,
            threshold=threshold,
            ones=onesRoll,
            tens=tensRolls,
        )

        return result

    @commands.command(guild_ids=[TEST_GUILD], description="")
    async def croll(
        self,
        ctx: ApplicationContext,
        dice: Option(
            str,
            description="Dice to roll. Enter 'help' for more details",
            required=True,
        ),
    ) -> None:
        print(f"\nCthulu check for {ctx.author}: {dice}")
        if dice == "help" or dice.strip() == "":
            print("Got help")
            await ctx.respond(self.HELP)
            return

        result = self.parse_roll(dice)
        if result == None:
            print("ID10T Error, got help")
            await ctx.respond(
                "Cannot understand dice string. Have some help: " + self.HELP
            )
            return

        print(f"Rolled {result.get_roll()}")
        button = self.PushRoll(on_push=self.parse_roll, original=result)
        await ctx.respond(embed=result.get_embed(), view=button)
