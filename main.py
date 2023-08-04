import sys
import os
from datetime import datetime
import math
import time
import json
import asyncio
import atexit

# 前置库安装
try:
    import colorama

    colorama.init()
except ModuleNotFoundError:
    now = datetime.now()
    print(f"[{now.year}:{now.month}:{now.day} {now.hour}:{now.minute}:{now.second}][WARN]检测到缺少模块:colorama,开始安装!")
    install = os.system(sys.executable + " -m pip install colorama")
    if install != 0:
        print(f"[{now.year}:{now.month}:{now.day} {now.hour}:{now.minute}:{now.second}][ERROR]安装失败!")
        sys.exit(1)
    else:
        import colorama

        colorama.init()
        print(
            f"[{colorama.Fore.RESET}{now.year}:{now.month}:{now.day} {now.hour}:{now.minute}:{now.second}][{colorama.Fore.GREEN}SUCCESS{colorama.Fore.RESET}]安装成功!")


# 创建Logger对象
class Logger:
    def success(self, out):
        now = datetime.now()
        print(
            colorama.Fore.RESET + f"[{now.year}:{now.month}:{now.day}:{now.hour}:{now.minute}:{now.second}][{colorama.Fore.GREEN}SUCCESS{colorama.Fore.RESET}]" + out)

    def info(self, out):
        now = datetime.now()
        print(
            colorama.Fore.RESET + f"[{now.year}:{now.month}:{now.day}:{now.hour}:{now.minute}:{now.second}][{colorama.Fore.BLUE}INFO{colorama.Fore.RESET}]" + out)

    def warn(self, out):
        now = datetime.now()
        print(
            colorama.Fore.RESET + f"[{now.year}:{now.month}:{now.day}:{now.hour}:{now.minute}:{now.second}][{colorama.Fore.YELLOW}WARN{colorama.Fore.RESET}]" + out)

    def error(self, out):
        now = datetime.now()
        print(
            colorama.Fore.RESET + f"[{now.year}:{now.month}:{now.day}:{now.hour}:{now.minute}:{now.second}][{colorama.Fore.RED}ERROR{colorama.Fore.RESET}]" + out)


logger = Logger()

# 继续安装前置库
try:
    import requests
except ModuleNotFoundError:
    logger.warn("检测到缺少模块:requests,开始安装!")
    install = os.system(sys.executable + " -m pip install requests")
    if install != 0:
        logger.error("安装失败!")
        sys.exit(1)
    else:
        import requests

        logger.success("安装成功!")
try:
    import httpx
except ModuleNotFoundError:
    logger.warn("检测到缺少模块:httpx,开始安装!")
    install = os.system(sys.executable + " -m pip install httpx")
    if install != 0:
        logger.error("安装失败!")
        sys.exit(1)
    else:
        import httpx

        logger.success("安装成功!")

# 创建文件夹
if not os.path.exists("plugins"):
    os.mkdir("plugins")
if not os.path.exists("data"):
    os.mkdir("data")


# 获取配置文件
def configreader():
    if os.path.exists("config.json"):
        return json.load(open("config.json"))
    else:
        logger.warn("缺少配置文件,启动配置文件创建程序!")
        username = input("输入用户名:")
        while username == "":
            logger.error("没有输入任何内容!")
            username = input("输入用户名:")
        password = input("请输入密码:")
        while password == "":
            logger.error("没有输入任何内容!")
            password = input("请输入密码:")
        waittime = input("输入每次获取消息的间隔时间(ms),默认500:")
        if waittime == "":
            waittime = 500
        else:
            while True:
                try:
                    waittime = int(waittime)
                    break
                except ValueError:
                    logger.error("错误:该值不是数字!")
                    waittime = input("输入每次获取消息的间隔时间(ms),默认500:")
        auto_accept = input("是否自动同意好友申请(true或false),默认true:")
        if auto_accept == "":
            auto_accept = True
        else:
            while True:
                if auto_accept == "true":
                    auto_accept = True
                    break
                elif auto_accept == "false":
                    auto_accept = False
                    break
                else:
                    logger.error("错误:请输入true或false:!")
                    waittime = input("是否自动同意好友申请(true或false),默认true:")
        config = {
            "username": username,
            "password": password,
            "wait_time": waittime,
            "auto_accept": auto_accept
        }
        with open("config.json", 'w') as f:
            f.write(json.dumps(config, indent=4))
        return config


