import _io
import asyncio

from THISDLChatBot import Plugin
from THISDLChatBot import Bot
from THISDLChatBot import Message

plugin = Plugin('say hello')


async def onload():
    plugin.bot.logger.info('插件加载...')


@plugin.on_command('hello')
async def hello(bot: Bot, message: Message):
    await asyncio.sleep(10)
    image: _io.BufferedReader
    image = open('logo.jpg', 'rb')
    await bot.send_image(await message.get_from_user(), image)


@plugin.on_message()
async def log(bot: Bot, message: Message):
    bot.logger.info(message)


plugin.onload = onload
