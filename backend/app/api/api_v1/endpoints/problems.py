from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from bson.objectid import ObjectId
from datetime import datetime

from app.db.mongodb import db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.schemas.problem import Problem, ProblemCreate, ProblemUpdate

router = APIRouter()

@router.post("/", response_model=Problem)
async def create_problem(
    problem_in: ProblemCreate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Create new problem. Only admin users can access this endpoint.
    """
    problems_collection = db.db.problems
    
    # 检查自定义ID是否已存在
    existing_problem = await problems_collection.find_one({"custom_id": problem_in.custom_id})
    if existing_problem:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Problem with custom ID '{problem_in.custom_id}' already exists"
        )
    
    problem_dict = problem_in.dict()
    problem_dict["author_id"] = current_user["id"]
    problem_dict["created_at"] = datetime.utcnow()
    problem_dict["updated_at"] = datetime.utcnow()
    problem_dict["submission_count"] = 0
    problem_dict["accepted_count"] = 0
    
    result = await problems_collection.insert_one(problem_dict)
    
    created_problem = await problems_collection.find_one({"_id": result.inserted_id})
    created_problem["id"] = str(created_problem.pop("_id"))
    
    return created_problem

@router.put("/{problem_id}", response_model=Problem)
async def update_problem(
    problem_id: str,
    problem_in: ProblemUpdate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Update a problem. Only admin users can access this endpoint.
    """
    problems_collection = db.db.problems
    
    problem = await problems_collection.find_one({"_id": ObjectId(problem_id)})
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    
    update_data = problem_in.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # 如果提供了自定义ID，检查是否已存在
    if "custom_id" in update_data and update_data["custom_id"]:
        existing = await problems_collection.find_one({
            "custom_id": update_data["custom_id"],
            "_id": {"$ne": ObjectId(problem_id)}
        })
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Problem with custom ID '{update_data['custom_id']}' already exists"
            )
    
    # 特殊处理test_cases，确保正确更新数组
    if "test_cases" in update_data and update_data["test_cases"]:
        # MongoDB $set操作可能无法正确处理嵌套数组，使用$set + $unset的组合操作
        
        # 首先将原有的test_cases数组删除
        await problems_collection.update_one(
            {"_id": ObjectId(problem_id)},
            {"$unset": {"test_cases": ""}}
        )
    
    # 执行更新    
    await problems_collection.update_one(
        {"_id": ObjectId(problem_id)},
        {"$set": update_data}
    )
    
    updated_problem = await problems_collection.find_one({"_id": ObjectId(problem_id)})
    updated_problem["id"] = str(updated_problem.pop("_id"))
    
    return updated_problem

@router.get("/{problem_id}", response_model=Problem)
async def read_problem(
    problem_id: str,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific problem by id or custom_id.
    """
    problems_collection = db.db.problems
    
    # 尝试先使用自定义ID查询
    problem = await problems_collection.find_one({
        "custom_id": problem_id,
        "$or": [
            {"is_public": True},
            {"author_id": current_user["id"]}
        ]
    })
    
    # 如果没有找到，尝试使用系统内部ID查询
    if not problem:
        try:
            problem = await problems_collection.find_one({
                "_id": ObjectId(problem_id),
                "$or": [
                    {"is_public": True},
                    {"author_id": current_user["id"]}
                ]
            })
        except:
            # 如果传入的ID不是一个有效的ObjectId
            pass
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found or access denied"
        )
    
    problem["id"] = str(problem.pop("_id"))
    return problem

@router.get("/", response_model=List[Problem])
async def read_problems(
    skip: int = 0,
    limit: int = 100,
    difficulty: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve problems with optional filtering.
    """
    problems_collection = db.db.problems
    
    # Build query filters
    query = {"is_public": True}
    
    if difficulty:
        query["difficulty"] = difficulty
    
    if tags:
        query["tags"] = {"$all": tags}
    
    # Execute query
    cursor = problems_collection.find(query).skip(skip).limit(limit)
    problems = await cursor.to_list(length=limit)
    
    # Convert MongoDB _id to string
    for problem in problems:
        problem["id"] = str(problem.pop("_id"))
    
    return problems

@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: str,
    current_user = Depends(get_current_admin_user)
) -> None:
    """
    Delete a problem. Only admin users can access this endpoint.
    """
    problems_collection = db.db.problems
    
    problem = await problems_collection.find_one({"_id": ObjectId(problem_id)})
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    
    await problems_collection.delete_one({"_id": ObjectId(problem_id)})
