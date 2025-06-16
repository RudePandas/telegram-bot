from aiogram.fsm.storage.base import BaseStorage
from ..models.config import BotConfiguration
from ..services.bot_service import TelegramBotService
from ..handlers.base import IMessageHandler, ICallbackHandler
from ..services.event_manager import IEventListener


class BotBuilder:
    """机器人构建器"""
    
    def __init__(self, token: str):
        self.config = BotConfiguration(token=token)
        self.handlers = []
        self.listeners = []
    
    def with_parse_mode(self, parse_mode: str) -> 'BotBuilder':
        """设置解析模式"""
        self.config.parse_mode = parse_mode
        return self
    
    def with_storage(self, storage: BaseStorage) -> 'BotBuilder':
        """设置存储"""
        self.config.storage = storage
        return self
    
    def with_drop_pending_updates(self, drop: bool = True) -> 'BotBuilder':
        """设置是否丢弃未处理的更新"""
        self.config.drop_pending_updates = drop
        return self
    
    def build(self) -> TelegramBotService:
        """构建机器人"""
        bot = TelegramBotService(self.config)
        
        # 添加处理器和监听器
        for handler in self.handlers:
            bot.add_handler(handler)
        
        for listener in self.listeners:
            bot.add_event_listener(listener)
        
        return bot 