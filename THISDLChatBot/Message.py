from .Constants import *
from .Types import MessageType, RoomType


class Message:
    """消息类"""
    def __init__(self, raw_message: dict, bot) -> None:
        """创建消息对象的方法"""
        self.raw_message = raw_message
        self.bot = bot

    def __getitem__(self, item: str):
        """获取消息json值的函数"""
        return self.raw_message[item]

    def __str__(self) -> str:
        """将消息信息专为字符串的方法"""
        return str(self.raw_message)

    def get_message_id(self):
        """获取消息msg_id的方法"""
        return self.raw_message.get('msgId')

    def get_type(self):
        """获取消息type的方法"""
        return MessageType(self.raw_message['type'])

    def get_room_type(self):
        """获取消息聊天室类型的方法"""
        if self.raw_message['msgId'].startswith('G'):
            return RoomType.Group
        return RoomType.Private

    def get_user_id(self):
        """获取消息发自用户user_id的方法"""
        return self.raw_message.get('fromUserId')

    async def get_from_user(self):
        """获取消息发自用户的方法"""
        return await self.bot.get_friend_profile(self.raw_message.get('fromUserId'))

    def get_group_id(self):
        """获取消息发自群group_id的方法"""
        if self.get_room_type() == RoomType.Private:
            return None
        return self.raw_message.get('toGroupId')

    async def get_from_group(self):
        """获取消息发自群的方法"""
        return await self.bot.get_group_profile(self.raw_message.get('toGroupId'))

    def get_pointer(self) -> str:
        """获取消息pointer的方法"""
        return self.raw_message['pointer']

    def get_data(self):
        """获取消息内容的方法
        若消息是文本消息,则返回消息的文本
        若消息是好友申请,则返回是否自动同意
        若消息是通知,则返回通知内容
        若消息是GIF表情、文件、图片,则返回GIF文件url
        若消息是撤回,则返回撤回消息的message_id
        若消息是html信息,则返回html源码"""
        if self.get_type() == MessageType.MessageText:
            return self.raw_message['text']['body']
        if self.get_type() == MessageType.MessageEventFriendRequest:
            return self.bot.config['auto_accept']
        if self.get_type() == MessageType.MessageNotice:
            return self.raw_message['notice']['body']
        if self.get_type() == MessageType.MessageWeb:
            if self.raw_message['web']['title'] == 'GIF':
                image_url = (f'{server}/'
                             + self.raw_message['web']['code'].split('<img src=\"')[1].split('\"')[0])
                return image_url
            return self.raw_message['web']['code']
        if self.get_type() == MessageType.MessageDocument:
            file_url = (f"{server}/index.php?action=http.file.downloadFile&fileId="
                        + self.raw_message['document']['url']
                        + "&returnBase64=0&isGroupMessage=0&messageId="
                        + self.raw_message['msgId']
                        + "&lang=1")
            return file_url
        if self.get_type() == MessageType.MessageImage:
            image_url = (f"{server}/index.php?action=http.file.downloadFile&fileId="
                         + self.raw_message['image']['url']
                         + "&returnBase64=0&lang=1")
            return image_url
        if self.get_type() == MessageType.MessageRecall:
            result = {'msgId': self.raw_message['recall']['msgId']}
            if self.get_room_type() == RoomType.Group:
                result['Group'] = self.get_from_group()
            else:
                result['Friend'] = self.get_from_user()
            return result

    def is_command(self):
        """判断消息是不是命令的方法"""
        return self.get_type() == MessageType.MessageText and self.get_data().startswith('/')
