## 插件开发指南(GPT写的)

1. 在`plugins`目录中创建一个新的Python文件，取一个描述性的名字作为插件名称（例如`MyPlugin.py`）。

2. 在新的Python文件中定义你的插件类。这个类至少应该有以下三个方法：

   ```python
   class MyPlugin:
       # 类名需与不带后缀的文件名相同
       def onLoad(self, logger, bot):
           # 当插件被加载时调用此方法
           # 可以在这里初始化资源，设置配置等
           pass

       def onEnable(self, logger, bot):
           # 当插件被启用时调用此方法
           # 返回一个包含插件支持的命令字典的列表
           # 每个命令字典应该有 'command' 和 'def'  两个键。
           # 'command': 命令名称（例如 'hello'）(我补充一句:不用加斜杠!)。
           # 'description': 命令的简要描述。
           # 'def': 当命令被调用时要执行的函数。
           return [
               {'command': 'hello', 'def': self.say_hello}
           ]

       def onDisable(self, logger, bot):
           # 当插件被禁用或机器人关闭时调用此方法
           # 可以在这里清理资源或保存数据
           pass

       async def say_hello(self, args, bot, from_userid):
           # 当'/hello'命令被调用时执行此方法
           # 'args' 是一个包含命令后提供的参数的列表（例如 ['John']）。
           # 'bot' 是用于向聊天发送消息的机器人对象。
           # 'from_userid' 是发送命令的用户ID。
           # 在这里实现命令功能。
           # 例如：await bot.send('text', '你好！', from_userid)
           pass
   ```

3. 在插件的`onEnable`方法中，返回一个包含支持的命令字典的列表。根据插件的需求添加所需的命令。

4. `onLoad`方法在插件被加载时由机器人调用。你可以在此方法中初始化任何必要的资源，设置配置或进行其他必要的设置。

5. `onDisable`方法在插件被禁用或机器人关闭时被调用。你可以在此方法中清理资源或保存数据。

6. 定义`async def say_hello(self, args, bot, 
from_userid)`方法（或者其他你添加的命令方法），用于实现命令的功能。当对应的命令被调用时，该方法会被执行。使用`bot`对象发送聊天消息。

7. 在主脚本中注册你的插件。主脚本已经加载了`plugins`目录下的所有Python文件。确保你的插件文件遵循命名规范，并包含一个有效的插件类。

8. 重启机器人来测试你的插件，它应该加载你的插件，并提供你定义的命令。

9. 你可以根据需要添加更多命令或实现其他功能。

10. 记得在你的插件中优雅地处理错误，因为它将在与其他插件并发运行的环境中执行。

有了这个指南，你应该能够开始为聊天机器人开发自定义插件，并根据需要扩展其功能。
