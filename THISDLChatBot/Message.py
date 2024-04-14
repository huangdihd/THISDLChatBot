class Message:
    def __init__(self, RawMessage: dict, bot) -> None:
        self.RawMessage = RawMessage
        self.bot = bot

    def __str__(self) -> str:
        return str(self.RawMessage)

    def GetMessageId(self):
        return self.RawMessage.get('msgId')

    def GetType(self):
        return self.RawMessage['type']

    def GetRoomType(self):
        if self.RawMessage['msgId'].startswith('G'):
            return 'Group'
        return 'Private'

    def GetFromUser(self):
        return self.bot.loop.run_until_complete(self.bot.GetFriendProfile(self.RawMessage.get('fromUserId')))

    def GetPointer(self) -> str:
        return self.RawMessage['pointer']

    def GetFromGroup(self):
        return self.bot.loop.run_until_complete(self.bot.GetGroupProfile(self.RawMessage.get('toGroupId')))

    def GetData(self):
        if self.GetType() == 'MessageText':
            return self.RawMessage['text']['body']
        if self.GetType() == 'MessageEventFriendRequest':
            return self.bot.config['auto_accept']
        if self.GetType() == 'MessageNotice':
            return self.RawMessage['notice']['body']
        if self.GetType() == 'MessageWeb':
            if self.RawMessage['web']['title'] == 'GIF':
                ImageUrl = ('http://chat.thisit.cc/'
                            + self.RawMessage['web']['code'].split('<img src=\"')[1].split('\"')[0])
                return self.bot.loop.run_until_complete(self.bot.DownLoadFile(ImageUrl))
            return self.RawMessage['web']['code']
        if self.GetType() == 'MessageDocument':
            FileUrl = (f"http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId="
                       + self.RawMessage['document']['url']
                       + "&returnBase64=0&isGroupMessage=0&messageId="
                       + self.RawMessage['msgId']
                       + "&lang=1")
            return self.bot.DownLoadFile(FileUrl)
        if self.GetType() == 'MessageImage':
            ImageUrl = ("http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId="
                        + self.RawMessage['image']['url']
                        + "&returnBase64=0&lang=1")
            return self.bot.loop.run_until_complete(self.bot.DownLoadFile(ImageUrl))
        if self.GetType() == 'MessageRecall':
            result = {'msgId': self.RawMessage['recall']['msgId']}
            if self.GetRoomType() == 'Group':
                result['Group'] = self.GetFromGroup()
            else:
                result['Friend'] = self.GetFromUser()
            return result

    def IsCommand(self):
        return self.GetType() == 'MessageText' and self.GetData().startswith('/')
