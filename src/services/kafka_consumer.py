import logging
import json
from typing import Optional, Dict, Any
from aiokafka import AIOKafkaConsumer
import asyncio
from aiogram import types

from .bot_manager import BotManager


class KafkaConsumerService:
    """Kafka消费者服务，用于处理来自Kafka的Telegram webhook消息"""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KafkaConsumerService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    async def __init__(self, 
                     bootstrap_servers: str,
                     topic: str,
                     group_id: str,
                     bot_manager: 'BotManager'):
        """异步初始化方法"""
        async with self._lock:
            if self._initialized:
                return
                
            self.bootstrap_servers = bootstrap_servers
            self.topic = topic
            self.group_id = group_id
            self.bot_manager = bot_manager
            self.consumer: Optional[AIOKafkaConsumer] = None
            self.logger = logging.getLogger(self.__class__.__name__)
            self._running = False
            self._consume_task: Optional[asyncio.Task] = None
            self._initialized = True
    
    @classmethod
    async def get_instance(cls, *args, **kwargs) -> 'KafkaConsumerService':
        """获取单例实例的线程安全方法"""
        if not cls._instance:
            async with cls._lock:
                if not cls._instance:
                    instance = cls(*args, **kwargs)
                    await instance.__init__(*args, **kwargs)
                    cls._instance = instance
        return cls._instance
    
    async def start(self) -> None:
        """启动Kafka消费者"""
        async with self._lock:
            if self._running:
                return
                
            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            await self.consumer.start()
            self._running = True
            self.logger.info(f"Kafka consumer started: topic={self.topic}")
            
            # 启动消费循环
            self._consume_task = asyncio.create_task(self._consume_loop())
    
    async def stop(self) -> None:
        """停止Kafka消费者"""
        async with self._lock:
            if not self._running:
                return
                
            self._running = False
            
            # 取消消费任务
            if self._consume_task:
                self._consume_task.cancel()
                try:
                    await self._consume_task
                except asyncio.CancelledError:
                    pass
                self._consume_task = None
            
            # 停止消费者
            if self.consumer:
                await self.consumer.stop()
                self.consumer = None
            
            self.logger.info("Kafka consumer stopped")
    
    async def _consume_loop(self) -> None:
        """消费循环"""
        try:
            async for message in self.consumer:
                if not self._running:
                    break
                    
                try:
                    await self._process_message(message.value)
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}", exc_info=True)
        except asyncio.CancelledError:
            self.logger.info("Consume loop cancelled")
        except Exception as e:
            self.logger.error(f"Consume loop error: {e}", exc_info=True)
        finally:
            await self.stop()
    
    async def _process_message(self, data: Dict[str, Any]) -> None:
        """处理Kafka消息"""
        try:
            # 解析bot_id
            bot_id = data.get('bot_id')
            if not bot_id:
                self.logger.error("Missing bot_id in message")
                return
                
            # 获取对应的bot实例
            bot = self.bot_manager.active_bots.get(bot_id)
            if not bot:
                self.logger.error(f"Bot {bot_id} not found")
                return
                
            # 解析Telegram更新对象
            update_data = data.get('update')
            if not update_data:
                self.logger.error("Missing update data in message")
                return
                
            # 创建Update对象
            update = types.Update(**update_data)
            
            # 处理更新
            await bot.dp.feed_update(bot=bot.bot, update=update)
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop() 