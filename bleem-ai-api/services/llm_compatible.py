"""
OpenAI 兼容 API 服务
支持任何 OpenAI 风格的 API 接口
"""
import httpx
import base64
import json
import re
import asyncio
from typing import List, Optional
from domain.prompts import CLOTHES_SEMANTIC_PROMPT,ITEMS_ANALYZE_PROMPT
from domain.clothes import ClothesSemantics
from storage.db_mysql import get_api_config,update_api_count


async def fetch_available_models() -> List[dict]:
    """
    获取可用模型列表
    """

    # 加载配置
    llm_configs = await get_api_config("llm")
    llm_config = llm_configs[0]
    print(f"当前运行的api：{llm_config}")
    # config = load_config()
    
    if not llm_config.api_key:
        return []
    
    # 确保 api_base 格式正确
    api_base = llm_config.api_base.rstrip("/")
    if not api_base.endswith("/v1"):
        api_base = api_base + "/v1"
    
    url = f"{api_base}/models"
    
    try:
        # 禁用代理设置
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                # 过滤出支持视觉的模型（通常包含 vision, gpt-4o, claude 等关键词）
                return [
                    {"id": m["id"], "name": m.get("name", m["id"])}
                    for m in models
                ]
            else:
                error_msg = f"API请求失败 ({response.status_code}): {response.text[:200]}"
                print(error_msg)
                raise Exception(error_msg)
    except Exception as e:
        print(f"获取模型列表异常: {e}")
        raise Exception(f"连接异常: {str(e)}")


def extract_json_from_response(text: str) -> dict:
    """
    从响应中提取 JSON
    处理可能的 markdown 代码块包装
    """
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 尝试提取 markdown 代码块中的 JSON
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # 尝试找到 { } 包围的内容
    brace_match = re.search(r'\{[\s\S]*\}', text)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"无法从响应中提取 JSON: {text}")


