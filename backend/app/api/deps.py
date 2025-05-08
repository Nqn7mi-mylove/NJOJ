from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from bson.objectid import ObjectId
from typing import Generator, Optional

from app.core.config import settings
from app.db.mongodb import db
from app.schemas.token import TokenPayload
from app.models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validate token and return current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenPayload(sub=user_id)
    except JWTError:
        raise credentials_exception
    
    users_collection = db.db.users
    user = await users_collection.find_one({"_id": ObjectId(token_data.sub)})
    
    if user is None:
        raise credentials_exception
    
    # 创建一个新的字典，确保不修改原始用户文档
    user_data = dict(user)
    # 始终确保id字段存在并正确设置（即使它已经存在）
    user_data["id"] = str(user_data["_id"])
    
    return user_data

async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Get current active user
    """
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user = Depends(get_current_active_user)):
    """
    Get current admin user
    """
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
