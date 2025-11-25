"""
語言相關錯誤處理和日誌記錄機制
"""
import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


# 設置語言相關的日誌記錄器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 創建文件處理器
file_handler = logging.FileHandler('logs/language_errors.log')
file_handler.setLevel(logging.WARNING)

# 創建控制台處理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 設置格式器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加處理器到記錄器
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class LanguageErrorHandler:
    """語言相關錯誤處理類"""
    
    @staticmethod
    def log_language_error(
        error_type: str, 
        error_message: str, 
        language_code: Optional[str] = None, 
        resource_key: Optional[str] = None,
        user_id: Optional[int] = None,
        additional_info: Optional[dict] = None
    ):
        """
        記錄語言相關錯誤
        
        Args:
            error_type: 錯誤類型
            error_message: 錯誤消息
            language_code: 語言代碼
            resource_key: 資源鍵
            user_id: 用戶ID
            additional_info: 額外信息
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "language_code": language_code,
            "resource_key": resource_key,
            "user_id": user_id,
            "additional_info": additional_info or {}
        }
        
        # 結構化日誌記錄
        logger.error(f"語言錯誤 - {error_type}: {error_message}", extra=log_data)
    
    @staticmethod
    def log_missing_translation(
        language_code: str, 
        resource_key: str, 
        namespace: str = "common",
        user_id: Optional[int] = None
    ):
        """
        記錄缺失的翻譯
        
        Args:
            language_code: 語言代碼
            resource_key: 資源鍵
            namespace: 命名空間
            user_id: 用戶ID
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "language_code": language_code,
            "resource_key": resource_key,
            "namespace": namespace,
            "user_id": user_id
        }
        
        logger.warning(f"缺失翻譯 - 語言: {language_code}, 鍵: {resource_key}", extra=log_data)
    
    @staticmethod
    def validate_language_code(language_code: str) -> bool:
        """
        驗證語言代碼是否支援
        
        Args:
            language_code: 要驗證的語言代碼
            
        Returns:
            bool: 是否支援該語言代碼
        """
        supported_languages = {"zh", "ja", "en"}
        is_valid = language_code in supported_languages
        
        if not is_valid:
            LanguageErrorHandler.log_language_error(
                error_type="INVALID_LANGUAGE_CODE",
                error_message=f"不支援的語言代碼: {language_code}",
                language_code=language_code
            )
        
        return is_valid
    
    @staticmethod
    def handle_language_resource_error(
        request: Request,
        db: Session,
        resource_id: int,
        error: Exception
    ) -> JSONResponse:
        """
        處理語言資源相關錯誤
        
        Args:
            request: HTTP請求對象
            db: 數據庫會話
            resource_id: 資源ID
            error: 發生的錯誤
            
        Returns:
            JSONResponse: 錯誤響應
        """
        from backend.models.languages import LanguageResource
        
        # 獲取資源信息以記錄詳細錯誤
        resource = db.query(LanguageResource).filter(
            LanguageResource.id == resource_id
        ).first()
        
        log_data = {
            "resource_id": resource_id,
            "resource_info": {
                "language_code": resource.language_code if resource else None,
                "resource_key": resource.resource_key if resource else None,
                "namespace": resource.namespace if resource else None
            } if resource else None,
            "error_type": type(error).__name__,
            "request_method": request.method,
            "request_url": str(request.url),
            "user_agent": request.headers.get("user-agent", "Unknown")
        }
        
        logger.error(f"語言資源錯誤 - ID: {resource_id}, 錯誤: {str(error)}", extra=log_data)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "處理語言資源時發生錯誤",
                "resource_id": resource_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def handle_language_not_found(
        language_code: str,
        additional_info: Optional[dict] = None
    ) -> HTTPException:
        """
        處理語言未找到錯誤
        
        Args:
            language_code: 語言代碼
            additional_info: 額外信息
            
        Returns:
            HTTPException: HTTP異常
        """
        LanguageErrorHandler.log_language_error(
            error_type="LANGUAGE_NOT_FOUND",
            error_message=f"請求的語言不存在: {language_code}",
            language_code=language_code,
            additional_info=additional_info
        )
        
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"語言 [{language_code}] 不存在"
        )
    
    @staticmethod
    def handle_resource_not_found(
        resource_key: str,
        language_code: str,
        namespace: str = "common"
    ) -> HTTPException:
        """
        處理資源未找到錯誤
        
        Args:
            resource_key: 資源鍵
            language_code: 語言代碼
            namespace: 命名空間
            
        Returns:
            HTTPException: HTTP異常
        """
        LanguageErrorHandler.log_language_error(
            error_type="RESOURCE_NOT_FOUND",
            error_message=f"語言資源不存在 - 語言: {language_code}, 鍵: {resource_key}, 命名空間: {namespace}",
            language_code=language_code,
            resource_key=resource_key,
            additional_info={"namespace": namespace}
        )
        
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"語言資源不存在: {resource_key} [{language_code}]"
        )


# 設置日誌目錄（如果不存在）
import os
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)