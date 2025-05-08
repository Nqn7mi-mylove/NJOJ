from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class SystemConfig(BaseModel):
    """系统配置模型，用于存储全局设置"""
    id: Optional[str] = None
    allow_signup: bool = True  # 是否允许注册
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    class Config:
        schema_extra = {
            "example": {
                "allow_signup": True,
            }
        }
