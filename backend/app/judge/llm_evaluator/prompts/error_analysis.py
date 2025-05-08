"""Error analysis prompt template for LLM code evaluation."""

ERROR_ANALYSIS_PROMPT = """
分析以下代码，结合测试结果，识别其中存在的问题并给出错误类型。

问题：
{problem_description}

学生代码：
{code}

测试结果：
{test_results}

错误类型说明：  
- WA (Wrong Answer): 逻辑错误导致输出结果错误  
- TLE (Time Limit Exceeded): 算法效率低下  
- MLE (Memory Limit Exceeded): 内存使用过高  
- RE (Runtime Error): 运行时错误（如除零、越界）  
- CE (Compilation Error): 编译错误
- AC (Accepted): 正确无误  

请判断学生代码的错误类型，并提供详细解释。

请分析步骤：
1. 首先检查每个失败的测试用例，了解它们的失败原因
2. 然后根据这些失败用例的共同特点，总结出程序存在的效率或逻辑问题
3. 最后给出整体的错误类型和解释

输出JSON格式的错误分析：
```json
{{
  "error_types": ["错误类型1", "错误类型2", ...],
  "explanation": "对程序整体问题的分析，包括导致错误的根本原因和问题所在",
  "error_details": [
    {{
      "type": "错误类型1",
      "description": "这类错误的详细描述",
      "test_cases": ["测试用例ID1", "测试用例ID2", ...]
    }},
    {{
      "type": "错误类型2",
      "description": "这类错误的详细描述",
      "test_cases": ["测试用例ID3", "测试用例ID4", ...]
    }}
  ]
}}
```
"""
