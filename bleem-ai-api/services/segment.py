"""
rembg 背景移除服务
"""
from rembg import remove
from PIL import Image
import io


def remove_background(image_bytes: bytes) -> bytes:
    """
    使用 rembg 移除图片背景

    Args:
        image_bytes: 原始图片的字节数据

    Returns:
        去除背景后的 PNG 图片字节数据
    """
    try:
        input_img = Image.open(io.BytesIO(image_bytes))
        output = remove(input_img)

        buf = io.BytesIO()
        output.save(buf, format="PNG")
        result = buf.getvalue()
        print(f"✅ 背景移除成功，输出大小: {len(result)} bytes")
        return result
    except Exception as e:
        print(f"❌ 背景移除失败: {str(e)}")
        # 如果背景移除失败，返回原始图片
        print("⚠️ 使用原始图片继续处理...")
        return image_bytes