config = configreader()

# 登录
logger.info("开始登录流程...")
logger.info("账号: " + config['username'])
login = requests.post(url="http://chat.thisit.cc/index.php?action=api.passport.passwordLogin&body_format=json&lang=1",
                      json={
                          "action": "api.passport.passwordLogin",
                          "body": {
                              "@type": "type.googleapis.com/site.ApiPassportPasswordLoginRequest",
                              "loginName": config['username'],
                              "password": config['password']
                          },
                          "header": {
                              "_4": "http://chat.thisit.cc/index.php",
                              "_8": "1",
                              "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                          },
                          "packageId": 1
                      })
try:
    t = login.json()['body']['preSessionId']
except KeyError:
    logger.error("登陆失败:" + login.text)
    sys.exit(1)
logger.info("preSessionId:" + t)
token = requests.post(
    url="http://chat.thisit.cc/index.php?action=page.passport.login&action=api.site.login&body_format=json", json={
        "action": "api.site.login",
        "body": {
            "@type": "type.googleapis.com/site.ApiSiteLoginRequest",
            "preSessionId": t,
            "loginName": "黄荻",
            "isRegister": False,
            "thirdPartyKey": ""
        },
        "header": {
            "_4": "http://chat.thisit.cc/index.php?action=page.passport.login",
            "_8": "1",
            "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        },
        "packageId": 2
    })
userid = token.json()['body']['profile']['public']['userId']
token = token.cookies['zaly_site_user']
logger.info("token:" + token)
logger.success("登录成功")


# 创建bot对象
class Bot:
    async def getuserid(self):
        global userid
        return userid

    async def send(self, type: str, data, to_userid: str):
        if type != "text":
            raise "Message_type_error"
        global packageId
        global userid
        requests.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1", json={
            "action": "im.cts.message",
            "body": {
                "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                "message": {
                    "fromUserId": userid,
                    "roomType": "MessageRoomU2",
                    "toUserId": to_userid,
                    "msgId": f"U2-{math.floor(round(time.time(), 3) * 1000)}",
                    "timeServer": round(time.time(), 3) * 1000,
                    "text": {
                        "body": data
                    },
                    "type": "MessageText"
                }
            },
            "header": {
                "_3": token,
                "_4": "http://chat.thisit.cc/index.php",
                "_8": "1",
                "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
            },
            "packageId": packageId
        })
        packageId += 1
        return True


bot = Bot()

# 加载插件
logger.info("开始加载插件...")
plugins = {}
for filename in os.listdir("plugins"):
    if filename.endswith(".py"):
        plugin = getattr(__import__("plugins." + filename[:-3], fromlist=[filename[:-3]]), filename[:-3])
        if hasattr(plugin, "onEnable") and hasattr(plugin, "onDisable") and hasattr(plugin, "onLoad"):
            plugin = plugin()
            plugins[filename[:-3]] = plugin
            plugin.onLoad(logger=logger, bot=bot)
            logger.success("成功加载插件" + filename[:-3] + "!")
logger.success("所有插件都加载完了!")

commands = []
messages = []

for plugin_name, plugin in plugins.items():
    plugin_data = plugin.onEnable(logger=logger, bot=bot)
    for i in plugin_data['commands']:
        commands.append(i)
    for i in plugin_data['messages']:
        messages.append(i)


async def process_command(command, args, bot, from_userid):
    for cmd in commands:
        if command == cmd['command']:
            await cmd['def'](logger=logger, args=args, bot=bot, from_userid=from_userid)
            return


async def process_message(message, bot, from_userid):
    for msg in messages:
        await msg['def'](logger=logger, message=message, bot=bot, from_userid=from_userid)
        return


# 创建关闭时的函数
def onExit():
    global plugins
    for plugin_name, plugin in plugins.items():
        plugin.onDisable(logger=logger, bot=bot)
        logger.success("成功关闭插件" + plugin_name + '!')
    logger.success("程序关闭")
    logger.success("Good Bye...")


