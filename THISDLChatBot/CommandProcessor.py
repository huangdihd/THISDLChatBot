import inspect

from . import Bot
from .Message import Message


class CommandProcessor:
    def __init__(self, command: str, func) -> None:
        self.command = command
        self.func = func

    async def Process(self, args: list, message: Message, bot: Bot):
        accepted = inspect.signature(self.func).parameters
        arg = {k: v for k, v in {'args': args, 'message': message, 'bot': bot}.items() if k in accepted}
        await self.func(**arg)
