class Friend:
    def __init__(self, profile: dict) -> None:
        self.profile = profile
        pass

    def __str__(self):
        return str(self.profile)

    def GetUserId(self) -> str:
        return self.profile['userId']

    def GetLoginName(self) -> str:
        return self.profile['loginName']

    def GetNickName(self) -> str:
        return self.profile['nickName']

    def GetAvatarUrl(self) -> str:
        return ('http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId='
                + self.profile["avatar"]
                + '&returnBase64=0&lang=1')
