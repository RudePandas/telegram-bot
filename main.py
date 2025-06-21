import asyncio
import logging.config
from src.config.settings import get_config
from src.services.bot_manager import BotManager
from src.models.database import DatabaseConnection
from src.utils.bot_builder import BotBuilder
from src.examples.handlers import AdvancedEventListener
from src.examples.bot_config import configure_bot


async def setup_logging():
    """设置日志配置"""
    logging_config = get_config('logging')
    logging.config.dictConfig(logging_config)


async def setup_database():
    """设置数据库连接"""
    db_config = get_config('database')
    await DatabaseConnection.initialize(**db_config)


async def main():
    """主函数"""
    try:
        # 设置日志
        await setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting bot service...")

        # 设置数据库
        await setup_database()
        logger.info("Database connection initialized")

        # 创建机器人管理器
        bot_manager = BotManager()
        await bot_manager.initialize(get_config('database'))
        logger.info("Bot manager initialized")

        # 加载所有活跃的机器人
        await bot_manager.load_bots()
        active_bots = bot_manager.active_bots
        
        if active_bots:
            logger.info(f"Loaded {len(active_bots)} active bots")
            
            # 为每个机器人配置处理器和事件监听器
            for bot_id, bot in active_bots.items():
                configure_bot(bot)
                bot.add_event_listener(AdvancedEventListener())
                logger.info(f"Configured bot {bot_id}")
            
            try:
                # 启动所有机器人
                logger.info("Starting all bots...")
                await asyncio.gather(
                    *[bot.run() for bot in active_bots.values()]
                )
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
            finally:
                # 停止所有机器人
                await bot_manager.stop_all()
                logger.info("All bots stopped")
        else:
            # 如果数据库中没有活跃的机器人，尝试从配置文件创建一个示例机器人
            logger.warning("No active bots found in database")
            bot_config = get_config('bot')
            
            if bot_config.get('token'):
                logger.info("Creating example bot from config...")
                bot = (BotBuilder(bot_config['token'])
                      .with_parse_mode(bot_config.get('parse_mode', 'HTML'))
                      .with_drop_pending_updates(bot_config.get('drop_pending_updates', True))
                      .build())
                
                # 配置示例处理器和事件监听器
                configure_bot(bot)
                bot.add_event_listener(AdvancedEventListener())
                
                try:
                    # 启动示例机器人
                    logger.info("Starting example bot...")
                    await bot.run()
                except KeyboardInterrupt:
                    logger.info("Received shutdown signal")
                finally:
                    await bot.stop()
                    logger.info("Bot stopped")
            else:
                logger.warning("No bot token configured. Please set the token in config.json or add bots to database")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
    finally:
        # 关闭数据库连接
        await DatabaseConnection.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot service stopped by user")