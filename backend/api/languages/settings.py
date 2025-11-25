"""
語言設置 API 端點實現
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from backend.database.base import get_db
from backend.models.languages import LanguageSetting, LanguagePack
from backend.schemas.language import LanguageSettingResponse, LanguageSettingUpdate
from backend.api.languages.base import router as base_router
from backend.api.deps import get_current_user
from backend.models.user import User


router = APIRouter()


@router.get("/settings", response_model=LanguageSettingResponse)
def get_language_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    獲取當前用戶的語言設置
    """
    # 查找用戶的語言設置
    user_lang_setting = db.query(LanguageSetting).filter(
        LanguageSetting.user_id == current_user.id
    ).first()
    
    # 如果用戶沒有個人語言設置，則返回系統默認設置
    if not user_lang_setting:
        user_lang_setting = db.query(LanguageSetting).filter(
            LanguageSetting.user_id.is_(None),  # 系統範圍設置
            LanguageSetting.is_default == True
        ).first()
    
    if not user_lang_setting:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系統默認語言設置缺失"
        )
    
    return user_lang_setting


@router.get("/settings/available", response_model=List[LanguageSettingResponse])
def get_available_languages(
    db: Session = Depends(get_db)
):
    """
    獲取所有可用的語言設置
    """
    # 查找所有啟用的語言包
    active_packs = db.query(LanguagePack).filter(
        LanguagePack.is_active == True
    ).all()
    
    # 返回對應的語言設置
    available_lang_settings = []
    for pack in active_packs:
        lang_setting = LanguageSetting(
            id=0,  # 僅返回語言信息，不包含具體的用戶關聯設置
            user_id=None,
            language_code=pack.language_code,
            is_default=False,
            is_active=True,
            created_at=pack.created_at,
            updated_at=pack.updated_at
        )
        
        # 檢查是否為系統默認語言
        default_setting = db.query(LanguageSetting).filter(
            LanguageSetting.user_id.is_(None),  # 系統範圍設置
            LanguageSetting.is_default == True,
            LanguageSetting.language_code == pack.language_code
        ).first()
        
        if default_setting:
            lang_setting.is_default = True
            
        available_lang_settings.append(lang_setting)
    
    return available_lang_settings


@router.put("/settings", response_model=LanguageSettingResponse)
def update_language_settings(
    lang_setting_update: LanguageSettingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新當前用戶的語言設置
    """
    # 驗證語言代碼
    if lang_setting_update.language_code:
        from backend.api.languages.base import validate_language_code
        if not validate_language_code(lang_setting_update.language_code):
            raise HTTPException(
                status_code=400,
                detail=f"不支援的語言代碼: {lang_setting_update.language_code}，支援的語言: zh, ja, en"
            )
    
    # 查找現有的用戶語言設置
    existing_setting = db.query(LanguageSetting).filter(
        LanguageSetting.user_id == current_user.id
    ).first()
    
    if existing_setting:
        # 更新現有設置
        if lang_setting_update.language_code is not None:
            existing_setting.language_code = lang_setting_update.language_code
        if lang_setting_update.is_default is not None:
            existing_setting.is_default = lang_setting_update.is_default
        if lang_setting_update.is_active is not None:
            existing_setting.is_active = lang_setting_update.is_active
    else:
        # 創建新的用戶語言設置
        existing_setting = LanguageSetting(
            user_id=current_user.id,
            language_code=lang_setting_update.language_code or "ja",  # 默認為日文
            is_default=lang_setting_update.is_default or False,
            is_active=lang_setting_update.is_active or True
        )
        db.add(existing_setting)
    
    db.commit()
    db.refresh(existing_setting)
    
    return existing_setting


# 將語言設置路由加入基礎路由
base_router.include_router(router)