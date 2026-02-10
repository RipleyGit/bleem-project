
"""
数据库连接和 CRUD 操作
支持 MySQL 和 SQLite
"""
import aiosqlite
import aiomysql
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from domain.clothes import ClothesItem, ClothesCreate
from storage.db_config import DB_TYPE, get_mysql_pool, DB_CONFIG
from domain.config import ApiConfig

from storage.models import (
    USERS_TABLE_SQL_MYSQL,
    API_CONFIG_TABLE_SQL_MYSQL,
    CLOTHES_TABLE_SQL_MYSQL,
    CLOTHES_INDEX_SQL_MYSQL
)

async def init_db():
    """初始化 MySQL 数据库"""
    await _init_mysql_db()


async def _init_mysql_db():
    """初始化 MySQL 数据库"""
    # 先连接到 MySQL 服务器（不指定数据库）
    mysql_config = DB_CONFIG["mysql"].copy()
    database_name = mysql_config.pop("db")  # 移除 db 参数

    # 创建临时连接来创建数据库
    async with aiomysql.connect(**mysql_config) as conn:
        async with conn.cursor() as cursor:
            # 创建数据库（如果不存在）
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        await conn.commit()

    # 现在连接到指定数据库并创建表
    # pool = await get_mysql_pool()
    # async with pool.acquire() as conn:
    #     async with conn.cursor() as cursor:
    #         # 先创建API表
    #         await cursor.execute(API_CONFIG_TABLE_SQL_MYSQL)
    #         print("✅ 创建 users 表")            
    #         # # 先创建用户表（因为衣物表有外键依赖）
    #         # await cursor.execute(USERS_TABLE_SQL_MYSQL)
    #         # print("✅ 创建 users 表")
            
    #         # # 再创建衣物表
    #         # await cursor.execute(CLOTHES_TABLE_SQL_MYSQL)
    #         # print("✅ 创建 clothes 表")

    #         # 创建索引
    #         try:
    #             await cursor.execute(CLOTHES_INDEX_SQL_MYSQL)
    #         except Exception as e:
    #             # 索引可能已存在，忽略错误
    #             pass
    #     await conn.commit()



async def add_clothes(clothes: ClothesCreate) -> int:
    """MySQL 添加衣物"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO clothes (
                    category, item, style_semantics, season_semantics,
                    usage_semantics, color_semantics, description, image_filename, image_data,user_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                """,
                (
                    clothes.category,
                    clothes.item,
                    json.dumps(clothes.style_semantics, ensure_ascii=False),
                    json.dumps(clothes.season_semantics, ensure_ascii=False),
                    json.dumps(clothes.usage_semantics, ensure_ascii=False),
                    clothes.color_semantics,
                    clothes.description,
                    clothes.image_filename,
                    clothes.image_data,
                    clothes.user_id
                )
            )
            await conn.commit()
            return cursor.lastrowid

async def get_all_clothes(user_id:str) -> List[ClothesItem]:
    """MySQL 获取所有衣物"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 开始新事务以确保读取最新数据
            await conn.begin()
            # 强制读取最新数据，不使用缓存
            await cursor.execute(
                "SELECT * FROM clothes WHERE del_flag = 0 and user_id = %s ORDER BY created_at DESC",
                (user_id,)
            )
            rows = await cursor.fetchall()
            await conn.commit()

            return [_row_to_clothes_item(row) for row in rows]



async def get_clothes_by_category(category: str,user_id:str) -> List[ClothesItem]:
    """MySQL 按类别获取衣物"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM clothes WHERE del_flag = 0 and category = %s AND user_id = %s ORDER BY created_at DESC",
                (category,user_id)
            )
            rows = await cursor.fetchall()

            return [_row_to_clothes_item(row) for row in rows]


async def get_clothes_by_id(clothes_id: int,user_id:str) -> Optional[ClothesItem]:
    """MySQL 按 ID 获取衣物"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM clothes WHERE del_flag = 0 and  id = %s AND user_id = %s",
                (clothes_id,user_id)
            )
            row = await cursor.fetchone()

            if row:
                try:
                    return _row_to_clothes_item(row)
                except Exception as e:
                    print(f"❌ 数据转换失败 ID {clothes_id}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return None
            return None


async def delete_clothes(clothes_id: int) -> bool:
    """MySQL 删除衣物"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # 先检查记录是否存在
            await cursor.execute("SELECT id FROM clothes WHERE del_flag = 0 and id = %s", (clothes_id,))
            exists = await cursor.fetchone()
            if not exists:
                return False

            await cursor.execute(
                "update clothes set del_flag = 1 WHERE id = %s",
                (clothes_id,)
            )
            await conn.commit()
            return cursor.rowcount > 0


