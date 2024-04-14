from .CommandProcessor import CommandProcessor
from .MessageProcessor import MessageProcessor

class Plugin:
    def __init__(self, name: str) -> None:
        self.name = name
        self.CommandProcessors = []
        self.MessageProcessors = []
        self.bot = None

    async def OnLoad(self):
        pass

    def OnCommand(self, command: str):
        def commandProcessor(func):
            def wrapper():
                self.CommandProcessors.append(CommandProcessor(command, func))
            return wrapper()
        return commandProcessor

    def OnMessage(self):
        def messageProcessor(func):
            def wrapper():
                self.MessageProcessors.append(MessageProcessor(func))
            return wrapper()
        return messageProcessor


def LoadPlugin(plugin: str) -> Plugin:
    return __import__(plugin).plugin
