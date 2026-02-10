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
from storage.models import (
    USERS_TABLE_SQL_MYSQL, USERS_TABLE_SQL_SQLITE,
    CLOTHES_TABLE_SQL_MYSQL, CLOTHES_TABLE_SQL_SQLITE,
    CLOTHES_INDEX_SQL_MYSQL, CLOTHES_INDEX_SQL_SQLITE
)
from storage.db_config import DB_TYPE, get_mysql_pool, DB_CONFIG

# SQLite 数据库文件路径（仅在 SQLite 模式下使用）
_default_path = Path(__file__).parent.parent / "wardrobe.db"
DB_PATH = Path(os.getenv("DB_FILE_PATH", _default_path))


async def init_db():
    """初始化数据库，创建表和索引"""
    if DB_TYPE == "mysql":
        await _init_mysql_db()
    else:
        await _init_sqlite_db()


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
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # 先创建用户表（因为衣物表有外键依赖）
            # await cursor.execute(USERS_TABLE_SQL_MYSQL)
            # print("✅ 创建 users 表")
            
            await cursor.execute(USERS_TABLE_SQL_MYSQL)
            print("✅ 创建 users 表")
            
            # 再创建衣物表
            await cursor.execute(CLOTHES_TABLE_SQL_MYSQL)
            print("✅ 创建 clothes 表")

            # 创建索引
            try:
                await cursor.execute(CLOTHES_INDEX_SQL_MYSQL)
            except Exception as e:
                # 索引可能已存在，忽略错误
                pass

        await conn.commit()


async def _init_sqlite_db():
    """初始化 SQLite 数据库"""
    # 确保数据库文件的父目录存在
    if not DB_PATH.parent.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        # 先创建用户表
        await db.execute(USERS_TABLE_SQL_SQLITE)
        # 再创建衣物表
        await db.execute(CLOTHES_TABLE_SQL_SQLITE)
        await db.execute(CLOTHES_INDEX_SQL_SQLITE)
        await db.commit()


async def add_clothes(clothes: ClothesCreate) -> int:
    """
    添加衣物到数据库

    Returns:
        新创建的衣物 ID
    """
    if DB_TYPE == "mysql":
        return await _add_clothes_mysql(clothes)
    else:
        return await _add_clothes_sqlite(clothes)


async def _add_clothes_mysql(clothes: ClothesCreate) -> int:
    """MySQL 添加衣物"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO clothes (
                    category, item, style_semantics, season_semantics,
                    usage_semantics, color_semantics, description, image_filename, image_data
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    clothes.image_data
                )
            )
            await conn.commit()
            return cursor.lastrowid


async def _add_clothes_sqlite(clothes: ClothesCreate) -> int:
    """SQLite 添加衣物"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO clothes (
                category, item, style_semantics, season_semantics,
                usage_semantics, color_semantics, description, image_filename, image_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                clothes.image_data
            )
        )
        await db.commit()
        return cursor.lastrowid


async def get_all_clothes() -> List[ClothesItem]:
    """获取所有衣物"""
    if DB_TYPE == "mysql":
        return await _get_all_clothes_mysql()
    else:
        return await _get_all_clothes_sqlite()


async def _get_all_clothes_mysql() -> List[ClothesItem]:
    """MySQL 获取所有衣物"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 开始新事务以确保读取最新数据
            await conn.begin()
            # 强制读取最新数据，不使用缓存
            await cursor.execute(
                "SELECT * FROM clothes ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            await conn.commit()

            return [_row_to_clothes_item(row) for row in rows]


async def _get_all_clothes_sqlite() -> List[ClothesItem]:
    """SQLite 获取所有衣物"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM clothes ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()

        return [_row_to_clothes_item(dict(row)) for row in rows]


async def get_clothes_by_category(category: str) -> List[ClothesItem]:
    """按类别获取衣物"""
    if DB_TYPE == "mysql":
        return await _get_clothes_by_category_mysql(category)
    else:
        return await _get_clothes_by_category_sqlite(category)


async def _get_clothes_by_category_mysql(category: str) -> List[ClothesItem]:
    """MySQL 按类别获取衣物"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM clothes WHERE category = %s ORDER BY created_at DESC",
                (category,)
            )
            rows = await cursor.fetchall()

            return [_row_to_clothes_item(row) for row in rows]


async def _get_clothes_by_category_sqlite(category: str) -> List[ClothesItem]:
    """SQLite 按类别获取衣物"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM clothes WHERE category = ? ORDER BY created_at DESC",
            (category,)
        )
        rows = await cursor.fetchall()

        return [_row_to_clothes_item(dict(row)) for row in rows]


async def get_clothes_by_id(clothes_id: int) -> Optional[ClothesItem]:
    """按 ID 获取衣物"""
    if DB_TYPE == "mysql":
        return await _get_clothes_by_id_mysql(clothes_id)
    else:
        return await _get_clothes_by_id_sqlite(clothes_id)


