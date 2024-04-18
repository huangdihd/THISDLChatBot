class Message:
    def __init__(self, raw_message: dict, bot) -> None:
        self.RawMessage = raw_message
        self.bot = bot

    def __str__(self) -> str:
        return str(self.RawMessage)

    def get_message_id(self):
        return self.RawMessage.get('msgId')

    def get_type(self):
        return self.RawMessage['type']

    def get_room_type(self):
        if self.RawMessage['msgId'].startswith('G'):
            return 'Group'
        return 'Private'

    async def get_from_user(self):
        return await self.bot.get_friend_profile(self.RawMessage.get('fromUserId'))

    async def get_from_group(self):
        return await self.bot.get_group_profile(self.RawMessage.get('toGroupId'))

    def get_pointer(self) -> str:
        return self.RawMessage['pointer']

    def get_data(self):
        if self.get_type() == 'MessageText':
            return self.RawMessage['text']['body']
        if self.get_type() == 'MessageEventFriendRequest':
            return self.bot.config['auto_accept']
        if self.get_type() == 'MessageNotice':
            return self.RawMessage['notice']['body']
        if self.get_type() == 'MessageWeb':
            if self.RawMessage['web']['title'] == 'GIF':
                image_url = ('http://chat.thisit.cc/'
                             + self.RawMessage['web']['code'].split('<img src=\"')[1].split('\"')[0])
                return image_url
            return self.RawMessage['web']['code']
        if self.get_type() == 'MessageDocument':
            file_url = (f"http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId="
                        + self.RawMessage['document']['url']
                        + "&returnBase64=0&isGroupMessage=0&messageId="
                        + self.RawMessage['msgId']
                        + "&lang=1")
            return file_url
        if self.get_type() == 'MessageImage':
            image_url = ("http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId="
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
        return self.get_type() == 'MessageText' and self.get_data().startswith('/')
