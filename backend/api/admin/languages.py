"""
管理員語言資源管理 API 端點
實現語言資源和語言包的完整管理功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.database.base import get_db
from backend.models.languages import LanguageResource, LanguagePack
from backend.schemas.language import (
    LanguageResourceResponse,
    LanguageResourceCreate,
    LanguageResourceUpdate,
    LanguagePackResponse
)
from backend.api.deps import get_current_admin
from backend.models.user import User


router = APIRouter(prefix="/admin/languages", tags=["admin", "languages"])


# 語言資源管理端點
@router.get("/resources", response_model=List[LanguageResourceResponse])
def get_all_language_resources(
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(100, ge=1, le=1000, description="返回的最大項目數"),
    search: Optional[str] = Query(None, description="搜索資源鍵或值"),
    language_code: Optional[str] = Query(None, description="過濾特定語言代碼"),
    namespace: Optional[str] = Query(None, description="過濾特定命名空間"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    獲取所有語言資源（分頁、搜索和過濾）
    """
    query = db.query(LanguageResource)

    # 應用搜索過濾
    if search:
        query = query.filter(
            or_(
                LanguageResource.resource_key.contains(search),
                LanguageResource.resource_value.contains(search)
            )
        )

    # 應用語言代碼過濾
    if language_code:
        query = query.filter(LanguageResource.language_code == language_code)

    # 應用命名空間過濾
    if namespace:
        query = query.filter(LanguageResource.namespace == namespace)

    # 應用分頁
    resources = query.offset(skip).limit(limit).all()
    return resources


