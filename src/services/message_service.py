import logging
from typing import Union, Optional
from aiogram import Bot, types
from aiogram.exceptions import TelegramAPIError

from .event_manager import EventManager


class MessageService:
    """消息服务类"""
    
    def __init__(self, bot: Bot, event_manager: EventManager):
        self._bot = bot
        self._event_manager = event_manager
    
    async def send_text(self, 
                       chat_id: Union[int, str], 
                       text: str, 
                       **kwargs) -> types.Message:
        """发送文本消息"""
        try:
            message = await self._bot.send_message(chat_id, text, **kwargs)
            await self._event_manager.emit_message_sent(message, None)
            return message
        except TelegramAPIError as e:
            logging.error(f"发送文本消息失败: {e}")
            raise
    
    async def send_photo(self, 
                        chat_id: Union[int, str], 
                        photo: Union[str, types.InputFile], 
                        caption: Optional[str] = None,
                        **kwargs) -> types.Message:
        """发送图片消息"""
        try:
            message = await self._bot.send_photo(chat_id, photo, caption=caption, **kwargs)
            await self._event_manager.emit_message_sent(message, None)
            return message
        except TelegramAPIError as e:
            logging.error(f"发送图片消息失败: {e}")
            raise
    
    async def send_document(self, 
                           chat_id: Union[int, str], 
                           document: Union[str, types.InputFile],
                           caption: Optional[str] = None,
                           **kwargs) -> types.Message:
        """发送文档消息"""
        try:
            message = await self._bot.send_document(chat_id, document, caption=caption, **kwargs)
            await self._event_manager.emit_message_sent(message, None)
            return message
        except TelegramAPIError as e:
            logging.error(f"发送文档消息失败: {e}")
            raise
    
    async def edit_message_text(self, 
                               text: str,
                               chat_id: Optional[Union[int, str]] = None,
                               message_id: Optional[int] = None,
                               inline_message_id: Optional[str] = None,
                               **kwargs) -> Union[types.Message, bool]:
        """编辑消息文本"""
        try:
            return await self._bot.edit_message_text(
                text, 
                chat_id=chat_id, 
                message_id=message_id, 
                inline_message_id=inline_message_id,
                **kwargs
            )
        except TelegramAPIError as e:
            logging.error(f"编辑消息失败: {e}")
            raise
    
    async def delete_message(self, chat_id: Union[int, str], message_id: int) -> bool:
        """删除消息"""
        try:
            return await self._bot.delete_message(chat_id, message_id)
        except TelegramAPIError as e:
            logging.error(f"删除消息失败: {e}")
            raise 