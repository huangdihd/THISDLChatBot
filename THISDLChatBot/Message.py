class Message:
    def __init__(self, RawMessage: dict, bot) -> None:
        self._RawMessage = RawMessage
        self.bot = bot

    def __str__(self) -> str:
        return str(self._RawMessage)

    def GetMessageId(self):
        return self._RawMessage.get('msgId')

    def GetType(self):
        return self._RawMessage['type']

    def GetRoomType(self):
        if self._RawMessage['msgId'].startswith('G'):
            return 'Group'
        return 'Private'

    async def GetFromUser(self):
        return await self.bot.GetFriendProfile(self._RawMessage.get('fromUserId'))

    def GetPointer(self) -> str:
        return self._RawMessage['pointer']

    async def GetFromGroup(self):
        return await self.bot.GetGroupProfile(self._RawMessage.get('toGroupId'))

    def GetData(self):
        if self.GetType() == 'MessageText':
            return self._RawMessage['text']['body']
        if self.GetType() == 'MessageEventFriendRequest':
            return self.bot.config['auto_accept']
        if self.GetType() == 'MessageNotice':
            return self._RawMessage['notice']['body']
        if self.GetType() == 'MessageWeb':
            if self._RawMessage['web']['title'] == 'GIF':
                ImageUrl = ('http://chat.thisit.cc/'
                            + self._RawMessage['web']['code'].split('<img src=\"')[1].split('\"')[0])
                return self.bot.loop.run_until_complete(self.bot.DownLoadFile(ImageUrl))
            return self._RawMessage['web']['code']
        if self.GetType() == 'MessageDocument':
            FileUrl = (f"http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId="
                       + self._RawMessage['document']['url']
                       + "&returnBase64=0&isGroupMessage=0&messageId="
                       + self._RawMessage['msgId']
                       + "&lang=1")
            return self.bot.DownLoadFile(FileUrl)
        if self.GetType() == 'MessageImage':
            ImageUrl = ("http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId="
                        + self._RawMessage['image']['url']
                        + "&returnBase64=0&lang=1")
            return self.bot.loop.run_until_complete(self.bot.DownLoadFile(ImageUrl))
        if self.GetType() == 'MessageRecall':
            result = {'msgId': self._RawMessage['recall']['msgId']}
            if self.GetRoomType() == 'Group':
                result['Group'] = self.GetFromGroup()
            else:
                result['Friend'] = self.GetFromUser()
            return result

    def IsCommand(self):
        return self.GetType() == 'MessageText' and self.GetData().startswith('/')
