"""
後端多語言 API 整合測試
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app  # 假設 FastAPI 應用實例在 main.py 中
from backend.database.base import Base
from backend.models.languages import LanguageResource, LanguageSetting, LanguagePack
from backend.database.init_lang_tables import init_default_language_settings


# 設置測試數據庫
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def client():
    """創建測試客戶端"""
    Base.metadata.create_all(bind=engine)
    
    # 初始化默認語言設置
    init_default_language_settings(engine)
    
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def db_session(client):
    """為每個測試創建新的數據庫會話"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


class TestLanguageResourcesAPI:
    """測試語言資源相關 API 端點"""
    
    def test_get_language_resources(self, client, db_session):
        """測試獲取語言資源"""
        # 添加測試數據
        resource = LanguageResource(
            language_code="ja",
            resource_key="test.key",
            resource_value="テスト値",
            namespace="test"
        )
        db_session.add(resource)
        db_session.commit()
        
        # 發送請求
        response = client.get("/api/languages/resources?lang=ja&namespace=test")
        
        # 驗證響應
        assert response.status_code == 200
        data = response.json()
        assert data["lang"] == "ja"
        assert data["namespace"] == "test"
        assert "test" in data["resources"]
        assert data["resources"]["test"]["key"] == "テスト値"
    
    def test_get_language_resources_invalid_language(self, client):
        """測試無效語言代碼"""
        response = client.get("/api/languages/resources?lang=invalid&namespace=common")
        assert response.status_code == 400  # 應該返回 400 錯誤
    
    def test_create_language_resource(self, client, db_session):
        """測試創建語言資源（需要管理員權限）"""
        # 由於此端點需要管理員權限，我們測試訪問被拒絕
        new_resource = {
            "language_code": "ja",
            "resource_key": "new.key",
            "resource_value": "新しい値",
            "namespace": "test"
        }
        response = client.post("/api/languages/resources", json=new_resource)
        
        # 應該返回 401（未授權）或 403（禁止訪問）
        assert response.status_code in [401, 403]
    
    def test_update_language_resource(self, client, db_session):
        """測試更新語言資源（需要管理員權限）"""
        # 首先添加一個測試資源
        resource = LanguageResource(
            language_code="zh",
            resource_key="update.test",
            resource_value="原始值",
            namespace="test"
        )
        db_session.add(resource)
        db_session.commit()
        
        # 嘗試更新（需要管理員權限）
        update_data = {
            "resource_value": "更新值",
            "namespace": "updated_test"
        }
        response = client.put(f"/api/languages/resources/{resource.id}", json=update_data)
        
        # 應該返回 401（未授權）或 403（禁止訪問）
        assert response.status_code in [401, 403]


class TestLanguageSettingsAPI:
    """測試語言設置相關 API 端點"""
    
    def test_get_language_settings(self, client):
        """測試獲取語言設置（需要用戶權限）"""
        response = client.get("/api/languages/settings")
        
        # 應該返回 401（未授權）因為需要用戶身份
        assert response.status_code == 401
    
    def test_get_available_languages(self, client):
        """測試獲取可用語言"""
        response = client.get("/api/languages/settings/available")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # 應該至少包含我們支持的三種語言
        language_codes = [item["language_code"] for item in data]
        assert "ja" in language_codes
        assert "en" in language_codes
        assert "zh" in language_codes


class TestAdminLanguageAPI:
    """測試管理員語言 API 端點"""
    
    def test_admin_get_resources_without_auth(self, client):
        """測試未授權訪問管理員端點"""
        response = client.get("/api/admin/languages/resources")
        # 應該返回 401（未授權）或 403（禁止訪問）
        assert response.status_code in [401, 403]
    
    def test_admin_create_pack_without_auth(self, client):
        """測試未授權創建語言包"""
        new_pack = {
            "language_code": "ko",
            "pack_name": "Korean Pack",
            "version": "1.0.0",
            "is_active": True
        }
        response = client.post("/api/admin/languages/packs", json=new_pack)
        # 應該返回 401（未授權）或 403（禁止訪問）
        assert response.status_code in [401, 403]


class TestLanguageValidation:
    """測試語言驗證功能"""
    
    @pytest.mark.parametrize("valid_code", ["zh", "ja", "en"])
    def test_valid_language_codes(self, client, valid_code):
        """測試有效語言代碼"""
        # 使用有效語言代碼請求資源
        response = client.get(f"/api/languages/resources?lang={valid_code}&namespace=common")
        # 有效語言代碼會得到 200 或 401（如果需要身份驗證）
        assert response.status_code in [200, 401]
    
    @pytest.mark.parametrize("invalid_code", ["xx", "fr", "de", "ko", ""])  
    def test_invalid_language_codes(self, client, invalid_code):
        """測試無效語言代碼"""
        if invalid_code == "":
            # 空字符串可能導致不同類型的錯誤
            response = client.get("/api/languages/resources?lang=&namespace=common")
        else:
            response = client.get(f"/api/languages/resources?lang={invalid_code}&namespace=common")
        
        # 無效語言代碼應該返回 400 錯誤
        assert response.status_code == 400