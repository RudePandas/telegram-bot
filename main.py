import asyncio
import logging
from datetime import datetime
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from src.models.enums import MessageType
from src.utils.bot_builder import BotBuilder
from src.services.event_manager import IEventListener


class AdvancedEventListener(IEventListener):
    """高级事件监听器"""
    
    def __init__(self):
        self.message_count = 0
        self.user_stats = {}
    
    async def on_startup(self, bot: 'TelegramBotService') -> None:
        print("🚀 [高级监听器] 机器人启动完成")
        print(f"🤖 机器人信息: @{bot.bot_info.username if bot.bot_info else 'Unknown'}")
    
    async def on_shutdown(self, bot: 'TelegramBotService') -> None:
        print("🛑 [高级监听器] 机器人已停止")
        print(f"📊 总消息数: {self.message_count}")
        print(f"👥 活跃用户数: {len(self.user_stats)}")
    
    async def on_message_received(self, message: Message, bot: 'TelegramBotService') -> None:
        self.message_count += 1
        
        if message.from_user:
            user_id = message.from_user.id
            if user_id not in self.user_stats:
                self.user_stats[user_id] = {
                    'name': message.from_user.full_name,
                    'message_count': 0,
                    'first_seen': datetime.now()
                }
            self.user_stats[user_id]['message_count'] += 1
        
        # 每100条消息打印统计
        if self.message_count % 100 == 0:
            print(f"📈 [统计] 已处理 {self.message_count} 条消息")
    
    async def on_message_sent(self, message: Message, bot: 'TelegramBotService') -> None:
        print(f"📤 [高级监听器] 发送消息到聊天 {message.chat.id}")
    
    async def on_error(self, error: Exception, bot: 'TelegramBotService') -> None:
        print(f"❌ [高级监听器] 捕获错误: {error}")


# 命令处理函数
async def start_command(message: Message, bot: 'TelegramBotService', state: FSMContext):
    """处理 /start 命令"""
    user_name = message.from_user.full_name if message.from_user else "朋友"
    welcome_text = f"👋 你好，<b>{user_name}</b>！\n\n欢迎使用极致面向对象的Telegram机器人！"
    
    await bot.send_message(
        message.chat.id, 
        welcome_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 查看功能", callback_data="show_features")],
            [InlineKeyboardButton(text="❓ 获取帮助", callback_data="show_help")]
        ])
    )


async def help_command(message: Message, bot: 'TelegramBotService', state: FSMContext):
    """处理 /help 命令"""
    help_text = """
🤖 <b>机器人功能列表</b>

<b>📋 基础命令:</b>
• /start - 开始使用机器人
• /help - 显示此帮助信息
• /echo &lt;文本&gt; - 回显指定文本
• /info - 显示用户信息
• /ping - 测试机器人响应

<b>🎯 智能功能:</b>
• 发送 "你好" 或 "hello" - 智能问候
• 发送图片 - 图片识别功能
• 发送文档 - 文档处理功能
• 发送位置 - 位置信息处理

<b>💡 提示:</b>
所有功能都支持群组和私聊使用！
    """
    await bot.send_message(message.chat.id, help_text)


async def echo_command(message: Message, bot: 'TelegramBotService', state: FSMContext):
    """处理 /echo 命令"""
    if message.text and len(message.text.split()) > 1:
        echo_text = " ".join(message.text.split()[1:])  # 去掉 "/echo"
        await bot.send_message(
            message.chat.id, 
            f"🔄 <b>回显:</b> {echo_text}",
            reply_to_message_id=message.message_id
        )
    else:
        await bot.send_message(
            message.chat.id, 
            "❌ 请在 /echo 后面输入要回显的文本\n\n<i>示例: /echo 你好世界</i>"
        )


async def info_command(message: Message, bot: 'TelegramBotService', state: FSMContext):
    """处理 /info 命令"""
    user = message.from_user
    chat = message.chat
    
    if not user:
        await bot.send_message(message.chat.id, "❌ 无法获取用户信息")
        return
    
    info_text = f"""
👤 <b>用户信息</b>

<b>🆔 用户ID:</b> <code>{user.id}</code>
<b>👤 用户名:</b> {f"@{user.username}" if user.username else "未设置"}
<b>📝 姓名:</b> {user.full_name}
<b>🌐 语言:</b> {user.language_code if user.language_code else "未知"}
<b>🤖 是否为机器人:</b> {"是" if user.is_bot else "否"}

<b>💬 聊天信息</b>

<b>🆔 聊天ID:</b> <code>{chat.id}</code>
<b>📱 聊天类型:</b> {chat.type}
<b>📝 聊天标题:</b> {chat.title if chat.title else "私聊"}
    """
    
    await bot.send_message(message.chat.id, info_text)


async def ping_command(message: Message, bot: 'TelegramBotService', state: FSMContext):
    """处理 /ping 命令"""
    import time
    start_time = time.time()
    
    sent_message = await bot.send_message(message.chat.id, "🏓 Pinging...")
    
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    
    await bot.message_service.edit_message_text(
        f"🏓 <b>Pong!</b>\n\n⏱️ 延迟: <code>{latency}ms</code>",
        chat_id=message.chat.id,
        message_id=sent_message.message_id
    )


