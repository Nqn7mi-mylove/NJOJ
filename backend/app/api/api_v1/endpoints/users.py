from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from bson.objectid import ObjectId

from app.db.mongodb import db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()

@router.get("/me", response_model=User)
async def read_user_me(current_user = Depends(get_current_active_user)) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Update own user.
    """
    users_collection = db.db.users
    user_id = ObjectId(current_user["id"])
    
    update_data = user_in.dict(exclude_unset=True)
    
    if "password" in update_data:
        from app.core.security import get_password_hash
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    
    updated_user = await users_collection.find_one({"_id": user_id})
    updated_user["id"] = str(updated_user["_id"])
    return updated_user

@router.get("/{user_id}", response_model=User)
async def read_user_by_id(
    user_id: str,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific user by id.
    """
    users_collection = db.db.users
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["id"] = str(user["_id"])
    return user

@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Retrieve users. Only admin users can access this endpoint.
    """
    from fastapi import Response
    
    users_collection = db.db.users
    
    # 获取用户总数
    total_count = await users_collection.count_documents({})
    
    cursor = users_collection.find().skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    
    # Convert MongoDB _id to string
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]  # 删除_id字段，因为已经复制到id字段
    
    # 设置响应头并返回用户列表
    response = Response()
    response.headers["X-Total-Count"] = str(total_count)
    return users
