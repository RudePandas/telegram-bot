import logging
import asyncio
from typing import Dict, Optional, List, Set
from collections import defaultdict
import aiojobs

from ..models.config import BotConfiguration
from ..models.database import DatabaseConnection, BotRecord, ChatRecord
from .bot_service import TelegramBotService
from .kafka_consumer import KafkaConsumerService


class BotManager:
    """机器人管理器，用于管理大规模机器人实例"""
    
    _instance = None
    _lock = asyncio.Lock()
    _initialized = False
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(BotManager, cls).__new__(cls)
        return cls._instance
    
    async def __init__(self):
        """异步初始化方法"""
        # 使用锁确保线程安全
        async with self._lock:
            if self._initialized:
                return
                
            self._bots: Dict[int, TelegramBotService] = {}
            self._scheduler = None
            self._chat_bot_mapping: Dict[int, Set[int]] = defaultdict(set)  # chat_id -> bot_ids
            self.logger = logging.getLogger(self.__class__.__name__)
            self._kafka_consumer: Optional[KafkaConsumerService] = None
            self._initialized = True
    
    @classmethod
    async def get_instance(cls) -> 'BotManager':
        """获取单例实例的线程安全方法"""
        if not cls._instance:
            async with cls._lock:
                if not cls._instance:
                    instance = cls()
                    await instance.__init__()
                    cls._instance = instance
        return cls._instance
    
    async def initialize(self, 
                        db_url: str,
                        kafka_config: Optional[Dict[str, str]] = None) -> None:
        """初始化管理器
        
        Args:
            db_url: 数据库URL
            kafka_config: Kafka配置，包含：
                - bootstrap_servers: Kafka服务器地址
                - topic: 主题名称
                - group_id: 消费者组ID
        """
        async with self._lock:
            # 初始化数据库连接
            await DatabaseConnection.initialize(db_url)
            
            # 创建必要的数据库表
            await BotRecord.create_table()
            await ChatRecord.create_table()
            
            # 初始化任务调度器，用于消息广播等并发任务
            self._scheduler = await aiojobs.create_scheduler(
                close_timeout=10.0,
                limit=1000,  # 降低最大并发任务数，避免资源耗尽
                pending_limit=2000  # 等待任务队列上限
            )
            
            # 如果提供了Kafka配置，初始化Kafka消费者
            if kafka_config:
                self._kafka_consumer = KafkaConsumerService(
                    bootstrap_servers=kafka_config['bootstrap_servers'],
                    topic=kafka_config['topic'],
                    group_id=kafka_config['group_id'],
                    bot_manager=self
                )
                await self._kafka_consumer.start()
    
    @property
    def active_bots(self) -> Dict[int, TelegramBotService]:
        """获取所有活跃的机器人实例"""
        return self._bots
    
    async def load_bots(self) -> None:
        """从数据库加载所有活跃的机器人"""
        bot_records = await BotRecord.get_active_bots()
        
        for record in bot_records:
            try:
                config = BotConfiguration(
                    token=record.token,
                    name=record.name,
                    **record.config
                )
                await self.register_bot(record.id, config)
            except Exception as e:
                self.logger.error(f"Failed to load bot {record.id}: {e}")
    
    async def register_bot(self, bot_id: int, config: BotConfiguration) -> TelegramBotService:
        """注册新的机器人实例"""
        async with self._lock:
            if bot_id in self._bots:
                raise ValueError(f"Bot with ID {bot_id} already exists")
            
            bot = TelegramBotService(config)
            self._bots[bot_id] = bot
            
            # 加载机器人的活跃聊天
            chats = await ChatRecord.get_active_chats(bot_id)
            for chat in chats:
                self._chat_bot_mapping[chat.chat_id].add(bot_id)
            
            self.logger.info(f"Registered bot {bot_id}")
            return bot
    
    async def unregister_bot(self, bot_id: int) -> None:
        """注销机器人实例"""
        async with self._lock:
            if bot_id in self._bots:
                bot = self._bots.pop(bot_id)
                await bot.stop()
                
                # 清理聊天映射
                for chat_id in list(self._chat_bot_mapping.keys()):
                    self._chat_bot_mapping[chat_id].discard(bot_id)
                    if not self._chat_bot_mapping[chat_id]:
                        del self._chat_bot_mapping[chat_id]
                
                self.logger.info(f"Unregistered bot {bot_id}")
    
    async def start_bot(self, bot_id: int, webhook_url: Optional[str] = None) -> None:
        """启动单个机器人
        
        Args:
            bot_id: 机器人ID
            webhook_url: webhook URL，如果提供则使用webhook模式，否则使用轮询模式
        """
        if bot_id not in self._bots:
            raise ValueError(f"Bot {bot_id} not found")
        
        bot = self._bots[bot_id]
        try:
            if webhook_url:
                # Webhook模式
                await bot.start_webhook(webhook_url)
                self.logger.info(f"Started bot {bot_id} in webhook mode")
            else:
                # 轮询模式
                await bot.start_polling()
                self.logger.info(f"Started bot {bot_id} in polling mode")
        except Exception as e:
            self.logger.error(f"Failed to start bot {bot_id}: {e}")
            raise
    
    async def stop_bot(self, bot_id: int) -> None:
        """停止单个机器人"""
        if bot_id not in self._bots:
            raise ValueError(f"Bot {bot_id} not found")
        
        bot = self._bots[bot_id]
        try:
            await bot.stop()
            self.logger.info(f"Stopped bot {bot_id}")
        except Exception as e:
            self.logger.error(f"Failed to stop bot {bot_id}: {e}")
            raise
    
    async def start_all(self, webhook_base_url: Optional[str] = None) -> None:
        """启动所有机器人
        
        Args:
            webhook_base_url: webhook基础URL，如果提供则使用webhook模式，否则使用轮询模式
                格式：https://example.com/webhook/
                最终的webhook URL将为：{webhook_base_url}{bot_id}
        """
        if not self._bots:
            self.logger.warning("No bots to start")
            return
            
        self.logger.info(f"Starting {len(self._bots)} bots...")
        start_tasks = []
        
        for bot_id in self._bots:
            webhook_url = f"{webhook_base_url}{bot_id}" if webhook_base_url else None
            start_tasks.append(self.start_bot(bot_id, webhook_url))
        
        results = await asyncio.gather(*start_tasks, return_exceptions=True)
        
        # 检查启动结果
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed:
            self.logger.error(f"{failed} bot(s) failed to start")
        else:
            self.logger.info("All bots started successfully")
    
    async def stop_all(self) -> None:
        """停止所有机器人"""
        if not self._bots:
            return
            
        self.logger.info(f"Stopping {len(self._bots)} bots...")
        stop_tasks = [self.stop_bot(bot_id) for bot_id in self._bots]
        results = await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        # 检查停止结果
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed:
            self.logger.error(f"{failed} bot(s) failed to stop")
        
        # 停止Kafka消费者
        if self._kafka_consumer:
            await self._kafka_consumer.stop()
            self.logger.info("Kafka consumer stopped")
        
        # 关闭调度器
        if self._scheduler:
            try:
                await self._scheduler.close()
                self.logger.info("Task scheduler closed")
            except Exception as e:
                self.logger.error(f"Failed to close task scheduler: {e}")
    
    async def broadcast_message(self, 
                              message: str, 
                              bot_ids: Optional[List[int]] = None, 
                              batch_size: int = 50,
                              retry_count: int = 3,
                              retry_delay: float = 1.0,
                              **kwargs) -> None:
        """向指定机器人的所有聊天发送广播消息
        
        Args:
            message: 要发送的消息
            bot_ids: 指定的机器人ID列表，为None时发送给所有机器人
            batch_size: 每批处理的聊天数量
            retry_count: 发送失败时的重试次数
            retry_delay: 重试之间的延迟（秒）
            **kwargs: 传递给send_message的额外参数
        """
        if bot_ids is None:
            bot_ids = list(self._bots.keys())
        
        total_success = 0
        total_failed = 0
        
        for bot_id in bot_ids:
            if bot_id not in self._bots:
                self.logger.warning(f"Bot {bot_id} not found, skipping")
                continue
            
            bot = self._bots[bot_id]
            try:
                # 获取活跃聊天
                chats = await ChatRecord.get_active_chats(bot_id)
                if not chats:
                    self.logger.info(f"No active chats for bot {bot_id}")
                    continue
                
                self.logger.info(f"Broadcasting to {len(chats)} chats for bot {bot_id}")
                
                # 分批处理聊天
                for i in range(0, len(chats), batch_size):
                    batch = chats[i:i + batch_size]
                    batch_tasks = []
                    
                    for chat in batch:
                        # 创建发送任务，包含重试逻辑
                        async def send_with_retry(chat_id: int) -> bool:
                            for attempt in range(retry_count):
                                try:
                                    await bot.send_message(chat_id, message, **kwargs)
                                    return True
                                except Exception as e:
                                    if attempt == retry_count - 1:
                                        self.logger.error(f"Failed to send message to chat {chat_id} after {retry_count} attempts: {e}")
                                        return False
                                    await asyncio.sleep(retry_delay)
                            return False
                        
                        task = self._scheduler.spawn(send_with_retry(chat.chat_id))
                        batch_tasks.append(task)
                    
                    # 等待当前批次完成
                    results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    
                    # 统计结果
                    batch_success = sum(1 for r in results if r is True)
                    batch_failed = sum(1 for r in results if r is False or isinstance(r, Exception))
                    
                    total_success += batch_success
                    total_failed += batch_failed
                    
                    self.logger.info(f"Batch complete: {batch_success} succeeded, {batch_failed} failed")
                    
                    # 添加小延迟，避免触发速率限制
                    await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Failed to process broadcast for bot {bot_id}: {e}")
                continue
        
        self.logger.info(f"Broadcast complete: {total_success} succeeded, {total_failed} failed")
    
    async def get_bot_chats(self, bot_id: int) -> List[ChatRecord]:
        """获取机器人的所有活跃聊天"""
        return await ChatRecord.get_active_chats(bot_id)
    
    async def update_chat_activity(self, bot_id: int, chat_id: int, 
                                 chat_type: str, is_active: bool = True) -> None:
        """更新聊天活动状态"""
        chat = ChatRecord(
            id=0,  # 新记录
            bot_id=bot_id,
            chat_id=chat_id,
            chat_type=chat_type,
            is_active=is_active,
            last_interaction=None  # 将由数据库设置
        )
        await chat.save()
        
        if is_active:
            self._chat_bot_mapping[chat_id].add(bot_id)
        else:
            self._chat_bot_mapping[chat_id].discard(bot_id)
            if not self._chat_bot_mapping[chat_id]:
                del self._chat_bot_mapping[chat_id]
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop_all()
        await DatabaseConnection.close() 