# 文本处理函数
async def hello_handler(message: Message, bot: 'TelegramBotService', state: FSMContext):
    """处理问候消息"""
    user_name = message.from_user.full_name if message.from_user else "朋友"
    greetings = [
        f"👋 你好，{user_name}！",
        f"🌟 很高兴见到你，{user_name}！",
        f"😊 {user_name}，你好呀！",
        f"🎉 欢迎，{user_name}！"
    ]
    
    import random
    greeting = random.choice(greetings)
    
    await bot.send_message(
        message.chat.id,
        greeting,
        reply_to_message_id=message.message_id
    )


# 媒体处理函数
async def photo_handler(message: Message, bot: 'TelegramBotService', state: FSMContext):
    """处理图片消息"""
    await bot.send_message(
        message.chat.id,
        "📷 <b>收到图片！</b>\n\n图片处理功能正在开发中...",
        reply_to_message_id=message.message_id
    )


async def document_handler(message: Message, bot: 'TelegramBotService', state: FSMContext):
    """处理文档消息"""
    doc = message.document
    if doc:
        file_info = f"""
📄 <b>收到文档！</b>

<b>📝 文件名:</b> {doc.file_name or "未知"}
<b>📏 文件大小:</b> {doc.file_size or 0} bytes
<b>🏷️ MIME类型:</b> {doc.mime_type or "未知"}
        """
        await bot.send_message(
            message.chat.id,
            file_info,
            reply_to_message_id=message.message_id
        )


async def location_handler(message: Message, bot: 'TelegramBotService', state: FSMContext):
    """处理位置消息"""
    location = message.location
    if location:
        location_info = f"""
📍 <b>收到位置信息！</b>

<b>🌐 纬度:</b> {location.latitude}
<b>🌐 经度:</b> {location.longitude}
<b>🎯 精度:</b> {location.horizontal_accuracy or "未知"} 米
        """
        await bot.send_message(
            message.chat.id,
            location_info,
            reply_to_message_id=message.message_id
        )


# 回调处理函数
async def features_callback(callback: CallbackQuery, bot: 'TelegramBotService', state: FSMContext):
    """处理功能展示回调"""
    features_text = """
🎯 <b>机器人核心功能</b>

✨ <b>智能特性:</b>
• 极致面向对象架构
• 异步消息处理
• 事件驱动系统
• 灵活的处理器链
• 状态管理支持

🔧 <b>技术特点:</b>
• 基于 aiogram 3.x
• 支持中间件
• 可扩展的过滤器系统
• 完整的错误处理
• 内存状态存储

🚀 <b>高级功能:</b>
• 回调查询处理
• 内联查询支持
• 文件上传下载
• 群组管理功能
• Webhook 支持
    """
    
    await callback.message.edit_text(
        features_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 返回主菜单", callback_data="back_to_main")]
        ])
    )
    await callback.answer()


async def help_callback(callback: CallbackQuery, bot: 'TelegramBotService', state: FSMContext):
    """处理帮助回调"""
    help_text = """
❓ <b>使用帮助</b>

<b>🎯 快速开始:</b>
1. 发送 /start 开始使用
2. 发送 /help 查看所有命令
3. 尝试发送 "你好" 体验智能回复

<b>📝 命令格式:</b>
• 所有命令以 / 开头
• 参数用空格分隔
• 支持中英文命令

<b>💡 小贴士:</b>
• 可以在群组中使用所有功能
• 支持回复消息
• 支持多媒体文件处理

<b>🆘 需要帮助?</b>
发送任何文本消息，机器人会智能识别并处理！
    """
    
    await callback.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 返回主菜单", callback_data="back_to_main")]
        ])
    )
    await callback.answer()


async def back_to_main_callback(callback: CallbackQuery, bot: 'TelegramBotService', state: FSMContext):
    """返回主菜单回调"""
    user_name = callback.from_user.full_name if callback.from_user else "朋友"
    welcome_text = f"👋 你好，<b>{user_name}</b>！\n\n欢迎使用极致面向对象的Telegram机器人！"
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 查看功能", callback_data="show_features")],
            [InlineKeyboardButton(text="❓ 获取帮助", callback_data="show_help")]
        ])
    )
    await callback.answer()


async def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 使用构建器模式创建机器人
    bot = (BotBuilder("YOUR_BOT_TOKEN")
           .with_parse_mode("HTML")
           .with_drop_pending_updates(True)
           .build())
    
    # 配置机器人（使用流畅的API）
    bot.add_command_handler("start", start_command) \
       .add_command_handler("help", help_command) \
       .add_command_handler("echo", echo_command) \
       .add_command_handler("info", info_command) \
       .add_command_handler("ping", ping_command) \
       .add_text_handler(hello_handler, contains="你好") \
       .add_text_handler(hello_handler, contains="hello") \
       .add_media_handler(MessageType.PHOTO, photo_handler) \
       .add_media_handler(MessageType.DOCUMENT, document_handler) \
       .add_media_handler(MessageType.LOCATION, location_handler) \
       .add_callback_handler(features_callback, data_pattern="show_features") \
       .add_callback_handler(help_callback, data_pattern="show_help") \
       .add_callback_handler(back_to_main_callback, data_pattern="back_to_main") \
       .add_event_listener(AdvancedEventListener())
    
    # 启动机器人
    print("🤖 启动极致面向对象的Telegram机器人...")
    print("📝 使用 Ctrl+C 停止机器人")
    
    try:
        # 使用上下文管理器确保资源正确清理
        async with bot:
            await bot.start_polling()
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号，正在关闭机器人...")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        raise


if __name__ == "__main__":
    # 运行机器人
    asyncio.run(main()) 