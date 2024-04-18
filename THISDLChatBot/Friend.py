class Friend:
    def __init__(self, profile: dict) -> None:
        self.profile = profile
        pass

    def __str__(self):
        return str(self.profile)

    def get_user_id(self) -> str:
        return self.profile['userId']

    def get_login_name(self) -> str:
        return self.profile['loginName']

    def get_nick_name(self) -> str:
        return self.profile['nickName']

    def get_avatar_url(self) -> str:
        return ('http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId='
                + self.profile["avatar"]
                + '&returnBase64=0&lang=1')
