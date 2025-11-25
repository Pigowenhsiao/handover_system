"""
語言資源相關的 Pydantic 模型定義
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 語言資源相關模型
class LanguageResourceBase(BaseModel):
    language_code: str
    resource_key: str
    resource_value: str
    namespace: Optional[str] = "common"


class LanguageResourceCreate(LanguageResourceBase):
    pass


class LanguageResourceUpdate(BaseModel):
    resource_value: Optional[str] = None
    namespace: Optional[str] = None


class LanguageResourceResponse(LanguageResourceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# 語言設置相關模型
class LanguageSettingBase(BaseModel):
    language_code: str
    is_default: bool = False
    is_active: bool = True


class LanguageSettingUpdate(BaseModel):
    language_code: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class LanguageSettingResponse(LanguageSettingBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 語言包相關模型
class LanguagePackBase(BaseModel):
    language_code: str
    pack_name: str
    version: Optional[str] = "1.0.0"
    is_active: bool = True


class LanguagePackResponse(LanguagePackBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 多語言資源響應模型
class LanguageResourcesResponse(BaseModel):
    lang: str
    namespace: str
    resources: dict

    class Config:
        from_attributes = True