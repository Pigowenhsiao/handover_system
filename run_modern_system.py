#!/usr/bin/env python3
"""
電子交接系統 - 現代化版本啟動器
包含所有修復、優化和現代化 UI
"""

import sys
import os
from pathlib import Path

# 設置項目根目錄
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

def check_dependencies():
    """檢查依賴套件"""
    print("🔍 檢查依賴套件...")
    
    required_packages = [
        "tkinter",
        "sqlalchemy", 
        "pandas",
        "bcrypt",
        "openpyxl",
        "matplotlib",
        "jwt",
        "pydantic"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  缺少以下套件: {', '.join(missing)}")
        print("請執行: pip install -r requirements.txt")
        return False
    
    print("   ✅ 所有依賴套件已安裝\n")
    return True


def initialize_database():
    """初始化資料庫"""
    print("🗄️  初始化資料庫...")
    
    try:
        from models import init_db
        init_db()
        print("   ✅ 資料庫初始化成功\n")
        return True
    except Exception as e:
        print(f"   ❌ 資料庫初始化失敗: {e}\n")
        return False


def start_modern_ui():
    """啟動現代化介面"""
    print("🚀 啟動現代化 UI...")
    
    try:
        import tkinter as tk
        from frontend.src.components.modern_main_frame import ModernMainFrame
        from frontend.main import LanguageManager
        
        # 創建主視窗
        root = tk.Tk()
        root.title("電子交接系統 v2.2")
        root.geometry("1300x800")
        
        # 設置高 DPI 支援
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        # 創建語言管理器
        locales_dir = project_root / "frontend" / "public" / "locales"
        lang_manager = LanguageManager(str(locales_dir))
        
        # 創建現代化主框架
        app = ModernMainFrame(root, lang_manager)
        
        print("   ✅ 現代化 UI 啟動成功\n")
        print("=" * 70)
        print("💡 系統使用提示:")
        print("   • 使用左側導航欄切換功能頁面")
        print("   • 點擊頂部語言選擇器切換語言(日/中/英)")
        print("   • 所有表單採用卡片式設計")
        print("   • 操作有即時狀態回饋")
        print("   • 管理員可重設使用者密碼")
        print("   • 支援密碼強度檢測")
        print("=" * 70)
        print()
        
        # 啟動主循環
        root.mainloop()
        
    except Exception as e:
        print(f"   ❌ 啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函數"""
    print("=" * 70)
    print("電子交接系統 - 現代化版本 v2.2")
    print("=" * 70)
    print()
    
    # 檢查依賴
    if not check_dependencies():
        response = input("是否繼續啟動? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # 初始化資料庫
    if not initialize_database():
        response = input("資料庫初始化失敗，是否繼續? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # 啟動現代化 UI
    start_modern_ui()


if __name__ == "__main__":
    main()
