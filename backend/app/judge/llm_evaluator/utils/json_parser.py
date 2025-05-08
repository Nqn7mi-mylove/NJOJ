"""JSON parsing utilities for LLM responses."""

import json
import re
from typing import Dict, Any, Optional


def clean_json_string(json_str: str) -> str:
    """清理和修复JSON字符串
    
    Args:
        json_str: 需要清理的JSON字符串
        
    Returns:
        str: 清理后的JSON字符串
    """
    # 移除开头的```json和结尾的```
    json_str = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'\s*```$', '', json_str, flags=re.MULTILINE)
    
    # 替换掉不规范的Unicode转义
    json_str = re.sub(r'\\u([0-9a-fA-F]{4})', r'\\u\1', json_str)
    
    # 修复常见的JSON格式错误
    json_str = re.sub(r',\s*}', '}', json_str)  # 移除对象末尾的逗号
    json_str = re.sub(r',\s*]', ']', json_str)  # 移除数组末尾的逗号
    
    return json_str


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """通用方法解析LLM响应文本为JSON
    
    Args:
        response_text: LLM的原始响应文本
        
    Returns:
        dict: 解析后的JSON数据，已规范化键名
    
    Raises:
        ValueError: 如果无法解析为有效JSON
    """
    # 1. 尝试直接解析
    try:
        return direct_json_parse(response_text)
    except Exception:
        pass
    
    # 2. 尝试从文本中提取JSON
    pattern = r'```(?:json)?\s*([\s\S]*?)```'
    matches = re.findall(pattern, response_text)
    
    if matches:
        for match in matches:
            try:
                cleaned = clean_json_string(match)
                return json.loads(cleaned)
            except Exception:
                continue
    
    # 3. 如果找不到JSON块，尝试强制解析整个响应
    try:
        cleaned = clean_json_string(response_text)
        return json.loads(cleaned)
    except Exception:
        pass
    
    # 4. 尝试修复明显的格式问题
    try:
        # 查找开始的 { 和结束的 }
        start = response_text.find('{')
        end = response_text.rfind('}')
        
        if start != -1 and end != -1:
            potential_json = response_text[start:end+1]
            cleaned = clean_json_string(potential_json)
            return json.loads(cleaned)
    except Exception:
        pass
    
    # 5. 尝试解析带有前导换行的JSON
    result = parse_newline_json(response_text)
    if result:
        return result
    
    # 如果所有尝试都失败，抛出错误
    raise ValueError("无法解析为有效JSON")


def normalize_dict_keys(data: Any) -> Any:
    """递归地规范化字典中的所有键名，移除前导和尾随的空白字符
    
    Args:
        data: 要规范化的数据，可以是任何类型
        
    Returns:
        规范化后的数据
    """
    if not isinstance(data, dict):
        # 如果是列表，则递归规范化每个元素
        if isinstance(data, list):
            return [normalize_dict_keys(item) for item in data]
        # 如果是其他类型，则直接返回
        return data
    
    # 对于字典，规范化键名并递归处理值
    result = {}
    for key, value in data.items():
        # 规范化键名（如果是字符串）
        normalized_key = key.strip() if isinstance(key, str) else key
        # 递归规范化值
        normalized_value = normalize_dict_keys(value)
        # 存储规范化后的键值对
        result[normalized_key] = normalized_value
        
    return result


def direct_json_parse(response_text: str) -> Dict[str, Any]:
    """直接解析LLM返回的带有前导换行符和空格的JSON格式
    
    专门处理测试中发现的格式，例如:
    {
      "key": "value",
      ...
    }
    
    Args:
        response_text: LLM的原始响应文本
        
    Returns:
        dict: 解析后的JSON数据，已规范化键名
    """
    try:
        # 去除前后空白字符
        cleaned_text = response_text.strip()
        
        # 如果文本被```包裹，则提取内容
        if cleaned_text.startswith('```') and cleaned_text.endswith('```'):
            # 提取```之间的内容
            content = re.search(r'```(?:json)?\s*([\s\S]*?)```', cleaned_text)
            if content:
                cleaned_text = content.group(1).strip()
        
        # 解析JSON
        json_data = json.loads(cleaned_text)
        
        # 规范化键名
        normalized_data = normalize_dict_keys(json_data)
        
        # 打印规范化前后的键对比，帮助调试
        if isinstance(json_data, dict) and isinstance(normalized_data, dict):
            print("\n====== 键名规范化前后对比 ======")
            original_keys = list(json_data.keys())
            normalized_keys = list(normalized_data.keys())
            for i in range(min(len(original_keys), len(normalized_keys))):
                if original_keys[i] != normalized_keys[i]:
                    print(f"原始键: '{original_keys[i]}' -> 规范化键: '{normalized_keys[i]}'")
            print("===============================\n")
        
        return normalized_data
    except Exception as e:
        raise ValueError(f"直接JSON解析失败: {str(e)}")


def parse_newline_json(text: str) -> Optional[Dict[str, Any]]:
    """专门处理以换行开头的JSON文本，如'\n "key"'格式
    
    Args:
        text: 以换行符开头的文本
        
    Returns:
        Optional[Dict]: 解析后的JSON数据或None
    """
    try:
        # 尝试修复常见格式问题
        fixed_text = text
        
        # 移除开头的非JSON字符
        fixed_text = re.sub(r'^[^{]*', '', fixed_text)
        
        # 移除结尾的非JSON字符
        fixed_text = re.sub(r'[^}]*$', '', fixed_text)
        
        # 解析JSON
        json_data = json.loads(fixed_text)
        
        # 规范化键名
        return normalize_dict_keys(json_data)
    except Exception:
        return None
