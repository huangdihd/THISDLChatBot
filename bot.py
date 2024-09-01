"""实例入口文件"""
import THISDLChatBot
from THISDLChatBot.Plugin import load_plugin
from THISDLChatBot.Bot import Bot
from THISDLChatBot.Logger import Logger
from THISDLChatBot.Config import Config

# 创建日志logger对象
logger = Logger()
# 创建配置文件对象
config = Config()
# 当没有配置文件时运行创建向导
if config.config == {}:
    config.create_guide(logger)
# 创建机器人对象
bot = Bot(config, logger)
# 加载testplugin插件
bot.load_plugin(load_plugin('testplugin'))
# 启动机器人
bot.start()
