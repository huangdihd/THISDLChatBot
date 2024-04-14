import _io
from typing import Any, Coroutine

import httpx
import time
import math
import asyncio
from PIL import Image
from .Config import Config
from .Exceptions import LoginFailedException, UpLoadFileFailedException
from .Friend import Friend
from .Group import Group
from .Logger import Logger
from .Message import Message
from .Plugin import Plugin


class Bot:

    def __init__(self, config: Config, logger: Logger) -> None:
        self.logger = logger
        self.config = config
        self.loop = asyncio.get_event_loop()
        self.packageId = 1
        self.plugins = []

    async def _start(self):
        while True:
            messages = await self._GetMessages()
            for RawMessage in messages:
                message = Message(RawMessage, self)
                await self._UpdatePointer(message)
                if (await message.GetFromUser()).GetUserId() == self.userid:
                    continue
                if message.IsCommand():
                    await self._CommandProcessor(message)
                if message.GetType() == 'MessageEventFriendRequest' and self.config['auto_accept']:
                    await self.Accept(True, (await message.GetFromUser()).GetUserId())
                await self._MessageProcessor(message)
            await asyncio.sleep(self.config['wait_time'] / 1000)

    async def _CommandProcessor(self, message: Message):
        for plugin in self.plugins:
            for commandProcessor in plugin.CommandProcessors:
                if (message.GetData() + ' ').startswith(f'/{commandProcessor.command} '):
                    await commandProcessor.Process((message.GetData() + ' ').split(' ')[1:], message, self)

    async def _MessageProcessor(self, message: Message):
        for plugin in self.plugins:
            for messageProcessor in plugin.MessageProcessors:
                await messageProcessor.Process(message, self)

    async def _UpdatePointer(self, message: Message):
        if message.GetRoomType() == 'Private':
            await self._httpclient.post(
                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
                json={
                    "action": "im.cts.updatePointer",
                    "body": {
                        "@type": "type.googleapis.com/site.ImCtsUpdatePointerRequest",
                        "u2Pointer": message.GetPointer(),
                        "groupsPointer": {}
                    },
                    "header": {
                        "_3": self.token,
                        "_4": "http://chat.thisit.cc/index.php",
                        "_8": "1",
                        "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/115.0.0.0 Safari/537.36"
                    },
                    "packageId": self.packageId
                })
        else:
            await self._httpclient.post(
                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
                json={
                    "action": "im.cts.updatePointer",
                    "body": {
                        "@type": "type.googleapis.com/site.ImCtsUpdatePointerRequest",
                        "u2Pointer": 0,
                        "groupsPointer": {
                            (await message.GetFromGroup()).GetGroupId(): message.GetPointer()
                        }
                    },
                    "header": {
                        "_3": self.token,
                        "_4": "http://chat.thisit.cc/index.php",
                        "_8": "1",
                        "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/115.0.0.0 Safari/537.36"
                    },
                    "packageId": self.packageId
                })
        self.packageId += 1

    async def _GetMessages(self):
        response = await self._httpclient.post(url="http://chat.thisit.cc/index.php?action=im.cts.sync&body_format"
                                                   "=json&lang=1",
                                               json={
                                                   "action": "im.cts.sync",
                                                   "body": {
                                                       "@type": "type.googleapis.com/site.ImCtsSyncRequest",
                                                       "u2Count": 200,
                                                       "groupCount": 200
                                                   },
                                                   "header": {
                                                       "_3": self.token,
                                                       "_4": "http://chat.thisit.cc/index.php",
                                                       "_8": "1",
                                                       "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 "
                                                             "Safari/537.36"
                                                   },
                                                   "packageId": self.packageId
                                               })
        self.packageId += 1
        try:
            return response.json()['body']['list'][:-1]
        except KeyError:
            self.logger.error('消息结构错误')
            if self.config['auto_login']:
                self.logger.error('重新登录...')
                await self._login()
                return await self._GetMessages()
            else:
                pass

    async def _UpLoadFile(self, File: _io.BufferedReader, FileType: int, FileName: str) -> str:
        Data = {
            'fileType': FileType,
            'isMessageAttachment': 'true'
        }
        file = {
            'file': (FileName, File, 'application/octet-stream')
        }
        response = await self._httpclient.post('http://chat.thisit.cc/index.php?action=http.file.uploadWeb', files=file,
                                               data=Data, cookies={'zaly_site_user': self.token})
        if response.json()['errorInfo'] != '':
            raise UpLoadFileFailedException(response.json()['errorInfo'])
        return response.json()['fileId']

    async def _GetPreSessionId(self) -> str:
        LoginData = {
            "action": "api.passport.passwordLogin",
            "body": {
                "@type": "type.googleapis.com/site.ApiPassportPasswordLoginRequest",
                "loginName": self.config['username'],
                "password": self.config['password']
            },
            "header": {
                "_4": "http://chat.thisit.cc/index.php",
                "_8": "1",
                "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
            },
            "packageId": 1
        }
        response = await self._httpclient.post(
            "http://chat.thisit.cc/index.php?action=api.passport.passwordLogin&body_format=json&lang=1",
            json=LoginData)
        try:
            preSessionId = response.json()['body']['preSessionId']
        except KeyError:
            raise LoginFailedException(response.json())
        return preSessionId

    async def _login(self):
        self._httpclient = httpx.AsyncClient()
        preSessionId = await self._GetPreSessionId()
        LoginData = {
            "action": "api.site.login",
            "body": {
                "@type": "type.googleapis.com/site.ApiSiteLoginRequest",
                "preSessionId": preSessionId,
                "loginName": self.config['username'],
                "isRegister": False,
                "thirdPartyKey": ""
            },
            "header": {
                "_4": "http://chat.thisit.cc/index.php?action=page.passport.login",
                "_8": "1",
                "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
            },
            "packageId": 2
        }
        response = await self._httpclient.post(
            "http://chat.thisit.cc/index.php?action=page.passport.login&action=api.site.login&body_format=json",
            json=LoginData)
        try:
            self.userid = response.json()['body']['profile']['public']['userId']
            self.token = response.cookies['zaly_site_user']
        except KeyError:
            raise LoginFailedException(response.json())

    async def DownLoadFile(self, Url: str) -> bytes:
        cookies = {'zaly_site_user': self.token}
        return (await self._httpclient.get(Url, cookies=cookies)).content

    async def GetFriends(self):
        response = await self._httpclient.post(
            'http://chat.thisit.cc/index.php?action=api.friend.list&body_format=json&lang=1', json={
                "action": "api.friend.list",
                "body": {
                    "@type": "type.googleapis.com/site.ApiFriendListRequest",
                    "offset": 0,
                    "count": 200
                },
                "header": {
                    "_3": self.token,
                    "_4": "http://chat.thisit.cc/",
                    "_8": "1",
                    "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36"
                },
                "packageId": self.packageId
            })
        self.packageId += 1
        friends = []
        try:
            for friend in response.json()['body']['friends']:
                if friend['profile']['userId'] != self.userid:
                    friends.append(self.GetFriendProfile(friend['profile']['userId']))
        except KeyError:
            return []
        return friends

    async def GetGroups(self):
        response = await self._httpclient.post(
            'http://chat.thisit.cc/index.php?action=api.group.list&body_format=json&lang=1', json={
                "action": "api.group.list",
                "body": {
                    "@type": "type.googleapis.com/site.ApiGroupListRequest",
                    "offset": 0,
                    "count": 200
                },
                "header": {
                    "_3": self.token,
                    "_4": "http://chat.thisit.cc/",
                    "_8": "1",
                    "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36"
                },
                "packageId": self.packageId
            })
        self.packageId += 1
        groups = []
        for group in response.json()['body']['list']:
            groups.append(await self.GetGroupProfile(group))
        try:
            return groups
        except KeyError:
            return []

    async def GetFriendProfile(self, user_id) -> Friend:
        response = await self._httpclient.post(
            url="http://chat.thisit.cc/index.php?action=api.friend.profile&body_format=json&lang=1",
            json={
                "action": "api.friend.profile",
                "body": {
                    "@type": "type.googleapis.com/site.ApiFriendProfileRequest",
                    "userId": user_id
                },
                "header": {
                    "_3": self.token,
                    "_4": "http://chat.thisit.cc/index.php",
                    "_8": "1",
                    "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
                },
                "packageId": self.packageId
            })
        self.packageId += 1
        return Friend(response.json()['body']['profile']['profile'])

    async def GetGroupProfile(self, group_id) -> Group:
        response = await self._httpclient.post(
            url='http://chat.thisit.cc/index.php?action=api.group.profile&body_format=json&lang=1',
            json={
                "action": "api.group.profile",
                "body": {
                    "@type": "type.googleapis.com/site.ApiGroupProfileRequest",
                    "groupId": group_id
                },
                "header": {
                    "_3": self.token,
                    "_4": "http://chat.thisit.cc/index.php",
                    "_8": "1",
                    "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36"
                },
                "packageId": self.packageId
            })
        self.packageId += 1
        return Group(response.json()['body']['profile'])

    async def GetUserid(self) -> str:
        return self.userid

    async def SendText(self, to: Friend, text: str) -> str:
        if text is None or text == '':
            raise ValueError("The text parameter must have a value!")
        msg_id = f"U2-{math.floor(round(time.time(), 3) * 1000)}"
        MessageData = {
            "action": "im.cts.message",
            "body": {
                "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                "message": {
                    "fromUserId": self.userid,
                    "roomType": "MessageRoomU2",
                    "toUserId": to.GetUserId(),
                    "msgId": msg_id,
                    "timeServer": round(time.time(), 3) * 1000,
                    "text": {
                        "body": text
                    },
                    "type": "MessageText"
                }
            },
            "header": {
                "_3": self.token,
                "_4": "http://chat.thisit.cc/index.php",
                "_8": "1",
                "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
            },
            "packageId": self.packageId
        }
        await self._httpclient.post('http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1',
                                    json=MessageData)
        self.packageId += 1
        return msg_id

    async def SendTextToGroup(self, to: Group, text: str) -> str:
        if text is None or text == '':
            raise ValueError("The text parameter must have a value!")
        msg_id = f"GROUP-{math.floor(round(time.time(), 3) * 1000)}"
        MessageData = {
            "action": "im.cts.message",
            "body": {
                "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                "message": {
                    "fromUserId": self.userid,
                    "roomType": "MessageRoomGroup",
                    "toGroupId": to.GetGroupId(),
                    "msgId": msg_id,
                    "timeServer": round(time.time(), 3) * 1000,
                    "text": {
                        "body": text
                    },
                    "type": "MessageText"
                }
            },
            "header": {
                "_3": self.token,
                "_4": "http://chat.thisit.cc/index.php",
                "_8": "1",
                "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
            },
            "packageId": self.packageId
        }
        await self._httpclient.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                                    json=MessageData)
        self.packageId += 1
        return msg_id

    async def SendFile(self, to: Friend, file: _io.BufferedReader, filename: str = None) -> str:
        if filename is None:
            filename = file.name
        fileId = await self._UpLoadFile(file, 3, filename)
        file.seek(0, 2)
        msg_id = f"U2-{math.floor(round(time.time(), 3) * 1000)}"
        await self._httpclient.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                                    json={
                                        "action": "im.cts.message",
                                        "body": {
                                            "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                            "message": {
                                                "fromUserId": self.userid,
                                                "roomType": "MessageRoomU2",
                                                "toUserId": to.GetUserId(),
                                                "msgId": f"U2-{math.floor(round(time.time(), 3) * 1000)}",
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "document": {
                                                    "url": fileId,
                                                    "size": file.tell(),
                                                    "name": filename
                                                },
                                                "type": "MessageDocument"
                                            }
                                        },
                                        "header": {
                                            "_3": self.token,
                                            "_4": "http://chat.thisit.cc/index.php",
                                            "_8": "1",
                                            "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
                                                  "like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
                                        },
                                        "packageId": self.packageId
                                    })
        self.packageId += 1
        return msg_id

    async def SendFileToGroup(self, to: Group, file: _io.BufferedReader, filename: str = None) -> str:
        if filename is None:
            filename = file.name
        fileId = await self._UpLoadFile(file, 3, filename)
        file.seek(0, 2)
        msg_id = f"GROUP-{math.floor(round(time.time(), 3) * 1000)}"
        await self._httpclient.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                                    json={
                                        "action": "im.cts.message",
                                        "body": {
                                            "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                            "message": {
                                                "fromUserId": self.userid,
                                                "roomType": "MessageRoomGroup",
                                                "toGroupId": to.GetGroupId(),
                                                "msgId": msg_id,
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "document": {
                                                    "url": fileId,
                                                    "size": file.tell(),
                                                    "name": file.name
                                                },
                                                "type": "MessageDocument"
                                            }
                                        },
                                        "header": {
                                            "_3": self.token,
                                            "_4": "http://chat.thisit.cc/index.php",
                                            "_8": "1",
                                            "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                                                  "KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                                        },
                                        "packageId": self.packageId
                                    })
        self.packageId += 1
        return msg_id

    async def SendImage(self, to: Friend, file: _io.BufferedReader, filename: str = None) -> str:
        if filename is None:
            filename = file.name
        fileId = await self._UpLoadFile(file, 1, filename)
        file.seek(0, 2)
        msg_id = f"U2-{math.floor(round(time.time(), 3) * 1000)}"
        await self._httpclient.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                                    json={
                                        "action": "im.cts.message",
                                        "body": {
                                            "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                            "message": {
                                                "fromUserId": self.userid,
                                                "roomType": "MessageRoomU2",
                                                "toUserId": to.GetUserId(),
                                                "msgId": msg_id,
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "image": {
                                                    "url": fileId,
                                                    "width": Image.open(file).size[0],
                                                    "height": Image.open(file).size[1]
                                                },
                                                "type": "MessageImage"
                                            }
                                        },
                                        "header": {
                                            "_3": self.token,
                                            "_4": "http://chat.thisit.cc/index.php",
                                            "_8": "1",
                                            "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                                                  "KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
                                        },
                                        "packageId": self.packageId
                                    })
        self.packageId += 1
        return msg_id

    async def SendImageToGroup(self, to: Group, file: _io.BufferedReader, filename: str = None) -> str:
        if filename is None:
            filename = file.name
        fileId = await self._UpLoadFile(file, 3, filename)
        file.seek(0, 2)
        msg_id = f"GROUP-{math.floor(round(time.time(), 3) * 1000)}"
        await self._httpclient.post(url="http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1",
                                    json={
                                        "action": "im.cts.message",
                                        "body": {
                                            "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                            "message": {
                                                "fromUserId": self.userid,
                                                "roomType": "MessageRoomGroup",
                                                "toGroupId": to.GetGroupId(),
                                                "msgId": msg_id,
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "image": {
                                                    "url": fileId,
                                                    "width": Image.open(file).size[0],
                                                    "height": Image.open(file).size[1]
                                                },
                                                "type": "MessageImage"
                                            }
                                        },
                                        "header": {
                                            "_3": self.token,
                                            "_4": "http://chat.thisit.cc/index.php",
                                            "_8": "1",
                                            "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                                                  "KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                                        },
                                        "packageId": self.packageId
                                    })
        self.packageId += 1
        return msg_id

    async def ApplyFriend(self, UserId: str, greeting: str):
        await self._httpclient.post(url='http://chat.thisit.cc/index.php?action=miniProgram.square.apply', json={
            "friendId": UserId,
            "greeting": greeting
        }, cookies={
            'zaly_site_user': self.token
        })

    async def RecallMessage(self, MessageId: str, user: Friend):
        await self._httpclient.post(url='http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1',
                                    json={
                                        "action": "im.cts.message",
                                        "body": {
                                            "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                            "message": {
                                                "fromUserId": self.userid,
                                                "roomType": "MessageRoomU2",
                                                "toUserId": user.GetUserId(),
                                                "msgId": f"U2-{math.floor(round(time.time(), 3) * 1000)}",
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "recall": {
                                                    "msgId": MessageId,
                                                    "msgText": "此消息被撤回"
                                                },
                                                "type": "MessageRecall"
                                            }
                                        },
                                        "header": {
                                            "_3": self.token,
                                            "_4": "http://chat.thisit.cc/",
                                            "_8": "1",
                                            "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                                                  "KHTML, like Gecko)"
                                                  "Chrome/115.0.0.0 Safari/537.36"
                                        },
                                        "packageId": self.packageId
                                    })
        self.packageId += 1

    async def RecallMessageFromGroup(self, MessageId: str, group: Group):
        await self._httpclient.post(url='http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1',
                                    json={
                                        "action": "im.cts.message",
                                        "body": {
                                            "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                            "message": {
                                                "fromUserId": self.userid,
                                                "roomType": "MessageRoomGroup",
                                                "toGroupId": group.GetGroupId(),
                                                "msgId": f"GROUP-{math.floor(round(time.time(), 3) * 1000)}",
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "recall": {
                                                    "msgId": MessageId,
                                                    "msgText": "此消息被撤回"
                                                },
                                                "type": "MessageRecall"
                                            }
                                        },
                                        "header": {
                                            "_3": self.token,
                                            "_4": "http://chat.thisit.cc/",
                                            "_8": "1",
                                            "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                                                  "KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                                        },
                                        "packageId": self.packageId
                                    })

    async def Accept(self, Agree: bool, UserId: str):
        response = await self._httpclient.post(
            url="http://chat.thisit.cc/index.php?action=api.friend.accept&body_format=json&lang=1",
            json={
                "action": "api.friend.accept",
                "body": {
                    "@type": "type.googleapis.com/site.ApiFriendAcceptRequest",
                    "applyUserId": UserId,
                    "agree": Agree
                },
                "header": {
                    "_3": self.token,
                    "_4": "http://chat.thisit.cc/index.php",
                    "_8": "1",
                    "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36"
                },
                "packageId": self.packageId
            })
        self.packageId += 1
        return response.json()['header']['_1'] == 'success'

    def start(self):
        self.logger.info('机器人启动...')
        self.loop.run_until_complete(self._login())
        self.logger.success('登录成功!')
        self.loop.run_until_complete(self._start())

    def LoadPlugin(self, plugin: Plugin):
        plugin.bot = self
        self.plugins.append(plugin)
        self.loop.run_until_complete(plugin.OnLoad())
