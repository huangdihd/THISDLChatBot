# 插件开发指南

## 给机器人编写插件主要有一下步骤
### 1. 创建插件对象
### 2. 设置on_load方法
### 3. 绑定命令和消息处理器

## 1.创建插件对象
#### 使用`Plugin.py`中的`load_plugin`方法加载的插件会默认获取一个名为`plugin`的插件对象,可以通过`plugin = Plugin([插件名称])`来进行创建

## 2.设置on_load方法
#### 机器人加载插件时会调用插件的on_load方法,默认只有pass,可以直接自己写一个函数然后赋值也可以继承后重写

## 3.绑定命令和消息处理器
#### 当创建好插件对象后,可以使用插件对象的`on_command`和`on_message`装饰器绑定,如:
#### 命令处理器:
```python
@plugin.on_command('hello')
async def hello(bot: Bot, message: Message):
    # 打开logo.jpg
    image = open('logo.jpg', 'rb')
    # 将它发送到发来命令的好友
    await bot.send_image(await message.get_from_user(), image)
```
#### 消息处理器:
````python
@plugin.on_message()
async def log(bot: Bot, message: Message):
    # 输出消息的详细信息
    bot.logger.info(message)
````

## 进阶
#### 如果您想更加深入的了解如bot的方法等内容,可以去翻包中各个类的源码,在这里就不一个个解释了

## 还是不懂?
#### 可以查看[testplugin](https://github.com/huangdihd/THISDLChatBot/blob/main/testplugin.py)或者联系作者邮箱`hd20100104@163.com`寻求帮助