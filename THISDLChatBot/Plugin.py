from .CommandProcessor import CommandProcessor
from .MessageProcessor import MessageProcessor


class Plugin:
    def __init__(self, name: str) -> None:
        self.name = name
        self.CommandProcessors = []
        self.MessageProcessors = []
        self.bot = None

    async def onload(self):
        pass

    def on_command(self, command: str):
        def command_processor(func):
            def wrapper():
                self.CommandProcessors.append(CommandProcessor(command, func))

            return wrapper()

        return command_processor

    def on_message(self):
        def message_processor(func):
            def wrapper():
                self.MessageProcessors.append(MessageProcessor(func))

            return wrapper()

        return message_processor


def load_plugin(plugin: str) -> Plugin:
    return __import__(plugin).plugin
