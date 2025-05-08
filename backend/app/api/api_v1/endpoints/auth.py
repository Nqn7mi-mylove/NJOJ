from datetime import timedelta, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from bson.objectid import ObjectId

from app.db.mongodb import db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings
from app.schemas.token import Token
from app.schemas.user import UserCreate

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    users_collection = db.db.users
    user = await users_collection.find_one({"username": form_data.username})
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user["_id"], expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=Token)
async def create_user_signup(user_in: UserCreate) -> Any:
    """
    Create new user without the need to be logged in.
    """
    # 检查系统是否允许注册
    configs_collection = db.db.system_configs
    config = await configs_collection.find_one({"_id": "system_config"})
    
    # 如果存在系统配置且禁止注册，则抛出异常
    if config and not config.get("allow_signup", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User registration is currently disabled"
        )
    
    users_collection = db.db.users
    
    existing_user = await users_collection.find_one({"username": user_in.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    existing_email = await users_collection.find_one({"email": user_in.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user_data = user_in.dict(exclude={"password"})
    user_data["hashed_password"] = get_password_hash(user_in.password)
    
    # Add timestamps
    current_time = datetime.utcnow()
    user_data["created_at"] = current_time
    user_data["updated_at"] = current_time
    user_data["solved_problems"] = []  # Initialize with empty list
    
    result = await users_collection.insert_one(user_data)
    user_id = result.inserted_id
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user_id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
