from .Friend import Friend


class Group:
    def __init__(self, profile: dict) -> None:
        self.profile = profile
        pass

    def __str__(self):
        return str(self.profile)

    def GetDescription(self) -> dict:
        return self.profile['description']

    def CanAddFriend(self) -> bool:
        return self.profile['canAddFriend']

    def GetPermissionJoin(self) -> str:
        return self.profile['permissionJoin']

    def GetCreateTime(self) -> int:
        return self.profile['timeCreate']

    def GetOwner(self) -> Friend:
        return Friend(self.profile['owner'])

    def GetGroupId(self) -> str:
        return self.profile['id']

    def GetName(self) -> str:
        return self.profile['name']

    def GetAvatarUrl(self) -> str:
        return f'http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId={self.profile["avatar"]}\
        &returnBase64=0&lang=1'
