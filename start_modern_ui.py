#!/usr/bin/env python3
"""
電子引き継ぎシステム - モダンUI起動スクリプト
新しい Material Design 風UIを使用
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk

# 將項目路徑添加到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 導入現代化框架
from frontend.src.components.modern_main_frame import ModernMainFrame
from frontend.main import LanguageManager


def main():
    """メイン関数"""
    # 創建主視窗
    root = tk.Tk()
    root.title("電子引き継ぎシステム V 0.1.4 - モダンUI")
    root.geometry("1300x800")
    
    # 設置窗口圖示（如果有）
    try:
        root.iconbitmap('assets/icon.ico')
    except:
        pass
    
    # 配置主窗口樣式
    style = ttk.Style()
    
    # 創建語言管理器
    locales_dir = project_root / "frontend" / "public" / "locales"
    lang_manager = LanguageManager(str(locales_dir))
    
    # 創建現代化主框架
    modern_frame = ModernMainFrame(root, lang_manager)
    
    # 啟動主循環
    print("🚀 電子引き継ぎシステムのモダンUIを起動しました")
    print("📌 ウィンドウサイズ: 1300x800")
    print("📌 デフォルト言語: 中文")
    print("💡 ヒント: 左側のナビゲーションで機能ページを切り替え")
    
    root.mainloop()


if __name__ == "__main__":
    main()
