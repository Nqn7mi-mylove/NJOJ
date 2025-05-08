"""Formatting utilities for test results."""

from typing import Dict, List, Any


def format_test_results(test_results: List[Dict[str, Any]]) -> str:
    """将测试结果格式化为易于理解的文本
    
    Args:
        test_results: 测试结果列表
        
    Returns:
        str: 格式化后的测试结果文本
    """
    if not test_results:
        return "无测试结果"
    
    formatted_results = []
    
    for i, test in enumerate(test_results):
        test_id = test.get("id", f"测试用例{i+1}")
        status = test.get("status", "未知")
        
        # 获取详细信息
        input_data = test.get("input", "无输入数据")
        expected = test.get("expected", "无预期输出")
        actual = test.get("actual", "无实际输出")
        error = test.get("error", "")
        
        # 格式化为易读的文本
        result_text = f"测试用例 {test_id}:\n"
        result_text += f"状态: {status}\n"
        result_text += f"输入: {input_data}\n"
        
        if status == "AC":
            result_text += f"输出: {actual}\n"
        else:
            result_text += f"预期: {expected}\n"
            result_text += f"实际: {actual}\n"
            
            if error:
                result_text += f"错误: {error}\n"
                
        formatted_results.append(result_text)
    
    # 连接所有测试结果
    return "\n".join(formatted_results)
