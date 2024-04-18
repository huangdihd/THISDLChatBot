from .Friend import Friend


class Group:
    def __init__(self, profile: dict) -> None:
        self.profile = profile
        pass

    def __str__(self):
        return str(self.profile)

    def get_description(self) -> dict:
        return self.profile['description']

    def can_add_friend(self) -> bool:
        return self.profile['canAddFriend']

    def get_permission_join(self) -> str:
        return self.profile['permissionJoin']

    def get_create_time(self) -> int:
        return self.profile['timeCreate']

    def get_owner(self) -> Friend:
        return Friend(self.profile['owner'])

    def get_group_id(self) -> str:
        return self.profile['id']

    def get_name(self) -> str:
        return self.profile['name']

    def get_avatar_url(self) -> str:
        return f'http://chat.thisit.cc/index.php?action=http.file.downloadFile&fileId={self.profile["avatar"]}\
        &returnBase64=0&lang=1'
