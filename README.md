# 极致面向对象的Telegram机器人框架

这是一个基于aiogram 3.x的Telegram机器人框架，采用极致面向对象设计，提供了优雅的API和完整的类型提示。

## 特性

- 🎯 极致面向对象设计
- 🚀 异步消息处理
- 📦 模块化架构
- 🔌 可扩展的处理器系统
- 🎭 事件驱动
- 🛡️ 完整的错误处理
- 📝 流畅的API设计
- 🔒 类型安全

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/telegram-bot.git
cd telegram-bot
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 快速开始

1. 在 `main.py` 中设置你的机器人token：

```python
bot = (BotBuilder("YOUR_BOT_TOKEN")
       .with_parse_mode("HTML")
       .with_drop_pending_updates(True)
       .build())
```

2. 运行机器人：

```bash
python main.py
```

## 项目结构

```
telegram-bot/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   └── config.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── message_handlers.py
│   │   └── callback_handlers.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bot_service.py
│   │   ├── event_manager.py
│   │   ├── handler_registry.py
│   │   └── message_service.py
│   └── utils/
│       ├── __init__.py
│       └── bot_builder.py
├── main.py
├── requirements.txt
└── README.md
```

## 使用示例

### 基本命令处理器

```python
async def start_command(message: Message, bot: TelegramBotService, state: FSMContext):
    await bot.send_message(message.chat.id, "Hello, World!")

bot.add_command_handler("start", start_command)
```

### 文本消息处理器

```python
async def hello_handler(message: Message, bot: TelegramBotService, state: FSMContext):
    await bot.send_message(message.chat.id, "你好！")

bot.add_text_handler(hello_handler, contains="你好")
```

### 媒体消息处理器

```python
async def photo_handler(message: Message, bot: TelegramBotService, state: FSMContext):
    await bot.send_message(message.chat.id, "收到图片！")

bot.add_media_handler(MessageType.PHOTO, photo_handler)
```

### 自定义事件监听器

```python
class MyEventListener(IEventListener):
    async def on_startup(self, bot: TelegramBotService) -> None:
        print("机器人启动了！")

bot.add_event_listener(MyEventListener())
```

## 贡献

欢迎提交Pull Request和Issue！

## 许可证

MIT License 