"""
初始化語言資源相關數據庫表的腳本
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.base import Base
from backend.models.languages import LanguageResource, LanguageSetting, LanguagePack
from backend.config import settings


def init_language_tables():
    """
    初始化語言資源相關的數據庫表
    """
    # 創建數據庫引擎
    engine = create_engine(settings.DATABASE_URL)
    
    # 創建所有語言資源相關的表
    Base.metadata.create_all(bind=engine)
    
    print("語言資源相關數據庫表已創建完成")
    
    # 初始化默認語言設置
    init_default_language_settings(engine)
    

def init_default_language_settings(engine):
    """
    初始化默認語言設置
    """
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 檢查是否已存在默認語言設置
        default_setting = db.query(LanguageSetting).filter(LanguageSetting.is_default == True).first()
        
        if not default_setting:
            # 創建默認為日文的系統語言設置
            default_lang_setting = LanguageSetting(
                user_id=None,  # 系統範圍設置
                language_code="ja",  # 默認為日文
                is_default=True,
                is_active=True
            )
            db.add(default_lang_setting)
            db.commit()
            print("默認語言設置已創建 (日文)")
        
        # 檢查是否已存在語言包
        ja_pack = db.query(LanguagePack).filter(LanguagePack.language_code == "ja").first()
        en_pack = db.query(LanguagePack).filter(LanguagePack.language_code == "en").first()
        zh_pack = db.query(LanguagePack).filter(LanguagePack.language_code == "zh").first()
        
        # 如果不存在，則創建默認語言包記錄
        if not ja_pack:
            ja_pack = LanguagePack(
                language_code="ja",
                pack_name="Japanese Pack",
                version="1.0.0",
                is_active=True
            )
            db.add(ja_pack)
        
        if not en_pack:
            en_pack = LanguagePack(
                language_code="en",
                pack_name="English Pack",
                version="1.0.0",
                is_active=True
            )
            db.add(en_pack)
            
        if not zh_pack:
            zh_pack = LanguagePack(
                language_code="zh",
                pack_name="Chinese Pack",
                version="1.0.0",
                is_active=True
            )
            db.add(zh_pack)
        
        db.commit()
        print("默認語言包記錄已創建")
        
    except Exception as e:
        db.rollback()
        print(f"初始化默認語言設置時出錯: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    init_language_tables()