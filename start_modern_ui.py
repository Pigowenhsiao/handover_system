#!/usr/bin/env python3
"""
電子交接系統 - 現代化介面啟動腳本
使用全新的 Material Design 風格介面
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
    """主函數"""
    # 創建主視窗
    root = tk.Tk()
    root.title("電子交接系統 v2.0 - 現代化介面")
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
    print("🚀 電子交接系統現代化介面已啟動")
    print("📌 窗口尺寸: 1300x800")
    print("📌 默認語言: 中文")
    print("💡 提示: 使用左側導航欄切換功能頁面")
    
    root.mainloop()


if __name__ == "__main__":
    main()
