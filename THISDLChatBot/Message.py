from .Constants import *


class Message:
    """消息类"""
    def __init__(self, raw_message: dict, bot) -> None:
        """创建消息对象的方法"""
        self.RawMessage = raw_message
        self.bot = bot

    def __str__(self) -> str:
        """将消息信息专为字符串的方法"""
        return str(self.RawMessage)

    def get_message_id(self):
        """获取消息msg_id的方法"""
        return self.RawMessage.get('msgId')

    def get_type(self):
        """获取消息type的方法"""
        return self.RawMessage['type']

    def get_room_type(self):
        """获取消息聊天室类型的方法"""
        if self.RawMessage['msgId'].startswith('G'):
            return 'Group'
        return 'Private'

    async def get_from_user(self):
        """获取消息发自用户的方法"""
        return await self.bot.get_friend_profile(self.RawMessage.get('fromUserId'))

    async def get_from_group(self):
        """获取消息发自群的方法"""
        return await self.bot.get_group_profile(self.RawMessage.get('toGroupId'))

    def get_pointer(self) -> str:
        """获取消息pointer的方法"""
        return self.RawMessage['pointer']

    def get_data(self):
        """获取消息内容的方法
        若消息是文本消息,则返回消息的文本
        若消息是好友申请,则返回是否自动同意
        若消息是通知,则返回通知内容
        若消息是GIF表情、文件、图片,则返回GIF文件url
        若消息是撤回,则返回撤回消息的message_id
        若消息是html信息,则返回html源码"""
        if self.get_type() == 'MessageText':
            return self.RawMessage['text']['body']
        if self.get_type() == 'MessageEventFriendRequest':
            return self.bot.config['auto_accept']
        if self.get_type() == 'MessageNotice':
            return self.RawMessage['notice']['body']
        if self.get_type() == 'MessageWeb':
            if self.RawMessage['web']['title'] == 'GIF':
                image_url = (f'{server}/'
                             + self.RawMessage['web']['code'].split('<img src=\"')[1].split('\"')[0])
                return image_url
            return self.RawMessage['web']['code']
        if self.get_type() == 'MessageDocument':
            file_url = (f"{server}/index.php?action=http.file.downloadFile&fileId="
                        + self.RawMessage['document']['url']
                        + "&returnBase64=0&isGroupMessage=0&messageId="
                        + self.RawMessage['msgId']
                        + "&lang=1")
            return file_url
        if self.get_type() == 'MessageImage':
            image_url = (f"{server}/index.php?action=http.file.downloadFile&fileId="
                         + self.RawMessage['image']['url']
                         + "&returnBase64=0&lang=1")
            return image_url
        if self.get_type() == 'MessageRecall':
            result = {'msgId': self.RawMessage['recall']['msgId']}
            if self.get_room_type() == 'Group':
                result['Group'] = self.get_from_group()
            else:
                result['Friend'] = self.get_from_user()
            return result

    def is_command(self):
        """判断消息是不是命令的方法"""
        return self.get_type() == 'MessageText' and self.get_data().startswith('/')
