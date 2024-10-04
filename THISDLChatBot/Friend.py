from .Constants import *


class Friend:
    """好友类"""
    def __init__(self, profile: dict) -> None:
        """创建好友对象的方法"""
        self.profile = profile
        pass

    def __str__(self):
        """将好友信息转成字符串的类"""
        return str(self.profile)

    def get_user_id(self) -> str:
        """获取好友user_id的方法"""
        return self.profile['userId']

    def get_login_name(self) -> str:
        """获取好友login_name的方法"""
        return self.profile['loginName']

    def get_nick_name(self) -> str:
        """获取好友nick_name的方法"""
        return self.profile['nickname']

    def get_avatar_url(self) -> str:
        """获取好友头像url的方法"""
        return (f'{server}/index.php?action=http.file.downloadFile&fileId='
                + self.profile["avatar"]
                + '&returnBase64=0&lang=1')
