"""
Pydantic 模型定義 - 用於 API 請求/響應驗證
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# 用戶相關架構
class UserRole(str, Enum):
    """用戶角色枚舉"""
    ADMIN = "admin"
    USER = "user"


class UserBase(BaseModel):
    """用戶基礎模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    role: Optional[UserRole] = UserRole.USER
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """創建用戶模型"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """更新用戶模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)


class UserInDBBase(UserBase):
    """數據庫用戶基礎模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class User(UserInDBBase):
    """用戶響應模型"""
    pass


# 認證相關架構
class Token(BaseModel):
    """令牌響應模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌數據模型"""
    username: Optional[str] = None


# 日報表相關架構
class ShiftType(str, Enum):
    """班別類型枚舉"""
    DAY = "Day"
    NIGHT = "Night"


class AreaType(str, Enum):
    """區域類型枚舉"""
    ETCHING_D = "etching_D"
    ETCHING_E = "etching_E"
    LITHO = "litho"
    THIN_FILM = "thin_film"


class DailyReportBase(BaseModel):
    """日報表基礎模型"""
    date: str  # 格式: YYYY-MM-DD
    shift: ShiftType
    area: AreaType
    summary_key_output: Optional[str] = None
    summary_issues: Optional[str] = None
    summary_countermeasures: Optional[str] = None


class DailyReportCreate(DailyReportBase):
    """創建日報表模型"""
    pass


class DailyReportUpdate(BaseModel):
    """更新日報表模型"""
    date: Optional[str] = None
    shift: Optional[ShiftType] = None
    area: Optional[AreaType] = None
    summary_key_output: Optional[str] = None
    summary_issues: Optional[str] = None
    summary_countermeasures: Optional[str] = None


class DailyReportInDBBase(DailyReportBase):
    """數據庫日報表基礎模型"""
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DailyReport(DailyReportInDBBase):
    """日報表響應模型"""
    author: User
    attendance_records: Optional[List["AttendanceRecord"]] = []
    equipment_logs: Optional[List["EquipmentLog"]] = []
    lot_logs: Optional[List["LotLog"]] = []


# 出勤記錄相關架構
class AttendanceCategory(str, Enum):
    """出勤類別枚舉"""
    REGULAR = "Regular"
    CONTRACTOR = "Contractor"


class AttendanceRecordBase(BaseModel):
    """出勤記錄基礎模型"""
    report_id: int
    category: AttendanceCategory
    scheduled_count: int = 0
    present_count: int = 0
    absent_count: int = 0
    reason: Optional[str] = None


class AttendanceRecordCreate(AttendanceRecordBase):
    """創建出勤記錄模型"""
    pass


class AttendanceRecordUpdate(BaseModel):
    """更新出勤記錄模型"""
    category: Optional[AttendanceCategory] = None
    scheduled_count: Optional[int] = None
    present_count: Optional[int] = None
    absent_count: Optional[int] = None
    reason: Optional[str] = None


class AttendanceRecordInDBBase(AttendanceRecordBase):
    """數據庫出勤記錄基礎模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceRecord(AttendanceRecordInDBBase):
    """出勤記錄響應模型"""
    pass


# 設備記錄相關架構
class EquipmentLogBase(BaseModel):
    """設備記錄基礎模型"""
    report_id: int
    equip_id: str
    description: str
    start_time: Optional[str] = None  # 格式: HH:MM
    impact_qty: Optional[int] = 0
    action_taken: Optional[str] = None
    image_path: Optional[str] = None


class EquipmentLogCreate(EquipmentLogBase):
    """創建設備記錄模型"""
    pass


class EquipmentLogUpdate(BaseModel):
    """更新設備記錄模型"""
    equip_id: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    impact_qty: Optional[int] = None
    action_taken: Optional[str] = None
    image_path: Optional[str] = None


class EquipmentLogInDBBase(EquipmentLogBase):
    """數據庫設備記錄基礎模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class EquipmentLog(EquipmentLogInDBBase):
    """設備記錄響應模型"""
    pass


# 批次記錄相關架構
class LotLogBase(BaseModel):
    """批次記錄基礎模型"""
    report_id: int
    lot_id: str
    description: str
    status: Optional[str] = None
    notes: Optional[str] = None


class LotLogCreate(LotLogBase):
    """創建批次記錄模型"""
    pass


class LotLogUpdate(BaseModel):
    """更新批次記錄模型"""
    lot_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class LotLogInDBBase(LotLogBase):
    """數據庫批次記錄基礎模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LotLog(LotLogInDBBase):
    """批次記錄響應模型"""
    pass


# 語言相關架構
class LanguageCode(str, Enum):
    """語言代碼枚舉"""
    JA = "ja"
    ZH = "zh"
    EN = "en"


class LanguageResourceBase(BaseModel):
    """語言資源基礎模型"""
    language_code: LanguageCode
    resource_key: str = Field(..., max_length=255)
    resource_value: str
    namespace: Optional[str] = "common"


class LanguageResourceCreate(LanguageResourceBase):
    """創建語言資源模型"""
    pass


class LanguageResourceUpdate(BaseModel):
    """更新語言資源模型"""
    resource_value: Optional[str] = None
    namespace: Optional[str] = None


class LanguageResource(LanguageResourceBase):
    """語言資源響應模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class LanguageSettingBase(BaseModel):
    """語言設定基礎模型"""
    user_id: Optional[int] = None
    language_code: LanguageCode
    is_default: bool = False
    is_active: bool = True


class LanguageSettingUpdate(BaseModel):
    """更新語言設定模型"""
    language_code: Optional[LanguageCode] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class LanguageSetting(LanguageSettingBase):
    """語言設定響應模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 更新引用模型
from typing import ForwardRef
User.update_forward_refs()
DailyReport.update_forward_refs()