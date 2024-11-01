from enum import Enum


class MessageType(Enum):
    MessageText = "MessageText"
    MessageEventFriendRequest = "MessageEventFriendRequest"
    MessageNotice = "MessageNotice"
    MessageWeb = "MessageWeb"
    MessageDocument = "MessageDocument"
    MessageImage = "MessageImage"
    MessageRecall = "MessageRecall"


class RoomType(Enum):
    Private = "Private"
    Group = "Group"
