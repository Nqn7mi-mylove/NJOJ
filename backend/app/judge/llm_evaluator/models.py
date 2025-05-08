"""Data models for LLM-based code evaluation."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail information."""
    
    type: str = Field(..., description="错误类型，如WA/TLE/MLE/RE/CE")
    description: str = Field(..., description="错误的详细描述")
    test_cases: List[str] = Field(default_factory=list, description="相关的测试用例ID列表")


class ErrorAnalysis(BaseModel):
    """Error analysis result."""
    
    error_types: List[str] = Field(default_factory=list, description="错误类型列表")
    explanation: str = Field("", description="错误分析说明")
    error_details: List[ErrorDetail] = Field(default_factory=list, description="详细错误信息")


class CodeQualityAssessment(BaseModel):
    """Code quality assessment with pros and cons."""
    
    pros: List[str] = Field(default_factory=list, description="优点列表")
    cons: List[str] = Field(default_factory=list, description="缺点列表")


class Inconsistency(BaseModel):
    """Code inconsistency data."""
    
    type: str = Field(..., description="问题类型")
    description: str = Field(..., description="问题描述")
    severity: str = Field(..., description="问题严重程度：Negligible/Small/Major/Fatal")


class ImprovementSuggestion(BaseModel):
    """Improvement suggestion model."""
    
    code_standard: Optional[CodeQualityAssessment] = Field(
        default_factory=CodeQualityAssessment, description="代码规范评估"
    )
    code_logic: Optional[CodeQualityAssessment] = Field(
        default_factory=CodeQualityAssessment, description="代码逻辑评估"
    )
    code_efficiency: Optional[CodeQualityAssessment] = Field(
        default_factory=CodeQualityAssessment, description="代码效率评估"
    )
    improvement_suggestions: List[str] = Field(default_factory=list, description="改进建议列表")
    summary: str = Field("", description="总结评价")
    overall_score: str = Field("0", description="总体评分")


class EvaluationResult(BaseModel):
    """Complete evaluation result."""
    
    # Error analysis
    error_types: List[str] = Field(default_factory=list, description="错误类型列表")
    explanation: str = Field("", description="错误分析说明")
    error_details: List[ErrorDetail] = Field(default_factory=list, description="详细错误信息")
    
    # Improvement suggestions
    code_standard: CodeQualityAssessment = Field(
        default_factory=CodeQualityAssessment, description="代码规范评估"
    )
    code_logic: CodeQualityAssessment = Field(
        default_factory=CodeQualityAssessment, description="代码逻辑评估"
    )
    code_efficiency: CodeQualityAssessment = Field(
        default_factory=CodeQualityAssessment, description="代码效率评估"
    )
    inconsistencies: Optional[List[Inconsistency]] = Field(
        default_factory=list, description="代码一致性问题"
    )
    improvement_suggestions: List[str] = Field(default_factory=list, description="改进建议列表")
    summary: str = Field("", description="总结评价")
    overall_score: str = Field("0", description="总体评分")
    
    # Error info
    error: Optional[str] = Field(None, description="评估过程中的错误信息")
    status: Optional[str] = Field(None, description="评估状态：AC/WA/TLE/MLE/RE/CE")
    
    def dict_response(self) -> Dict[str, Any]:
        """Convert to a dictionary for API response."""
        return self.model_dump(exclude_none=True)
