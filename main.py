import sys
import os
from datetime import datetime
import math
import time
import json
import asyncio
import atexit
import getpass

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

    def input(self, out):
        now = datetime.now()
        return input(
            colorama.Fore.RESET + f"[{now.year}:{now.month}:{now.day}:{now.hour}:{now.minute}:{now.second}][{colorama.Fore.MAGENTA}INPUT{colorama.Fore.RESET}]" + out)

    def password(self, out):
        now = datetime.now()
        return getpass.getpass(
            colorama.Fore.RESET + f"[{now.year}:{now.month}:{now.day}:{now.hour}:{now.minute}:{now.second}][{colorama.Fore.LIGHTMAGENTA_EX}PASSWORD{colorama.Fore.RESET}]" + out)


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
try:
    from PIL import Image
except ModuleNotFoundError:
    logger.warn("检测到缺少模块:pillow,开始安装!")
    install = os.system(sys.executable + " -m pip install pillow")
    if install != 0:
        logger.error("安装失败!")
        sys.exit(1)
    else:
        from PIL import Image

        logger.success("安装成功!")
try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    logger.warn("检测到缺少模块:beautifulsoup4,开始安装!")
    install = os.system(sys.executable + " -m pip install beautifulsoup4")
    if install != 0:
        logger.error("安装失败!")
        sys.exit(1)
    else:
        from bs4 import BeautifulSoup

        logger.success("安装成功!")

# 创建文件夹
if not os.path.exists("plugins"):
    os.mkdir("plugins")
if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists("files"):
    os.mkdir("files")
if not os.path.exists("images"):
    os.mkdir("images")


# 获取配置文件
def configreader():
    if os.path.exists("config.json") and "username" in json.load(open("config.json")) and "password" in json.load(
            open("config.json")) and "wait_time" in json.load(open("config.json")) and "width" in json.load(
        open("config.json")) and "auto_login" in json.load(open("config.json")) and "auto_accept" in json.load(
        open("config.json")):
        return json.load(open("config.json"))
    else:
        logger.warn("缺少配置文件或配置问价缺少值,启动配置文件创建程序!")
        if not os.path.exists("config.json") or "username" not in json.load(open("config.json")):
            username = logger.input("输入用户名:")
            while username == "":
                logger.error("没有输入任何内容!")
                username = logger.input("输入用户名:")
        else:
            username = json.load(open("config.json"))["username"]
        if not os.path.exists("config.json") or "password" not in json.load(open("config.json")):
            password = logger.password("请输入密码(不显示):")
            while password == "":
                logger.error("没有输入任何内容!")
                password = logger.password("请输入密码(不显示):")
        else:
            password = json.load(open("config.json"))["password"]
        if not os.path.exists("config.json") or "wait_time" not in json.load(open("config.json")):
            waittime = logger.input("输入每次获取消息的间隔时间(ms),默认500:")
            if waittime == "":
                waittime = 500
            else:
                while True:
                    try:
                        waittime = int(waittime)
                        break
                    except ValueError:
                        logger.error("错误:该值不是数字!")
                        waittime = logger.input("输入每次获取消息的间隔时间(ms),默认500:")
        else:
            waittime = json.load(open("config.json"))["wait_time"]
        if not os.path.exists("config.json") or "width" not in json.load(open("config.json")):
            width = logger.input("快捷显示表情包的宽度(字符),默认100,0则不显示:")
            if width == "":
                width = 100
            else:
                while True:
                    try:
                        width = int(width)
                        break
                    except ValueError:
                        logger.error("错误:该值不是数字!")
                        width = logger.input("快捷显示表情包的宽度(字符),默认100,0则不显示:")
        else:
            width = json.load(open("config.json"))["width"]
        if not os.path.exists("config.json") or "auto_login" not in json.load(open("config.json")):
            auto_login = logger.input("是否自动重新登录(true或false),默认true:")
            if auto_login == "":
                auto_login = True
            else:
                while True:
                    if auto_login == "true":
                        auto_login = True
                        break
                    elif auto_login == "false":
                        auto_login = False
                        break
                    else:
                        logger.error("错误:请输入true或false:!")
                        auto_login = logger.input("是否自动同意好友申请(true或false),默认true:")
        else:
            auto_login = json.load(open("config.json"))["auto_login"]
        if not os.path.exists("config.json") or "auto_accept" not in json.load(open("config.json")):
            auto_accept = logger.input("是否自动同意好友申请(true或false),默认true:")
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
                        auto_accept = logger.input("是否自动同意好友申请(true或false),默认true:")
        else:
            auto_accept = json.load(open("config.json"))["auto_login"]
        config = {
            "username": username,
            "password": password,
            "wait_time": waittime,
            "width": width,
            "auto_login": auto_login,
            "auto_accept": auto_accept
        }
        with open("config.json", 'w') as f:
            f.write(json.dumps(config, indent=4))
        return config


