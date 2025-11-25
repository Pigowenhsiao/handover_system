"""
語言資源 API 端點實現
"""
import hashlib
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.database.base import get_db
from backend.models.languages import LanguageResource
from backend.schemas.language import LanguageResourceResponse, LanguageResourceCreate, LanguageResourceUpdate, LanguageResourcesResponse
from backend.api.languages.base import router as base_router, validate_language_code, get_language_resource_by_key
from backend.api.deps import get_current_user
from backend.models.user import User
from backend.utils.lang_error_handler import LanguageErrorHandler


# 簡單的內存緩存實現（在實際應用中應使用 Redis 等）
# 格式: {cache_key: (data, expire_time)}
cache = {}
CACHE_TIMEOUT = timedelta(minutes=30)  # 30分鐘緩存


def get_cache_key(lang: str, namespace: str) -> str:
    """生成緩存鍵"""
    return f"lang_resources:{lang}:{namespace}"


def get_cached_resources(lang: str, namespace: str):
    """從緩存獲取資源"""
    cache_key = get_cache_key(lang, namespace)
    cached_item = cache.get(cache_key)

    if cached_item:
        data, expire_time = cached_item
        if datetime.now() < expire_time:
            print(f"從緩存獲取語言資源: {lang}/{namespace}")
            return data
        else:
            # 緩存已過期，刪除它
            del cache[cache_key]

    return None


def set_cached_resources(lang: str, namespace: str, data):
    """設置緩存資源"""
    cache_key = get_cache_key(lang, namespace)
    expire_time = datetime.now() + CACHE_TIMEOUT
    cache[cache_key] = (data, expire_time)
    print(f"緩存語言資源: {lang}/{namespace}, 有效期至 {expire_time}")


def invalidate_cache(lang: str, namespace: str):
    """使緩存失效"""
    cache_key = get_cache_key(lang, namespace)
    if cache_key in cache:
        del cache[cache_key]
        print(f"緩存已失效: {lang}/{namespace}")


router = APIRouter()


@router.get("/resources", response_model=LanguageResourcesResponse)
def get_language_resources(
    lang: str = Query(..., description="語言代碼，例如: zh, ja, en"),
    namespace: str = Query("common", description="命名空間，默認為 'common'"),
    db: Session = Depends(get_db)
):
    """
    獲取指定語言和命名空間的翻譯資源（帶緩存）
    """
    # 驗證語言代碼
    if not validate_language_code(lang):
        raise HTTPException(
            status_code=400,
            detail=f"不支援的語言代碼: {lang}，支援的語言: zh, ja, en"
        )

    # 首先嘗試從緩存獲取
    cached_result = get_cached_resources(lang, namespace)
    if cached_result:
        return LanguageResourcesResponse(
            lang=lang,
            namespace=namespace,
            resources=cached_result
        )

    # 如果緩存中沒有，則從數據庫查詢
    try:
        resources_db = db.query(LanguageResource).filter(
            LanguageResource.language_code == lang,
            LanguageResource.namespace == namespace
        ).all()

        # 將查詢結果轉換為字典格式
        resources_dict = {}
        for resource in resources_db:
            # 處理嵌套鍵（用點號分隔）
            keys = resource.resource_key.split('.')
            current_dict = resources_dict

            # 遞歸構建嵌套字典結構
            for key in keys[:-1]:
                if key not in current_dict:
                    current_dict[key] = {}
                current_dict = current_dict[key]

            # 設置最終值
            current_dict[keys[-1]] = resource.resource_value

        # 將結果存入緩存
        set_cached_resources(lang, namespace, resources_dict)

        return LanguageResourcesResponse(
            lang=lang,
            namespace=namespace,
            resources=resources_dict
        )
    except Exception as e:
        LanguageErrorHandler.log_language_error(
            error_type="DATABASE_QUERY_ERROR",
            error_message=f"查詢語言資源時發生錯誤: {str(e)}",
            language_code=lang,
            resource_key=f"namespace:{namespace}",
            additional_info={"namespace": namespace}
        )
        raise HTTPException(
            status_code=500,
            detail="查詢語言資源時發生服務器錯誤"
        )


@router.get("/resources/{resource_id}", response_model=LanguageResourceResponse)
def get_language_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """
    獲取單個翻譯資源
    """
    resource = db.query(LanguageResource).filter(
        LanguageResource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="翻譯資源不存在"
        )

    return resource


@router.post("/resources", response_model=LanguageResourceResponse, dependencies=[Depends(get_current_user)])
def create_language_resource(
    resource: LanguageResourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    創建新的翻譯資源 (僅管理員)
    """
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
        updated_by=current_user.id
    )

    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)

    # 使相關緩存失效
    invalidate_cache(resource.language_code, resource.namespace)

    return db_resource


@router.put("/resources/{resource_id}", response_model=LanguageResourceResponse, dependencies=[Depends(get_current_user)])
def update_language_resource(
    resource_id: int,
    resource_update: LanguageResourceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新翻譯資源 (僅管理員)
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

    # 保存原始的語言代碼和命名空間，以便後續清除緩存
    original_lang = db_resource.language_code
    original_namespace = db_resource.namespace

    # 更新資源屬性
    if resource_update.resource_value is not None:
        db_resource.resource_value = resource_update.resource_value
    if resource_update.namespace is not None:
        db_resource.namespace = resource_update.namespace

    # 更新最後修改用戶
    db_resource.updated_by = current_user.id

    db.commit()
    db.refresh(db_resource)

    # 使相關緩存失效
    invalidate_cache(original_lang, original_namespace)

    # 如果命名空間發生變化，也需要清除新命名空間的緩存
    if resource_update.namespace and resource_update.namespace != original_namespace:
        invalidate_cache(original_lang, resource_update.namespace)

    return db_resource


@router.delete("/resources/{resource_id}", dependencies=[Depends(get_current_user)])
def delete_language_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """
    刪除翻譯資源 (僅管理員)
    """
    resource = db.query(LanguageResource).filter(
        LanguageResource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="翻譯資源不存在"
        )

    # 保存語言代碼和命名空間，以便清除緩存
    lang_code = resource.language_code
    namespace = resource.namespace

    db.delete(resource)
    db.commit()

    # 使相關緩存失效
    invalidate_cache(lang_code, namespace)

    return {"message": "翻譯資源已成功刪除"}


# 將語言資源路由加入基礎路由
base_router.include_router(router)