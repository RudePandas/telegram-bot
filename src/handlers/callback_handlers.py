from typing import Optional, Callable, Any
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import asyncio

from .base import ICallbackHandler


class CallbackQueryHandler(ICallbackHandler):
    """回调查询处理器"""
    
    def __init__(self, 
                 data_pattern: Optional[str] = None,
                 callback: Optional[Callable] = None,
                 startswith: Optional[str] = None):
        self.data_pattern = data_pattern
        self.callback = callback
        self.startswith = startswith
    
    async def can_handle(self, callback_query: CallbackQuery, state: FSMContext) -> bool:
        if not callback_query.data:
            return False
        
        if self.data_pattern:
            return callback_query.data == self.data_pattern
        
        if self.startswith:
            return callback_query.data.startswith(self.startswith)
        
        return True
    
    async def handle(self, callback_query: CallbackQuery, bot: 'TelegramBotService', state: FSMContext) -> Any:
        if self.callback:
            try:
                if asyncio.iscoroutinefunction(self.callback):
                    return await self.callback(callback_query, bot, state)
                else:
                    return self.callback(callback_query, bot, state)
            except Exception as e:
                await bot.handle_error(e, callback_query) 