"""
密碼變更對話框
提供安全的密碼變更介面
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加後端路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    from backend.utils.password_validator import password_validator
except ImportError:
    # 如果無法導入，提供本地備份
    class LocalPasswordValidator:
        @staticmethod
        def validate_strength(password):
            if len(password) < 6:
                return False, ["密碼至少需要 6 個字元"]
            return True, []
        
        @staticmethod
        def get_strength_score(password):
            return 50, "medium", "密碼強度中等"
        
        @staticmethod
        def generate_suggestions(password):
            return []
    
    password_validator = LocalPasswordValidator()


class PasswordChangeDialog:
    """密碼變更對話框"""
    
    def __init__(self, parent, lang_manager, current_username, on_password_changed=None):
        """
        初始化密碼變更對話框
        
        Args:
            parent: 父視窗
            lang_manager: 語言管理器
            current_username: 當前使用者名稱
            on_password_changed: 密碼變更成功後的回調函數
        """
        self.parent = parent
        self.lang_manager = lang_manager
        self.current_username = current_username
        self.on_password_changed = on_password_changed
        
        self.window = tk.Toplevel(parent)
        self.window.title(self.lang_manager.get_text("password.change_title", "變更密碼"))
        self.window.geometry("450x500")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(False, False)
        
        self.setup_ui()
        self.update_language()
    
    def setup_ui(self):
        """設置介面元素"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # 使用者名稱顯示
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(username_frame, text=self.lang_manager.get_text("common.username", "使用者名稱:") + " ").pack(side="left")
        ttk.Label(username_frame, text=self.current_username, font=("TkDefaultFont", 10, "bold")).pack(side="left")
        
        # 當前密碼
        ttk.Label(main_frame, text=self.lang_manager.get_text("password.current", "當前密碼:") + " *").pack(anchor="w", pady=(10, 2))
        self.current_password_var = tk.StringVar()
        current_entry = ttk.Entry(main_frame, textvariable=self.current_password_var, show="*", width=40)
        current_entry.pack(fill="x", pady=(0, 10))
        current_entry.focus()
        
        # 新密碼
        ttk.Label(main_frame, text=self.lang_manager.get_text("password.new", "新密碼:") + " *").pack(anchor="w", pady=(10, 2))
        self.new_password_var = tk.StringVar()
        new_entry = ttk.Entry(main_frame, textvariable=self.new_password_var, show="*", width=40)
        new_entry.pack(fill="x", pady=(0, 5))
        
        # 顯示/隱藏新密碼按鈕
        show_new_btn = ttk.Checkbutton(
            main_frame,
            text=self.lang_manager.get_text("password.show", "顯示密碼"),
            command=self.toggle_new_password_visibility
        )
        show_new_btn.pack(anchor="w")
        
        # 新密碼強度指示
        self.strength_frame = ttk.Frame(main_frame)
        self.strength_frame.pack(fill="x", pady=(5, 10))
        
        self.strength_label = ttk.Label(self.strength_frame, text="")
        self.strength_label.pack(side="left")
        
        self.strength_bar = ttk.Progressbar(self.strength_frame, length=100, mode='determinate')
        self.strength_bar.pack(side="right", padx=(10, 0))
        
        # 確認新密碼
        ttk.Label(main_frame, text=self.lang_manager.get_text("password.confirm", "確認新密碼:") + " *").pack(anchor="w", pady=(10, 2))
        self.confirm_password_var = tk.StringVar()
        confirm_entry = ttk.Entry(main_frame, textvariable=self.confirm_password_var, show="*", width=40)
        confirm_entry.pack(fill="x", pady=(0, 5))
        
        show_confirm_btn = ttk.Checkbutton(
            main_frame,
            text=self.lang_manager.get_text("password.show", "顯示密碼"),
            command=self.toggle_confirm_password_visibility
        )
        show_confirm_btn.pack(anchor="w")
        
        # 密碼要求說明
        ttk.Label(main_frame, text=self.lang_manager.get_text("password.requirements", "密碼要求:"), font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(15, 5))
        
        requirements = [
            "• " + self.lang_manager.get_text("password.req_length", "至少 8 個字元"),
            "• " + self.lang_manager.get_text("password.req_uppercase", "包含大寫字母"),
            "• " + self.lang_manager.get_text("password.req_lowercase", "包含小寫字母"),
            "• " + self.lang_manager.get_text("password.req_number", "包含數字"),
            "• " + self.lang_manager.get_text("password.req_special", "包含特殊字元 (!@#$%^&*(),.?:{}|<>)"),
        ]
        
        for req in requirements:
            ttk.Label(main_frame, text=req, font=("TkDefaultFont", 9)).pack(anchor="w", padx=(10, 0))
        
        # 建議文字區域
        self.suggestions_frame = ttk.Frame(main_frame)
        self.suggestions_frame.pack(fill="x", pady=(10, 0))
        
        # 按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(
            button_frame,
            text=self.lang_manager.get_text("common.cancel", "取消"),
            command=self.window.destroy
        ).pack(side="right", padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text=self.lang_manager.get_text("password.change", "變更密碼"),
            command=self.change_password,
            style="Accent.TButton"
        ).pack(side="right")
        
        # 綁定密碼變更事件
        new_entry.bind("<KeyRelease>", self.update_password_strength)
        
        # 設定按鈕樣式
        try:
            style = ttk.Style()
            style.configure("Accent.TButton", font=("TkDefaultFont", 10, "bold"))
        except:
            pass
    
    def update_language(self):
        """更新語言"""
        self.window.title(self.lang_manager.get_text("password.change_title", "變更密碼"))
        # 其他語言更新將在需要時實施
    
    def toggle_new_password_visibility(self):
        """切換新密碼顯示/隱藏"""
        # 這個方法需要存取 new_entry，需要重構
        pass
    
    def toggle_confirm_password_visibility(self):
        """切換確認密碼顯示/隱藏"""
        pass
    
    def update_password_strength(self, event=None):
        """更新密碼強度顯示"""
        password = self.new_password_var.get()
        
        if not password:
            self.strength_label.config(text="")
            self.strength_bar['value'] = 0
            return
        
        score, level, desc = password_validator.get_strength_score(password)
        
        # 更新進度條
        self.strength_bar['value'] = score
        
        # 根據強度設定顏色
        colors = {
            "weak": "red",
            "medium": "orange",
            "strong": "green",
            "very_strong": "darkgreen"
        }
        
        color = colors.get(level, "black")
        
        # 獲取語言對應的強度文字
        level_texts = {
            "weak": self.lang_manager.get_text("password.strength_weak", "弱"),
            "medium": self.lang_manager.get_text("password.strength_medium", "中等"),
            "strong": self.lang_manager.get_text("password.strength_strong", "強"),
            "very_strong": self.lang_manager.get_text("password.strength_very_strong", "非常強")
        }
        
        level_text = level_texts.get(level, level)
        
        self.strength_label.config(
            text=f"{self.lang_manager.get_text('password.strength', '密碼強度')}: {level_text}",
            foreground=color
        )
        
        # 顯示建議
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        
        if level in ["weak", "medium"]:
            suggestions = password_validator.generate_suggestions(password)
            if suggestions:
                ttk.Label(self.suggestions_frame, text=self.lang_manager.get_text("password.suggestions", "建議:"), font=("TkDefaultFont", 9, "bold")).pack(anchor="w", pady=(5, 2))
                for suggestion in suggestions:
                    ttk.Label(self.suggestions_frame, text=f"• {suggestion}", font=("TkDefaultFont", 8), foreground="gray").pack(anchor="w", padx=(10, 0))
    
    def change_password(self):
        """執行密碼變更"""
        current_password = self.current_password_var.get()
        new_password = self.new_password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        # 驗證輸入
        if not current_password:
            messagebox.showerror("錯誤", self.lang_manager.get_text("password.error_current_required", "請輸入當前密碼"))
            return
        
        if not new_password:
            messagebox.showerror("錯誤", self.lang_manager.get_text("password.error_new_required", "請輸入新密碼"))
            return
        
        if not confirm_password:
            messagebox.showerror("錯誤", self.lang_manager.get_text("password.error_confirm_required", "請確認新密碼"))
            return
        
        if new_password != confirm_password:
            messagebox.showerror("錯誤", self.lang_manager.get_text("password.error_mismatch", "新密碼與確認密碼不符"))
            return
        
        if new_password == current_password:
            messagebox.showerror("錯誤", self.lang_manager.get_text("password.error_same", "新密碼不能與當前密碼相同"))
            return
        
        # 驗證密碼強度
        is_valid, errors = password_validator.validate_strength(new_password)
        if not is_valid:
            error_msg = "\n".join(errors)
            messagebox.showerror("密碼強度不足", f"{self.lang_manager.get_text('password.error_strength', '新密碼不符合安全要求:')}\n\n{error_msg}")
            return
        
        # 這裡應該呼叫後端 API 來變更密碼
        # 為了示例，我們只顯示成功訊息
        # TODO: 實際實施時需要連接到後端 API
        
        if messagebox.showinfo(
            "成功",
            self.lang_manager.get_text("password.success", "密碼變更成功！"),
            icon="info"
        ):
            if self.on_password_changed:
                self.on_password_changed()
            self.window.destroy()


# 測試函數
def test_password_dialog():
    """測試密碼變更對話框"""
    root = tk.Tk()
    root.withdraw()
    
    # 模擬語言管理器
    class MockLangManager:
        def get_text(self, key, default):
            return default
        def get_current_language(self):
            return "zh"
    
    dialog = PasswordChangeDialog(root, MockLangManager(), "test_user")
    root.mainloop()


if __name__ == "__main__":
    test_password_dialog()
