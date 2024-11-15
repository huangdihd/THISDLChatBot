"""实例入口文件"""
from THISDLChatBot.Bot import Bot
from THISDLChatBot.Config import ChatBotConfig
from THISDLChatBot.Logger import Logger
from THISDLChatBot.Plugin import load_plugin

# 创建日志logger对象
logger = Logger()
# 创建配置文件对象
config = ChatBotConfig()
# 当没有配置文件时运行创建向导
config.create_guide(logger)
# 创建机器人对象
bot = Bot(config, logger)
# 加载testplugin插件
bot.load_plugin(load_plugin('testplugin'))
# 启动机器人
bot.start()
