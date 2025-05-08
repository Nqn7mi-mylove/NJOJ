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

重要说明：
- 如果所有测试用例都通过 (AC)，那么error_types列表应该为空，不应该包含任何错误类型。
- 对于已经通过的代码，仅在explanation字段中对代码规范性和可读性等方面进行评价，不应该指出任何错误。

请分析步骤：
1. 首先检查所有测试用例是否全部通过（AC）。如果全部通过，则跳到步骤 4。
2. 如果有失败的测试用例，分析它们的失败原因。
3. 然后根据这些失败用例的共同特点，总结出程序存在的问题。
4. 如果所有测试用例都通过，则仅对代码规范性和可读性进行评价。

输出JSON格式的错误分析：
```json
{{
  "error_types": ["错误类型1", "错误类型2", ...], 〈如果所有测试都通过，则此列表应为空数组 []〉
  "explanation": "对程序整体的分析和评价，对于有错误的代码包括问题所在，对于正确代码则可以评价代码规范和风格",
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
请注意：如果所有测试用例都通过（AC），错误类型列表必须为空数组 []!
"""
