## 插件开发指南(GPT写的)

# 在`plugins`目录中创建一个新的Python文件，取一个描述性的名字作为插件名称（例如`MyPlugin.py`）。

   ## 1. 在新的Python文件中定义你的插件类。这个类至少应该有以下三个方法:
```python
class MyPlugin:
    # 类名需与不带后缀的文件名相同
    def onLoad(self, logger, bot):
        # 当插件被加载时调用此方法
        # 可以在这里初始化资源，设置配置等
        pass

    def onEnable(self, logger, bot):
        # 当插件被启用时调用此方法。
        # 返回一个包含插件支持的命令和消息处理的字典。
        # 每个命令字典应该有 'commands' 和 'messages' 两个键。
        # 'commands': 一个列表,应含有一个或多个命令描述词典。
        # 命令描述词典应该有 'command' 和 'def' 两个键。
        # 'command': 命令名称,如 'hello' (不加首位的'/')。
        # 'def': 当命令被调用时要执行的函数。
        # 'messages': 一个列表,应含有一个或多个消息处理描述词典。
        # 消息处理描述词典应该有 'def' 键。
        # 'def': 当有人发消息时时要执行的函数。
        return {'commands': [
                   {'command': 'hello', 'def': self.say_hello}
                   ], 'messages': [
                   {'def': self.write_file}
                   ]
               }

    def onDisable(self, logger, bot):
        # 当插件被禁用或机器人关闭时调用此方法
        # 可以在这里清理资源或保存数据
        pass

    async def say_hello(self, logger, args, bot, from_userid, group):
        # 当'/hello'命令被调用时执行此方法
        # 'logger' 是一个日志输出对象,可以用logger.success()、logger.info()、logger.warn()、logger.error()、logger.input()、logger.password()来输入或输出输出对应等级的日志
        # 'args' 是一个包含命令后提供的参数的列表（例如 ['John']）。
        # 'bot' 是用于向聊天发送消息的机器人对象。
        # 'from_userid' 是发送命令的用户ID。
        # 'group' 是群号,如果不是群就是None
        # 在这里实现命令功能。
        # 这里使用bot.send()方法发送了一个'你好!'
        # 'type' 是消息类型,有text(文本),image(图片),file(文件)几个类型
        # 'data' 是内容,是文件或图片的话请用open('路径', 'rb')打开
        # 'to_userid' 是接收者的userid,'group' 不是None则不生效
        # 'group' 是发送的群号,为None则是私聊
        await bot.send(type='text', data='你好！', to_userid=from_userid, group=group)

    async def write_file(self, message_type, logger, message, bot, from_userid, group):
        # 当有人发消息时时执行此方法
        # 'message_type' 是消息的类型, 有text(文本), file(文件), image(图片), html, gif(表情), recall(撤回), add_friend(添加好友)几个类型
        # 'logger' 是一个日志输出对象,可以用logger.success()、logger.info()、logger.warn()、logger.error()、logger.input()、logger.password()来输入或输出对应等级的日志
        # 'message' 是对方发送的消息(如果是add_friend则是是否自动添加)
        # 'bot' 是用于向聊天发送消息的机器人对象。
        # 'from_userid' 是发送命令的用户ID。
        # 在这里实现命令功能。
        # 例如这里就记录了一个日志
        if message_type != 'text':
            return 
        if group is None:
            with open("log",'a') as log:
                log.write(from_userid + ": " + message + '\n')
        else:
            with open("log",'a') as log:
                log.write(from_userid + " in " + group + ": " + message + '\n')
```
   ### 为了方便开发，这里给出 bot 的所有方法：

   #### `send`: 发送消息,传入 type、data、to_userid、group 四个参数, 返回消息message_id

   - `type`: 消息类型，有 text(文本)、image(图片)、file(文件) 几个类型
   - `data`: 内容，如果是文件或图片，请使用 `open('路径', 'rb')` 打开
   - `to_userid`: 接收者的用户 ID，如果 `group` 不为 None 则不生效
   - `group`: 发送的群号，如果为 None 则是私聊
   #### `getfriends`: 获取所有好友信息
   #### `getgroups`: 获取所有群信息
   #### `getuserprofile`: 获取指定用户信息,传入user_id

   - `user_id`: 查询的用户的user_id
   #### `getgroupprofile`: 获取指定群信息,传入group_id
   - `group_id`: 查询的群的group_id
   #### `getuserid`: 获取机器人的user_id
   #### `apply_friend`: 申请添加用户为好友, 传入user_id、greeting两个参数
   - `user_id`: 对方的user_id
   - `greeting`: 申请消息
   #### `recall_message`: 撤回消息, 传入message_id、group_id、user_id三个参数
   - `message_id`: 撤回的消息id
   - `group_id`: 消息所在的群,私聊就传入None
   - `user_id`: 消息发给的用户(group_id是None才启用)
   #### `accept`: 同意好友申请, 传入agree、user_id两个参数, 返回是否成功
   - `agree`: 是否同意该好友申请
   - `user_id`: 统一的用户id


## 2. 在插件的`onEnable`方法中，返回一个包含支持的命令字典的列表。根据插件的需求添加所需的命令。

## 3. `onLoad`方法在插件被加载时由机器人调用。你可以在此方法中初始化任何必要的资源，设置配置或进行其他必要的设置。

## 4. `onDisable`方法在插件被禁用或机器人关闭时被调用。你可以在此方法中清理资源或保存数据。

## 5. 定义`async def say_hello(self, args, bot,from_userid, group)`方法（或者其他你添加的命令方法），用于实现命令的功能。当对应的命令被调用时，该方法会被执行。使用`bot`对象发送聊天消息。

## 6. 在主脚本中注册你的插件。主脚本已经加载了`plugins`目录下的所有Python文件。确保你的插件文件遵循命名规范，并包含一个有效的插件类。

## 7. 重启机器人来测试你的插件，它应该加载你的插件，并提供你定义的命令。

## 8. 你可以根据需要添加更多命令或实现其他功能。

## 9. 记得在你的插件中优雅地处理错误，因为它将在与其他插件并发运行的环境中执行。

# 有了这个指南，你应该能够开始为聊天机器人开发自定义插件，并根据需要扩展其功能。
