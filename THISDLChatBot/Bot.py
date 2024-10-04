import _io
from typing import Any, Coroutine

import httpcore
import httpx
import time
import math
import asyncio
from PIL import Image
from httpx import Response

from .Constants import *
from .Config import Config
from .Exceptions import LoginFailedException, UpLoadFileFailedException, HttpResponseException
from .Friend import Friend
from .Group import Group
from .Logger import Logger
from .Message import Message
from .Plugin import Plugin


class Bot:
    """机器人类"""

    def __init__(self, config: Config, logger: Logger) -> None:
        """创建一个机器人对象"""
        self.logger = logger
        self.config = config
        self.loop = asyncio.get_event_loop()
        self.packageId = 1
        self._plugins = []
        self.token = ""
        self._running = False
        logger.set_level(config['logger_level'])

    async def _start(self):
        """用于启动机器人的内部异步方法"""
        while self._running:
            messages = await self._get_messages()
            for raw_message in messages:
                message = Message(raw_message, self)
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
        """用于处理命令的内部方法"""
        for plugin in self._plugins:
            plugin.process_command(message)

    def _message_processor(self, message: Message):
        """用于处理命令的内部方法"""
        for plugin in self._plugins:
            plugin.process_message(message)

    def _get_requests_json(self, action: str, body: dict) -> dict:
        """用于生成带有bot的token信息和package_id的json请求体的内部方法"""
        return {
            "action": action,
            "body": body,
            "header": {
                "_3": self.token,
                "_4": f"{server}/index.php",
                "_8": "1",
                "_6": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
            },
            "packageId": self.packageId
        }

    async def _http_post(self, url: str, action: str, body: dict) -> Response:
        """用于发出post请求的内部方法"""
        self.packageId += 1
        for step in range(self.config['http_retry']):
            try:
                response = await self._httpclient.post(url=url, json=self._get_requests_json(action, body))
                if response.status_code != 200:
                    raise HttpResponseException(response.text)

                try:
                    response.json()
                except ValueError:
                    raise HttpResponseException(response.text)

                try:
                    status = response.json()['header']['_1']
                except KeyError:
                    raise HttpResponseException(response.text)

                if status != 'success':
                    raise HttpResponseException(response.text)
                return response
            except HttpResponseException as exc:
                self.logger.error(f'http请求返回信息错误:{exc}')
            except httpx.ReadTimeout:
                self.logger.error('请求超时,请检查网络...')
            except httpx.ConnectTimeout:
                self.logger.error('请求超时,请检查网络...')
            except httpcore.ConnectError as exc:
                self.logger.error(f'连接失败,请检查网络:{exc}')
            except httpx.ConnectError as exc:
                self.logger.error(f'连接失败,请检查网络:{exc}')
            await asyncio.sleep(2)

    async def _update_pointer(self, message: Message):
        """用于更新pointer的内部方法"""
        u2_pointer = 0
        groups_pointer = {}
        if message.get_room_type() == 'Private':
            u2_pointer = message.get_pointer()
        else:
            groups_pointer = {
                (await message.get_from_group()).get_group_id(): message.get_pointer()
            }
        await self._http_post(
            url=f"{server}/index.php?action=im.cts.updatePointer&body_format=json&lang=1",
            action="im.cts.updatePointer",
            body={
                "@type": "type.googleapis.com/site.ImCtsUpdatePointerRequest",
                "u2Pointer": u2_pointer,
                "groupsPointer": groups_pointer
            }
        )

    async def _get_messages(self):
        """用于获取消息列表的内部方法"""
        response = await self._http_post(
            url=f"{server}/index.php?action=im.cts.sync&body_format=json&lang=1",
            action="im.cts.sync",
            body={
                "@type": "type.googleapis.com/site.ImCtsSyncRequest",
                "u2Count": 200,
                "groupCount": 200
            }
        )

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
        """用于上传文件的内部方法"""
        data = {
            'fileType': file_type,
            'isMessageAttachment': 'true'
        }
        file = {
            'file': (file_name, file, 'application/octet-stream')
        }
        response = await self._httpclient.post(
            url=f'{server}/index.php?action=http.file.uploadWeb',
            files=file,
            data=data,
            cookies=dict(zaly_site_user=self.token)
        )
        if response.json()['errorInfo'] != '':
            raise UpLoadFileFailedException(response.json()['errorInfo'])
        return response.json()['fileId']

    async def _get_pre_session_id(self) -> str:
        """获取pre_session_id的内部方法"""
        response = await self._http_post(
            f"{server}/index.php?action=api.passport.passwordLogin&body_format=json&lang=1",
            action="api.passport.passwordLogin",
            body={
                "@type": "type.googleapis.com/site.ApiPassportPasswordLoginRequest",
                "loginName": self.config['username'],
                "password": self.config['password']
            })
        try:
            pre_session_id = response.json()['body']['preSessionId']
        except KeyError:
            raise LoginFailedException(response.json())
        return pre_session_id

    async def _login(self):
        """用于登录的内部方法"""
        self._httpclient = httpx.AsyncClient()
        pre_session_id = await self._get_pre_session_id()
        response = await self._http_post(
            f"{server}/index.php?action=page.passport.login&action=api.site.login&body_format=json",
            action="api.site.login",
            body={
                "@type": "type.googleapis.com/site.ApiSiteLoginRequest",
                "preSessionId": pre_session_id,
                "loginName": self.config['username'],
                "isRegister": False,
                "thirdPartyKey": ""
            })
        try:
            self.userid = response.json()['body']['profile']['public']['userId']
            self.token = response.cookies['zaly_site_user']
        except KeyError:
            raise LoginFailedException(response.json())

    async def download_file(self, url: str) -> bytes:
        """用于使用机器人账户信息下载带鉴权文件的方法"""
        cookies = {'zaly_site_user': self.token}
        return (await self._httpclient.get(url, cookies=cookies)).content

    async def get_friends(self) -> list[Any] | list[Coroutine[Any, Any, Friend]]:
        """获取机器人好友列表的方法"""
        response = await self._http_post(
            f'{server}/index.php?action=api.friend.list&body_format=json&lang=1',
            action="api.friend.list",
            body={
                "@type": "type.googleapis.com/site.ApiFriendListRequest",
                "offset": 0,
                "count": 200
            }
        )
        try:
            friends = [self.get_friend_profile(friend['profile']['userId'])
                       for friend in response.json()['body']['friends'] if friend['profile']['userId'] != self.userid]
        except KeyError:
            return []
        return friends

    async def get_groups(self):
        """获取机器人所有所在群列表的方法"""
        response = await self._http_post(
            f'{server}/index.php?action=api.group.list&body_format=json&lang=1',
            action="api.group.list",
            body={
                "@type": "type.googleapis.com/site.ApiGroupListRequest",
                "offset": 0,
                "count": 200
            }
        )
        groups = [await self.get_group_profile(group) for group in response.json()['body']['list']]
        try:
            return groups
        except KeyError:
            return []

    async def get_friend_profile(self, user_id) -> Friend:
        """通过好友user_id获取好友详细信息的方法"""
        response = await self._http_post(
            url=f"{server}/index.php?action=api.friend.profile&body_format=json&lang=1",
            action="api.friend.profile",
            body={
                "@type": "type.googleapis.com/site.ApiFriendProfileRequest",
                "userId": user_id
            }
        )

        return Friend(response.json()['body']['profile']['profile'])

    async def get_group_profile(self, group_id) -> Group:
        """通过群group_id获取群详细信息的方法"""
        response = await self._http_post(
            url=f'{server}/index.php?action=api.group.profile&body_format=json&lang=1',
            action="api.group.profile",
            body={
                "@type": "type.googleapis.com/site.ApiGroupProfileRequest",
                "groupId": group_id
            }
        )

        return Group(response.json()['body']['profile'])

    async def get_userid(self) -> str:
        """获取机器人user_id的方法"""
        return self.userid

    async def send_text(self, to: Friend, text: str) -> str:
        """发送文本消息到好友的方法"""
        if text is None or text == '':
            raise ValueError("The text parameter must have a value!")
        msg_id = f"U2-{math.floor(round(time.time(), 3) * 1000)}"
        await self._http_post(
            url=f'{server}/index.php?action=im.cts.message&body_format=json&lang=1',
            action="im.cts.message",
            body={
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
            }
        )
        return msg_id

    async def send_text_to_group(self, to: Group, text: str) -> str:
        """发送文本消息到群的方法"""
        if text is None or text == '':
            raise ValueError("The text parameter must have a value!")
        msg_id = f"GROUP-{math.floor(round(time.time(), 3) * 1000)}"
        await self._http_post(
            url=f'{server}/index.php?action=im.cts.message&body_format=json&lang=1',
            action="im.cts.message",
            body={
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
            }
        )
        return msg_id

    async def send_file(self, to: Friend, file: _io.BufferedReader, filename: str = None) -> str:
        """发送文件到好友的方法"""
        if filename is None:
            filename = file.name
        file_id = await self._up_load_file(file, 3, filename)
        file.seek(0, 2)
        msg_id = f"U2-{math.floor(round(time.time(), 3) * 1000)}"
        await self._http_post(
            url=f'{server}/index.php?action=im.cts.message&body_format=json&lang=1',
            action="im.cts.message",
            body={
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
            }
        )
        return msg_id

    async def send_file_to_group(self, to: Group, file: _io.BufferedReader, filename: str = None) -> str:
        """发送文件到群的方法"""
        if filename is None:
            filename = file.name
        file_id = await self._up_load_file(file, 3, filename)
        file.seek(0, 2)
        msg_id = f"GROUP-{math.floor(round(time.time(), 3) * 1000)}"
        await self._http_post(
            url=f'{server}/index.php?action=im.cts.message&body_format=json&lang=1',
            action="im.cts.message",
            body={
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
            }
        )
        return msg_id

    async def send_image(self, to: Friend, file: _io.BufferedReader, filename: str = None) -> str:
        """发送图片到好友的方法"""
        if filename is None:
            filename = file.name
        file_id = await self._up_load_file(file, 1, filename)
        file.seek(0, 2)
        msg_id = f"U2-{math.floor(round(time.time(), 3) * 1000)}"
        await self._http_post(
            url=f'{server}/index.php?action=im.cts.message&body_format=json&lang=1',
            action="im.cts.message",
            body={
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
            }
        )
        return msg_id

    async def send_image_to_group(self, to: Group, file: _io.BufferedReader, filename: str = None) -> str:
        """发送文件到群的方法"""
        if filename is None:
            filename = file.name
        file_id = await self._up_load_file(file, 3, filename)
        file.seek(0, 2)
        msg_id = f"GROUP-{math.floor(round(time.time(), 3) * 1000)}"
        await self._http_post(
            url=f'{server}/index.php?action=im.cts.message&body_format=json&lang=1',
            action="im.cts.message",
            body={
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
            }
        )
        return msg_id

    async def apply_friend(self, user_id: str, greeting: str):
        """发送好友申请的方法"""
        await self._httpclient.post(url=f'{server}/index.php?action=miniProgram.square.apply', json={
            "friendId": user_id,
            "greeting": greeting
        }, cookies={
            'zaly_site_user': self.token
        })

    async def recall_message(self, message_id: str, user: Friend):
        """撤回发送到好友的消息的方法"""
        await self._http_post(
            url=f'{server}/index.php?action=im.cts.message&body_format=json&lang=1',
            action="im.cts.message",
            body={
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
            }
        )

    async def recall_message_from_group(self, message_id: str, group: Group):
        """撤回发送到群的消息的方法"""
        await self._http_post(
            url=f'{server}/index.php?action=im.cts.message&body_format=json&lang=1',
            action="im.cts.message",
            body={
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
            }
        )

    async def accept(self, agree: bool, user_id: str):
        """设置是否通过好友申请的方法"""
        response = await self._http_post(
            url=f"{server}/index.php?action=api.friend.accept&body_format=json&lang=1",
            action="api.friend.accept",
            body={
                "@type": "type.googleapis.com/site.ApiFriendAcceptRequest",
                "applyUserId": user_id,
                "agree": agree
            }
        )

        return response.json()['header']['_1'] == 'success'

    def start(self):
        """启动机器人的方法"""
        if self._running:
            return
        try:
            self.logger.info('机器人启动...')
            # 插件启用
            for plugin in self._plugins:
                self.loop.run_until_complete(plugin.on_enable())
            self.loop.run_until_complete(self._login())
            self.logger.success('登录成功!')
            self._running = True
            self.loop.run_until_complete(self._start())
        finally:
            # 插件卸载
            for plugin in self._plugins:
                self.loop.run_until_complete(plugin.on_disable())
            self.logger.info("机器人关闭!")
            self._running = False

    def get_plugins(self) -> list[str]:
        """获取机器人插件列表的方法"""
        return [plugin.name for plugin in self._plugins]

    def has_plugins(self, plugin_name: str) -> bool:
        """查看机器人是否有名为某字符串的插件的方法"""
        return any(plugin.name == plugin_name for plugin in self._plugins)

    def get_plugin(self, plugin_name: str) -> list[Plugin] | None:
        """获取所有名为某字符串的插件的方法"""
        if not self.has_plugins(plugin_name):
            return None
        return [plugin for plugin in self._plugins if plugin.name == plugin_name]

    def load_plugin(self, plugin: Plugin):
        """加载插件的方法"""
        plugin.bot = self
        self._plugins.append(plugin)
        self.loop.run_until_complete(plugin.on_load())
