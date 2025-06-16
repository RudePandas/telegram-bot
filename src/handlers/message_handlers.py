from typing import Optional, Callable
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from .base import BaseMessageHandler
from ..models.enums import MessageType, HandlerPriority


class CommandMessageHandler(BaseMessageHandler):
    """命令消息处理器"""
    
    def __init__(self, 
                 command: str,
                 callback: Callable,
                 description: str = "",
                 priority: int = HandlerPriority.HIGH.value):
        super().__init__(
            name=f"Command_{command}",
            description=description or f"处理 /{command} 命令",
            priority=priority,
            filters=[Command(command)]
        )
        self.command = command
        self.callback = callback
    
    async def can_handle(self, message: Message, state: FSMContext) -> bool:
        if not await super().can_handle(message, state):
            return False
        return message.text and message.text.startswith(f"/{self.command}")
    
    async def handle(self, message: Message, bot: 'TelegramBotService', state: FSMContext) -> Any:
        try:
            if asyncio.iscoroutinefunction(self.callback):
                return await self.callback(message, bot, state)
            else:
                return self.callback(message, bot, state)
        except Exception as e:
            await bot.handle_error(e, message)


class TextMessageHandler(BaseMessageHandler):
    """文本消息处理器"""
    
    def __init__(self, 
                 callback: Callable,
                 contains: Optional[str] = None,
                 startswith: Optional[str] = None,
                 endswith: Optional[str] = None,
                 case_sensitive: bool = False,
                 priority: int = HandlerPriority.NORMAL.value):
        super().__init__(
            name=f"Text_{contains or startswith or endswith or 'Any'}",
            priority=priority
        )
        self.callback = callback
        self.contains = contains
        self.startswith = startswith
        self.endswith = endswith
        self.case_sensitive = case_sensitive
    
    async def can_handle(self, message: Message, state: FSMContext) -> bool:
        if not await super().can_handle(message, state):
            return False
        
        if not message.text:
            return False
        
        text = message.text if self.case_sensitive else message.text.lower()
        
        if self.contains:
            check_text = self.contains if self.case_sensitive else self.contains.lower()
            return check_text in text
        
        if self.startswith:
            check_text = self.startswith if self.case_sensitive else self.startswith.lower()
            return text.startswith(check_text)
        
        if self.endswith:
            check_text = self.endswith if self.case_sensitive else self.endswith.lower()
            return text.endswith(check_text)
        
        return True
    
    async def handle(self, message: Message, bot: 'TelegramBotService', state: FSMContext) -> Any:
        if self.callback:
            try:
                if asyncio.iscoroutinefunction(self.callback):
                    return await self.callback(message, bot, state)
                else:
                    return self.callback(message, bot, state)
            except Exception as e:
                await bot.handle_error(e, message)


class MediaMessageHandler(BaseMessageHandler):
    """媒体消息处理器"""
    
    def __init__(self, 
                 media_type: MessageType,
                 callback: Callable,
                 priority: int = HandlerPriority.NORMAL.value):
        super().__init__(
            name=f"Media_{media_type.value}",
            description=f"处理 {media_type.value} 类型消息",
            priority=priority
        )
        self.media_type = media_type
        self.callback = callback
    
    async def can_handle(self, message: Message, state: FSMContext) -> bool:
        if not await super().can_handle(message, state):
            return False
        
        type_map = {
            MessageType.PHOTO: message.photo,
            MessageType.DOCUMENT: message.document,
            MessageType.VOICE: message.voice,
            MessageType.VIDEO: message.video,
            MessageType.STICKER: message.sticker,
            MessageType.LOCATION: message.location,
            MessageType.CONTACT: message.contact,
            MessageType.ANIMATION: message.animation,
            MessageType.AUDIO: message.audio,
        }
        
        return type_map.get(self.media_type) is not None
    
    async def handle(self, message: Message, bot: 'TelegramBotService', state: FSMContext) -> Any:
        try:
            if asyncio.iscoroutinefunction(self.callback):
                return await self.callback(message, bot, state)
            else:
                return self.callback(message, bot, state)
        except Exception as e:
            await bot.handle_error(e, message) 