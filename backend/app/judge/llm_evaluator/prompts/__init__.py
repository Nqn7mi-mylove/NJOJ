"""Prompt templates for LLM-based code evaluation.

This package contains various prompt templates used for different stages of code evaluation.
"""

from .error_analysis import ERROR_ANALYSIS_PROMPT
from .improvement import IMPROVEMENT_PROMPT

__all__ = ["ERROR_ANALYSIS_PROMPT", "IMPROVEMENT_PROMPT"]
