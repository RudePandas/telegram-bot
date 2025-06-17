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

## 面向对象高级特性

### 1. 抽象类和接口设计
```python
class IEventListener(ABC):
    """事件监听器接口"""
    @abstractmethod
    async def on_startup(self, bot: 'TelegramBotService') -> None:
        pass
```
- 使用 `ABC` (Abstract Base Class) 创建抽象基类
- 使用 `@abstractmethod` 定义必须实现的方法
- 强制子类实现特定的接口方法

### 2. 依赖注入和控制反转
```python
class MessageService:
    def __init__(self, bot: Bot, event_manager: EventManager):
        self._bot = bot
        self._event_manager = event_manager
```
- 通过构造函数注入依赖
- 降低组件间的耦合度
- 便于单元测试和模块替换

### 3. 建造者模式（Builder Pattern）
```python
bot = (BotBuilder("YOUR_BOT_TOKEN")
       .with_parse_mode("HTML")
       .with_drop_pending_updates(True)
       .build())
```
- 使用流式接口（Fluent Interface）
- 分步骤构建复杂对象
- 提供优雅的API设计

### 4. 事件驱动设计
```python
class EventManager:
    def __init__(self):
        self._listeners: List[IEventListener] = []
    
    async def emit_startup(self, bot: 'TelegramBotService') -> None:
        for listener in self._listeners:
            await listener.on_startup(bot)
```
- 观察者模式的实现
- 事件发布/订阅机制
- 松耦合的组件通信

### 5. 责任链模式（Chain of Responsibility）
```python
class HandlerRegistry:
    async def _process_message(self, message: types.Message, state: FSMContext) -> None:
        handlers = self.get_message_handlers()
        for handler in handlers:
            if await handler.can_handle(message, state):
                await handler.handle(message, self, state)
                break
```
- 处理器链式处理消息
- 动态的处理器优先级
- 灵活的处理器注册机制

### 6. 数据类和不可变对象
```python
@dataclass
class BotConfiguration:
    token: str
    parse_mode: str = "HTML"
    disable_web_page_preview: bool = False
```
- 使用 `@dataclass` 装饰器
- 自动生成特殊方法
- 不可变配置对象

### 7. 枚举类型
```python
class BotState(Enum):
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
```
- 使用 `Enum` 定义状态
- 类型安全的状态管理
- 自文档化的代码

### 8. 上下文管理器
```python
class TelegramBotService:
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
```
- 实现异步上下文管理器
- 自动资源管理
- 优雅的错误处理

### 9. 组合优于继承
```python
class TelegramBotService:
    def __init__(self, config: BotConfiguration):
        self.handler_registry = HandlerRegistry()
        self.event_manager = EventManager()
        self.message_service = MessageService(self.bot, self.event_manager)
```
- 使用组合而不是继承
- 更灵活的功能扩展
- 更好的代码重用

### 10. 类型注解和泛型
```python
def register_message_handler(self, handler: IMessageHandler) -> None:
    self._message_handlers.append(handler)
```
- 使用类型提示
- 支持静态类型检查
- 提高代码可读性和可维护性

### 11. 异步编程支持
```python
async def handle_message(self, message: Message, bot: 'TelegramBotService', state: FSMContext) -> Any:
    try:
        if asyncio.iscoroutinefunction(self.callback):
            return await self.callback(message, bot, state)
```
- 异步方法和协程
- 非阻塞I/O操作
- 高效的并发处理

## 设计优势

### 1. 可维护性
- 清晰的代码结构
- 易于理解的组件关系
- 方便的调试和测试

### 2. 可扩展性
- 容易添加新功能
- 灵活的组件替换
- 松耦合的设计

### 3. 可重用性
- 模块化的组件
- 通用的接口设计
- 可移植的代码

### 4. 类型安全
- 编译时错误检查
- IDE智能提示
- 减少运行时错误

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