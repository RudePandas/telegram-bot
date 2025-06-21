from datetime import datetime
import random
import time
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from ..services.bot_service import TelegramBotService
from ..services.event_manager import IEventListener


class AdvancedEventListener(IEventListener):
    """高级事件监听器示例"""
    
    def __init__(self):
        self.message_count = 0
        self.user_stats = {}
    
    async def on_startup(self, bot: TelegramBotService) -> None:
        print(f"🚀 [高级监听器] 机器人 @{bot.bot_info.username if bot.bot_info else 'Unknown'} 启动完成")
    
    async def on_shutdown(self, bot: TelegramBotService) -> None:
        print(f"🛑 [高级监听器] 机器人 @{bot.bot_info.username if bot.bot_info else 'Unknown'} 已停止")
        print(f"📊 总消息数: {self.message_count}")
        print(f"👥 活跃用户数: {len(self.user_stats)}")
    
    async def on_message_received(self, message: Message, bot: TelegramBotService) -> None:
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
    
    async def on_message_sent(self, message: Message, bot: TelegramBotService) -> None:
        print(f"📤 [高级监听器] 发送消息到聊天 {message.chat.id}")
    
    async def on_error(self, error: Exception, bot: TelegramBotService) -> None:
        print(f"❌ [高级监听器] 捕获错误: {error}")


# 命令处理函数
async def start_command(message: Message, bot: TelegramBotService, state: FSMContext):
    """处理 /start 命令"""
    user_name = message.from_user.full_name if message.from_user else "朋友"
    welcome_text = f"👋 你好，<b>{user_name}</b>！\n\n欢迎使用多机器人框架！"
    
    await bot.send_message(
        message.chat.id, 
        welcome_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 查看功能", callback_data="show_features")],
            [InlineKeyboardButton(text="❓ 获取帮助", callback_data="show_help")]
        ])
    )


async def help_command(message: Message, bot: TelegramBotService, state: FSMContext):
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


async def echo_command(message: Message, bot: TelegramBotService, state: FSMContext):
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


async def info_command(message: Message, bot: TelegramBotService, state: FSMContext):
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


async def ping_command(message: Message, bot: TelegramBotService, state: FSMContext):
    """处理 /ping 命令"""
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
async def hello_handler(message: Message, bot: TelegramBotService, state: FSMContext):
    """处理问候消息"""
    user_name = message.from_user.full_name if message.from_user else "朋友"
    greetings = [
        f"👋 你好，{user_name}！",
        f"🌟 很高兴见到你，{user_name}！",
        f"😊 {user_name}，你好呀！",
        f"🎉 欢迎，{user_name}！"
    ]
    
    greeting = random.choice(greetings)
    
    await bot.send_message(
        message.chat.id,
        greeting,
        reply_to_message_id=message.message_id
    )


# 媒体处理函数
async def photo_handler(message: Message, bot: TelegramBotService, state: FSMContext):
    """处理图片消息"""
    await bot.send_message(
        message.chat.id,
        "📷 <b>收到图片！</b>\n\n图片处理功能正在开发中...",
        reply_to_message_id=message.message_id
    )


async def document_handler(message: Message, bot: TelegramBotService, state: FSMContext):
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


async def location_handler(message: Message, bot: TelegramBotService, state: FSMContext):
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
async def features_callback(callback: CallbackQuery, bot: TelegramBotService, state: FSMContext):
    """处理功能展示回调"""
    features_text = """
🎯 <b>机器人核心功能</b>

✨ <b>多机器人支持:</b>
• 多机器人实例管理
• 独立的配置和状态
• 统一的消息广播
• 集中的事件处理

🔧 <b>技术特点:</b>
• 基于 aiogram 3.x
• 支持中间件
• 可扩展的过滤器系统
• 完整的错误处理

🚀 <b>高级功能:</b>
• 回调查询处理
• 内联查询支持
• 文件上传下载
• 群组管理功能
    """
    
    await callback.message.edit_text(
        features_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 返回主菜单", callback_data="back_to_main")]
        ])
    )


async def help_callback(callback: CallbackQuery, bot: TelegramBotService, state: FSMContext):
    """处理帮助回调"""
    help_text = """
❓ <b>如何使用机器人</b>

1️⃣ <b>基础使用:</b>
• 直接发送消息与机器人对话
• 使用 /help 查看所有命令
• 使用 /info 查看个人信息

2️⃣ <b>群组使用:</b>
• 将机器人添加到群组
• 授予必要的管理权限
• 使用 /help 查看群组功能

3️⃣ <b>进阶功能:</b>
• 发送媒体文件
• 使用内联按钮
• 尝试各种命令

4️⃣ <b>获取支持:</b>
• 遇到问题请联系管理员
• 查看项目文档
• 提交功能建议
    """
    
    await callback.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 返回主菜单", callback_data="back_to_main")]
        ])
    )


async def back_to_main_callback(callback: CallbackQuery, bot: TelegramBotService, state: FSMContext):
    """处理返回主菜单回调"""
    user_name = callback.from_user.full_name if callback.from_user else "朋友"
    welcome_text = f"👋 你好，<b>{user_name}</b>！\n\n欢迎使用多机器人框架！"
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 查看功能", callback_data="show_features")],
            [InlineKeyboardButton(text="❓ 获取帮助", callback_data="show_help")]
        ])
    )