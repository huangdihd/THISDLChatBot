import inspect

from . import Bot
from .Message import Message


class MessageProcessor:
    def __init__(self, func) -> None:
        self.func = func

    async def Process(self, message: Message, bot: Bot):
        accepted = inspect.signature(self.func).parameters
        arg = {k: v for k, v in {'message': message, 'bot': bot}.items() if k in accepted}
        await self.func(**arg)
