"""Single step evaluation prompt template for LLM code evaluation."""

SINGLE_STEP_PROMPT = """
你将被提供一个问题描述和一段代码。你的任务是评估这段代码的质量，并提供详细的分析。

评估步骤：
1. 仔细阅读问题描述，理解问题要求
2. 分析学生代码，识别代码中的问题
3. 输出JSON格式的评估结果

评估重点：
1. 代码规范性 - 代码结构、命名规范、注释质量等
2. 代码效率 - 时间复杂度和空间复杂度分析

代码规范性问题目录：
1. 变量或函数名不清晰：轻微 (Negligible)
2. 不必要的语句：轻微 (Negligible)
3. 过多重复内容，代码冗余过多：小错误 (Small)
4. 其他错误：小错误 (Small)

代码效率问题目录：
1. 程序时间复杂度过高：重大错误 (Major)
2. 程序空间复杂度过高：重大错误 (Major)
3. 无终止的程序执行：致命错误 (Fatal)
4. 其他错误：小错误 (Small)

问题：
{problem_description}

代码：
{code}

测试结果：
{test_results}

评估输出（JSON格式）：
```json
{
  "code_standard": {
    "pros": ["优点1", "优点2", ...],
    "cons": ["缺点1", "缺点2", ...]
  },
  "code_efficiency": {
    "pros": ["优点1", "优点2", ...],
    "cons": ["缺点1", "缺点2", ...]
  },
  "inconsistencies": [
    {"type": "问题类型", "description": "问题描述", "severity": "严重程度"}
  ],
  "summary": "总结评价",
  "suggestions": ["建议1", "建议2", ...],
  "status": "AC/WA/TLE/MLE/RE/CE之一"
}
```
"""
