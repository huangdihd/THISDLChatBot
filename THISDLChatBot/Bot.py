import _io

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
            messages = await self._get_messages()
            for RawMessage in messages:
                message = Message(RawMessage, self)
                await self._update_pointer(message)
                if (await message.get_from_user()).get_user_id() == self.userid:
                    continue
                if message.is_command():
                    self._command_processor(message)
                if message.get_type() == 'MessageEventFriendRequest' and self.config['auto_accept']:
                    await self.accept(True, (await message.get_from_user()).get_user_id())
                self._message_processor(message)
            await asyncio.sleep(self.config['wait_time'] / 1000)

    def _command_processor(self, message: Message):
        for plugin in self.plugins:
            for commandProcessor in plugin.CommandProcessors:
                if (message.get_data() + ' ').startswith(f'/{commandProcessor.command} '):
                    asyncio.create_task(
                        commandProcessor.process((message.get_data() + ' ').split(' ')[1:], message, self))

    def _message_processor(self, message: Message):
        for plugin in self.plugins:
            for messageProcessor in plugin.MessageProcessors:
                asyncio.create_task(messageProcessor.process(message, self, ))

    async def _update_pointer(self, message: Message):
        if message.get_room_type() == 'Private':
            await self._httpclient.post(
                url="http://chat.thisit.cc/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
                json={
                    "action": "im.cts.updatePointer",
                    "body": {
                        "@type": "type.googleapis.com/site.ImCtsUpdatePointerRequest",
                        "u2Pointer": message.get_pointer(),
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
                            (await message.get_from_group()).get_group_id(): message.get_pointer()
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

    async def _get_messages(self):
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
                return await self._get_messages()
            else:
                pass

    async def _up_load_file(self, file: _io.BufferedReader, file_type: int, file_name: str) -> str:
        data = {
            'fileType': file_type,
            'isMessageAttachment': 'true'
        }
        file = {
            'file': (file_name, file, 'application/octet-stream')
        }
        response = await self._httpclient.post('http://chat.thisit.cc/index.php?action=http.file.uploadWeb', files=file,
                                               data=data, cookies=dict(zaly_site_user=self.token))
        if response.json()['errorInfo'] != '':
            raise UpLoadFileFailedException(response.json()['errorInfo'])
        return response.json()['fileId']

    async def _get_pre_session_id(self) -> str:
        login_data = {
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
            json=login_data)
        try:
            pre_session_id = response.json()['body']['preSessionId']
        except KeyError:
            raise LoginFailedException(response.json())
        return pre_session_id

    async def _login(self):
        self._httpclient = httpx.AsyncClient()
        pre_session_id = await self._get_pre_session_id()
        login_data = {
            "action": "api.site.login",
            "body": {
                "@type": "type.googleapis.com/site.ApiSiteLoginRequest",
                "preSessionId": pre_session_id,
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
            json=login_data)
        try:
            self.userid = response.json()['body']['profile']['public']['userId']
            self.token = response.cookies['zaly_site_user']
        except KeyError:
            raise LoginFailedException(response.json())

    async def download_file(self, url: str) -> bytes:
        cookies = {'zaly_site_user': self.token}
        return (await self._httpclient.get(url, cookies=cookies)).content

    async def get_friends(self):
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
                    friends.append(self.get_friend_profile(friend['profile']['userId']))
        except KeyError:
            return []
        return friends

    async def get_groups(self):
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
            groups.append(await self.get_group_profile(group))
        try:
            return groups
        except KeyError:
            return []

    async def get_friend_profile(self, user_id) -> Friend:
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

    async def get_group_profile(self, group_id) -> Group:
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

    async def get_userid(self) -> str:
        return self.userid

    async def send_text(self, to: Friend, text: str) -> str:
        if text is None or text == '':
            raise ValueError("The text parameter must have a value!")
        msg_id = f"U2-{math.floor(round(time.time(), 3) * 1000)}"
        message_data = {
            "action": "im.cts.message",
            "body": {
                "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                "message": {
                    "fromUserId": self.userid,
                    "roomType": "MessageRoomU2",
                    "toUserId": to.get_user_id(),
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
                                    json=message_data)
        self.packageId += 1
        return msg_id

    async def send_text_to_group(self, to: Group, text: str) -> str:
        if text is None or text == '':
            raise ValueError("The text parameter must have a value!")
        msg_id = f"GROUP-{math.floor(round(time.time(), 3) * 1000)}"
        message_data = {
            "action": "im.cts.message",
            "body": {
                "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                "message": {
                    "fromUserId": self.userid,
                    "roomType": "MessageRoomGroup",
                    "toGroupId": to.get_group_id(),
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
                                    json=message_data)
        self.packageId += 1
        return msg_id

    async def send_file(self, to: Friend, file: _io.BufferedReader, filename: str = None) -> str:
        if filename is None:
            filename = file.name
        file_id = await self._up_load_file(file, 3, filename)
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
                                                "toUserId": to.get_user_id(),
                                                "msgId": f"U2-{math.floor(round(time.time(), 3) * 1000)}",
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "document": {
                                                    "url": file_id,
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

    async def send_file_to_group(self, to: Group, file: _io.BufferedReader, filename: str = None) -> str:
        if filename is None:
            filename = file.name
        file_id = await self._up_load_file(file, 3, filename)
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
                                                "toGroupId": to.get_group_id(),
                                                "msgId": msg_id,
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "document": {
                                                    "url": file_id,
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

    async def send_image(self, to: Friend, file: _io.BufferedReader, filename: str = None) -> str:
        if filename is None:
            filename = file.name
        file_id = await self._up_load_file(file, 1, filename)
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
                                                "toUserId": to.get_user_id(),
                                                "msgId": msg_id,
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "image": {
                                                    "url": file_id,
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

    async def send_image_to_group(self, to: Group, file: _io.BufferedReader, filename: str = None) -> str:
        if filename is None:
            filename = file.name
        file_id = await self._up_load_file(file, 3, filename)
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
                                                "toGroupId": to.get_group_id(),
                                                "msgId": msg_id,
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "image": {
                                                    "url": file_id,
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

    async def apply_friend(self, user_id: str, greeting: str):
        await self._httpclient.post(url='http://chat.thisit.cc/index.php?action=miniProgram.square.apply', json={
            "friendId": user_id,
            "greeting": greeting
        }, cookies={
            'zaly_site_user': self.token
        })

    async def recall_message(self, message_id: str, user: Friend):
        await self._httpclient.post(url='http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1',
                                    json={
                                        "action": "im.cts.message",
                                        "body": {
                                            "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                            "message": {
                                                "fromUserId": self.userid,
                                                "roomType": "MessageRoomU2",
                                                "toUserId": user.get_user_id(),
                                                "msgId": f"U2-{math.floor(round(time.time(), 3) * 1000)}",
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "recall": {
                                                    "msgId": message_id,
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

    async def recall_message_from_group(self, message_id: str, group: Group):
        await self._httpclient.post(url='http://chat.thisit.cc/index.php?action=im.cts.message&body_format=json&lang=1',
                                    json={
                                        "action": "im.cts.message",
                                        "body": {
                                            "@type": "type.googleapis.com/site.ImCtsMessageRequest",
                                            "message": {
                                                "fromUserId": self.userid,
                                                "roomType": "MessageRoomGroup",
                                                "toGroupId": group.get_group_id(),
                                                "msgId": f"GROUP-{math.floor(round(time.time(), 3) * 1000)}",
                                                "timeServer": round(time.time(), 3) * 1000,
                                                "recall": {
                                                    "msgId": message_id,
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

    async def accept(self, agree: bool, user_id: str):
        response = await self._httpclient.post(
            url="http://chat.thisit.cc/index.php?action=api.friend.accept&body_format=json&lang=1",
            json={
                "action": "api.friend.accept",
                "body": {
                    "@type": "type.googleapis.com/site.ApiFriendAcceptRequest",
                    "applyUserId": user_id,
                    "agree": agree
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

    def load_plugin(self, plugin: Plugin):
        plugin.bot = self
        self.plugins.append(plugin)
        self.loop.run_until_complete(plugin.onload())
