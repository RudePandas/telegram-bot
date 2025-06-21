import asyncio
import os
from dotenv import load_dotenv
from src.models.database import DatabaseConnection, BotRecord, ChatRecord

async def init_database():
    """初始化数据库和表"""
    try:
        # 加载环境变量
        load_dotenv()
        
        # 初始化数据库连接
        await DatabaseConnection.initialize(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            db=os.getenv('MYSQL_DATABASE', 'telegram_bots'),
            min_size=int(os.getenv('MYSQL_MIN_CONNECTIONS', '10')),
            max_size=int(os.getenv('MYSQL_MAX_CONNECTIONS', '100')),
        )
        
        # 创建必要的表
        await BotRecord.create_table()
        await ChatRecord.create_table()
        
        print("数据库初始化成功！")
        
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        raise
    finally:
        await DatabaseConnection.close()

if __name__ == "__main__":
    asyncio.run(init_database())