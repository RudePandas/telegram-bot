import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'db': os.getenv('MYSQL_DATABASE', 'telegram_bots'),
    'min_size': int(os.getenv('MYSQL_MIN_CONNECTIONS', '10')),
    'max_size': int(os.getenv('MYSQL_MAX_CONNECTIONS', '100')),
}

# 机器人配置
BOT_CONFIG = {
    'parse_mode': 'HTML',
    'disable_web_page_preview': True,
    'drop_pending_updates': True,
}

# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/bot.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# 消息处理配置
MESSAGE_CONFIG = {
    'max_message_length': 4096,
    'message_rate_limit': 30,  # 每分钟最大消息数
    'media_group_timeout': 10,  # 媒体组超时时间（秒）
}

# 错误处理配置
ERROR_CONFIG = {
    'max_retries': 3,
    'retry_delay': 1,  # 重试延迟（秒）
    'error_notification_chat_id': os.getenv('ERROR_NOTIFICATION_CHAT_ID', None)
}

# 缓存配置
CACHE_CONFIG = {
    'enable': True,
    'ttl': 3600,  # 缓存过期时间（秒）
    'max_size': 1000,  # 最大缓存条目数
}

def get_config(section: str) -> Dict[str, Any]:
    """获取指定配置段"""
    config_map = {
        'database': DATABASE_CONFIG,
        'bot': BOT_CONFIG,
        'logging': LOGGING_CONFIG,
        'message': MESSAGE_CONFIG,
        'error': ERROR_CONFIG,
        'cache': CACHE_CONFIG,
    }
    return config_map.get(section, {}) 