async def update_clothes(clothes_id: int, clothes: ClothesCreate) -> bool:
    """MySQL 更新衣物信息"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # 先检查记录是否存在
            await cursor.execute("SELECT id FROM clothes WHERE del_flag = 0 and id = %s", (clothes_id,))
            exists = await cursor.fetchone()
            print(f"clothes_id: {clothes_id}, exists: {exists}")
            if not exists:
                return False

            # 执行更新
            await cursor.execute(
                """
                UPDATE clothes
                SET category = %s, item = %s, style_semantics = %s,
                    season_semantics = %s, usage_semantics = %s,
                    color_semantics = %s, description = %s, image_filename = %s
                WHERE id = %s
                """,
                (
                    clothes.category,
                    clothes.item,
                    json.dumps(clothes.style_semantics, ensure_ascii=False),
                    json.dumps(clothes.season_semantics, ensure_ascii=False),
                    json.dumps(clothes.usage_semantics, ensure_ascii=False),
                    clothes.color_semantics,
                    clothes.description,
                    clothes.image_filename,
                    clothes_id
                )
            )

            await conn.commit()
            return True



def _row_to_clothes_item(row: Dict[str, Any]) -> ClothesItem:
    """将数据库行转换为 ClothesItem"""
    try:
        # 处理 created_at 字段的格式差异
        created_at = row.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        elif isinstance(created_at, datetime):
            pass  # 已经是 datetime 对象
        else:
            created_at = datetime.now()

        # 解析 JSON 字段
        style_semantics = json.loads(row.get("style_semantics") or "[]")
        season_semantics = json.loads(row.get("season_semantics") or "[]")
        usage_semantics = json.loads(row.get("usage_semantics") or "[]")

        result = ClothesItem(
            id=row["id"],
            category=row["category"],
            item=row["item"],
            user_id=str(row.get("user_id") or ""),
            style_semantics=style_semantics,
            season_semantics=season_semantics,
            usage_semantics=usage_semantics,
            color_semantics=row.get("color_semantics") or "",
            description=row.get("description") or "",
            image_url=f"/api/clothes/image/{row['id']}",
            created_at=created_at
        )

        return result

    except Exception as e:
        print(f"❌ 转换失败 ID {row.get('id', 'Unknown')}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise



# ==================== Api相关操作 ====================

async def update_api_count(api_id: int) -> bool:
    """MySQL 更新衣物信息"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # 先检查记录是否存在
            await cursor.execute("SELECT id FROM api_config WHERE del_flag = 0 and id = %s", (api_id,))
            exists = await cursor.fetchone()
            print(f"api_id: {api_id}, exists: {exists}")
            if not exists:
                return False

            # 执行更新
            await cursor.execute(
                """
                UPDATE api_config
                SET usage_count = usage_count + 1
                WHERE id = %s
                """,
                (
                    api_id
                )
            )
            await conn.commit()
            return True

async def get_api_config(api_type: str) -> List[ApiConfig]:
    """MySQL 获取API配置"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 开始新事务以确保读取最新数据
            await conn.begin()
            # 强制读取最新数据，不使用缓存
            await cursor.execute(
                "SELECT * FROM api_config WHERE del_flag = 0 and api_type = %s ORDER BY usage_count ASC",
                (api_type,)
            )
            rows = await cursor.fetchall()
            await conn.commit()
            return [
                ApiConfig(
                id=row["id"],
                api_base=row["api_base"],
                api_key=row["api_key"],
                model=row["model"],
                api_type=row["api_type"],
                usage_count=row["usage_count"]
            ) for row in rows]


# ==================== 用户相关操作 ====================

async def get_or_create_user(openid: str, user_data: Dict[str, Any]) -> int:
    """
    获取或创建用户
    
    Args:
        openid: 微信用户唯一标识
        user_data: 用户信息字典，包含 nickname, city, province, country 等
        
    Returns:
        用户 ID
    """
    """MySQL 获取或创建用户"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 先尝试查找用户
            await cursor.execute("SELECT id FROM users WHERE openid = %s", (openid,))
            user = await cursor.fetchone()
            
            if user:
                # 用户已存在，更新登录时间和城市信息
                await cursor.execute(
                    """
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP,
                        city = %s,
                        province = %s,
                        country = %s,
                        location_id = %s,
                        latitude = %s,
                        longitude = %s,
                        nickname = COALESCE(%s, nickname),
                        avatar_url = COALESCE(%s, avatar_url),
                        gender = COALESCE(%s, gender)
                    WHERE openid = %s
                    """,
                    (
                        user_data.get("city"),
                        user_data.get("province"),
                        user_data.get("country"),
                        user_data.get("location_id"),
                        user_data.get("latitude"),
                        user_data.get("longitude"),
                        user_data.get("nickname"),
                        user_data.get("avatar_url"),
                        user_data.get("gender"),
                        openid
                    )
                )
                await conn.commit()
                return user["id"]
            else:
                # 创建新用户
                await cursor.execute(
                    """
                    INSERT INTO users (
                        openid, nickname, avatar_url, gender, 
                        city, province, country, location_id,
                        latitude, longitude
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        openid,
                        user_data.get("nickname", "微信用户"),
                        user_data.get("avatar_url", ""),
                        user_data.get("gender", 0),
                        user_data.get("city", ""),
                        user_data.get("province", ""),
                        user_data.get("country", ""),
                        user_data.get("location_id", ""),
                        user_data.get("latitude"),
                        user_data.get("longitude")
                    )
                )
                await conn.commit()
                return cursor.lastrowid




async def get_user_by_openid(openid: str) -> Optional[Dict[str, Any]]:
    """根据 openid 获取用户信息"""
    """MySQL 根据 openid 获取用户"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM users WHERE openid = %s", (openid,))
            return await cursor.fetchone()


async def update_user_location(openid: str, latitude: float, longitude: float, city: str):
    """MySQL 更新用户位置信息"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE users 
                SET latitude = %s, longitude = %s, city = %s
                WHERE openid = %s
                """,
                (latitude, longitude, city, openid)
            )
            await conn.commit()
            return cursor.rowcount > 0


