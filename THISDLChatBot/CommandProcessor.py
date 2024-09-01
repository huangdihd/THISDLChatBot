import inspect

from .Message import Message


class CommandProcessor:
    """命令处理器类"""
    def __init__(self, command: str, func) -> None:
        """创建一个命令处理器"""
        self.command = command
        self.func = func

    async def process(self, args: list, message: Message, bot):
        """处理命令的方法"""
        accepted = inspect.signature(self.func).parameters
        arg = {k: v for k, v in {'args': args, 'message': message, 'bot': bot}.items() if k in accepted}
        await self.func(**arg)
