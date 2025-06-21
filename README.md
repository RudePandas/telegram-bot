# Telegram Bot Service

一个高性能、可扩展的 Telegram 机器人服务框架，支持 Webhook 模式和消息队列。

## 特性

- ✨ 支持 Webhook 和轮询两种模式
- 🚀 基于 aiogram 的异步实现
- 🔒 线程安全的单例模式
- 📦 Kafka 消息队列集成
- 🎯 模块化的事件处理系统
- 📝 完整的日志记录
- 🔌 可扩展的插件系统
- 💾 MySQL/MariaDB 数据持久化
- 🔄 自动重连和错误恢复
- 🔑 SSL 证书支持

## 系统要求

- Python 3.7+
- MySQL/MariaDB
- Kafka
- SSL 证书（用于 Webhook 模式）

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/telegram-bot.git
cd telegram-bot
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

1. 数据库配置：
```python
await DatabaseConnection.initialize(
    host='localhost',
    port=3306,
    user='your_user',
    password='your_password',
    db='telegram_bots'
)
```

2. Bot 配置：
```python
config = BotConfiguration(
    token="your_bot_token",
    name="your_bot_name",
    # Webhook 配置（可选）
    webhook_host="https://your-domain.com",
    webhook_path="/webhook/123",
    webhook_secret_token="your_secret_token",
    webhook_max_connections=40,
    webhook_certificate_path="path/to/cert.pem",
    webhook_certificate_key_path="path/to/private.key"
)
```

3. Kafka 配置：
```python
kafka_config = {
    "bootstrap_servers": "localhost:9092",
    "topic": "telegram_updates",
    "group_id": "bot_group"
}
```

## 使用示例

### 1. 基本使用

```python
import asyncio
from src.services.bot_manager import BotManager
from src.models.config import BotConfiguration

async def main():
    # 获取 BotManager 实例
    bot_manager = await BotManager.get_instance()
    
    # 初始化
    await bot_manager.initialize(
        db_url="mysql://user:pass@localhost/telegram_bots",
        kafka_config={
            "bootstrap_servers": "localhost:9092",
            "topic": "telegram_updates",
            "group_id": "bot_group"
        }
    )
    
    # 配置 bot
    config = BotConfiguration(
        token="your_bot_token",
        name="your_bot_name",
        webhook_host="https://your-domain.com"
    )
    
    # 注册 bot
    bot_id = 123
    bot = await bot_manager.register_bot(bot_id, config)
    
    # 启动所有 bot（Webhook 模式）
    await bot_manager.start_all(webhook_base_url="https://your-domain.com/webhook/")
    
    try:
        # 保持程序运行
        await asyncio.Event().wait()
    finally:
        # 停止所有 bot
        await bot_manager.stop_all()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 添加消息处理器

```python
from src.handlers.message_handlers import CommandMessageHandler

async def start_command(message: types.Message, bot: TelegramBotService, state: FSMContext):
    await message.reply("Hello! I'm your bot.")

bot.add_command_handler("start", start_command, "Start the bot")
```

### 3. 广播消息

```python
await bot_manager.broadcast_message(
    message="Important announcement!",
    bot_ids=[123, 456],  # 可选，指定特定的 bot
    batch_size=50,
    retry_count=3
)
```

## Webhook 设置

1. 准备 SSL 证书：
   - 可以使用 Let's Encrypt 获取免费证书
   - 或使用自签名证书（仅用于测试）

2. 配置 Nginx：
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;

    location /webhook/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. 启动 Webhook 服务器：
   - 使用你喜欢的 Web 框架（如 FastAPI、aiohttp）
   - 接收 Telegram 更新并发送到 Kafka

## 项目结构

```
telegram-bot/
├── src/
│   ├── handlers/          # 消息处理器
│   ├── models/           # 数据模型
│   └── services/         # 核心服务
├── tests/               # 测试用例
├── requirements.txt     # 项目依赖
└── README.md           # 项目文档
```

## 贡献

欢迎提交 Pull Request 或创建 Issue！

## 许可证

MIT License

## 作者

Your Name <your.email@example.com>

## 更新日志

### v1.0.0 (2024-03-xx)
- 初始版本发布
- 支持 Webhook 模式
- 添加 Kafka 集成
- 实现线程安全的单例模式 
