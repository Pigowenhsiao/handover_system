from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.base import Base


class LanguageResource(Base):
    """
    語言資源模型 - 存儲多語言翻譯內容
    """
    __tablename__ = "language_resources"

    id = Column(Integer, primary_key=True, index=True)
    language_code = Column(String(10), nullable=False)  # 例如: "zh", "ja", "en"
    resource_key = Column(String(255), nullable=False)  # 翻譯鍵，例如: "header.title", "button.save"
    resource_value = Column(Text, nullable=False)       # 翻譯值
    namespace = Column(String(100), default='common')   # 命名空間，例如: "common", "validation"
    
    # 記錄創建和更新時間
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # 記錄最後更新的用戶（可選）
    updated_by = Column(Integer, ForeignKey("users.id"))  # 關聯到用戶表
    updated_by_user = relationship("User", back_populates="language_resources")


class LanguageSetting(Base):
    """
    語言設置模型 - 存儲用戶或系統的語言偏好
    """
    __tablename__ = "language_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 可選，NULL 表示系統範圍設置
    language_code = Column(String(10), nullable=False)                # 例如: "zh", "ja", "en"
    is_default = Column(Boolean, default=False)                       # 是否為默認語言
    is_active = Column(Boolean, default=True)                         # 該語言是否啟用
    
    # 記錄創建和更新時間
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # 與用戶關係
    user = relationship("User", back_populates="language_settings")


class LanguagePack(Base):
    """
    語言包模型 - 管理完整的語言包
    """
    __tablename__ = "language_packs"

    id = Column(Integer, primary_key=True, index=True)
    language_code = Column(String(10), nullable=False)      # 例如: "zh", "ja", "en"
    pack_name = Column(String(100), nullable=False)         # 語言包名稱，例如: "Chinese Pack"
    version = Column(String(20), default="1.0.0")           # 語言包版本
    is_active = Column(Boolean, default=True)               # 該語言包是否啟用
    
    # 記錄創建和更新時間
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # 與語言資源的關係
    resources = relationship("LanguageResource", back_populates="language_pack")


# 更新 LanguageResource 模型，添加與 LanguagePack 的關係
LanguageResource.language_pack = relationship("LanguagePack", back_populates="resources")