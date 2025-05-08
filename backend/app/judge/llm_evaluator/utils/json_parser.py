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
        dict: 解析后的JSON数据
    
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
        dict: 解析后的JSON数据
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
        return json.loads(cleaned_text)
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
        return json.loads(fixed_text)
    except Exception:
        return None
