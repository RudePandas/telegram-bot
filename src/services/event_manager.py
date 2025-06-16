import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from aiogram.types import Message


class IEventListener(ABC):
    """事件监听器接口"""
    
    @abstractmethod
    async def on_startup(self, bot: 'TelegramBotService') -> None:
        """启动事件"""
        pass
    
    @abstractmethod
    async def on_shutdown(self, bot: 'TelegramBotService') -> None:
        """关闭事件"""
        pass
    
    @abstractmethod
    async def on_message_received(self, message: Message, bot: 'TelegramBotService') -> None:
        """消息接收事件"""
        pass
    
    @abstractmethod
    async def on_message_sent(self, message: Message, bot: 'TelegramBotService') -> None:
        """消息发送事件"""
        pass
    
    @abstractmethod
    async def on_error(self, error: Exception, bot: 'TelegramBotService') -> None:
        """错误事件"""
        pass


class DefaultEventListener(IEventListener):
    """默认事件监听器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    async def on_startup(self, bot: 'TelegramBotService') -> None:
        self.logger.info(f"机器人 {bot.bot_info.username if bot.bot_info else 'Unknown'} 启动成功")
    
    async def on_shutdown(self, bot: 'TelegramBotService') -> None:
        self.logger.info("机器人已关闭")
    
    async def on_message_received(self, message: Message, bot: 'TelegramBotService') -> None:
        user_name = message.from_user.full_name if message.from_user else "Unknown"
        self.logger.info(f"收到消息: {message.text or '[非文本消息]'} 来自: {user_name}")
    
    async def on_message_sent(self, message: Message, bot: 'TelegramBotService') -> None:
        self.logger.info(f"发送消息: {message.text or '[非文本消息]'} 到: {message.chat.id}")
    
    async def on_error(self, error: Exception, bot: 'TelegramBotService') -> None:
        self.logger.error(f"发生错误: {error}", exc_info=True)


class EventManager:
    """事件管理器"""
    
    def __init__(self):
        self._listeners: List[IEventListener] = []
    
    def add_listener(self, listener: IEventListener) -> None:
        """添加事件监听器"""
        self._listeners.append(listener)
    
    def remove_listener(self, listener: IEventListener) -> None:
        """移除事件监听器"""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    async def emit_startup(self, bot: 'TelegramBotService') -> None:
        """触发启动事件"""
        for listener in self._listeners:
            try:
                await listener.on_startup(bot)
            except Exception as e:
                await self._handle_listener_error(e, listener, "startup")
    
    async def emit_shutdown(self, bot: 'TelegramBotService') -> None:
        """触发关闭事件"""
        for listener in self._listeners:
            try:
                await listener.on_shutdown(bot)
            except Exception as e:
                await self._handle_listener_error(e, listener, "shutdown")
    
    async def emit_message_received(self, message: Message, bot: 'TelegramBotService') -> None:
        """触发消息接收事件"""
        for listener in self._listeners:
            try:
                await listener.on_message_received(message, bot)
            except Exception as e:
                await self._handle_listener_error(e, listener, "message_received")
    
    async def emit_message_sent(self, message: Message, bot: 'TelegramBotService') -> None:
        """触发消息发送事件"""
        for listener in self._listeners:
            try:
                await listener.on_message_sent(message, bot)
            except Exception as e:
                await self._handle_listener_error(e, listener, "message_sent")
    
    async def emit_error(self, error: Exception, bot: 'TelegramBotService') -> None:
        """触发错误事件"""
        for listener in self._listeners:
            try:
                await listener.on_error(error, bot)
            except Exception as e:
                await self._handle_listener_error(e, listener, "error")
    
    async def _handle_listener_error(self, error: Exception, listener: IEventListener, event: str) -> None:
        """处理监听器错误"""
        logging.error(f"事件监听器 {listener.__class__.__name__} 在处理 {event} 事件时出错: {error}") 