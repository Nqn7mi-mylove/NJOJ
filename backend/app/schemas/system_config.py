from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# 基础系统配置Schema
class SystemConfigBase(BaseModel):
    allow_signup: bool = True

# 创建系统配置的Schema
class SystemConfigCreate(SystemConfigBase):
    pass

# 更新系统配置的Schema
class SystemConfigUpdate(BaseModel):
    allow_signup: Optional[bool] = None

# 系统配置响应Schema
class SystemConfig(SystemConfigBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "6071b7a45c6bc2314500e6a7",
                "allow_signup": True,
                "created_at": "2025-04-10T15:30:00",
                "updated_at": "2025-04-10T15:30:00"
            }
        }
