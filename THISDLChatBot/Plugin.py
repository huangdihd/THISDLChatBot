import asyncio

from .Processors import CommandProcessor
from .Processors import MessageProcessor
from .Message import Message
from functools import wraps
from abc import ABC, abstractmethod

from .Types import MessageType, RoomType


class Plugin(ABC):
    """插件类"""
    def __init__(self, name: str) -> None:
        """创建一个插件对象"""
        self.name = name
        self.CommandProcessors = {}
        self.MessageProcessors = []
        self.bot = None

    @abstractmethod
    async def on_load(self):
        """插件加载时会调用的方法"""
        pass

    @abstractmethod
    async def on_enable(self):
        """插件启用时会调用的方法"""
        pass

    @abstractmethod
    async def on_disable(self):
        """插件卸载时会调用的方法"""
        pass

    def on_command(self, command: str, alias: list[str] = None, room_type: RoomType = None):
        """用于绑定命令处理器的装饰器"""
        def command_processor(func):
            @wraps(func)
            def wrapper():
                commands = alias if alias is not None else [command]
                for cmd in commands:
                    if cmd not in self.CommandProcessors:
                        self.CommandProcessors[cmd] = []
                    self.CommandProcessors[cmd].append(CommandProcessor(cmd, func, room_type))

            return wrapper()

        return command_processor

    def on_message(self, message_type: MessageType = None, room_type: RoomType = None):
        """用于绑定消息处理器的装饰器"""
        def message_processor(func):
            @wraps(func)
            def wrapper():
                self.MessageProcessors.append(MessageProcessor(func, message_type, room_type))

            return wrapper()

        return message_processor

    def process_command(self, message: Message):
        """用于处理命令的函数"""
        if message.get_data().split(' ')[0][1:] not in self.CommandProcessors:
            return
        for commandProcessor in self.CommandProcessors[message.get_data().split(' ')[0][1:]]:
            asyncio.create_task(
                commandProcessor.process((message.get_data() + ' ').split(' ')[1:-1], message, self.bot))

    def process_message(self, message: Message):
        """用于处理消息的函数"""
        for messageProcessor in self.MessageProcessors:
            asyncio.create_task(messageProcessor.process(message, self.bot))


def load_plugin(plugin: str) -> Plugin:
    """用于获取某插件中的插件对象的函数"""
    pl = __import__(plugin)
    if '.' not in plugin:
        return pl.plugin
    for package in plugin.split('.')[1:]:
        pl = getattr(pl, package)
    return pl.plugin
