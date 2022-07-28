from types import FunctionType
from typing import Callable, Optional
import discord
from discord import Button, Interaction, commands, Bot, Option, Embed, Cog
from discord.ui import View, Item
from discord.commands.context import ApplicationContext

class CSkillResult:
    def __init__(self) -> None:
        pass

PushFunc = Callable[[str], CSkillResult]
class Cthulu(Cog):
    bot: Bot

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    class PushRoll(View):
        onPush: 
        rollStr: str

        def __init__(self, *items: Item, timeout: Optional[float] = 180, onPush: Cal):
            super().__init__(*items, timeout=timeout)
            