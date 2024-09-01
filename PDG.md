# 插件开发指南

## 给机器人编写插件主要有一下步骤
### 1. 继承并创建自己的插件类
### 2. 创建插件实例
### 3. 绑定命令和消息处理器

## 1.创建插件对象
#### 继承使用`Plugin.py`中的`Plugin`抽象类可以方便的创建自己的插件类
```python
from THISDLChatBot.Plugin import Plugin
from THISDLChatBot.Bot import Bot
from THISDLChatBot.Message import Message

# 继承抽象类Plugin
class TestPlugin(Plugin):
    # 插件加载时调用的方法,必须重写
    async def on_load(self):
        self.bot.logger.info("load!")
        
    # 插件启用时调用的方法,必须重写
    async def on_enable(self):
        self.bot.logger.info("enable!")
    
    # 插件卸载时调用的方法,必须重写
    async def on_disable(self):
        self.bot.logger.info("disable!")

```

## 2.创建插件实例
#### 使用Plugin.py中的load_plugin方法加载的插件会默认获取一个名为plugin的插件对象,需要创建自己的插件插件实例
```python
# 变量名必须是plugin
plugin = TestPlugin('say hello')
```

## 3.绑定命令和消息处理器
#### 当创建好插件对象后,可以使用插件对象的`on_command`和`on_message`装饰器绑定,如:
#### 命令处理器:
```python
@plugin.on_command('hello')
# 当好友发送命令/hello时向好友发送logo.jpg
async def hello(bot: Bot, message: Message):
    # 打开logo.jpg
    image = open('logo.jpg', 'rb')
    # 将它发送到发来命令的好友
    await bot.send_image(await message.get_from_user(), image)
```
#### 消息处理器:
````python
@plugin.on_message()
# 当收到消息时输出日志
async def log(bot: Bot, message: Message):
    # 输出消息的详细信息
    bot.logger.info(message)
````

## 进阶
#### 如果您想更加深入的了解如bot的方法等内容,可以去翻包中各个类的源码,在这里就不一个个解释了

## 还是不懂?
#### 可以查看[testplugin](https://github.com/huangdihd/THISDLChatBot/blob/main/testplugin.py)或者联系作者邮箱`hd20100104@163.com`寻求帮助