from dataclasses import dataclass
from typing import Optional, List
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage


@dataclass
class BotConfiguration:
    """机器人配置类"""
    token: str
    parse_mode: str = "HTML"
    disable_web_page_preview: bool = False
    drop_pending_updates: bool = True
    allowed_updates: Optional[List[str]] = None
    storage: Optional[BaseStorage] = None
    
    def __post_init__(self):
        if self.storage is None:
            self.storage = MemoryStorage() 