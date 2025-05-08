#!/usr/bin/env python3
"""测试LLM连接和响应格式"""

import os
import json
import time
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取API密钥和基础URL
api_key = os.getenv("OPENAI_API_KEY", "")
api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

print(f"使用API基础URL: {api_base}")
print(f"API密钥长度: {len(api_key)}")

# 设置环境变量
if api_base != "https://api.openai.com/v1":
    os.environ["OPENAI_API_BASE"] = api_base

# 创建LLM客户端
model_name = "gpt-3.5-turbo"
print(f"使用模型: {model_name}")

try:
    # 初始化ChatOpenAI
    chat_model = ChatOpenAI(
        api_key=api_key,
        model=model_name,
        temperature=0.2,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    
    print("ChatOpenAI初始化成功")
    
    # 简单的测试提示
    test_prompt = """
    请以JSON格式回复以下问题：
    
    1. 你是什么模型？
    2. 当前的年份是？
    
    回复必须是有效的JSON格式，格式如下：
    {
      "model": "你的模型名称",
      "current_year": "当前年份",
      "status": "ok"
    }
    """
    
    print("开始API调用...")
    start_time = time.time()
    
    # 调用API
    response = chat_model.invoke(test_prompt)
    
    end_time = time.time()
    print(f"API调用完成，耗时: {end_time - start_time:.2f}秒")
    
    # 获取响应内容
    result = response.content
    
    # 显示响应信息
    print(f"响应长度: {len(result)}")
    print(f"原始响应前50个字符: '{result[:50]}'")
    print(f"原始响应后50个字符: '{result[-50:]}'")
    
    # 尝试解析JSON
    try:
        json_result = json.loads(result)
        print("JSON解析成功!")
        print(f"解析结果: {json.dumps(json_result, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {str(e)}")
        print(f"错误位置附近文本: '{result[max(0, e.pos-20):min(len(result), e.pos+20)]}'")
        
        # 尝试清理处理
        cleaned_result = result.strip()
        first_brace = cleaned_result.find('{')
        last_brace = cleaned_result.rfind('}')
        
        if first_brace >= 0 and last_brace > first_brace:
            print("尝试提取JSON部分...")
            json_part = cleaned_result[first_brace:last_brace+1]
            print(f"提取的JSON部分: '{json_part}'")
            try:
                json_result = json.loads(json_part)
                print("JSON提取并解析成功!")
                print(f"解析结果: {json.dumps(json_result, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError as e2:
                print(f"JSON提取后解析仍然失败: {str(e2)}")
    
except Exception as e:
    print(f"发生错误: {type(e).__name__} - {str(e)}")
