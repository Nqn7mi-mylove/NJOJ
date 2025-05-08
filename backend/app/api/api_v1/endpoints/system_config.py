from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from bson.objectid import ObjectId

from app.db.mongodb import db
from app.api.deps import get_current_admin_user
from app.schemas.system_config import SystemConfig, SystemConfigUpdate

router = APIRouter()

# 系统配置的唯一ID，因为我们只需要一个系统配置记录
CONFIG_ID = "system_config"

@router.get("/", response_model=SystemConfig)
async def get_system_config() -> Any:
    """
    获取系统配置
    """
    configs_collection = db.db.system_configs
    
    # 尝试获取系统配置，如果不存在则创建默认配置
    config = await configs_collection.find_one({"_id": CONFIG_ID})
    
    if not config:
        # 创建默认配置
        default_config = {
            "_id": CONFIG_ID,
            "allow_signup": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await configs_collection.insert_one(default_config)
        config = default_config
    
    # 将_id转换为id以符合Schema
    config["id"] = config.pop("_id")
    
    return config

@router.put("/", response_model=SystemConfig)
async def update_system_config(
    config_in: SystemConfigUpdate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    更新系统配置（仅管理员可用）
    """
    configs_collection = db.db.system_configs
    
    # 将输入数据转换为字典，排除空值
    update_data = {k: v for k, v in config_in.dict(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    # 添加更新时间
    update_data["updated_at"] = datetime.utcnow()
    
    # 查找系统配置是否存在
    config = await configs_collection.find_one({"_id": CONFIG_ID})
    
    if not config:
        # 如果不存在，创建一个带有默认值的新配置
        default_config = {
            "_id": CONFIG_ID,
            "allow_signup": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        # 更新默认配置
        default_config.update(update_data)
        await configs_collection.insert_one(default_config)
        config = default_config
    else:
        # 更新现有配置
        await configs_collection.update_one(
            {"_id": CONFIG_ID},
            {"$set": update_data}
        )
        config = await configs_collection.find_one({"_id": CONFIG_ID})
    
    # 将_id转换为id以符合Schema
    config["id"] = config.pop("_id")
    
    return config
