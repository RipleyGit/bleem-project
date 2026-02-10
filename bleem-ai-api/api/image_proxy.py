"""
图片代理服务 - 将 HTTP 图片转换为 HTTPS
"""
from fastapi import APIRouter, HTTPException
import httpx
import io
from fastapi.responses import Response

router = APIRouter(tags=["image_proxy"])

@router.get("/image-proxy")
async def proxy_image(url: str):
    """
    代理图片请求，支持 HTTP 到 HTTPS 的转换

    Args:
        url: 原始图片 URL

    Returns:
        图片数据
    """
    try:
        print(f"代理图片请求: {url}")

        # 下载图片
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.get(url)
            response.raise_for_status()

            # 获取内容类型
            content_type = response.headers.get('content-type', 'image/jpeg')

            # 返回图片数据
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",  # 缓存1天
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET",
                    "Access-Control-Allow-Headers": "*"
                }
            )

    except httpx.HTTPError as e:
        print(f"图片代理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to proxy image: {str(e)}")
    except Exception as e:
        print(f"图片代理异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image proxy error: {str(e)}")