import _io
import asyncio
from THISDLChatBot.Plugin import Plugin
from THISDLChatBot.Bot import Bot
from THISDLChatBot.Message import Message


class TestPlugin(Plugin):
    async def on_load(self):
        self.bot.logger.info("load!")

    async def on_enable(self):
        self.bot.logger.info("enable!")

    async def on_disable(self):
        self.bot.logger.info("disable!")


plugin = TestPlugin('say hello')


@plugin.on_command('hello')
async def hello(bot: Bot, message: Message):
    await asyncio.sleep(10)
    image: _io.BufferedReader
    image = open('logo.jpg', 'rb')
    await bot.send_image(await message.get_from_user(), image)


@plugin.on_message()
async def log(bot: Bot, message: Message):
    bot.logger.info(message)
