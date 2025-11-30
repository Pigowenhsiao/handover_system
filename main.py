"""
電子交接本系統 - 前端桌面應用程式啟動腳本
"""
import tkinter as tk
from frontend.main import MainApplication


def main():
    """主函數"""
    root = tk.Tk()
    app = MainApplication(root)
    
    # 設置窗口關閉事件
    def on_closing():
        if tk.messagebox.askokcancel(
            app.lang_manager.get_text("common.quit", "退出"),
            app.lang_manager.get_text("common.confirmQuit", "確定要退出電子交接系統嗎？")
        ):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()


if __name__ == "__main__":
    main()