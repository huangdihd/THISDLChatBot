import inspect

from THISDLChatBot.Message import Message
from THISDLChatBot.Types import MessageType, RoomType


class MessageProcessor:
    """消息处理器类"""
    def __init__(self, func, message_type: MessageType = None, room_type: RoomType = None) -> None:
        """创建一个消息处理器"""
        self.func = func
        self.message_type = message_type
        self.room_type = room_type

    async def process(self, message: Message, bot) -> None:
        """处理消息的方法"""
        if message.get_type() != self.message_type and self.message_type is not None:
            return
        if message.get_room_type() != self.room_type and self.room_type is not None:
            return
        accepted = inspect.signature(self.func).parameters
        arg = {k: v for k, v in {'message': message, 'bot': bot}.items() if k in accepted}
        await self.func(**arg)
