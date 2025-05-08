from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.models.problem import DifficultyLevel, TestCase

# Base Problem Schema
class ProblemBase(BaseModel):
    title: str
    description: str
    difficulty: DifficultyLevel
    tags: List[str] = []
    time_limit: int = 1000  # ms
    memory_limit: int = 256  # MB
    is_public: bool = True
    has_special_judge: bool = False

# Schema for creating a problem
class ProblemCreate(ProblemBase):
    custom_id: Optional[str] = None  # 用户自定义的问题ID，例如 "P1001"
    test_cases: List[TestCase] = []
    sample_test_cases: List[TestCase] = []
    special_judge_code: Optional[str] = None

# Schema for updating a problem
class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    tags: Optional[List[str]] = None
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    is_public: Optional[bool] = None
    has_special_judge: Optional[bool] = None
    test_cases: Optional[List[TestCase]] = None
    sample_test_cases: Optional[List[TestCase]] = None
    special_judge_code: Optional[str] = None

# Schema for problem response
class Problem(ProblemBase):
    id: str
    custom_id: Optional[str] = None  # 用户自定义的问题ID
    created_at: datetime
    updated_at: datetime
    author_id: str
    submission_count: int = 0
    accepted_count: int = 0
    sample_test_cases: List[TestCase] = []

    class Config:
        schema_extra = {
            "example": {
                "id": "60d21b4967d0d8992e610c85",
                "title": "Two Sum",
                "description": "# Two Sum\n\nGiven an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\n## Example\n\nInput: nums = [2,7,11,15], target = 9\nOutput: [0,1]\nExplanation: Because nums[0] + nums[1] == 9, we return [0, 1].",
                "difficulty": "easy",
                "tags": ["array", "hash-table"],
                "time_limit": 1000,
                "memory_limit": 256,
                "is_public": True,
                "has_special_judge": False,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "author_id": "60d21b4967d0d8992e610c86",
                "submission_count": 100,
                "accepted_count": 75,
                "sample_test_cases": [
                    {
                        "input": "[2,7,11,15]\n9",
                        "output": "[0,1]",
                        "is_sample": True
                    }
                ]
            }
        }
