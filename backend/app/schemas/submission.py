from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.models.submission import Language, JudgeStatus, TestCaseResult

# Base Submission Schema
class SubmissionBase(BaseModel):
    problem_id: str
    code: str
    language: Language

# Schema for creating a submission
class SubmissionCreate(SubmissionBase):
    pass

# Schema for submission response
class Submission(SubmissionBase):
    id: str
    user_id: str
    submitted_at: datetime
    status: JudgeStatus
    time_used: int = 0  # ms
    memory_used: int = 0  # KB
    error_message: Optional[str] = None
    test_case_results: List[TestCaseResult] = []
    llm_evaluation: Optional[Dict[str, Any]] = None  # LLM-based code evaluation results

    class Config:
        schema_extra = {
            "example": {
                "id": "60d21b4967d0d8992e610c87",
                "problem_id": "60d21b4967d0d8992e610c85",
                "user_id": "60d21b4967d0d8992e610c86",
                "code": "#include <iostream>\nusing namespace std;\n\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}",
                "language": "cpp",
                "submitted_at": "2023-01-01T00:00:00",
                "status": "accepted",
                "time_used": 5,
                "memory_used": 1024,
                "error_message": None,
                "test_case_results": [
                    {
                        "test_case_id": "tc1",
                        "status": "accepted",
                        "time_used": 5,
                        "memory_used": 1024,
                        "error_message": None,
                        "output": "3"
                    }
                ],
                "llm_evaluation": {
                    "code_standard": {
                        "pros": ["Clear variable naming", "Good code structure"],
                        "cons": ["Missing comments"]
                    },
                    "code_logic": {
                        "pros": ["Correct algorithm", "Handles edge cases well"],
                        "cons": []
                    },
                    "code_efficiency": {
                        "pros": ["Optimal time complexity"],
                        "cons": ["Could improve memory usage"]
                    },
                    "error_types": [],
                    "improvement_suggestions": ["Add more comments to explain the logic"],
                    "overall_score": "90",
                    "summary": "Well-written solution with good structure and logic."
                }
            }
        }

# Schema for listing submissions
class SubmissionList(BaseModel):
    id: str
    problem_id: str
    user_id: str
    language: Language
    submitted_at: datetime
    status: JudgeStatus
    time_used: int = 0
    memory_used: int = 0

    class Config:
        schema_extra = {
            "example": {
                "id": "60d21b4967d0d8992e610c87",
                "problem_id": "60d21b4967d0d8992e610c85",
                "user_id": "60d21b4967d0d8992e610c86",
                "language": "cpp",
                "submitted_at": "2023-01-01T00:00:00",
                "status": "accepted",
                "time_used": 5,
                "memory_used": 1024
            }
        }
