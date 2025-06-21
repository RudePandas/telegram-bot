import asyncio
import aiomysql
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from dataclasses import dataclass


class DatabaseConnection:
    """数据库连接管理类"""
    _pool: Optional[aiomysql.Pool] = None
    _logger = logging.getLogger("DatabaseConnection")

    @classmethod
    async def initialize(cls,
                        host: str = 'localhost',
                        port: int = 3306,
                        user: str = 'root',
                        password: str = '',
                        db: str = 'telegram_bots',
                        min_size: int = 10,
                        max_size: int = 100,
                        **kwargs) -> None:
        """初始化数据库连接池"""
        try:
            cls._pool = await aiomysql.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                db=db,
                minsize=min_size,
                maxsize=max_size,
                autocommit=True,
                **kwargs
            )
            cls._logger.info("Database connection pool initialized successfully")
        except Exception as e:
            cls._logger.error(f"Failed to initialize database connection pool: {e}")
            raise

    @classmethod
    async def get_connection(cls) -> aiomysql.Connection:
        """获取数据库连接"""
        if cls._pool is None:
            raise RuntimeError("Database connection pool not initialized")
        return await cls._pool.acquire()

    @classmethod
    async def close(cls) -> None:
        """关闭数据库连接池"""
        if cls._pool is not None:
            cls._pool.close()
            await cls._pool.wait_closed()
            cls._pool = None
            cls._logger.info("Database connection pool closed")


@dataclass
class BotRecord:
    """机器人记录模型"""
    id: int
    token: str
    name: str
    is_active: bool
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    async def create_table(cls) -> None:
        """创建机器人表"""
        async with await DatabaseConnection.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bots (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        token VARCHAR(255) NOT NULL UNIQUE,
                        name VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        config JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

    @classmethod
    async def get_active_bots(cls) -> List['BotRecord']:
        """获取所有活跃的机器人"""
        async with await DatabaseConnection.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, token, name, is_active, config, created_at, updated_at "
                    "FROM bots WHERE is_active = TRUE"
                )
                records = await cursor.fetchall()
                return [
                    cls(
                        id=record[0],
                        token=record[1],
                        name=record[2],
                        is_active=record[3],
                        config=record[4],
                        created_at=record[5],
                        updated_at=record[6]
                    )
                    for record in records
                ]

    async def save(self) -> None:
        """保存或更新机器人记录"""
        async with await DatabaseConnection.get_connection() as conn:
            async with conn.cursor() as cursor:
                if self.id == 0:  # 新记录
                    await cursor.execute(
                        "INSERT INTO bots (token, name, is_active, config) VALUES (%s, %s, %s, %s)",
                        (self.token, self.name, self.is_active, self.config)
                    )
                    self.id = cursor.lastrowid
                else:  # 更新记录
                    await cursor.execute(
                        "UPDATE bots SET token=%s, name=%s, is_active=%s, config=%s WHERE id=%s",
                        (self.token, self.name, self.is_active, self.config, self.id)
                    )


@dataclass
class ChatRecord:
    """聊天记录模型"""
    id: int
    bot_id: int
    chat_id: int
    chat_type: str
    is_active: bool
    last_interaction: Optional[datetime]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    async def create_table(cls) -> None:
        """创建聊天表"""
        async with await DatabaseConnection.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chats (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        bot_id INT NOT NULL,
                        chat_id BIGINT NOT NULL,
                        chat_type VARCHAR(50) NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        last_interaction TIMESTAMP NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE,
                        UNIQUE KEY unique_bot_chat (bot_id, chat_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

    @classmethod
    async def get_active_chats(cls, bot_id: int) -> List['ChatRecord']:
        """获取机器人的所有活跃聊天"""
        async with await DatabaseConnection.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, bot_id, chat_id, chat_type, is_active, last_interaction, "
                    "created_at, updated_at FROM chats WHERE bot_id = %s AND is_active = TRUE",
                    (bot_id,)
                )
                records = await cursor.fetchall()
                return [
                    cls(
                        id=record[0],
                        bot_id=record[1],
                        chat_id=record[2],
                        chat_type=record[3],
                        is_active=record[4],
                        last_interaction=record[5],
                        created_at=record[6],
                        updated_at=record[7]
                    )
                    for record in records
                ]

    async def save(self) -> None:
        """保存或更新聊天记录"""
        async with await DatabaseConnection.get_connection() as conn:
            async with conn.cursor() as cursor:
                if self.id == 0:  # 新记录
                    await cursor.execute(
                        "INSERT INTO chats (bot_id, chat_id, chat_type, is_active, last_interaction) "
                        "VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) "
                        "ON DUPLICATE KEY UPDATE is_active=%s, last_interaction=CURRENT_TIMESTAMP",
                        (self.bot_id, self.chat_id, self.chat_type, self.is_active, self.is_active)
                    )
                    self.id = cursor.lastrowid
                else:  # 更新记录
                    await cursor.execute(
                        "UPDATE chats SET is_active=%s, last_interaction=CURRENT_TIMESTAMP "
                        "WHERE id=%s",
                        (self.is_active, self.id)
                    )