async def _get_clothes_by_id_mysql(clothes_id: int) -> Optional[ClothesItem]:
    """MySQL 按 ID 获取衣物"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM clothes WHERE id = %s",
                (clothes_id,)
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


async def _get_clothes_by_id_sqlite(clothes_id: int) -> Optional[ClothesItem]:
    """SQLite 按 ID 获取衣物"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM clothes WHERE id = ?",
            (clothes_id,)
        )
        row = await cursor.fetchone()

        if row:
            return _row_to_clothes_item(dict(row))
        return None


async def delete_clothes(clothes_id: int) -> bool:
    """删除衣物"""
    if DB_TYPE == "mysql":
        return await _delete_clothes_mysql(clothes_id)
    else:
        return await _delete_clothes_sqlite(clothes_id)


async def _delete_clothes_mysql(clothes_id: int) -> bool:
    """MySQL 删除衣物"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # 先检查记录是否存在
            await cursor.execute("SELECT id FROM clothes WHERE id = %s", (clothes_id,))
            exists = await cursor.fetchone()
            if not exists:
                return False

            await cursor.execute(
                "DELETE FROM clothes WHERE id = %s",
                (clothes_id,)
            )
            await conn.commit()
            return cursor.rowcount > 0


async def _delete_clothes_sqlite(clothes_id: int) -> bool:
    """SQLite 删除衣物"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM clothes WHERE id = ?",
            (clothes_id,)
        )
        await db.commit()
        return cursor.rowcount > 0


async def update_clothes(clothes_id: int, clothes: ClothesCreate) -> bool:
    """更新衣物信息"""
    if DB_TYPE == "mysql":
        return await _update_clothes_mysql(clothes_id, clothes)
    else:
        return await _update_clothes_sqlite(clothes_id, clothes)


async def _update_clothes_mysql(clothes_id: int, clothes: ClothesCreate) -> bool:
    """MySQL 更新衣物信息"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # 先检查记录是否存在
            await cursor.execute("SELECT id FROM clothes WHERE id = %s", (clothes_id,))
            exists = await cursor.fetchone()
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


async def _update_clothes_sqlite(clothes_id: int, clothes: ClothesCreate) -> bool:
    """SQLite 更新衣物信息"""
    async with aiosqlite.connect(DB_PATH) as db:
        # 先检查记录是否存在
        cursor = await db.execute("SELECT id FROM clothes WHERE id = ?", (clothes_id,))
        exists = await cursor.fetchone()
        if not exists:
            return False

        # 执行更新
        cursor = await db.execute(
            """
            UPDATE clothes
            SET category = ?, item = ?, style_semantics = ?,
                season_semantics = ?, usage_semantics = ?,
                color_semantics = ?, description = ?, image_filename = ?
            WHERE id = ?
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
        await db.commit()
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
    if DB_TYPE == "mysql":
        return await _get_or_create_user_mysql(openid, user_data)
    else:
        return await _get_or_create_user_sqlite(openid, user_data)


async def _get_or_create_user_mysql(openid: str, user_data: Dict[str, Any]) -> int:
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


async def _get_or_create_user_sqlite(openid: str, user_data: Dict[str, Any]) -> int:
    """SQLite 获取或创建用户"""
    async with aiosqlite.connect(DB_PATH) as db:
        # 先尝试查找用户
        cursor = await db.execute("SELECT id FROM users WHERE openid = ?", (openid,))
        user = await cursor.fetchone()
        
        if user:
            # 用户已存在，更新信息
            await db.execute(
                """
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP,
                    city = ?,
                    province = ?,
                    country = ?,
                    location_id = ?,
                    latitude = ?,
                    longitude = ?,
                    nickname = COALESCE(?, nickname),
                    avatar_url = COALESCE(?, avatar_url),
                    gender = COALESCE(?, gender)
                WHERE openid = ?
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
            await db.commit()
            return user[0]
        else:
            # 创建新用户
            cursor = await db.execute(
                """
                INSERT INTO users (
                    openid, nickname, avatar_url, gender,
                    city, province, country, location_id,
                    latitude, longitude
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            await db.commit()
            return cursor.lastrowid


async def get_user_by_openid(openid: str) -> Optional[Dict[str, Any]]:
    """根据 openid 获取用户信息"""
    if DB_TYPE == "mysql":
        return await _get_user_by_openid_mysql(openid)
    else:
        return await _get_user_by_openid_sqlite(openid)


async def _get_user_by_openid_mysql(openid: str) -> Optional[Dict[str, Any]]:
    """MySQL 根据 openid 获取用户"""
    pool = await get_mysql_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM users WHERE openid = %s", (openid,))
            return await cursor.fetchone()


async def _get_user_by_openid_sqlite(openid: str) -> Optional[Dict[str, Any]]:
    """SQLite 根据 openid 获取用户"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE openid = ?", (openid,))
        row = await cursor.fetchone()
        return dict(row) if row else None
