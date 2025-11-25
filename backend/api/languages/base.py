"""
語言資源 API 基礎結構
定義語言資源相關端點的基礎結構和通用功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session

from backend.database.base import get_db
from backend.models.languages import LanguageResource, LanguageSetting
from backend.schemas.language import (
    LanguageResourceResponse, 
    LanguageResourceCreate, 
    LanguageResourceUpdate,
    LanguageSettingResponse,
    LanguageSettingUpdate
)
from backend.api.deps import get_current_user
from backend.models.user import User


router = APIRouter(prefix="/languages", tags=["languages"])


def validate_language_code(language_code: str) -> bool:
    """
    驗證語言代碼是否為系統支援的語言
    """
    supported_languages = {"zh", "ja", "en"}
    return language_code in supported_languages


def get_language_resource_by_key(db: Session, language_code: str, resource_key: str, namespace: str = "common"):
    """
    根據語言代碼、資源鍵和命名空間獲取語言資源
    """
    return db.query(LanguageResource).filter(
        LanguageResource.language_code == language_code,
        LanguageResource.resource_key == resource_key,
        LanguageResource.namespace == namespace
    ).first()


def ensure_resource_exists(db: Session, resource_id: int) -> LanguageResource:
    """
    確保資源存在，如果不存在則拋出異常
    """
    resource = db.query(LanguageResource).filter(LanguageResource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="語言資源不存在"
        )
    return resource