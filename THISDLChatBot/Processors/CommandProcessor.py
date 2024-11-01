import inspect

from THISDLChatBot.Message import Message
from THISDLChatBot.Types import RoomType


class CommandProcessor:
    """命令处理器类"""
    def __init__(self, command: str, func, room_type: RoomType) -> None:
        """创建一个命令处理器"""
        self.command = command
        self.func = func
        self.room_type = room_type

    async def process(self, args: list, message: Message, bot) -> None:
        """处理命令的方法"""
        if message.get_room_type() != self.room_type and self.room_type is not None:
            return
        accepted = inspect.signature(self.func).parameters
        arg = {k: v for k, v in {'args': args, 'message': message, 'bot': bot}.items() if k in accepted}
        await self.func(**arg)
