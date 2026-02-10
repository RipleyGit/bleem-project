"""
图片上传 API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
import uuid
import os
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from services.local_segment import remove_background
from services.removebg import remove_background_api
from services.llm_compatible import analyze_clothes_openai, analyze_items_openai
from storage.db_mysql import get_api_config,update_api_count

router = APIRouter()

# 上传目录
UPLOAD_DIR = Path(__file__).parent.parent / "ai_analyze"
UPLOAD_DIR.mkdir(exist_ok=True)

class ClotheItem(BaseModel):
    """衣橱中的单个衣物"""
    category: str
    item: str
    style_semantics: List[str]
    season_semantics: List[str]
    usage_semantics: List[str]
    color_semantics: str
    description: str
    created_at: datetime


@router.post("/clothe_analyze", response_model=ClotheItem)
async def clothe_analyze(
    file: UploadFile = File(...)
):
    """
    上传衣物图片
    
    流程：
    1. 接收图片
    2. 根据配置使用 rembg 或 remove.bg API 去除背景
    3. 使用 LLM Vision 进行语义分析
    4. 保存到数据库
    5. 返回衣物信息
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    try:
        # 读取原始图片
        raw_bytes = await file.read()
        print(f"📥 接收到文件: {file.filename}, 大小: {len(raw_bytes)} bytes")

        removebg_type = os.getenv("REMOVEBG_TYPE", "local")
        # 根据配置选择背景移除方式
        if removebg_type ==  "local":
            print("🎨 使用本地 rembg 处理...")
            processed_bytes = remove_background(raw_bytes)
        else:
            # 使用 remove.bg API
            try:
                # 加载配置
                api_configs = await get_api_config("removebg")
                api_config = api_configs[0]
                print(f"当前运行的api：{api_config}")
                print("🎨 使用 remove.bg API 处理背景...")
                processed_bytes = await remove_background_api(
                    raw_bytes,
                    api_config.api_base,
                    api_config.api_key 
                )
                await update_api_count(api_config.id) 
                print("🎨 使用 remove.bg API 处理背景完成")
            except ValueError as e:
                # 如果 remove.bg 失败，回退到本地处理
                print(f"⚠️ remove.bg API 失败，回退到本地处理: {e}")
                print("🎨 使用本地 rembg 处理...")
                processed_bytes = remove_background(raw_bytes)
    
        # 使用 OpenAI 兼容 API 进行语义分析
        print(f"🔍 开始语义分析，处理后图片大小: {len(processed_bytes)} bytes")
        semantics: ClothesSemantics = await analyze_clothes_openai(processed_bytes)
        print(f"✅ 语义分析完成: {semantics.item}")
        
        # 生成文件名（保留用于标识，但不再保存到磁盘）
        filename = f"{uuid.uuid4()}.png"

        # 直接将图片数据保存到数据库
        print(f"💾 准备保存图片到数据库，文件名: {filename}")
        
        clothes_data = ClotheItem(
            category=semantics.category,
            item=semantics.item,
            style_semantics=semantics.style_semantics,
            season_semantics=semantics.season_semantics,
            usage_semantics=semantics.usage_semantics,
            color_semantics=semantics.color_semantics,
            description=semantics.description,
            created_at=datetime.now()
        )
        return clothes_data
    except ValueError as e:
        print(f"❌ ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=f"图片分析失败: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/items_analyze", response_model=dict)
async def items_analyze(
    file: UploadFile = File(...)
):
    """
    上传衣物图片
    
    流程：
    1. 接收图片
    2. 根据配置使用 rembg 或 remove.bg API 去除背景
    3. 使用 LLM Vision 进行语义分析
    4. 保存到数据库
    5. 返回衣物信息
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    try:
        # 读取原始图片
        raw_bytes = await file.read()
        print(f"📥 接收到文件: {file.filename}, 大小: {len(raw_bytes)} bytes")

        removebg_type = os.getenv("REMOVEBG_TYPE", "local")
        # 根据配置选择背景移除方式
        if removebg_type ==  "local":
            print("🎨 使用本地 rembg 处理...")
            processed_bytes = remove_background(raw_bytes)
        else:
            # 使用 remove.bg API
            try:
                # 加载配置
                api_configs = await get_api_config("removebg")
                api_config = api_configs[0]
                print(f"当前运行的api：{api_config}")
                print("🎨 使用 remove.bg API 处理背景...")
                processed_bytes = await remove_background_api(
                    raw_bytes,
                    api_config.api_base,
                    api_config.api_key 
                )
                await update_api_count(api_config.id) 
                print("🎨 使用 remove.bg API 处理背景完成")
            except ValueError as e:
                # 如果 remove.bg 失败，回退到本地处理
                print(f"⚠️ remove.bg API 失败，回退到本地处理: {e}")
                print("🎨 使用本地 rembg 处理...")
                processed_bytes = remove_background(raw_bytes)
    
        # 使用 OpenAI 兼容 API 进行语义分析
        print(f"🔍 开始语义分析，处理后图片大小: {len(processed_bytes)} bytes")
        return await analyze_items_openai(processed_bytes)
    except ValueError as e:
        print(f"❌ ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=f"图片分析失败: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
