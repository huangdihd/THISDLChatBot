import THISDLChatBot
from THISDLChatBot.Plugin import load_plugin

logger = THISDLChatBot.Logger()
config = THISDLChatBot.Config()
if config.config == {}:
    config.create_guide(logger)
bot = THISDLChatBot.Bot(config, logger)
bot.load_plugin(load_plugin('testplugin'))
bot.start()

