"""Improvement suggestions prompt template for LLM code evaluation."""

IMPROVEMENT_PROMPT = """
基于前面的错误分析和测试结果，给出具体的改进建议。

问题：
{problem_description}

学生代码：
{code}

测试结果：
{test_results}

错误分析：
{analysis}

请根据错误分析和测试结果，提供具体的改进建议，帮助学生修复代码中的问题。
特别注意：
- 如果测试结果为AC，则关注代码规范问题，提供代码风格和可读性的改进建议
- 如果测试结果为WA，则重点提供修复逻辑错误的建议
- 如果测试结果为TLE，则重点提供优化算法效率的建议
- 如果测试结果为MLE，则重点提供减少内存使用的建议
- 如果测试结果为RE，则重点提供修复运行时错误的建议
- 如果测试结果为CE，则重点提供修复编译错误的建议

输出JSON格式的改进建议：
```json
{
  "code_standard": [
    "代码规范建议1",
    "代码规范建议2",
    ...
  ],
  "improvement_suggestions": [
    "具体的修改建议1，针对代码中的问题提供明确的改进方法",
    "具体的修改建议2，可以包含代码示例或算法优化思路",
    ...
  ],
  "summary": "总结评价"
}
```
"""
