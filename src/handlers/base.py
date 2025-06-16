from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Any, Callable
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import BaseFilter

from ..models.enums import HandlerPriority


@dataclass
class HandlerMetadata:
    """处理器元数据"""
    name: str
    description: str
    priority: int
    enabled: bool = True
    filters: List[BaseFilter] = field(default_factory=list)
    middleware: List[Any] = field(default_factory=list)


class IMessageHandler(ABC):
    """消息处理器接口"""
    
    def __init__(self, metadata: Optional[HandlerMetadata] = None):
        self.metadata = metadata or HandlerMetadata(
            name=self.__class__.__name__,
            description="",
            priority=HandlerPriority.NORMAL.value
        )
    
    @abstractmethod
    async def can_handle(self, message: Message, state: FSMContext) -> bool:
        """判断是否能处理该消息"""
        pass
    
    @abstractmethod
    async def handle(self, message: Message, bot: 'TelegramBotService', state: FSMContext) -> Any:
        """处理消息"""
        pass
    
    def get_filters(self) -> List[BaseFilter]:
        """获取过滤器"""
        return self.metadata.filters
    
    def add_filter(self, filter_obj: BaseFilter) -> 'IMessageHandler':
        """添加过滤器"""
        self.metadata.filters.append(filter_obj)
        return self


class ICallbackHandler(ABC):
    """回调处理器接口"""
    
    @abstractmethod
    async def can_handle(self, callback: CallbackQuery, state: FSMContext) -> bool:
        """判断是否能处理该回调"""
        pass
    
    @abstractmethod
    async def handle(self, callback: CallbackQuery, bot: 'TelegramBotService', state: FSMContext) -> Any:
        """处理回调"""
        pass


class BaseMessageHandler(IMessageHandler):
    """基础消息处理器"""
    
    def __init__(self, 
                 name: str = "",
                 description: str = "",
                 priority: int = HandlerPriority.NORMAL.value,
                 filters: Optional[List[BaseFilter]] = None):
        metadata = HandlerMetadata(
            name=name or self.__class__.__name__,
            description=description,
            priority=priority,
            filters=filters or []
        )
        super().__init__(metadata)
    
    async def can_handle(self, message: Message, state: FSMContext) -> bool:
        """默认实现：检查是否启用"""
        return self.metadata.enabled
    
    async def handle(self, message: Message, bot: 'TelegramBotService', state: FSMContext) -> Any:
        """默认实现：空处理"""
        pass 