atexit.register(onExit)

# 消息获取循环
packageId = 1


async def message_loop():
    global packageId
    global token
    while True:
        response = requests.post(url="http://chat.thisit.cc/index.php?action=im.cts.sync&body_format=json&lang=1",
                                 json={
                                     "action": "im.cts.sync",
                                     "body": {
                                         "@type": "type.googleapis.com/site.ImCtsSyncRequest",
                                         "u2Count": 200,
                                         "groupCount": 200
                                     },
                                     "header": {
                                         "_3": token,
                                         "_4": "http://chat.thisit.cc/index.php",
                                         "_8": "1",
                                         "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                                     },
                                     "packageId": packageId
                                 })
        try:
            if len(response.json()['body']['list']) > 1:
                for i in response.json()['body']['list'][:-1]:
                    res = requests.post(
                        url="http://chat.thisit.cc/index.php?action=api.friend.profile&body_format=json&lang=1",
                        json={
                            "action": "api.friend.profile",
                            "body": {
                                "@type": "type.googleapis.com/site.ApiFriendProfileRequest",
                                "userId": i['fromUserId']
                            },
                            "header": {
                                "_3": token,
                                "_4": "http://chat.thisit.cc/index.php",
                                "_8": "1",
                                "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
                            },
                            "packageId": packageId
                        })
                    packageId += 1
                    if i['type'] == 'MessageEventFriendRequest':
                        logger.info("收到来自用户" + res.json()['body']['profile']['profile']['nickname'] + "的好友申请!")
                        if config['auto_accept']:
                            requests.post(
                                url="http://chat.thisit.cc/index.php?action=api.friend.accept&body_format=json&lang=1",
                                json={
                                    "action": "api.friend.accept",
                                    "body": {
                                        "@type": "type.googleapis.com/site.ApiFriendAcceptRequest",
                                        "applyUserId": i['fromUserId'],
                                        "agree": True
                                    },
                                    "header": {
                                        "_3": token,
                                        "_4": "http://chat.thisit.cc/index.php",
                                        "_8": "1",
                                        "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                                    },
                                    "packageId": packageId
                                })
                            packageId += 1
                    requests.post(url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
                                  json={
                                      "action": "im.cts.updatePointer",
                                      "body": {
                                          "@type": "type.googleapis.com/site.ImCtsUpdatePointerRequest",
                                          "u2Pointer": i['pointer'],
                                          "groupsPointer": {}
                                      },
                                      "header": {
                                          "_3": token,
                                          "_4": "http://chat.thisit.cc/index.php",
                                          "_8": "1",
                                          "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                                      },
                                      "packageId": packageId
                                  })
                    packageId += 1
                    if i['fromUserId'] == userid:
                        res = requests.post(
                            url="http://chat.thisit.cc/index.php?action=api.friend.profile&body_format=json&lang=1",
                            json={
                                "action": "api.friend.profile",
                                "body": {
                                    "@type": "type.googleapis.com/site.ApiFriendProfileRequest",
                                    "userId": i['toUserId']
                                },
                                "header": {
                                    "_3": token,
                                    "_4": "http://chat.thisit.cc/index.php",
                                    "_8": "1",
                                    "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
                                },
                                "packageId": packageId
                            })
                        logger.info(
                            "发送到用户" + res.json()['body']['profile']['profile']['nickname'] + "的消息:" + i['text']['body'])
                        continue
                    logger.info("来自用户" + res.json()['body']['profile']['profile']['nickname'] + "的消息:" + i['text']['body'])
                    await process_message(i['text']['body'], bot, i['fromUserId'])
                    if i['text']['body'].startswith("/"):
                        args = i['text']['body'][1:].split(' ')
                        command = args[0]
                        await process_command(command, args[1:], bot, i['fromUserId'])
        except KeyError:
            logger.warn('出现了一个无法解析的消息!')
        except Exception as e:
            logger.error('出现了一个错误:' + str(e))
        await asyncio.sleep(config['wait_time'] / 1000)


asyncio.run(message_loop())
