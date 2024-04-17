import asyncio

from THISDLChatBot import Plugin
from THISDLChatBot import Bot
from THISDLChatBot import Message

plugin = Plugin('say hello')


async def OnLoad():
    plugin.bot.logger.info('插件加载...')


@plugin.OnCommand('hello')
async def hello(bot: Bot, message: Message):
    await asyncio.sleep(10)
    await bot.SendImage(await message.GetFromUser(), open('logo.jpg', 'rb'))


@plugin.OnMessage()
async def log(bot: Bot, message: Message):
    bot.logger.info(message)


plugin.OnLoad = OnLoad
