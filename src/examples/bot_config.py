from ..models.enums import MessageType, HandlerPriority
from ..handlers.message_handlers import CommandMessageHandler, TextMessageHandler, MediaMessageHandler
from ..handlers.callback_handlers import CallbackQueryHandler
from .handlers import (
    start_command, help_command, echo_command, info_command, ping_command,
    hello_handler, photo_handler, document_handler, location_handler,
    features_callback, help_callback, back_to_main_callback
)


def configure_bot(bot):
    """配置机器人处理器"""
    
    # 注册命令处理器
    bot.add_handler(CommandMessageHandler("start", start_command))
    bot.add_handler(CommandMessageHandler("help", help_command))
    bot.add_handler(CommandMessageHandler("echo", echo_command))
    bot.add_handler(CommandMessageHandler("info", info_command))
    bot.add_handler(CommandMessageHandler("ping", ping_command))
    
    # 注册文本处理器
    bot.add_handler(TextMessageHandler(
        hello_handler,
        contains="你好",
        priority=HandlerPriority.NORMAL.value
    ))
    bot.add_handler(TextMessageHandler(
        hello_handler,
        contains="hello",
        case_sensitive=False,
        priority=HandlerPriority.NORMAL.value
    ))
    
    # 注册媒体处理器
    bot.add_handler(MediaMessageHandler(MessageType.PHOTO, photo_handler))
    bot.add_handler(MediaMessageHandler(MessageType.DOCUMENT, document_handler))
    bot.add_handler(MediaMessageHandler(MessageType.LOCATION, location_handler))
    
    # 注册回调处理器
    bot.add_handler(CallbackQueryHandler(data_pattern="show_features", callback=features_callback))
    bot.add_handler(CallbackQueryHandler(data_pattern="show_help", callback=help_callback))
    bot.add_handler(CallbackQueryHandler(data_pattern="back_to_main", callback=back_to_main_callback)) 