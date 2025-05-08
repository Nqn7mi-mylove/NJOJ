"""Error handling utilities for LLM-based code evaluation."""

from typing import Dict, Any


def create_error_response(error_message: str) -> Dict[str, Any]:
    """创建一个标准的错误响应
    
    Args:
        error_message: 错误消息
        
    Returns:
        Dict[str, Any]: 标准格式的错误响应
    """
    return {
        "error": error_message,
        "summary": "评估失败，请稍后再试",
        "improvement_suggestions": ["由于技术原因无法提供详细建议"],
        "overall_score": "0"
    }


def create_fallback_evaluation(reason: str) -> Dict[str, Any]:
    """创建一个基本但有用的评估回退响应
    
    Args:
        reason: 回退原因
        
    Returns:
        Dict[str, Any]: 有用的回退评估
    """
    return {
        "improvement_suggestions": ["由于技术问题，无法提供详细评估和建议"],
        "summary": f"评估部分失败（原因：{reason}），请稍后再试",
        "overall_score": "0"
    }


def create_fallback_response(text: str) -> Dict[str, Any]:
    """最后的回退选项：根据文本内容创建一个简单的有效响应
    
    Args:
        text: 无法解析的文本
        
    Returns:
        Dict: 构建的响应
    """
    # 从文本中尝试提取有用信息
    import re
    
    # 提取可能的错误类型
    error_types = []
    for error_type in ["WA", "TLE", "MLE", "RE", "CE", "AC"]:
        if error_type in text:
            error_types.append(error_type)
    
    # 提取可能的建议
    suggestions = []
    suggestion_pattern = r'建议[：:](.*?)(?=\n\n|\Z)'
    matches = re.findall(suggestion_pattern, text, re.DOTALL)
    if matches:
        for match in matches:
            suggestions.append(match.strip())
    
    # 如果没有找到建议，尝试从文本中提取有意义的句子
    if not suggestions:
        sentences = re.split(r'\.\s+|\n', text)
        for sentence in sentences:
            if len(sentence) > 20 and len(sentence) < 200:  # 合理长度的句子
                suggestions.append(sentence.strip())
                if len(suggestions) >= 2:  # 最多提取两个
                    break
    
    # 创建回退响应
    return {
        "error_types": error_types if error_types else ["未知"],
        "explanation": "无法解析完整评估结果",
        "code_standard": {"pros": [], "cons": ["无法进行详细评估"]},
        "code_logic": {"pros": [], "cons": []},
        "code_efficiency": {"pros": [], "cons": []},
        "improvement_suggestions": suggestions if suggestions else ["由于技术问题，无法提供详细建议"],
        "summary": "评估解析失败，仅提供部分信息",
        "overall_score": "0"
    }
