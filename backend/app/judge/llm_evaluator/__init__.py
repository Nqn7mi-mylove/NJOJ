"""LLM-based code evaluator for the Online Judge system.

This package integrates LLM-based code evaluation to provide detailed feedback
on code quality, efficiency, and correctness beyond test case results.
Implementation uses LangChain framework for more reliable LLM interactions.
"""

from .core import llm_evaluator, LLMEvaluator
from .models import (
    ErrorDetail, 
    ErrorAnalysis, 
    CodeQualityAssessment,
    Inconsistency, 
    ImprovementSuggestion, 
    EvaluationResult
)
from .config import llm_config

__all__ = [
    # Main evaluator instance and class
    "llm_evaluator", 
    "LLMEvaluator",
    
    # Models
    "ErrorDetail",
    "ErrorAnalysis", 
    "CodeQualityAssessment",
    "Inconsistency", 
    "ImprovementSuggestion", 
    "EvaluationResult",
    
    # Config
    "llm_config"
]
