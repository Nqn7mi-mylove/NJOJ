from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class Language(str, Enum):
    CPP = "cpp"
    # More languages to be added later

class JudgeStatus(str, Enum):
    PENDING = "pending"
    JUDGING = "judging"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"
    SYSTEM_ERROR = "system_error"

class TestCaseResult(BaseModel):
    test_case_id: str
    status: JudgeStatus
    time_used: int = 0  # ms
    memory_used: int = 0  # KB
    error_message: Optional[str] = None
    output: Optional[str] = None

class Submission(BaseModel):
    id: Optional[str] = None
    problem_id: str
    user_id: str
    code: str
    language: Language
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    status: JudgeStatus = JudgeStatus.PENDING
    time_used: int = 0  # ms (maximum of all test cases)
    memory_used: int = 0  # KB (maximum of all test cases)
    error_message: Optional[str] = None
    test_case_results: List[TestCaseResult] = []
    llm_evaluation: Optional[Dict[str, Any]] = None  # Store LLM evaluation results
    
    class Config:
        schema_extra = {
            "example": {
                "problem_id": "problem123",
                "user_id": "user456",
                "code": "#include <iostream>\nusing namespace std;\n\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}",
                "language": "cpp",
                "status": "pending"
            }
        }
