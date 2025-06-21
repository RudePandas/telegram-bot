from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage


@dataclass
class BotConfiguration:
    """机器人配置类"""
    token: str
    name: str
    parse_mode: str = "HTML"
    disable_web_page_preview: bool = False
    drop_pending_updates: bool = True
    allowed_updates: Optional[List[str]] = None
    storage: Optional[BaseStorage] = None
    
    # Webhook相关配置
    webhook_host: Optional[str] = None  # Webhook主机地址
    webhook_path: Optional[str] = None  # Webhook路径
    webhook_secret_token: Optional[str] = None  # Webhook密钥
    webhook_max_connections: int = 40  # 最大并发连接数
    webhook_ip_address: Optional[str] = None  # 服务器IP地址
    webhook_certificate_path: Optional[str] = None  # SSL证书路径
    webhook_certificate_key_path: Optional[str] = None  # SSL证书密钥路径
    
    def __post_init__(self):
        if self.storage is None:
            self.storage = MemoryStorage()
    
    def get_webhook_url(self) -> Optional[str]:
        """获取完整的webhook URL"""
        if not self.webhook_host or not self.webhook_path:
            return None
        return f"{self.webhook_host.rstrip('/')}/{self.webhook_path.lstrip('/')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于数据库存储"""
        return {
            "parse_mode": self.parse_mode,
            "disable_web_page_preview": self.disable_web_page_preview,
            "drop_pending_updates": self.drop_pending_updates,
            "allowed_updates": self.allowed_updates,
            "webhook_host": self.webhook_host,
            "webhook_path": self.webhook_path,
            "webhook_secret_token": self.webhook_secret_token,
            "webhook_max_connections": self.webhook_max_connections,
            "webhook_ip_address": self.webhook_ip_address,
            "webhook_certificate_path": self.webhook_certificate_path,
            "webhook_certificate_key_path": self.webhook_certificate_key_path
        }
    
    @classmethod
    def from_dict(cls, token: str, name: str, config: Dict[str, Any]) -> 'BotConfiguration':
        """从字典创建配置实例"""
        return cls(
            token=token,
            name=name,
            **config
        ) 