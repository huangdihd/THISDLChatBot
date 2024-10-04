from .Friend import Friend
from .Constants import *


class Group:
    """群类"""
    def __init__(self, profile: dict) -> None:
        """创建群对象的方法"""
        self.profile = profile
        pass

    def __str__(self):
        """将群信息转成字符串的类"""
        return str(self.profile)

    def get_description(self) -> dict:
        """获取群description的方法"""
        return self.profile['description']

    def can_add_friend(self) -> bool:
        """获取群can_add_friend的方法"""
        return self.profile['canAddFriend']

    def get_permission_join(self) -> str:
        """获取群permission_join的方法"""
        return self.profile['permissionJoin']

    def get_create_time(self) -> int:
        """获取群time_create的方法"""
        return self.profile['timeCreate']

    def get_owner(self) -> Friend:
        """获取群owner的方法"""
        return Friend(self.profile['owner'])

    def get_group_id(self) -> str:
        """获取群group_id的方法"""
        return self.profile['id']

    def get_name(self) -> str:
        """获取群name的方法"""
        return self.profile['name']

    def get_avatar_url(self) -> str:
        """获取群头像url的方法"""
        return f'{server}/index.php?action=http.file.downloadFile&fileId={self.profile["avatar"]}\
        &returnBase64=0&lang=1'
