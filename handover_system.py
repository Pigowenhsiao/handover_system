#!/usr/bin/env python3
"""
電子引き継ぎシステム - モダン版ランチャー
修正・最適化・モダンUIを含む
"""

import sys
import os
from pathlib import Path

# 設置項目根目錄
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

def check_dependencies():
    """依存パッケージを確認"""
    print("🔍 依存パッケージを確認中...")
    
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
        print(f"\n⚠️  次のパッケージが不足しています: {', '.join(missing)}")
        print("実行してください: pip install -r requirements.txt")
        return False
    
    print("   ✅ 必要な依存パッケージはすべてインストール済みです\n")
    return True


def initialize_database():
    """データベースを初期化"""
    print("🗄️  データベースを初期化中...")
    
    try:
        from models import init_db
        init_db()
        print("   ✅ データベースの初期化に成功しました\n")
        return True
    except Exception as e:
        print(f"   ❌ データベース初期化に失敗しました: {e}\n")
        return False


def start_modern_ui():
    """モダンUIを起動"""
    print("🚀 モダンUIを起動中...")
    
    try:
        import tkinter as tk
        from frontend.src.components.modern_main_frame import ModernMainFrame
        from frontend.main import LanguageManager
        
        # 創建主視窗
        root = tk.Tk()
        root.title("電子交接系統 V 0.1.4")
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
        
        print("   ✅ モダンUIの起動に成功しました\n")
        print("=" * 70)
        print("💡 システム利用のヒント:")
        print("   • 左側のナビゲーションで機能ページを切り替え")
        print("   • 上部の言語セレクターで言語を切り替え（日本語/中文/English）")
        print("   • すべてのフォームはカード型デザイン")
        print("   • 操作結果はリアルタイムに表示")
        print("   • 管理者はユーザーのパスワードをリセット可能")
        print("   • パスワード強度チェックに対応")
        print("=" * 70)
        print()
        
        # 啟動主循環
        root.mainloop()
        
    except Exception as e:
        print(f"   ❌ 啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def prompt_continue(message, default=True):
    if sys.stdin is None or not sys.stdin.isatty():
        fallback = "y" if default else "n"
        print(f"{message} [自動回覆: {fallback}]")
        return default
    response = input(message)
    return response.strip().lower() == 'y'


def main():
    """メイン関数"""
    print("=" * 70)
    print("電子引き継ぎシステム - モダン版 V 0.1.4")
    print("=" * 70)
    print()
    
    # 檢查依賴
    if not check_dependencies():
        if not prompt_continue("続行して起動しますか? (y/n): ", default=True):
            sys.exit(0)
    
    # 初始化資料庫
    if not initialize_database():
        if not prompt_continue("データベース初期化に失敗しました。続行しますか? (y/n): ", default=True):
            sys.exit(0)
    
    # 啟動現代化 UI
    start_modern_ui()


if __name__ == "__main__":
    main()
