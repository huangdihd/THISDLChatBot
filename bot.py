import THISDLChatBot
from THISDLChatBot.Plugin import LoadPlugin

logger = THISDLChatBot.Logger()
config = THISDLChatBot.Config()
if config.config == {}:
    config.CreateGuide(logger)
bot = THISDLChatBot.Bot(config, logger)
bot.LoadPlugin(LoadPlugin('testplugin'))
bot.start()