async def analyze_clothes_openai(image_bytes: bytes) -> ClothesSemantics:
    """
    使用 OpenAI 兼容 API 分析衣物图片
    
    Args:
        image_bytes: 图片的字节数据
        
    Returns:
        ClothesSemantics: 衣物语义信息
    """
    # config = load_config()
    # 加载配置
    
    # 加载配置
    llm_configs = await get_api_config("llm")
    llm_config = llm_configs[0]
    print(f"当前运行的api：{llm_config}")
    if not llm_config.api_key:
        raise ValueError("请先配置 API Key")
    
    # 确保 api_base 格式正确
    api_base = llm_config.api_base.rstrip("/")
    if not api_base.endswith("/v1"):
        api_base = api_base + "/v1"
    
    url = f"{api_base}/chat/completions"
    
    # 将图片转换为 base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    # 构建请求体
    payload = {
        "model": llm_config.model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": CLOTHES_SEMANTIC_PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }
    
    # 尝试最多3次请求
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"API 请求尝试 {attempt + 1}/{max_retries} 到 {llm_config.api_base}")
            # 创建 httpx 客户端，禁用系统代理
            # 因为通义千问等国内API不需要代理，系统代理反而会导致连接问题
            async with httpx.AsyncClient(
                timeout=60.0,
                trust_env=False  # 禁用环境变量中的代理设置
            ) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {llm_config.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

                if response.status_code != 200:
                    error_msg = f"API 请求失败: {response.status_code} - {response.text}"
                    print(f"{error_msg}")
                    if attempt == max_retries - 1:
                        raise ValueError(error_msg)
                    print(f"⏳ 5秒后重试...")
                    await asyncio.sleep(5)
                    continue

                # 请求成功，跳出循环
                await update_api_count(llm_config.id) 
                break

        except httpx.RequestError as e:
            error_msg = f"网络请求错误: {str(e)}"
            print(f" {error_msg}")
            if attempt == max_retries - 1:
                raise ValueError(error_msg)
            print(f"⏳ 5秒后重试...")
            await asyncio.sleep(5)
            continue

    # 如果循环正常结束（所有重试都失败了）
    if response is None:
        raise ValueError("API 请求失败：已达到最大重试次数")

    # 解析响应
    try:
        data = response.json()
        print(f"API响应状态: {response.status_code}")
    except Exception as e:
        print(f"解析响应失败: {str(e)}")
        raise ValueError(f"解析响应失败: {str(e)}")

    # 检查响应格式
    if "choices" not in data or not data["choices"]:
        print(f"响应格式错误: {data}")
        raise ValueError(f"响应格式错误: {data}")

    # 提取响应内容
    try:
        content = data["choices"][0]["message"]["content"]
        print(f"AI响应内容: {content[:200]}...")
    except (KeyError, IndexError) as e:
        print(f"提取内容失败: {str(e)}")
        raise ValueError(f"提取内容失败: {str(e)}")

    # 解析 JSON
    try:
        result = extract_json_from_response(content)
        print(f"AI分析结果: {result}")
    except ValueError as e:
        print(f"JSON解析失败: {str(e)}")
        raise ValueError(f"JSON解析失败: {str(e)}")

    # 数据清洗和标准化
    try:
        # 处理 color_semantics - 如果是数组，转换为字符串
        if 'color_semantics' in result and isinstance(result['color_semantics'], list):
            print(f"color_semantics 是数组格式，需要转换")
            result['color_semantics'] = ', '.join(result['color_semantics'])
            print(f"转换后的 color_semantics: {result['color_semantics']}")

        # 确保所有必需字段都存在
        if 'category' not in result or result['category'] not in ['top', 'bottom', 'shoes']:
            # 如果category不在预期值中，尝试从item推断
            item_lower = result.get('item', '').lower()
            if any(word in item_lower for word in ['上衣', '衬衫', '夹克', '外套', 'T恤', '毛衣']):
                result['category'] = 'top'
            elif any(word in item_lower for word in ['裤', '裙', '短裤', '长裤']):
                result['category'] = 'bottom'
            elif any(word in item_lower for word in ['鞋', '靴', '运动鞋', '拖鞋']):
                result['category'] = 'shoes'
            else:
                result['category'] = 'top'  # 默认值

        # 确保数组字段是正确的格式
        array_fields = ['style_semantics', 'season_semantics', 'usage_semantics']
        for field in array_fields:
            if field in result and isinstance(result[field], str):
                # 如果是字符串，按逗号分割
                result[field] = [s.strip() for s in result[field].split(',') if s.strip()]
            elif field not in result:
                result[field] = []  # 默认空数组

        return ClothesSemantics(**result)
    except Exception as e:
        print(f"创建语义对象失败: {str(e)}")
        raise ValueError(f"创建语义对象失败: {str(e)}")


async def analyze_items_openai(image_bytes: bytes) -> dict:
    """
    使用 OpenAI 兼容 API 分析衣物图片
    
    Args:
        image_bytes: 图片的字节数据
        
    Returns:
        ClothesSemantics: 衣物语义信息
    """
    # config = load_config()
    # 加载配置
    
    # 加载配置
    llm_configs = await get_api_config("llm")
    llm_config = llm_configs[0]
    print(f"当前运行的api：{llm_config}")
    if not llm_config.api_key:
        raise ValueError("请先配置 API Key")
    
    # 确保 api_base 格式正确
    api_base = llm_config.api_base.rstrip("/")
    if not api_base.endswith("/v1"):
        api_base = api_base + "/v1"
    
    url = f"{api_base}/chat/completions"
    
    # 将图片转换为 base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    # 构建请求体
    payload = {
        "model": llm_config.model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": ITEMS_ANALYZE_PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }
    
    # 尝试最多3次请求
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"API 请求尝试 {attempt + 1}/{max_retries} 到 {llm_config.api_base}")
            # 创建 httpx 客户端，禁用系统代理
            # 因为通义千问等国内API不需要代理，系统代理反而会导致连接问题
            async with httpx.AsyncClient(
                timeout=60.0,
                trust_env=False  # 禁用环境变量中的代理设置
            ) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {llm_config.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

                if response.status_code != 200:
                    error_msg = f"API 请求失败: {response.status_code} - {response.text}"
                    print(f"{error_msg}")
                    if attempt == max_retries - 1:
                        raise ValueError(error_msg)
                    print(f"⏳ 5秒后重试...")
                    await asyncio.sleep(5)
                    continue

                # 请求成功，跳出循环
                await update_api_count(llm_config.id) 
                break

        except httpx.RequestError as e:
            error_msg = f"网络请求错误: {str(e)}"
            print(f" {error_msg}")
            if attempt == max_retries - 1:
                raise ValueError(error_msg)
            print(f"⏳ 5秒后重试...")
            await asyncio.sleep(5)
            continue

    # 如果循环正常结束（所有重试都失败了）
    if response is None:
        raise ValueError("API 请求失败：已达到最大重试次数")

    # 解析响应
    try:
        data = response.json()
        print(f"API响应状态: {response.status_code}")
    except Exception as e:
        print(f"解析响应失败: {str(e)}")
        raise ValueError(f"解析响应失败: {str(e)}")

    # 检查响应格式
    if "choices" not in data or not data["choices"]:
        print(f"响应格式错误: {data}")
        raise ValueError(f"响应格式错误: {data}")

    # 提取响应内容
    try:
        content = data["choices"][0]["message"]["content"]
        print(f"AI响应内容: {content[:200]}...")
    except (KeyError, IndexError) as e:
        print(f"提取内容失败: {str(e)}")
        raise ValueError(f"提取内容失败: {str(e)}")

    # 解析 JSON
    try:
        result = extract_json_from_response(content)
        print(f"AI分析结果: {result}")
        return result
    except ValueError as e:
        print(f"JSON解析失败: {str(e)}")
        raise ValueError(f"JSON解析失败: {str(e)}")
