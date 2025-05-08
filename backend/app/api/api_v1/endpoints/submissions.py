from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from bson.objectid import ObjectId
from datetime import datetime

from app.db.mongodb import db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.schemas.submission import Submission, SubmissionCreate, SubmissionList
from app.models.submission import JudgeStatus
from app.judge.judge_service import judge_submission

router = APIRouter()

@router.post("/", response_model=Submission)
async def create_submission(
    submission_in: SubmissionCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Submit code for a problem.
    """
    submissions_collection = db.db.submissions
    problems_collection = db.db.problems
    
    # Check if problem exists
    problem = await problems_collection.find_one({
        "_id": ObjectId(submission_in.problem_id),
        "$or": [
            {"is_public": True},
            {"author_id": current_user["id"]}
        ]
    })
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found or access denied"
        )
    
    submission_dict = submission_in.dict()
    submission_dict["user_id"] = current_user["id"]
    submission_dict["submitted_at"] = datetime.utcnow()
    submission_dict["status"] = JudgeStatus.PENDING
    submission_dict["time_used"] = 0
    submission_dict["memory_used"] = 0
    submission_dict["test_case_results"] = []
    
    result = await submissions_collection.insert_one(submission_dict)
    submission_id = result.inserted_id
    
    # Add background task for judging
    background_tasks.add_task(
        judge_submission, 
        str(submission_id), 
        str(problem["_id"]),
        current_user["id"]
    )
    
    # Increment submission count
    await problems_collection.update_one(
        {"_id": ObjectId(submission_in.problem_id)},
        {"$inc": {"submission_count": 1}}
    )
    
    created_submission = await submissions_collection.find_one({"_id": submission_id})
    created_submission["id"] = str(created_submission.pop("_id"))
    
    return created_submission

@router.get("/{submission_id}", response_model=Submission)
async def read_submission(
    submission_id: str,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific submission by id.
    """
    submissions_collection = db.db.submissions
    
    # Regular users can only view their own submissions
    # Admin users can view all submissions
    query = {"_id": ObjectId(submission_id)}
    if current_user.get("role") != "admin":
        query["user_id"] = current_user["id"]
    
    submission = await submissions_collection.find_one(query)
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or access denied"
        )
    
    submission["id"] = str(submission.pop("_id"))
    return submission

@router.get("/", response_model=List[SubmissionList])
async def read_submissions(
    skip: int = 0,
    limit: int = 100,
    problem_id: Optional[str] = None,
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve submissions with optional filtering.
    """
    submissions_collection = db.db.submissions
    
    # Build query filters
    query = {}
    
    # Regular users can only view their own submissions
    # Admin users can view all submissions or filter by user_id
    if current_user.get("role") != "admin":
        query["user_id"] = current_user["id"]
    elif user_id:
        query["user_id"] = user_id
    
    if problem_id:
        query["problem_id"] = problem_id
    
    if status:
        query["status"] = status
    
    # Execute query
    cursor = submissions_collection.find(query).sort("submitted_at", -1).skip(skip).limit(limit)
    submissions = await cursor.to_list(length=limit)
    
    # Convert MongoDB _id to string
    for submission in submissions:
        submission["id"] = str(submission.pop("_id"))
    
    return submissions
