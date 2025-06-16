from typing import List
from ..handlers.base import IMessageHandler, ICallbackHandler


class HandlerRegistry:
    """处理器注册表"""
    
    def __init__(self):
        self._message_handlers: List[IMessageHandler] = []
        self._callback_handlers: List[ICallbackHandler] = []
        self._sorted = False
    
    def register_message_handler(self, handler: IMessageHandler) -> None:
        """注册消息处理器"""
        self._message_handlers.append(handler)
        self._sorted = False
    
    def register_callback_handler(self, handler: ICallbackHandler) -> None:
        """注册回调处理器"""
        self._callback_handlers.append(handler)
    
    def unregister_message_handler(self, handler: IMessageHandler) -> None:
        """注销消息处理器"""
        if handler in self._message_handlers:
            self._message_handlers.remove(handler)
    
    def unregister_callback_handler(self, handler: ICallbackHandler) -> None:
        """注销回调处理器"""
        if handler in self._callback_handlers:
            self._callback_handlers.remove(handler)
    
    def get_message_handlers(self) -> List[IMessageHandler]:
        """获取已排序的消息处理器"""
        if not self._sorted:
            self._message_handlers.sort(
                key=lambda h: h.metadata.priority if hasattr(h, 'metadata') else 50,
                reverse=True
            )
            self._sorted = True
        return self._message_handlers
    
    def get_callback_handlers(self) -> List[ICallbackHandler]:
        """获取回调处理器"""
        return self._callback_handlers
    
    def clear(self) -> None:
        """清空所有处理器"""
        self._message_handlers.clear()
        self._callback_handlers.clear() 