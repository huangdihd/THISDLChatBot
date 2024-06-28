from .CommandProcessor import CommandProcessor
from .MessageProcessor import MessageProcessor
from functools import wraps


class Plugin:
    """插件类"""
    def __init__(self, name: str) -> None:
        """创建一个插件对象"""
        self.name = name
        self.CommandProcessors = []
        self.MessageProcessors = []
        self.bot = None

    async def onload(self):
        pass

    def on_command(self, command: str):
        """用于绑定命令处理器的装饰器"""
        def command_processor(func):
            @wraps(func)
            def wrapper():
                self.CommandProcessors.append(CommandProcessor(command, func))

            return wrapper()

        return command_processor

    def on_message(self):
        """用于绑定消息处理器的装饰器"""
        def message_processor(func):
            @wraps(func)
            def wrapper():
                self.MessageProcessors.append(MessageProcessor(func))

            return wrapper()

        return message_processor


def load_plugin(plugin: str) -> Plugin:
    """用于获取某插件中的插件对象的函数"""
    pl = __import__(plugin)
    if '.' not in plugin:
        return pl.plugin
    for package in plugin.split('.')[1:]:
        pl = getattr(pl, package)
    return pl.plugin
