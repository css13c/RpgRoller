import random
import discord
from discord import Button, Interaction, commands, Bot, Option, Embed, Cog
from discord.ui import View, Item
from discord.commands.context import ApplicationContext
from constants import COL_ROLL, TEST_GUILD
from typing import List, Optional

class DiceResult:
    die: str
    rolls: List[int]
    total: int

    def __init__(self, dice: str = "", total: int = 0) -> None:
        self.die = dice
        self.rolls = []
        self.total = total

    def __str__(self) -> str:
        return f"Rolls for {self.die}: [{','.join(str(x) for x in self.rolls)}] = {self.total}"

    def getSumRolls(self) -> str:
        if self.rolls == []:
            return str(self.total)
        else:
            return f"({'+'.join(str(x) for x in self.rolls)})"

    def addRoll(self, roll: int) -> None:
        self.rolls.append(roll)
        self.total += roll

    def max(self) -> int:
        return max(self.rolls)

    def min(self) -> int:
        return min(self.rolls)

class RollResult:
    dice: List[DiceResult]

    def __init__(self) -> None:
        self.dice = []
    
    def __str__(self) -> str:
        return self.total()

    def add(self, die: DiceResult) -> None:
        self.dice.append(die)

    def total(self) -> int:
        return sum([x.total for x in self.dice])

    class RollList:
        def __init__(self, rolls: List[int], die: str) -> None:
            self.rolls = rolls
            self.die = die

    def rolls(self) -> List[RollList]:
        return [self.RollList(x.rolls, x.die) for x in self.dice]

    def output(self) -> str:
        return " + ".join(r.getSumRolls() for r in self.dice)


def get_breakdown(dice: str, rolls: DiceResult) -> str:
    return dice + "\n" + rolls.output()

class Roller(Cog):
    bot: Bot

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    class BdButton(View):
        rolls: DiceResult
        dice: str
        active: bool

        show_label = "Show breakdown"
        hide_label = "Hide breakdown"

        def __init__(self, *items: Item, timeout: Optional[float] = 180, rolls: DiceResult, dice: str):
            super().__init__(*items, timeout=timeout)
            self.rolls = rolls
            self.dice = dice
            self.active = False

        @discord.ui.button(label=show_label, style=discord.ButtonStyle.primary)
        async def button_callback(self, button: Button, interaction: Interaction):
            current = interaction.message.embeds[0]
            em = Embed(title=current.title, color=COL_ROLL)
            if self.active:
                button.label=self.show_label
                em.remove_footer()
            else:
                button.label=self.hide_label
                em.set_footer(text=get_breakdown(self.dice, self.rolls))

            self.active = not self.active
            await interaction.response.edit_message(embed=em, view=self)

    HELP = """```
/roll [[diceCount=1]d[diceSize]] + more dice or number

You can also use 'breakdown' = True to see all the rolls

Examples:
    /roll d6
    5
    
    /roll 3d6 + 1d4
    12
    
    /roll 6d6 + 2
    25
    
    /roll 2d10 + 5 True
    10
    (3 + 2) + 5
```
"""

    def parseRoll(self, dice: str) -> DiceResult:
        try:
            split = dice.strip().split()
            result = RollResult()
            for die in split:
                if die == "+":
                    continue
                elif die.isdigit():
                    result.add(DiceResult(die, int(die)))
                else:
                    roll = self.roll_die_str(die)
                    result.add(roll)

            return result 
        except Exception:
            return None

    def roll_die_str(self, diceStr: str) -> DiceResult:
        splitDice = diceStr.split("d")
        [rolls, dieNumStr] = splitDice
        if rolls == "":
            rolls = 1

        result = DiceResult(dice = diceStr)
        dieNum = int(dieNumStr)
        for _ in range(int(rolls)):
            result.addRoll(random.randint(1, dieNum))

        return result

    def roll_die(self, dieNum: int, rolls: int = 1) -> DiceResult:
        result = DiceResult(dice = f"{rolls}d{dieNum}")
        for _ in range(rolls):
            result.addRoll(random.randint(1, dieNum))

        return result

    @commands.command(guild_ids=[TEST_GUILD], description="Rolls dice.")
    async def roll(
        self,
        ctx: ApplicationContext,
        dice: Option(str, description="Dice to roll. Enter 'help' for more details", required=True),
        bd: Option(bool, name="breakdown", description="Shows all values rolled to reach the result", default=False)
    ) -> None:
        print(f"\n{ctx.author} rolled {dice}")
        if dice == "help" or dice.strip() == "":
            print(f"Got help")
            await ctx.respond(self.HELP)
            return

        result = self.parseRoll(dice)
        if result == None:
            print(f"ID10T Error, got help")
            await ctx.respond("Cannot understand dice rolled. Here's some help: " + self.HELP)
            return

        desc = f"{dice}"
        if bd:
            desc += '\n' + result.output()

        total = result.total()
        print(f"Rolled {total}")
        em = Embed(title=f"{total}", color=COL_ROLL)
        button = None
        if bd:
            em.set_footer(text=self.get_breakdown(dice, result))
        else:
            button = self.BdButton(rolls=result, dice=dice)

        await ctx.respond(embed=em, view=button)