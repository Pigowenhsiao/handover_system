"""
後端架構模組
包含所有 Pydantic 架構定義
"""

# Token 架構
from backend.schemas.token import Token, TokenData

# 從 base.py 匯入所有主要架構
# base.py 包含了系統中所有的 Pydantic 模型
from backend.schemas.base import (
    # 使用者相關
    UserRole,
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDBBase,
    User,
    
    # Token 相關
    Token as BaseToken,
    TokenData as BaseTokenData,
    
    # 日報表相關
    ShiftType,
    AreaType,
    DailyReportBase,
    DailyReportCreate,
    DailyReportUpdate,
    DailyReportInDBBase,
    DailyReport,
    
    # 出勤記錄相關
    AttendanceCategory,
    AttendanceRecordBase,
    AttendanceRecordCreate,
    AttendanceRecordUpdate,
    AttendanceRecordInDBBase,
    AttendanceRecord,
    
    # 設備異常相關
    EquipmentLogBase,
    EquipmentLogCreate,
    EquipmentLogUpdate,
    EquipmentLogInDBBase,
    EquipmentLog,
    
    # 異常批次相關
    LotLogBase,
    LotLogCreate,
    LotLogUpdate,
    LotLogInDBBase,
    LotLog,
    
    # 語言資源相關
    LanguageCode,
    LanguageResourceBase,
    LanguageResourceCreate,
    LanguageResourceUpdate,
    LanguageResource,
    LanguageSettingBase,
    LanguageSettingUpdate,
    LanguageSetting,
)

# 優先使用 token.py 中的 Token 定義（如果有衝突）
# token.py 是專門為 Token 設計的，應該優先使用
Token = Token if 'Token' in dir() else BaseToken
TokenData = TokenData if 'TokenData' in dir() else BaseTokenData

__all__ = [
    # Token
    "Token",
    "TokenData",
    
    # User
    "UserRole",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDBBase",
    "User",
    
    # Daily Report
    "ShiftType",
    "AreaType",
    "DailyReportBase",
    "DailyReportCreate",
    "DailyReportUpdate",
    "DailyReportInDBBase",
    "DailyReport",
    
    # Attendance
    "AttendanceCategory",
    "AttendanceRecordBase",
    "AttendanceRecordCreate",
    "AttendanceRecordUpdate",
    "AttendanceRecordInDBBase",
    "AttendanceRecord",
    
    # Equipment
    "EquipmentLogBase",
    "EquipmentLogCreate",
    "EquipmentLogUpdate",
    "EquipmentLogInDBBase",
    "EquipmentLog",
    
    # Lot
    "LotLogBase",
    "LotLogCreate",
    "LotLogUpdate",
    "LotLogInDBBase",
    "LotLog",
    
    # Language
    "LanguageCode",
    "LanguageResourceBase",
    "LanguageResourceCreate",
    "LanguageResourceUpdate",
    "LanguageResource",
    "LanguageSettingBase",
    "LanguageSettingUpdate",
    "LanguageSetting",
]
