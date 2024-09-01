import inspect

from .Message import Message


class MessageProcessor:
    """消息处理器类"""
    def __init__(self, func) -> None:
        """创建一个消息处理器"""
        self.func = func

    async def process(self, message: Message, bot):
        """处理消息的方法"""
        accepted = inspect.signature(self.func).parameters
        arg = {k: v for k, v in {'message': message, 'bot': bot}.items() if k in accepted}
        await self.func(**arg)
