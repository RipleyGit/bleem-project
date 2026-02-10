"""
数据库连接池配置
支持 SQLite 和 MySQL
"""
import os
from typing import Dict, Any
import aiomysql

# 数据库配置
DB_CONFIG = {
    "sqlite": {
        "type": "sqlite"
    },
    "mysql": {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "db": os.getenv("MYSQL_DATABASE", "aiwardrobe"),  # aiomysql 使用 'db' 而不是 'database'
        "charset": "utf8mb4",
        "autocommit": False
    }
}

# 当前使用的数据库类型（可通过环境变量切换）
DB_TYPE = os.getenv("DB_TYPE", "mysql")  # 默认使用 MySQL

# MySQL 连接池配置
MYSQL_POOL_CONFIG = {
    "minsize": 1,
    "maxsize": 10,
}

# 全局连接池变量
mysql_pool = None

async def get_mysql_pool():
    """获取 MySQL 连接池"""
    global mysql_pool
    if mysql_pool is None:
        mysql_pool = await aiomysql.create_pool(
            **DB_CONFIG["mysql"],
            **MYSQL_POOL_CONFIG
        )
    return mysql_pool

async def close_mysql_pool():
    """关闭 MySQL 连接池"""
    global mysql_pool
    if mysql_pool:
        mysql_pool.close()
        await mysql_pool.wait_closed()
        mysql_pool = None