@router.post("/resources", response_model=LanguageResourceResponse)
def create_language_resource(
    resource: LanguageResourceCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    創建新的語言資源
    """
    from backend.api.languages.base import validate_language_code

    # 驗證語言代碼
    if not validate_language_code(resource.language_code):
        raise HTTPException(
            status_code=400,
            detail=f"不支援的語言代碼: {resource.language_code}，支援的語言: zh, ja, en"
        )

    # 檢查是否已存在相同的資源鍵
    existing_resource = db.query(LanguageResource).filter(
        LanguageResource.language_code == resource.language_code,
        LanguageResource.resource_key == resource.resource_key,
        LanguageResource.namespace == resource.namespace
    ).first()

    if existing_resource:
        raise HTTPException(
            status_code=400,
            detail="相同語言、鍵和命名空間的翻譯資源已存在"
        )

    # 創建新的翻譯資源
    db_resource = LanguageResource(
        language_code=resource.language_code,
        resource_key=resource.resource_key,
        resource_value=resource.resource_value,
        namespace=resource.namespace,
        updated_by=current_admin.id
    )

    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)

    return db_resource


@router.put("/resources/{resource_id}", response_model=LanguageResourceResponse)
def update_language_resource(
    resource_id: int,
    resource_update: LanguageResourceUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新翻譯資源
    """
    # 獲取現有資源
    db_resource = db.query(LanguageResource).filter(
        LanguageResource.id == resource_id
    ).first()

    if not db_resource:
        raise HTTPException(
            status_code=404,
            detail="翻譯資源不存在"
        )

    # 更新資源屬性
    if resource_update.resource_value is not None:
        db_resource.resource_value = resource_update.resource_value
    if resource_update.namespace is not None:
        db_resource.namespace = resource_update.namespace

    # 更新最後修改用戶
    db_resource.updated_by = current_admin.id

    db.commit()
    db.refresh(db_resource)

    return db_resource


@router.delete("/resources/{resource_id}")
def delete_language_resource(
    resource_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    刪除翻譯資源
    """
    resource = db.query(LanguageResource).filter(
        LanguageResource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="翻譯資源不存在"
        )

    db.delete(resource)
    db.commit()

    return {"message": "翻譯資源已成功刪除"}


@router.get("/resources/bulk", response_model=List[LanguageResourceResponse])
def get_language_resources_bulk(
    language_code: str = Query(..., description="語言代碼"),
    namespace: str = Query("common", description="命名空間"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    批量獲取語言資源
    """
    from backend.api.languages.base import validate_language_code

    # 驗證語言代碼
    if not validate_language_code(language_code):
        raise HTTPException(
            status_code=400,
            detail=f"不支援的語言代碼: {language_code}，支援的語言: zh, ja, en"
        )

    # 批量獲取語言資源
    resources = db.query(LanguageResource).filter(
        LanguageResource.language_code == language_code,
        LanguageResource.namespace == namespace
    ).all()

    return resources


@router.post("/resources/bulk")
def create_language_resources_bulk(
    resources: List[LanguageResourceCreate],
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    批量創建語言資源
    """
    from backend.api.languages.base import validate_language_code

    created_resources = []
    errors = []

    for resource in resources:
        # 驗證語言代碼
        if not validate_language_code(resource.language_code):
            errors.append({
                "resource": resource,
                "error": f"不支援的語言代碼: {resource.language_code}"
            })
            continue

        # 檢查是否已存在相同的資源鍵
        existing_resource = db.query(LanguageResource).filter(
            LanguageResource.language_code == resource.language_code,
            LanguageResource.resource_key == resource.resource_key,
            LanguageResource.namespace == resource.namespace
        ).first()

        if existing_resource:
            errors.append({
                "resource": resource,
                "error": "相同語言、鍵和命名空間的翻譯資源已存在"
            })
            continue

        # 創建新的翻譯資源
        db_resource = LanguageResource(
            language_code=resource.language_code,
            resource_key=resource.resource_key,
            resource_value=resource.resource_value,
            namespace=resource.namespace,
            updated_by=current_admin.id
        )

        db.add(db_resource)
        created_resources.append(db_resource)

    if created_resources:
        db.commit()
        # 刷新創建的資源以獲取ID
        for resource in created_resources:
            db.refresh(resource)

    return {
        "created_count": len(created_resources),
        "error_count": len(errors),
        "created_resources": created_resources,
        "errors": errors
    }


# 語言包管理端點
@router.get("/packs", response_model=List[LanguagePackResponse])
def get_all_language_packs(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    獲取所有語言包
    """
    packs = db.query(LanguagePack).all()
    return packs


@router.post("/packs", response_model=LanguagePackResponse)
def create_language_pack(
    pack: "LanguagePackBase",  # 使用 Pydantic 模型
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    創建語言包
    """
    from backend.api.languages.base import validate_language_code
    from backend.schemas.language import LanguagePackBase

    # 驗證語言代碼
    if not validate_language_code(pack.language_code):
        raise HTTPException(
            status_code=400,
            detail=f"不支援的語言代碼: {pack.language_code}，支援的語言: zh, ja, en"
        )

    # 檢查語言包是否已存在
    existing_pack = db.query(LanguagePack).filter(
        LanguagePack.language_code == pack.language_code
    ).first()

    if existing_pack:
        raise HTTPException(
            status_code=400,
            detail="語言包已存在"
        )

    # 創建語言包
    db_pack = LanguagePack(
        language_code=pack.language_code,
        pack_name=pack.pack_name,
        version=pack.version,
        is_active=pack.is_active
    )

    db.add(db_pack)
    db.commit()
    db.refresh(db_pack)

    return db_pack


@router.put("/packs/{pack_id}", response_model=LanguagePackResponse)
def update_language_pack(
    pack_id: int,
    pack_update: "LanguagePackUpdate",  # 使用 Pydantic 模型
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新語言包
    """
    from backend.schemas.language import LanguagePackUpdate

    # 獲取現有語言包
    db_pack = db.query(LanguagePack).filter(
        LanguagePack.id == pack_id
    ).first()

    if not db_pack:
        raise HTTPException(
            status_code=404,
            detail="語言包不存在"
        )

    # 更新語言包屬性
    if pack_update.pack_name is not None:
        db_pack.pack_name = pack_update.pack_name
    if pack_update.version is not None:
        db_pack.version = pack_update.version
    if pack_update.is_active is not None:
        db_pack.is_active = pack_update.is_active

    db.commit()
    db.refresh(db_pack)

    return db_pack


@router.delete("/packs/{pack_id}")
def delete_language_pack(
    pack_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    刪除語言包
    """
    pack = db.query(LanguagePack).filter(
        LanguagePack.id == pack_id
    ).first()

    if not pack:
        raise HTTPException(
            status_code=404,
            detail="語言包不存在"
        )

    db.delete(pack)
    db.commit()

    return {"message": "語言包已成功刪除"}