config = configreader()


# 图转文函数
def image_to_ascii(image_path, new_width=config['width']):
    def resize_image(image, new_width):
        width, height = image.size
        ratio = height / float(width)
        new_height = int(float(new_width) * ratio / 2.0)
        resized_image = image.resize((new_width, new_height))
        return resized_image

    def grayscale(image):
        return image.convert("L")

    def pixel_to_ascii(image):
        ascii_chars = "@%#$&*+=-:. "
        pixels = image.getdata()
        ascii_str = ""
        for pixel_value in pixels:
            normalized_pixel = pixel_value * (len(ascii_chars) - 1) // 255
            ascii_str += ascii_chars[int(normalized_pixel)]
        return ascii_str

    try:
        image = Image.open(image_path)
    except Exception as e:
        return "错误：" + str(e)

    resized_image = resize_image(image, new_width)
    grayscale_image = grayscale(resized_image)
    ascii_str = pixel_to_ascii(grayscale_image)

    img_width = resized_image.width
    ascii_str_len = len(ascii_str)
    ascii_img = ""
    for i in range(0, ascii_str_len, img_width):
        ascii_img += ascii_str[i:i + img_width] + "\n"

    return ascii_img


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
            "loginName": config['username'],
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
    async def getfriends(self):
        global packageId
        global token
        res = requests.post('http://chat.thisit.cc/index.php?action=api.friend.list&body_format=json&lang=1', json={
            "action": "api.friend.list",
            "body": {
                "@type": "type.googleapis.com/site.ApiFriendListRequest",
                "offset": 0,
                "count": 200
            },
            "header": {
                "_3": token,
                "_4": "http://chat.thisit.cc/",
                "_8": "1",
                "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            },
            "packageId": packageId
        })
        packageId += 1
        return res.json()['body']['friends']

    async def getgroups(self):
        global packageId
        global token
        res = requests.post('http://chat.thisit.cc/index.php?action=api.group.list&body_format=json&lang=1', json={
            "action": "api.group.list",
            "body": {
                "@type": "type.googleapis.com/site.ApiGroupListRequest",
                "offset": 0,
                "count": 200
            },
            "header": {
                "_3": token,
                "_4": "http://chat.thisit.cc/",
                "_8": "1",
                "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            },
            "packageId": packageId
        })
        packageId += 1
        return res.json()['body']['list']

    async def getuserprofile(self, user_id):
        global packageId
        global token
        res = requests.post(
            url="http://chat.thisit.cc/index.php?action=api.friend.profile&body_format=json&lang=1",
            json={
                "action": "api.friend.profile",
                "body": {
                    "@type": "type.googleapis.com/site.ApiFriendProfileRequest",
                    "userId": user_id
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
        return res.json()['body']['profile']['profile']

    async def getgroupprofile(self, group_id):
        global packageId
        global token
        res = requests.post(
            url='http://chat.thisit.cc/index.php?action=api.group.profile&body_format=json&lang=1',
            json={
                "action": "api.group.profile",
                "body": {
                    "@type": "type.googleapis.com/site.ApiGroupProfileRequest",
                    "groupId": group_id
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
        return res.json()['body']['profile']

    async def getuserid(self):
        global userid
        return userid

    async def send(self, type: str, data, to_userid: str, group):
        global packageId
        global userid
        if type == "text":
            if group is None:
                requests.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                              json={
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
            else:
                requests.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                              json={
                                  "action": "im.cts.message",
                                  "body": {
                                      "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                      "message": {
                                          "fromUserId": userid,
                                          "roomType": "MessageRoomGroup",
                                          "toGroupId": group,
                                          "msgId": f"GROUP-{math.floor(round(time.time(), 3) * 1000)}",
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
                                      "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                                  },
                                  "packageId": packageId
                              })
                packageId += 1
                return True
        elif type == 'file':
            da = {
                'fileType': '3',
                'isMessageAttachment': 'true'
            }
            files = {
                'file': (data.name, data, 'application/octet-stream'),
            }
            response = requests.post(url='http://chat.thisit.cc/index.php?action=http.file.uploadWeb'
                                     , files=files, data=da, cookies={
                    'zaly_site_user': token,
                })
            if response.json()['errorInfo'] != '':
                raise ValueError(response.json()['errorInfo'])
            data.seek(0, 2)
            if group is None:
                requests.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                              json={
                                  "action": "im.cts.message",
                                  "body": {
                                      "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                      "message": {
                                          "fromUserId": userid,
                                          "roomType": "MessageRoomU2",
                                          "toUserId": to_userid,
                                          "msgId": f"U2-{math.floor(round(time.time(), 3) * 1000)}",
                                          "timeServer": round(time.time(), 3) * 1000,
                                          "document": {
                                              "url": response.json()['fileId'],
                                              "size": data.tell(),
                                              "name": data.name
                                          },
                                          "type": "MessageDocument"
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
            else:
                requests.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                              json={
                                  "action": "im.cts.message",
                                  "body": {
                                      "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                      "message": {
                                          "fromUserId": userid,
                                          "roomType": "MessageRoomGroup",
                                          "toGroupId": group,
                                          "msgId": f"GROUP-{math.floor(round(time.time(), 3) * 1000)}",
                                          "timeServer": round(time.time(), 3) * 1000,
                                          "document": {
                                              "url": response.json()['fileId'],
                                              "size": data.tell(),
                                              "name": data.name
                                          },
                                          "type": "MessageDocument"
                                      }
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
                return True
        elif type == 'image':
            da = {
                'fileType': '1',
                'isMessageAttachment': 'true'
            }
            files = {
                'file': (data.name, data, 'application/octet-stream'),
            }
            response = requests.post(url='http://chat.thisit.cc/index.php?action=http.file.uploadWeb'
                                     , files=files, data=da, cookies={
                    'zaly_site_user': token,
                })
            if response.json()['errorInfo'] != '':
                raise ValueError(response.json()['errorInfo'])
            if group is None:
                requests.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                              json={
                                  "action": "im.cts.message",
                                  "body": {
                                      "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                      "message": {
                                          "fromUserId": userid,
                                          "roomType": "MessageRoomU2",
                                          "toUserId": to_userid,
                                          "msgId": f"U2-{math.floor(round(time.time(), 3) * 1000)}",
                                          "timeServer": round(time.time(), 3) * 1000,
                                          "image": {
                                              "url": response.json()['fileId'],
                                              "width": Image.open(data).size[0],
                                              "height": Image.open(data).size[1]
                                          },
                                          "type": "MessageImage"
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
            else:
                requests.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                              json={
                                  "action": "im.cts.message",
                                  "body": {
                                      "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                      "message": {
                                          "fromUserId": userid,
                                          "roomType": "MessageRoomGroup",
                                          "toGroupId": group,
                                          "msgId": f"GROUP-{math.floor(round(time.time(), 3) * 1000)}",
                                          "timeServer": round(time.time(), 3) * 1000,
                                          "image": {
                                              "url": response.json()['fileId'],
                                              "width": Image.open(data).size[0],
                                              "height": Image.open(data).size[1]
                                          },
                                          "type": "MessageImage"
                                      }
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
                return True
        else:
            raise ValueError("Message_type_error")


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


async def process_command(command, args, bot, from_userid, group):
    for cmd in commands:
        if command == cmd['command']:
            await cmd['def'](logger=logger, args=args, bot=bot, from_userid=from_userid, group=group)
            return


async def process_message(typt, message, bot, from_userid, group):
    for msg in messages:
        await msg['def'](type=typt, logger=logger, message=message, bot=bot, from_userid=from_userid, group=group)
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
logger.success(
    '成功加载' + str(len(asyncio.run(bot.getfriends()))) + '个好友,' + str(len(asyncio.run(bot.getgroups()))) + '个群')


async def message_loop():
    global userid
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
                    elif i['type'] == 'MessageNotice':
                        logger.info('收到一个消息:' + i['notice']['body'])
                        if i['msgId'].startswith('GP-'):
                            requests.post(
                                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
                                json={
                                    "action": "im.cts.updatePointer",
                                    "body": {
                                        "@type": "type.googleapis.com/site.ImCtsUpdatePointerRequest",
                                        "u2Pointer": 0,
                                        "groupsPointer": {
                                            i['toGroupId']: i['pointer']
                                        }
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
                    elif i['type'] == 'MessageWeb':
                        group = None
                        file = None
                        filename = None
                        type = 'html'
                        if i['msgId'].startswith('G'):
                            group = i['toGroupId']
                            requests.post(
                                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
                                json={
                                    "action": "im.cts.updatePointer",
                                    "body": {
                                        "@type": "type.googleapis.com/site.ImCtsUpdatePointerRequest",
                                        "u2Pointer": 0,
                                        "groupsPointer": {
                                            i['toGroupId']: i['pointer']
                                        }
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
                            ress = requests.post(
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
                            res = requests.post(
                                url='http://chat.thisit.cc/index.php?action=api.group.profile&body_format=json&lang=1',
                                json={
                                    "action": "api.group.profile",
                                    "body": {
                                        "@type": "type.googleapis.com/site.ApiGroupProfileRequest",
                                        "groupId": i['toGroupId']
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
                            web = BeautifulSoup(i['web']['code'], 'html.parser')
                            if i['web']['title'] == 'GIF':
                                type = 'gif'
                                url = web.find('img')['src']
                                gif = requests.get(
                                    url="http://chat.thisit.cc/index.php?action=miniProgram.gif.info&gifId=" + url,
                                    cookies={
                                        'zaly_site_user': token,
                                        'duckchat_page_url': 'http://chat.thisit.cc?page=groupMsg&x=' + i['toGroupId']
                                    })
                                type = gif.headers.get('Content-Type').split('/')[1]
                                filename = url.split('&gifId=')[1] + '.' + type
                                if i['fromUserId'] == userid:
                                    logger.info(
                                        "发送到群" + res.json()['body']['profile']['name'] + "的表情:" + url)
                                    continue
                                logger.info(
                                    "来自用户" + ress.json()['body']['profile']['profile']['nickname'] + "在群" +
                                    res.json()['body']['profile']['name'] + "中的表情:" + filename + ",存放于" +
                                    'images' + os.sep + '[' + i['msgId'] + ']' + filename)
                                with open("images" + os.sep + '[' + i['msgId'] + ']' + filename, 'wb') as f:
                                    f.write(gif.content)
                                if config['width'] != 0:
                                    for line in image_to_ascii(
                                            "images" + os.sep + '[' + i['msgId'] + ']' + filename).split('\n')[:-1]:
                                        logger.info(line)
                                continue
                            if i['fromUserId'] == userid:
                                logger.info(
                                    "发送到群" + res.json()['body']['profile']['name'] + "的HTML消息:" + web.text)
                                continue

                            logger.info(
                                "来自用户" + ress.json()['body']['profile']['profile']['nickname'] + "在群" +
                                res.json()['body']['profile']['name'] + "中的HTML消息:" + web.text)

                        else:
                            requests.post(
                                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
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
                            packageId += 1
                            web = BeautifulSoup(i['web']['code'], 'html.parser')
                            if i['web']['title'] == 'GIF':
                                type = 'gif'
                                url = web.find('img')['src']
                                gif = requests.get(url="http://chat.thisit.cc/" + url, cookies={
                                    'zaly_site_user': token
                                })
                                type = gif.headers.get('content-type').split('/')[1]
                                filename = url.split('&gifId=')[1] + '.' + type
                                if i['fromUserId'] == userid:
                                    logger.info(
                                        "发送到用户" + res.json()['body']['profile']['profile']['nickname'] + "的表情:" + url)
                                    continue
                                logger.info(
                                    "来自用户" + res.json()['body']['profile']['profile']['nickname'] + "的表情:" + filename +
                                    ",存放于" + 'images' + os.sep + '[' + i['msgId'] + ']' + filename)
                                with open("images" + os.sep + '[' + i['msgId'] + ']' + filename, 'wb') as f:
                                    f.write(gif.content)
                                if config['width'] != 0:
                                    for line in image_to_ascii(
                                            "images" + os.sep + '[' + i['msgId'] + ']' + filename).split('\n')[:-1]:
                                        logger.info(line)
                                continue
                            if i['fromUserId'] == userid:
                                logger.info(
                                    "发送到用户" + res.json()['body']['profile']['profile'][
                                        'nickname'] + "的HTML消息:" + web.text)
                                continue

                            logger.info(
                                "来自用户" + res.json()['body']['profile']['profile']['nickname'] + "的HTML消息:" + web.text)
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
                                    "发送到用户" + res.json()['body']['profile']['profile']['nickname'] + "的文件:" +
                                    i['document']['name'])
                                continue
                            logger.info(
                                "来自用户" + res.json()['body']['profile']['profile']['nickname'] + "的文件:" + i['document'][
                                    'name'] + ",存放于" + 'files' + os.sep + '[' + i['msgId'] + ']' + i['document'][
                                    'name'])
                            file = requests.get(
                                f"http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId={i['document']['url']}&returnBase64=0&isGroupMessage=0&messageId={i['msgId']}&lang=1",
                                cookies={
                                    'zaly_site_user': token
                                })
                        if type == 'html':
                            await process_message('html', i['web']['code'], bot,i['fromUserId'], group)
                        else:
                            await process_message('gif', open("images" + os.sep + '[' + i['msgId'] + ']' + filename, 'wb'), bot, i['fromUserId'], group)
                    elif i['type'] == 'MessageDocument':
                        group = None
                        file = None
                        if i['msgId'].startswith('GROUP-'):
                            group = i['toGroupId']
                            requests.post(
                                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
                                json={
                                    "action": "im.cts.updatePointer",
                                    "body": {
                                        "@type": "type.googleapis.com/site.ImCtsUpdatePointerRequest",
                                        "u2Pointer": 0,
                                        "groupsPointer": {
                                            i['toGroupId']: i['pointer']
                                        }
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
                            ress = requests.post(
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
                            res = requests.post(
                                url='http://chat.thisit.cc/index.php?action=api.group.profile&body_format=json&lang=1',
                                json={
                                    "action": "api.group.profile",
                                    "body": {
                                        "@type": "type.googleapis.com/site.ApiGroupProfileRequest",
                                        "groupId": i['toGroupId']
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
                                logger.info(
                                    "发送到群" + res.json()['body']['profile']['name'] + "的文件:" + i['document'][
                                        'name'])
                                continue
                            logger.info(
                                "来自用户" + ress.json()['body']['profile']['profile']['nickname'] + "在群" +
                                res.json()['body']['profile']['name'] + "中的文件:" + i['document']['name'] + ",存放于" +
                                'files' + os.sep + '[' + i['msgId'] + ']' + i['document']['name'])
                            file = requests.get(
                                f"http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId={i['document']['url']}&returnBase64=0&isGroupMessage=1&messageId={i['msgId']}&lang=1",
                                cookies={
                                    'zaly_site_user': token
                                })
                        else:
                            requests.post(
                                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
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
                                    "发送到用户" + res.json()['body']['profile']['profile']['nickname'] + "的文件:" +
                                    i['document']['name'])
                                continue
                            logger.info(
                                "来自用户" + res.json()['body']['profile']['profile']['nickname'] + "的文件:" + i['document'][
                                    'name'] + ",存放于" + 'files' + os.sep + '[' + i['msgId'] + ']' + i['document'][
                                    'name'])
                            file = requests.get(
                                f"http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId={i['document']['url']}&returnBase64=0&isGroupMessage=0&messageId={i['msgId']}&lang=1",
                                cookies={
                                    'zaly_site_user': token
                                })
                        with open('files' + os.sep + '[' + i['msgId'] + ']' + i['document']['name'], 'wb') as f:
                            f.write(file.content)
                        await process_message('file', open('files' + os.sep + '[' + i['msgId'] + ']' + i['document']['name'], 'rb'), bot, i['fromUserId'], group)
                    elif i['type'] == 'MessageImage':
                        group = None
                        file = None
                        if i['msgId'].startswith('GROUP-'):
                            group = i['toGroupId']
                            requests.post(
                                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
                                json={
                                    "action": "im.cts.updatePointer",
                                    "body": {
                                        "@type": "type.googleapis.com/site.ImCtsUpdatePointerRequest",
                                        "u2Pointer": 0,
                                        "groupsPointer": {
                                            i['toGroupId']: i['pointer']
                                        }
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
                            ress = requests.post(
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
                            res = requests.post(
                                url='http://chat.thisit.cc/index.php?action=api.group.profile&body_format=json&lang=1',
                                json={
                                    "action": "api.group.profile",
                                    "body": {
                                        "@type": "type.googleapis.com/site.ApiGroupProfileRequest",
                                        "groupId": i['toGroupId']
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
                                logger.info(
                                    "发送到群" + res.json()['body']['profile']['name'] + "的图片:" + i['image'][
                                        'url'])
                                continue
                            logger.info(
                                "来自用户" + ress.json()['body']['profile']['profile']['nickname'] + "在群" +
                                res.json()['body']['profile']['name'] + "中的图片:" + i['image']['url'] + ",存放于" +
                                'images' + os.sep + '[' + i['msgId'] + ']' + i['image']['url'])
                            file = requests.get(
                                f"http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId={i['image']['url']}&returnBase64=0&lang=1",
                                cookies={
                                    'zaly_site_user': token
                                })
                        else:
                            requests.post(
                                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
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
                                    "发送到用户" + res.json()['body']['profile']['profile']['nickname'] + "的图片:" +
                                    i['image']['url'])
                                continue
                            logger.info(
                                "来自用户" + res.json()['body']['profile']['profile']['nickname'] + "的图片:" + i['image'][
                                    'url'] + ",存放于" + 'images' + os.sep + '[' + i['msgId'] + ']' + i['image']['url'])
                            file = requests.get(
                                f"http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId={i['image']['url']}&returnBase64=0&lang=1",
                                cookies={
                                    'zaly_site_user': token
                                })
                        with open('images' + os.sep + '[' + i['msgId'] + ']' + i['image']['url'], 'wb') as f:
                            f.write(file.content)
                        await process_message('image', open('images' + os.sep + '[' + i['msgId'] + ']' + i['image']['url'], 'rb'), bot, i['fromUserId'], group)
                    elif i['type'] == 'MessageText':
                        group = None
                        if i['msgId'].startswith('GROUP-'):
                            group = i['toGroupId']
                            requests.post(
                                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
                                json={
                                    "action": "im.cts.updatePointer",
                                    "body": {
                                        "@type": "type.googleapis.com/site.ImCtsUpdatePointerRequest",
                                        "u2Pointer": 0,
                                        "groupsPointer": {
                                            i['toGroupId']: i['pointer']
                                        }
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
                            ress = requests.post(
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
                            res = requests.post(
                                url='http://chat.thisit.cc/index.php?action=api.group.profile&body_format=json&lang=1',
                                json={
                                    "action": "api.group.profile",
                                    "body": {
                                        "@type": "type.googleapis.com/site.ApiGroupProfileRequest",
                                        "groupId": i['toGroupId']
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
                                logger.info(
                                    "发送到群" + res.json()['body']['profile']['name'] + "的消息:" + i['text'][
                                        'body'])
                                continue
                            logger.info(
                                "来自用户" + ress.json()['body']['profile']['profile']['nickname'] + "在群" +
                                res.json()['body']['profile']['name'] + "中的消息:" + i['text'][
                                    'body'])
                        else:
                            requests.post(
                                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
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
                                    "发送到用户" + res.json()['body']['profile']['profile']['nickname'] + "的消息:" + i['text'][
                                        'body'])
                                continue
                            logger.info(
                                "来自用户" + res.json()['body']['profile']['profile']['nickname'] + "的消息:" + i['text'][
                                    'body'])
                        await process_message('text', i['text']['body'], bot, i['fromUserId'], group)
                        if i['text']['body'].startswith("/"):
                            args = i['text']['body'][1:].split(' ')
                            command = args[0]
                            await process_command(command, args[1:], bot, i['fromUserId'], group)
        except KeyError as e:
            if response.json()['header']['_1'] == 'error.session':
                if config['auto_login']:
                    logger.error('获取消息失败,session错误,正在尝试重新登录!')
                    logger.info("开始登录流程...")
                    logger.info("账号: " + config['username'])
                    login = requests.post(
                        url="http://chat.thisit.cc/index.php?action=api.passport.passwordLogin&body_format=json&lang=1",
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
                        url="http://chat.thisit.cc/index.php?action=page.passport.login&action=api.site.login&body_format=json",
                        json={
                            "action": "api.site.login",
                            "body": {
                                "@type": "type.googleapis.com/site.ApiSiteLoginRequest",
                                "preSessionId": t,
                                "loginName": config['username'],
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
                else:
                    logger.error('获取消息失败,session错误!')
                    sys.exit()
            else:
                logger.warn('出现了一个无法解析的消息!' + str(e))
        except Exception as e:
            logger.error('出现了一个错误:' + str(e))
        await asyncio.sleep(config['wait_time'] / 1000)


asyncio.run(message_loop())
