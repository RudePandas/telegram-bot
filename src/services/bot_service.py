import logging
from typing import Any, Union, Optional
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from ..models.config import BotConfiguration
from ..models.enums import BotState
from .handler_registry import HandlerRegistry
from .event_manager import EventManager, DefaultEventListener
from .message_service import MessageService


class TelegramBotService:
    """Telegram机器人服务主类"""
    
    def __init__(self, config: BotConfiguration):
        self.config = config
        self.bot = Bot(token=config.token)
        self.dp = Dispatcher(storage=config.storage)
        self.handler_registry = HandlerRegistry()
        self.event_manager = EventManager()
        self.message_service = MessageService(self.bot, self.event_manager)
        
        # 状态管理
        self.state = BotState.IDLE
        self.bot_info: Optional[types.User] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 添加默认事件监听器
        self.event_manager.add_listener(DefaultEventListener(self.logger))
        
        # 注册内部处理器
        self._register_internal_handlers()
    
    def _register_internal_handlers(self) -> None:
        """注册内部处理器"""
        # 注册消息处理器
        @self.dp.message()
        async def handle_message(message: types.Message, state: FSMContext):
            await self.event_manager.emit_message_received(message, self)
            await self._process_message(message, state)
        
        # 注册回调查询处理器
        @self.dp.callback_query()
        async def handle_callback_query(callback: types.CallbackQuery, state: FSMContext):
            await self._process_callback_query(callback, state)
        
        # 注册启动和关闭事件
        @self.dp.startup()
        async def on_startup():
            await self._on_startup()
        
        @self.dp.shutdown()
        async def on_shutdown():
            await self._on_shutdown()
    
    async def _process_message(self, message: types.Message, state: FSMContext) -> None:
        """处理消息"""
        handlers = self.handler_registry.get_message_handlers()
        
        for handler in handlers:
            try:
                if await handler.can_handle(message, state):
                    await handler.handle(message, self, state)
                    break  # 只处理第一个匹配的处理器
            except Exception as e:
                await self.handle_error(e, message)
    
    async def _process_callback_query(self, callback: types.CallbackQuery, state: FSMContext) -> None:
        """处理回调查询"""
        handlers = self.handler_registry.get_callback_handlers()
        
        for handler in handlers:
            try:
                if await handler.can_handle(callback, state):
                    await handler.handle(callback, self, state)
                    break
            except Exception as e:
                await self.handle_error(e, callback)
    
    async def _on_startup(self) -> None:
        """启动事件处理"""
        self.state = BotState.STARTING
        try:
            self.bot_info = await self.bot.get_me()
            self.state = BotState.RUNNING
            await self.event_manager.emit_startup(self)
        except Exception as e:
            self.state = BotState.ERROR
            await self.handle_error(e)
    
    async def _on_shutdown(self) -> None:
        """关闭事件处理"""
        self.state = BotState.STOPPING
        try:
            await self.event_manager.emit_shutdown(self)
            self.state = BotState.STOPPED
        except Exception as e:
            await self.handle_error(e)
    
    async def handle_error(self, error: Exception, context: Any = None) -> None:
        """处理错误"""
        self.logger.error(f"处理错误: {error}", exc_info=True)
        await self.event_manager.emit_error(error, self)
    
    # 流畅的API方法
    def add_command_handler(self, 
                           command: str, 
                           callback: Callable,
                           description: str = "",
                           priority: int = HandlerPriority.HIGH.value) -> 'TelegramBotService':
        """添加命令处理器"""
        handler = CommandMessageHandler(command, callback, description, priority)
        self.handler_registry.register_message_handler(handler)
        return self
    
    def add_text_handler(self, 
                        callback: Callable,
                        contains: Optional[str] = None,
                        startswith: Optional[str] = None,
                        endswith: Optional[str] = None,
                        priority: int = HandlerPriority.NORMAL.value) -> 'TelegramBotService':
        """添加文本处理器"""
        handler = TextMessageHandler(
            callback=callback,
            contains=contains,
            startswith=startswith,
            endswith=endswith,
            priority=priority
        )
        self.handler_registry.register_message_handler(handler)
        return self
    
    def add_media_handler(self, 
                         media_type: MessageType,
                         callback: Callable,
                         priority: int = HandlerPriority.NORMAL.value) -> 'TelegramBotService':
        """添加媒体处理器"""
        handler = MediaMessageHandler(media_type, callback, priority)
        self.handler_registry.register_message_handler(handler)
        return self
    
    def add_callback_handler(self, 
                            callback: Callable,
                            data_pattern: Optional[str] = None,
                            startswith: Optional[str] = None) -> 'TelegramBotService':
        """添加回调处理器"""
        handler = CallbackQueryHandler(data_pattern, callback, startswith)
        self.handler_registry.register_callback_handler(handler)
        return self
    
    def add_handler(self, handler: Union[IMessageHandler, ICallbackHandler]) -> 'TelegramBotService':
        """添加处理器"""
        if isinstance(handler, IMessageHandler):
            self.handler_registry.register_message_handler(handler)
        elif isinstance(handler, ICallbackHandler):
            self.handler_registry.register_callback_handler(handler)
        return self
    
    def add_event_listener(self, listener: IEventListener) -> 'TelegramBotService':
        """添加事件监听器"""
        self.event_manager.add_listener(listener)
        return self
    
    # 消息发送方法
    async def send_message(self, chat_id: Union[int, str], text: str, **kwargs) -> types.Message:
        """发送消息"""
        return await self.message_service.send_text(chat_id, text, **kwargs)
    
    async def send_photo(self, chat_id: Union[int, str], photo: Union[str, types.InputFile], **kwargs) -> types.Message:
        """发送图片"""
        return await self.message_service.send_photo(chat_id, photo, **kwargs)
    
    async def send_document(self, chat_id: Union[int, str], document: Union[str, types.InputFile], **kwargs) -> types.Message:
        """发送文档"""
        return await self.message_service.send_document(chat_id, document, **kwargs)
    
    # 生命周期管理
    async def start_polling(self, **kwargs) -> None:
        """开始轮询"""
        try:
            await self.dp.start_polling(
                self.bot, 
                drop_pending_updates=self.config.drop_pending_updates,
                allowed_updates=self.config.allowed_updates,
                **kwargs
            )
        except Exception as e:
            await self.handle_error(e)
            raise
    
    async def start_webhook(self, webhook_url: str, **kwargs) -> None:
        """开始webhook"""
        try:
            await self.bot.set_webhook(webhook_url, **kwargs)
        except Exception as e:
            await self.handle_error(e)
            raise
    
    async def stop(self) -> None:
        """停止机器人"""
        try:
            await self.bot.session.close()
        except Exception as e:
            await self.handle_error(e)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop() 