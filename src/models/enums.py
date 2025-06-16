from enum import Enum

class BotState(Enum):
    """机器人状态枚举"""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class MessageType(Enum):
    """消息类型枚举"""
    TEXT = "text"
    PHOTO = "photo"
    DOCUMENT = "document"
    VOICE = "voice"
    VIDEO = "video"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACT = "contact"
    ANIMATION = "animation"
    AUDIO = "audio"


class HandlerPriority(Enum):
    """处理器优先级枚举"""
    HIGHEST = 100
    HIGH = 80
    NORMAL = 50
    LOW = 20
    LOWEST = 10 