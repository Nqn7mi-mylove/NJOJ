from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class TestCase(BaseModel):
    input: str
    output: str
    is_sample: bool = False
    
class Problem(BaseModel):
    id: Optional[str] = None
    title: str
    description: str  # Markdown content
    difficulty: DifficultyLevel
    tags: List[str] = []
    time_limit: int = 1000  # ms
    memory_limit: int = 256  # MB
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    author_id: str
    is_public: bool = True
    test_cases: List[TestCase] = []
    sample_test_cases: List[TestCase] = []
    has_special_judge: bool = False
    special_judge_code: Optional[str] = None
    submission_count: int = 0
    accepted_count: int = 0
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Two Sum",
                "description": "# Two Sum\n\nGiven an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\n## Example\n\nInput: nums = [2,7,11,15], target = 9\nOutput: [0,1]\nExplanation: Because nums[0] + nums[1] == 9, we return [0, 1].",
                "difficulty": "easy",
                "tags": ["array", "hash-table"],
                "time_limit": 1000,
                "memory_limit": 256,
                "is_public": True,
                "has_special_judge": False
            }
        }
