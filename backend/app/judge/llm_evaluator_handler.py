"""LLM Evaluator Handler Module.

This module serves as an interface between the Online Judge system and the
LLM-based code evaluator, handling the evaluation requests and formatting the responses.
"""

from typing import Dict, List, Any, Optional
from app.judge.llm_evaluator import llm_evaluator


async def evaluate_submission(
    code: str,
    problem_description: str,
    test_results: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Evaluate a submission using the LLM evaluator.
    
    Args:
        code: The submitted code
        problem_description: The problem description
        test_results: Optional test results
        
    Returns:
        Dict[str, Any]: The evaluation results
    """
    try:
        # Call the LLM evaluator
        evaluation_result = await llm_evaluator.evaluate_code(
            code=code,
            problem_description=problem_description,
            test_results=test_results
        )
        
        return evaluation_result
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # Return error response
        return {
            "error": f"评估失败: {str(e)}",
            "summary": "评估过程中发生错误",
            "code_standard": {"pros": [], "cons": []},
            "code_logic": {"pros": [], "cons": []},
            "code_efficiency": {"pros": [], "cons": []},
            "improvement_suggestions": ["评估服务暂时不可用，请稍后再试"],
            "overall_score": "0"
        }
