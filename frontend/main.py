"""
電子交接本系統 - 輕量級桌面應用程式
實現多語言支持和同時顯示正社員與契約社員出勤記錄功能
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os
import threading
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None


def ensure_requests_installed():
    """若缺 requests，提示使用者安裝並中止當前操作。"""
    if requests is None:
        messagebox.showerror(
            "缺少依賴",
            "未安裝 requests，請先執行：pip install -r requirements.txt"
        )
        return False
    return True


class LoginScreen:
    """登入畫面"""
    def __init__(self, root, lang_manager, on_success):
        self.root = root
        self.lang_manager = lang_manager
        self.on_success = on_success
        self.window = tk.Toplevel(root)
        self.window.title(self.lang_manager.get_text("header.login", "登入"))
        self.window.geometry("350x200")
        self.window.transient(root)
        self.window.grab_set()

        self.setup_ui()
        self.update_language()

    def setup_ui(self):
        """設置登入介面"""
        self.frame = ttk.Frame(self.window, padding="20")
        self.frame.pack(expand=True, fill="both")

        self.username_label = ttk.Label(self.frame, text="使用者名稱:")
        self.username_label.grid(row=0, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(self.frame, textvariable=self.username_var).grid(row=0, column=1, sticky="ew", pady=5, columnspan=2)

        self.password_label = ttk.Label(self.frame, text="密碼:")
        self.password_label.grid(row=1, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(self.frame, textvariable=self.password_var, show="*").grid(row=1, column=1, sticky="ew", pady=5, columnspan=2)
        
        # 語言選擇器
        self.lang_label = ttk.Label(self.frame, text="語言:")
        self.lang_label.grid(row=2, column=0, sticky="w", pady=5)
        self.lang_var = tk.StringVar()
        self.lang_combo = ttk.Combobox(
            self.frame,
            textvariable=self.lang_var,
            values=sorted(["日本語", "中文", "English"], key=str.lower),
            state="readonly",
            width=10
        )
        self.lang_combo.grid(row=2, column=1, sticky="w", pady=5)
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)


        self.login_btn = ttk.Button(self.frame, text="登入", command=self.login)
        self.login_btn.grid(row=2, column=2, sticky="e", pady=10)

        self.frame.columnconfigure(1, weight=1)
    
    def on_language_change(self, event):
        """處理語言變化事件"""
        lang_map = {"日本語": "ja", "English": "en", "中文": "zh"}
        selected_lang = self.lang_var.get()
        new_lang_code = lang_map.get(selected_lang, "ja")
        
        self.lang_manager.set_language(new_lang_code)
        self.update_language()

    def update_language(self):
        """更新此畫面的語言"""
        lang_map = {"ja": "日本語", "zh": "中文", "en": "English"}
        current_lang_name = lang_map.get(self.lang_manager.get_current_language(), "日本語")
        self.lang_var.set(current_lang_name)
        
        self.window.title(self.lang_manager.get_text("header.login", "登入"))
        self.username_label.config(text=self.lang_manager.get_text("common.username", "使用者名稱:"))
        self.password_label.config(text=self.lang_manager.get_text("common.password", "密碼:"))
        self.lang_label.config(text=self.lang_manager.get_text("header.languageSwitch", "語言:"))
        self.login_btn.config(text=self.lang_manager.get_text("header.login", "登入"))

    def login(self):
        """處理登入邏輯"""
        username = self.username_var.get()
        password = self.password_var.get()
        if not ensure_requests_installed():
            return
        
        try:
            # 在實際應用中，這裡的 URL 應該從配置文件讀取
            response = requests.post(
                "http://127.0.0.1:8000/api/v1/auth/login",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                self.window.destroy()
                self.on_success(response.json()["access_token"])
            else:
                messagebox.showerror(
                    self.lang_manager.get_text("login.failed", "登入失敗"),
                    self.lang_manager.get_text("login.incorrect", "使用者名稱或密碼錯誤。")
                )
        except requests.exceptions.ConnectionError:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                self.lang_manager.get_text("login.connectError", "無法連接到後端伺服器。")
            )


class LanguageManager:
    """
    語言管理器
    負責管理多語言資源並提供翻譯功能
    """
    
    def __init__(self, locales_dir: str = "frontend/public/locales"):
        self.locales_dir = locales_dir
        self.current_language = "ja"  # 默認為日文
        self.translations = {}

        # 支援的語言
        self.supported_languages = ["ja", "zh", "en"]

        # 加載所有語言資源
        self.load_all_translations()

    def load_all_translations(self):
        """加載所有支援語言的翻譯資源"""
        for lang_code in self.supported_languages:
            self.translations[lang_code] = self.load_language_translations(lang_code)

    def load_language_translations(self, lang_code: str):
        """加載特定語言的翻譯資源"""
        try:
            # 檢查目錄是否存在
            os.makedirs(self.locales_dir, exist_ok=True)
            
            # 檢查語言文件是否存在，如果不存在則創建默認文件
            file_path = os.path.join(self.locales_dir, f"{lang_code}.json")
            if not os.path.exists(file_path):
                self.create_default_language_file(lang_code)
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 找不到語言文件 {file_path}")
            # 返回默認翻譯
            return self.get_default_translations(lang_code)
        except json.JSONDecodeError:
            print(f"錯誤: 語言文件 {file_path} 格式無效")
            return {}

    def create_default_language_file(self, lang_code: str):
        """創建默認語言文件"""
        default_translations = self.get_default_translations(lang_code)
        file_path = os.path.join(self.locales_dir, f"{lang_code}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_translations, f, ensure_ascii=False, indent=2)

    def get_default_translations(self, lang_code: str):
        """獲取默認翻譯資源"""
        defaults = {
            "ja": {
                "header": {
                    "title": "電子交接系統",
                    "languageSwitch": "言語切替",
                    "login": "ログイン",
                    "logout": "ログアウト"
                },
                "navigation": {
                    "home": "ホーム",
                    "reports": "レポート",
                    "settings": "設定",
                    "admin": "管理",
                    "masterData": "基本データ管理"
                },
                "common": {
                    "date": "日付",
                    "shift": "シフト",
                    "area": "区域",
                    "save": "保存",
                    "cancel": "キャンセル",
                    "create": "作成",
                    "update": "更新",
                    "delete": "削除",
                    "search": "検索",
                    "edit": "編集",
                    "confirm": "確認",
                    "yes": "はい",
                    "no": "いいえ",
                    "loading": "読み込み中...",
                    "error": "エラー",
                    "success": "成功",
                    "scheduled": "定員",
                    "present": "出勤",
                    "absent": "欠勤",
                    "reason": "理由",
                    "regular": "正社員",
                    "contractor": "契約社員",
                    "add": "追加",
                    "newArea": "新しい区域",
                    "areaName": "区域名",
                    "username": "ユーザー名",
                    "password": "パスワード"
                },
                "attendance": {
                    "regular": "正社員",
                    "contractor": "契約社員",
                    "input": "出勤入力",
                    "records": "出勤記録"
                },
                "equipment": {
                    "equipId": "設備ID",
                    "startTime": "発生時刻",
                    "description": "異常内容",
                    "impactQty": "影響数量",
                    "actionTaken": "対応内容",
                    "image": "画像"
                },
                "lot": {
                    "lotId": "ロットNO",
                    "status": "処置状況",
                    "notes": "特記事項"
                },
                "summary": {
                    "keyOutput": "Key Machine Output",
                    "issues": "Key Issues",
                    "countermeasures": "Countermeasures"
                },
                "cards": {
                    "summaryQueryTable": "サマリー検索結果"
                },
                "login": {
                    "failed": "ログイン失敗",
                    "incorrect": "ユーザー名またはパスワードが違います。",
                    "connectError": "バックエンドサーバーに接続できません。",
                    "welcome": "ようこそ, {username}",
                    "welcome_generic": "ようこそ",
                    "welcome_offline": "ようこそ (オフライン)"
                }
            },
            "zh": {
                "header": {
                    "title": "電子交接系統",
                    "languageSwitch": "語言切換",
                    "login": "登入",
                    "logout": "登出"
                },
                "navigation": {
                    "home": "首頁",
                    "reports": "報表",
                    "settings": "設定",
                    "admin": "管理",
                    "masterData": "基本資料管理"
                },
                "common": {
                    "date": "日期",
                    "shift": "班別",
                    "area": "區域",
                    "save": "保存",
                    "cancel": "取消",
                    "create": "新增",
                    "update": "更新",
                    "delete": "刪除",
                    "search": "搜尋",
                    "edit": "編輯",
                    "confirm": "確認",
                    "yes": "是",
                    "no": "否",
                    "loading": "載入中...",
                    "error": "錯誤",
                    "success": "成功",
                    "scheduled": "定員",
                    "present": "出勤",
                    "absent": "欠勤",
                    "reason": "理由",
                    "regular": "正社員",
                    "contractor": "契約社員",
                    "add": "新增",
                    "newArea": "新區域",
                    "areaName": "區域名稱",
                    "username": "使用者名稱",
                    "password": "密碼"
                },
                "attendance": {
                    "regular": "正社員",
                    "contractor": "契約社員",
                    "input": "出勤輸入",
                    "records": "出勤記錄"
                },
                "equipment": {
                    "equipId": "設備ID",
                    "startTime": "發生時刻",
                    "description": "異常內容",
                    "impactQty": "影響數量",
                    "actionTaken": "對應內容",
                    "image": "圖片"
                },
                "lot": {
                    "lotId": "批號",
                    "status": "處置狀況",
                    "notes": "特記事項"
                },
                "summary": {
                    "keyOutput": "Key Machine Output",
                    "issues": "Key Issues",
                    "countermeasures": "Countermeasures"
                },
                "cards": {
                    "summaryQueryTable": "摘要查詢結果"
                },
                "login": {
                    "failed": "登入失敗",
                    "incorrect": "使用者名稱或密碼錯誤。",
                    "connectError": "無法連接到後端伺服器。",
                    "welcome": "歡迎, {username}",
                    "welcome_generic": "歡迎",
                    "welcome_offline": "歡迎 (離線)"
                }
            },
            "en": {
                "header": {
                    "title": "Digital Handover System",
                    "languageSwitch": "Language Switch",
                    "login": "Login",
                    "logout": "Logout"
                },
                "navigation": {
                    "home": "Home",
                    "reports": "Reports",
                    "settings": "Settings",
                    "admin": "Admin",
                    "masterData": "Master Data Management"
                },
                "common": {
                    "date": "Date",
                    "shift": "Shift",
                    "area": "Area",
                    "save": "Save",
                    "cancel": "Cancel",
                    "create": "Create",
                    "update": "Update",
                    "delete": "Delete",
                    "search": "Search",
                    "edit": "Edit",
                    "confirm": "Confirm",
                    "yes": "Yes",
                    "no": "No",
                    "loading": "Loading...",
                    "error": "Error",
                    "success": "Success",
                    "scheduled": "Scheduled",
                    "present": "Present",
                    "absent": "Absent",
                    "reason": "Reason",
                    "regular": "Regular Staff",
                    "contractor": "Contractor Staff",
                    "add": "Add",
                    "newArea": "New Area",
                    "areaName": "Area Name",
                    "username": "Username",
                    "password": "Password"
                },
                "attendance": {
                    "regular": "Regular",
                    "contractor": "Contractor",
                    "input": "Attendance Input",
                    "records": "Attendance Records"
                },
                "equipment": {
                    "equipId": "Equipment ID",
                    "startTime": "Start Time",
                    "description": "Description",
                    "impactQty": "Impact Qty",
                    "actionTaken": "Action Taken",
                    "image": "Image"
                },
                "lot": {
                    "lotId": "Lot ID",
                    "status": "Status",
                    "notes": "Notes"
                },
                "summary": {
                    "keyOutput": "Key Machine Output",
                    "issues": "Key Issues",
                    "countermeasures": "Countermeasures"
                },
                "cards": {
                    "summaryQueryTable": "Summary Query Results"
                },
                "login": {
                    "failed": "Login Failed",
                    "incorrect": "Incorrect username or password.",
                    "connectError": "Could not connect to the backend server.",
                    "welcome": "Welcome, {username}",
                    "welcome_generic": "Welcome",
                    "welcome_offline": "Welcome (Offline)"
                }
            }
        }

        return defaults.get(lang_code, {})

    def get_text(self, key: str, default_text: str = "") -> str:
        """
        獲取指定鍵的翻譯文本
        :param key: 翻譯鍵 (例如: "header.title")
        :param default_text: 默認文本
        :return: 翻譯後的文本或默認文本
        """
        try:
            # 分割鍵以支持嵌套結構 (例如: "header.title")
            keys = key.split('.')
            current_dict = self.translations[self.current_language]

            for k in keys:
                current_dict = current_dict.get(k, {})

            if isinstance(current_dict, str):
                return current_dict
            else:
                # 如果找不到確切的鍵，返回默認值或鍵本身
                return default_text or key
        except (TypeError, AttributeError):
            # 如果當前語言中找不到翻譯，則檢查其他語言
            for lang_code in self.supported_languages:
                if lang_code != self.current_language:
                    try:
                        current_dict = self.translations[lang_code]
                        for k in keys:
                            current_dict = current_dict.get(k, {})
                        
                        if isinstance(current_dict, str):
                            return current_dict
                    except (KeyError, TypeError, AttributeError):
                        continue

            # 如果所有語言都沒有找到，返回默認文本或鍵值
            return default_text or key

    def set_language(self, language_code: str) -> bool:
        """
        設置當前語言
        :param language_code: 語言代碼
        :return: 設置成功與否
        """
        if language_code in self.supported_languages:
            self.current_language = language_code
            return True
        else:
            print(f"不支援的語言代碼: {language_code}")
            return False

    def get_current_language(self) -> str:
        """
        獲取當前語言代碼
        :return: 當前語言代碼
        """
        return self.current_language

    def get_supported_languages(self) -> list:
        """
        獲取支援的語言列表
        :return: 支援的語言代碼列表
        """
        return self.supported_languages


class AttendanceSection:
    """
    出勤記錄組件
    同時顯示正社員和契約社員的出勤記錄輸入區域
    """
    
    def __init__(self, parent, lang_manager, callback=None):
        """
        初始化出勤記錄組件
        
        Args:
            parent: 父組件
            lang_manager: 語言管理器實例
            callback: 處理回調函數（如保存操作）
        """
        self.parent = parent
        self.lang_manager = lang_manager
        self.callback = callback
        
        # 創建界面
        self.create_ui()
    
    def create_ui(self):
        """創建界面元素"""
        # 主框架
        self.frame = ttk.LabelFrame(self.parent, text="出勤記錄", padding="10")
        
        # 正社員出勤記錄區域
        self.regular_frame = ttk.LabelFrame(self.frame, text="正社員 (Regular Staff)", padding="5")
        self.regular_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.regular_frame.columnconfigure(1, weight=1)
        
        # 定員、出勤、欠勤、理由欄位 (正社員)
        self.regular_scheduled_label = ttk.Label(self.regular_frame, text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:")
        self.regular_scheduled_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.regular_scheduled_var = tk.StringVar(value="0")
        ttk.Entry(self.regular_frame, textvariable=self.regular_scheduled_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(0, 15), pady=2)
        
        self.regular_present_label = ttk.Label(self.regular_frame, text=f"{self.lang_manager.get_text('common.present', '出勤')}:")
        self.regular_present_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 5), pady=2)
        self.regular_present_var = tk.StringVar(value="0")
        ttk.Entry(self.regular_frame, textvariable=self.regular_present_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=(0, 15), pady=2)
        
        self.regular_absent_label = ttk.Label(self.regular_frame, text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:")
        self.regular_absent_label.grid(row=0, column=4, sticky=tk.W, padx=(0, 5), pady=2)
        self.regular_absent_var = tk.StringVar(value="0")
        ttk.Entry(self.regular_frame, textvariable=self.regular_absent_var, width=10).grid(row=0, column=5, sticky=tk.W, padx=(0, 15), pady=2)
        
        self.regular_reason_label = ttk.Label(self.regular_frame, text=f"{self.lang_manager.get_text('common.reason', '理由')}:")
        self.regular_reason_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.regular_reason_var = tk.StringVar()
        ttk.Entry(self.regular_frame, textvariable=self.regular_reason_var, width=50).grid(row=1, column=1, columnspan=5, sticky=(tk.W, tk.E), pady=2)
        
        # 契約社員出勤記錄區域 - 同時顯示，不使用下拉選單切換
        self.contractor_frame = ttk.LabelFrame(self.frame, text="契約社員 (Contractor Staff)", padding="5")
        self.contractor_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.contractor_frame.columnconfigure(1, weight=1)
        
        # 定員、出勤、欠勤、理由欄位 (契約社員)
        self.contractor_scheduled_label = ttk.Label(self.contractor_frame, text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:")
        self.contractor_scheduled_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.contractor_scheduled_var = tk.StringVar(value="0")
        ttk.Entry(self.contractor_frame, textvariable=self.contractor_scheduled_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(0, 15), pady=2)
        
        self.contractor_present_label = ttk.Label(self.contractor_frame, text=f"{self.lang_manager.get_text('common.present', '出勤')}:")
        self.contractor_present_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 5), pady=2)
        self.contractor_present_var = tk.StringVar(value="0")
        ttk.Entry(self.contractor_frame, textvariable=self.contractor_present_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=(0, 15), pady=2)
        
        self.contractor_absent_label = ttk.Label(self.contractor_frame, text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:")
        self.contractor_absent_label.grid(row=0, column=4, sticky=tk.W, padx=(0, 5), pady=2)
        self.contractor_absent_var = tk.StringVar(value="0")
        ttk.Entry(self.contractor_frame, textvariable=self.contractor_absent_var, width=10).grid(row=0, column=5, sticky=tk.W, padx=(0, 15), pady=2)
        
        self.contractor_reason_label = ttk.Label(self.contractor_frame, text=f"{self.lang_manager.get_text('common.reason', '理由')}:")
        self.contractor_reason_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.contractor_reason_var = tk.StringVar()
        ttk.Entry(self.contractor_frame, textvariable=self.contractor_reason_var, width=50).grid(row=1, column=1, columnspan=5, sticky=(tk.W, tk.E), pady=2)
        
        # 驗證按鈕 - 檢查輸入數據的合理性
        self.validate_btn = ttk.Button(
            self.frame,
            text="驗證數據",
            command=self.validate_attendance_data
        )
        self.validate_btn.grid(row=2, column=0, sticky=tk.E, pady=5)
    
    def validate_attendance_data(self) -> bool:
        """驗證出勤數據的合理性"""
        try:
            # 驗證正社員數據
            regular_scheduled = int(self.regular_scheduled_var.get() or "0")
            regular_present = int(self.regular_present_var.get() or "0")
            regular_absent = int(self.regular_absent_var.get() or "0")
            
            if regular_present + regular_absent > regular_scheduled:
                messagebox.showwarning(
                    "數據不合理",
                    f"正社員出勤人數 ({regular_present}) + 欠勤人數 ({regular_absent}) > 定員人數 ({regular_scheduled})"
                )
                return False
            
            # 驗證契約社員數據
            contractor_scheduled = int(self.contractor_scheduled_var.get() or "0")
            contractor_present = int(self.contractor_present_var.get() or "0")
            contractor_absent = int(self.contractor_absent_var.get() or "0")
            
            if contractor_present + contractor_absent > contractor_scheduled:
                messagebox.showwarning(
                    "數據不合理",
                    f"契約社員出勤人數 ({contractor_present}) + 欠勤人數 ({contractor_absent}) > 定員人數 ({contractor_scheduled})"
                )
                return False
            
            # 如果所有驗證通過
            messagebox.showinfo(
                "驗證成功",
                "所有出勤數據輸入合理。\n" +
                f"正社員: 定員 {regular_scheduled}, 出勤 {regular_present}, 欠勤 {regular_absent}\n" +
                f"契約社員: 定員 {contractor_scheduled}, 出勤 {contractor_present}, 欠勤 {contractor_absent}"
            )
            return True
            
        except ValueError:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                self.lang_manager.get_text("common.invalidNumbers", "請確保輸入的都是有效數字")
            )
            return False
    
    def get_data(self) -> dict:
        """獲取當前輸入的數據"""
        return {
            "regular": {
                "scheduled": int(self.regular_scheduled_var.get() or "0"),
                "present": int(self.regular_present_var.get() or "0"),
                "absent": int(self.regular_absent_var.get() or "0"),
                "reason": self.regular_reason_var.get()
            },
            "contractor": {
                "scheduled": int(self.contractor_scheduled_var.get() or "0"),
                "present": int(self.contractor_present_var.get() or "0"),
                "absent": int(self.contractor_absent_var.get() or "0"),
                "reason": self.contractor_reason_var.get()
            }
        }
    
    def get_widget(self):
        """獲取組件主框架"""
        return self.frame

    def update_language(self):
        """更新此組件的語言"""
        self.frame.config(text=self.lang_manager.get_text("attendance.records", "出勤記錄"))
        self.regular_frame.config(text=self.lang_manager.get_text('common.regular', '正社員'))
        self.contractor_frame.config(text=self.lang_manager.get_text('common.contractor', '契約社員'))
        
        self.regular_scheduled_label.config(text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:")
        self.regular_present_label.config(text=f"{self.lang_manager.get_text('common.present', '出勤')}:")
        self.regular_absent_label.config(text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:")
        self.regular_reason_label.config(text=f"{self.lang_manager.get_text('common.reason', '理由')}:")
        
        self.contractor_scheduled_label.config(text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:")
        self.contractor_present_label.config(text=f"{self.lang_manager.get_text('common.present', '出勤')}:")
        self.contractor_absent_label.config(text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:")
        self.contractor_reason_label.config(text=f"{self.lang_manager.get_text('common.reason', '理由')}:")
        
        self.validate_btn.config(text=self.lang_manager.get_text('common.validate', '驗證數據'))
		
    def update_language(self):
        """更新此組件的語言"""
        self.frame.config(text=self.lang_manager.get_text("attendance.records", "出勤記錄"))
        self.frame.winfo_children()[0].config(text=self.lang_manager.get_text('common.regular', '正社員'))
        self.frame.winfo_children()[1].config(text=self.lang_manager.get_text('common.contractor', '契約社員'))
        
        regular_frame = self.frame.winfo_children()[0]
        regular_frame.winfo_children()[0].config(text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:")
        regular_frame.winfo_children()[2].config(text=f"{self.lang_manager.get_text('common.present', '出勤')}:")
        regular_frame.winfo_children()[4].config(text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:")
        regular_frame.winfo_children()[6].config(text=f"{self.lang_manager.get_text('common.reason', '理由')}:")
        
        contractor_frame = self.frame.winfo_children()[1]
        contractor_frame.winfo_children()[0].config(text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:")
        contractor_frame.winfo_children()[2].config(text=f"{self.lang_manager.get_text('common.present', '出勤')}:")
        contractor_frame.winfo_children()[4].config(text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:")
        contractor_frame.winfo_children()[6].config(text=f"{self.lang_manager.get_text('common.reason', '理由')}:")
        
        validate_btn = self.frame.winfo_children()[2]
        validate_btn.config(text=self.lang_manager.get_text('common.validate', '驗證數據'))

    def update_language(self):
        """更新此組件的語言"""
        self.frame.config(text=self.lang_manager.get_text("attendance.records", "出勤記錄"))
        self.frame.winfo_children()[0].config(text=self.lang_manager.get_text('common.regular', '正社員'))
        self.frame.winfo_children()[1].config(text=self.lang_manager.get_text('common.contractor', '契約社員'))
        
        regular_frame = self.frame.winfo_children()[0]
        ttk.Label(regular_frame, text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        ttk.Label(regular_frame, text=f"{self.lang_manager.get_text('common.present', '出勤')}:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5), pady=2)
        ttk.Label(regular_frame, text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5), pady=2)
        ttk.Label(regular_frame, text=f"{self.lang_manager.get_text('common.reason', '理由')}:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        
        contractor_frame = self.frame.winfo_children()[1]
        ttk.Label(contractor_frame, text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        ttk.Label(contractor_frame, text=f"{self.lang_manager.get_text('common.present', '出勤')}:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5), pady=2)
        ttk.Label(contractor_frame, text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5), pady=2)
        ttk.Label(contractor_frame, text=f"{self.lang_manager.get_text('common.reason', '理由')}:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        
        validate_btn = self.frame.winfo_children()[2]
        validate_btn.config(text=self.lang_manager.get_text('common.validate', '驗證數據'))


class MainApplication:
    """
    電子交接本系統主應用程式界面
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("電子交接系統")
        self.root.withdraw() # 初始隱藏主視窗
        
        self.access_token = None
        self.main_frame = None

        # 語言和資料管理器
        self.lang_manager = LanguageManager()
        self.master_data_path = "data/master_data.json"
        self.master_data = self.load_master_data()

        # 存儲界面組件的引用
        self.ui_components = {}
        
        # 設置樣式
        self.setup_styles()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """處理窗口關閉事件"""
        if messagebox.askokcancel(
            self.lang_manager.get_text("common.quit", "退出"),
            self.lang_manager.get_text("common.confirmQuit", "確定要退出電子交接系統嗎？")
        ):
            self.root.destroy()

    def show_login_screen(self):
        """顯示登入畫面"""
        LoginScreen(self.root, self.lang_manager, self.login_success)

    def login_success(self, token):
        """登入成功後的回調"""
        self.access_token = token
        self.root.deiconify() # 顯示主視窗
        self.setup_ui()
        self.fetch_current_user()

    def fetch_current_user(self):
        """獲取當前使用者資訊並更新UI"""
        if not self.access_token:
            return
        if not ensure_requests_installed():
            self.welcome_label.config(text=self.lang_manager.get_text("login.welcome_offline", "歡迎 (離線)"))
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get("http://127.0.0.1:8000/api/v1/auth/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get("username", "User")
                welcome_text = self.lang_manager.get_text("login.welcome", "Welcome, {username}").format(username=username)
                self.welcome_label.config(text=welcome_text)
            else:
                self.welcome_label.config(text=self.lang_manager.get_text("login.welcome_generic", "歡迎"))
        except requests.exceptions.ConnectionError:
            self.welcome_label.config(text=self.lang_manager.get_text("login.welcome_offline", "歡迎 (離線)"))

    def logout(self):
        """登出"""
        self.access_token = None
        if self.main_frame:
            self.main_frame.destroy()
        self.root.withdraw()
        self.show_login_screen()

    def load_master_data(self):
        """從 JSON 文件加載基本資料"""
        try:
            if os.path.exists(self.master_data_path):
                with open(self.master_data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 如果文件不存在，返回一個空的預設結構
                return {"areas": [], "shifts": []}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            messagebox.showerror("錯誤", f"無法加載基本資料: {e}")
            return {"areas": [], "shifts": []}

    def save_master_data(self):
        """將基本資料保存到 JSON 文件"""
        try:
            os.makedirs(os.path.dirname(self.master_data_path), exist_ok=True)
            with open(self.master_data_path, 'w', encoding='utf-8') as f:
                json.dump(self.master_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("錯誤", f"無法保存基本資料: {e}")

    def setup_styles(self):
        """設置界面樣式"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 定義顏色
        self.primary_color = "#333333"
        self.secondary_color = "#f2f2f2"
        self.accent_color = "#0078d4"
        self.text_color = "#ffffff"

        # 配置全局字體
        self.default_font = ("Microsoft YaHei UI", 10)
        self.title_font = ("Microsoft YaHei UI", 16, "bold")

        self.style.configure('.', 
                             background=self.secondary_color,
                             foreground=self.primary_color,
                             font=self.default_font)

        # 框架和標籤框架樣式
        self.style.configure('TFrame', background=self.secondary_color)
        self.style.configure('TLabel', background=self.secondary_color, foreground=self.primary_color)
        self.style.configure('TLabelFrame', 
                             background=self.secondary_color, 
                             foreground=self.primary_color,
                             font=self.default_font)
        self.style.configure('TLabelFrame.Label', 
                             background=self.secondary_color, 
                             foreground=self.primary_color,
                             font=("Microsoft YaHei UI", 11, "bold"))
        
        # 按鈕樣式
        self.style.configure('TButton', 
                             background=self.accent_color, 
                             foreground=self.text_color,
                             font=("Microsoft YaHei UI", 10, "bold"),
                             padding=(10, 5))
        self.style.map('TButton',
                       background=[('active', '#005a9e')])

        # 輸入框和下拉選單樣式
        self.style.configure('TEntry', 
                             fieldbackground="#ffffff", 
                             foreground=self.primary_color)
        self.style.configure('TCombobox', 
                             fieldbackground="#ffffff", 
                             foreground=self.primary_color)
        
        # Notebook 樣式
        self.style.configure('TNotebook', 
                             background=self.secondary_color,
                             borderwidth=0)
        self.style.configure('TNotebook.Tab', 
                             background=self.secondary_color,
                             foreground=self.primary_color,
                             padding=(10, 5),
                             font=("Microsoft YaHei UI", 10, "bold"))
        self.style.map('TNotebook.Tab',
                       background=[('selected', self.accent_color)],
                       foreground=[('selected', self.text_color)])
    
    def setup_ui(self):
        """設置界面元素"""
        # 創建主框架
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置窗口大小調整
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # 頂部導航欄
        self.top_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        self.top_frame.columnconfigure(1, weight=1)
        
        # 標題
        self.title_label = ttk.Label(
            self.top_frame, 
            text=self.lang_manager.get_text("header.title", "電子交接系統"), 
            font=self.title_font,
            style='TLabel'
        )
        self.title_label.grid(row=0, column=0, sticky=tk.W)

        # 歡迎訊息和登出按鈕
        user_frame = ttk.Frame(self.top_frame, style='TFrame')
        user_frame.grid(row=0, column=1, sticky=tk.E, padx=10)

        self.welcome_label = ttk.Label(user_frame, style='TLabel')
        self.welcome_label.pack(side=tk.LEFT)

        logout_btn = ttk.Button(user_frame, text=self.lang_manager.get_text("header.logout", "登出"), command=self.logout)
        logout_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 語言選擇器框架
        lang_frame = ttk.Frame(self.top_frame, style='TFrame')
        lang_frame.grid(row=0, column=2, sticky=tk.E)

        lang_label = ttk.Label(lang_frame, text="語言/Language/言語:", style='TLabel')
        lang_label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.lang_var = tk.StringVar()
        self.lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=sorted(["日本語", "中文", "English"], key=str.lower),
            state="readonly",
            width=12
        )
        self.lang_combo.pack(side=tk.RIGHT)
        
        # 設置當前語言顯示
        lang_map = {"ja": "日本語", "zh": "中文", "en": "English"}
        current_lang_name = lang_map.get(self.lang_manager.get_current_language(), "日本語")
        self.lang_var.set(current_lang_name)
        
        # 綁定語言選擇事件
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # 主內容區域 (使用 Notebook 顯示不同頁面)
        self.notebook = ttk.Notebook(self.main_frame, style='TNotebook')
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 創建各個頁面標籤
        self.create_daily_report_tab()
        self.create_attendance_tab()
        self.create_equipment_tab()
        self.create_lot_log_tab()
        self.create_master_data_tab() # 新增基本資料管理頁面
        self.create_summary_tab()
        
        # 底部狀態欄
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5
        )
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 設置當前狀態
        lang_names = {"ja": "日本語", "zh": "中文", "en": "English"}
        lang_name = lang_names.get(self.lang_manager.get_current_language(), "日本語")
        self.status_var.set(f"就緒 - 當前語言: {lang_name}")
    
    def on_language_change(self, event):
        """處理語言變化事件"""
        lang_map = {"日本語": "ja", "English": "en", "中文": "zh"}
        selected_lang = self.lang_var.get()
        new_lang_code = lang_map.get(selected_lang, "ja")
        
        # 更新語言管理器中的當前語言
        self.lang_manager.set_language(new_lang_code)
        
        # 更新界面語言
        self.update_ui_language()
        
        # 更新窗口標題
        self.root.title(self.lang_manager.get_text("header.title", "電子交接系統"))
        
        # 更新狀態欄
        lang_names = {"ja": "日本語", "zh": "中文", "en": "English"}
        lang_name = lang_names.get(self.lang_manager.get_current_language(), "日本語")
        self.status_var.set(f"就緒 - 當前語言: {lang_name}")
    
    def update_ui_language(self):
        """根據當前語言更新界面標示"""
        # 更新標題
        self.title_label.config(text=self.lang_manager.get_text("header.title", "電子交接系統"))
        
        # 更新 Notebook 標籤
        self.notebook.tab(0, text=self.lang_manager.get_text("navigation.reports", "報表"))
        self.notebook.tab(1, text=self.lang_manager.get_text("attendance.records", "出勤記錄"))
        self.notebook.tab(2, text=self.lang_manager.get_text("common.equipment", "設備異常"))
        self.notebook.tab(3, text=self.lang_manager.get_text("common.lots", "異常批次"))
        self.notebook.tab(4, text=self.lang_manager.get_text("navigation.masterData", "基本資料管理")) # 新增的頁面標籤
        self.notebook.tab(5, text=self.lang_manager.get_text("common.summary", "總結"))
        
        # 更新各個頁面內容
        self.update_daily_report_tab_language()
        self.update_attendance_tab_language()
        self.update_equipment_tab_language()
        self.update_lot_log_tab_language()
        self.update_master_data_tab_language() # 更新基本資料管理頁面語言
        self.update_summary_tab_language()
    
    def update_daily_report_tab_language(self):
        """更新日報表頁面語言"""
        if hasattr(self, 'info_frame'):
            self.info_frame.config(text=self.lang_manager.get_text("common.basicInfo", "基本信息"))
        
        if hasattr(self, 'date_label'):
            self.date_label.config(text=f"{self.lang_manager.get_text('common.date', '日期')}:")
        
        if hasattr(self, 'shift_label'):
            self.shift_label.config(text=f"{self.lang_manager.get_text('common.shift', '班別')}:")
        
        if hasattr(self, 'area_label'):
            self.area_label.config(text=f"{self.lang_manager.get_text('common.area', '區域')}:")
            # 更新區域下拉選單的值
            if hasattr(self, 'area_combo'):
                self.area_combo['values'] = self.master_data.get("areas", [])

        if hasattr(self, 'summary_frame'):
            self.summary_frame.config(text="摘要")
        
        if hasattr(self, 'key_output_label'):
            self.key_output_label.config(text=self.lang_manager.get_text("summary.keyOutput", "Key Machine Output"))
        
        if hasattr(self, 'issues_label'):
            self.issues_label.config(text=self.lang_manager.get_text("summary.issues", "Key Issues"))
        
        if hasattr(self, 'countermeasures_label'):
            self.countermeasures_label.config(text=self.lang_manager.get_text("summary.countermeasures", "Countermeasures"))
        
        if hasattr(self, 'save_report_btn'):
            self.save_report_btn.config(text=self.lang_manager.get_text("common.save", "保存"))
    
    def update_attendance_tab_language(self):
        """更新出勤記錄頁面語言"""
        if hasattr(self, 'attendance_section'):
            self.attendance_section.update_language()
    
    def update_equipment_tab_language(self):
        """更新設備異常頁面語言"""
        if hasattr(self, 'equip_id_label'):
            self.equip_id_label.config(text=f"{self.lang_manager.get_text('equipment.equipId', '設備ID')}:")
        
        if hasattr(self, 'equip_desc_label'):
            self.equip_desc_label.config(text=f"{self.lang_manager.get_text('common.description', '異常內容')}:")
        
        if hasattr(self, 'equip_start_time_label'):
            self.equip_start_time_label.config(text=f"{self.lang_manager.get_text('equipment.startTime', '發生時刻')}:")
        
        if hasattr(self, 'equip_impact_qty_label'):
            self.equip_impact_qty_label.config(text=f"{self.lang_manager.get_text('equipment.impactQty', '影響數量')}:")
        
        if hasattr(self, 'equip_action_taken_label'):
            self.equip_action_taken_label.config(text=f"{self.lang_manager.get_text('equipment.actionTaken', '對應內容')}:")
        
        if hasattr(self, 'equip_image_label'):
            self.equip_image_label.config(text=f"{self.lang_manager.get_text('common.image', '圖片')}:")
        
        if hasattr(self, 'browse_btn'):
            self.browse_btn.config(text=self.lang_manager.get_text("common.browse", "瀏覽"))
        
        if hasattr(self, 'add_equipment_btn'):
            self.add_equipment_btn.config(text=self.lang_manager.get_text("common.add", "添加記錄"))
    
    def update_lot_log_tab_language(self):
        """更新異常批次頁面語言"""
        if hasattr(self, 'lot_id_label'):
            self.lot_id_label.config(text=f"{self.lang_manager.get_text('lot.lotId', '批號')}:")
        
        if hasattr(self, 'lot_desc_label'):
            self.lot_desc_label.config(text=f"{self.lang_manager.get_text('common.description', '異常內容')}:")
        
        if hasattr(self, 'lot_status_label'):
            self.lot_status_label.config(text=f"{self.lang_manager.get_text('lot.status', '處置狀況')}:")
        
        if hasattr(self, 'lot_notes_label'):
            self.lot_notes_label.config(text=f"{self.lang_manager.get_text('common.notes', '特記事項')}:")
        
        if hasattr(self, 'add_lot_btn'):
            self.add_lot_btn.config(text=self.lang_manager.get_text("common.add", "添加記錄"))

    def update_master_data_tab_language(self):
        """更新基本資料管理頁面語言"""
        if hasattr(self, 'master_data_frame'):
            self.master_data_frame.config(text=self.lang_manager.get_text("navigation.masterData", "基本資料管理"))
        if hasattr(self, 'area_input_label'):
            self.area_input_label.config(text=f"{self.lang_manager.get_text('common.area', '區域')}:")
        if hasattr(self, 'add_area_btn'):
            self.add_area_btn.config(text=self.lang_manager.get_text('common.create', '新增'))
        if hasattr(self, 'update_area_btn'):
            self.update_area_btn.config(text=self.lang_manager.get_text('common.update', '更新'))
        if hasattr(self, 'delete_area_btn'):
            self.delete_area_btn.config(text=self.lang_manager.get_text('common.delete', '刪除'))
        # 重新填充 Treeview
        if hasattr(self, 'area_tree'):
            self.area_tree.heading("AreaName", text=self.lang_manager.get_text("common.areaName", "區域名稱"))
            # self.populate_area_list() # 這行不需要，因為 populate_area_list 不會翻譯內容

    def update_summary_tab_language(self):
        """更新總結頁面語言"""
        if hasattr(self, 'output_frame'):
            self.output_frame.config(text=self.lang_manager.get_text("summary.keyOutput", "Key Machine Output"))
        
        if hasattr(self, 'issues_frame'):
            self.issues_frame.config(text=self.lang_manager.get_text("summary.issues", "Key Issues"))
        
        if hasattr(self, 'countermeasures_frame'):
            self.countermeasures_frame.config(text=self.lang_manager.get_text("summary.countermeasures", "Countermeasures"))

    
    def create_daily_report_tab(self):
        """創建日報表標籤頁"""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text=self.lang_manager.get_text("navigation.reports", "報表"))
        tab_frame.columnconfigure(0, weight=1)

        # 日期和班別區域
        self.info_frame = ttk.LabelFrame(tab_frame, text="基本信息", padding="15")
        self.info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # 日期、班別、區域
        date_frame = ttk.Frame(self.info_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        self.date_label = ttk.Label(date_frame, text=f"{self.lang_manager.get_text('common.date', '日期')}:")
        self.date_label.pack(side=tk.LEFT, padx=(0, 5))
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.date_var, width=15).pack(side=tk.LEFT, padx=(0, 20))
        
        self.shift_label = ttk.Label(date_frame, text=f"{self.lang_manager.get_text('common.shift', '班別')}:")
        self.shift_label.pack(side=tk.LEFT, padx=(0, 5))
        self.shift_var = tk.StringVar(value="Day")
        shift_combo = ttk.Combobox(
            date_frame,
            textvariable=self.shift_var,
            values=sorted(["Day", "Night"], key=str.lower),
            state="readonly",
            width=10
        )
        shift_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        self.area_label = ttk.Label(date_frame, text=f"{self.lang_manager.get_text('common.area', '區域')}:")
        self.area_label.pack(side=tk.LEFT, padx=(0, 5))
        self.area_var = tk.StringVar(value="etching_D")
        area_combo = ttk.Combobox(
            date_frame,
            textvariable=self.area_var,
            values=sorted(["etching_D", "etching_E", "litho", "thin_film"], key=str.lower),
            state="readonly",
            width=15
        )
        area_combo.pack(side=tk.LEFT)
        
        # 摘要區域
        self.summary_frame = ttk.LabelFrame(tab_frame, text="摘要", padding="15")
        self.summary_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        tab_frame.rowconfigure(1, weight=1)
        self.summary_frame.columnconfigure(0, weight=1)
        self.summary_frame.rowconfigure(1, weight=1)
        self.summary_frame.rowconfigure(3, weight=1)
        self.summary_frame.rowconfigure(5, weight=1)

        # Key Machine Output
        self.key_output_label = ttk.Label(self.summary_frame, text=self.lang_manager.get_text("summary.keyOutput", "Key Machine Output"))
        self.key_output_label.grid(row=0, column=0, sticky="w")
        self.key_output_text = tk.Text(self.summary_frame, height=4, relief=tk.FLAT, bg="white")
        self.key_output_text.grid(row=1, column=0, sticky="nsew", pady=(5, 10))
        
        # Key Issues
        self.issues_label = ttk.Label(self.summary_frame, text=self.lang_manager.get_text("summary.issues", "Key Issues"))
        self.issues_label.grid(row=2, column=0, sticky="w")
        self.issues_text = tk.Text(self.summary_frame, height=4, relief=tk.FLAT, bg="white")
        self.issues_text.grid(row=3, column=0, sticky="nsew", pady=(5, 10))
        
        # Countermeasures
        self.countermeasures_label = ttk.Label(self.summary_frame, text=self.lang_manager.get_text("summary.countermeasures", "Countermeasures"))
        self.countermeasures_label.grid(row=4, column=0, sticky="w")
        self.countermeasures_text = tk.Text(self.summary_frame, height=4, relief=tk.FLAT, bg="white")
        self.countermeasures_text.grid(row=5, column=0, sticky="nsew", pady=(5, 0))
        
        # 保存按鈕
        button_frame = ttk.Frame(tab_frame)
        button_frame.grid(row=2, column=0, sticky="e", pady=(10, 0))
        self.save_report_btn = ttk.Button(button_frame, text=self.lang_manager.get_text("common.save", "保存"), command=self.save_daily_report)
        self.save_report_btn.pack()
    
    def create_attendance_tab(self):
        """創建出勤記錄標籤頁 - 同時顯示正社員和契約社員的輸入欄位，不使用下拉式選單區分"""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text=self.lang_manager.get_text("attendance.records", "出勤記錄"))
        tab_frame.columnconfigure(0, weight=1)
        
        # 使用出勤記錄組件 - 同時顯示正社員和契約社員的欄位
        self.attendance_section = AttendanceSection(tab_frame, self.lang_manager)
        self.attendance_section.get_widget().grid(row=0, column=0, sticky="ew")
        
        # 保存按鈕
        button_frame = ttk.Frame(tab_frame)
        button_frame.grid(row=1, column=0, sticky="e", pady=(10, 0))
        ttk.Button(button_frame, text=self.lang_manager.get_text("common.save", "保存"), command=self.save_attendance_record).pack()
    
    def create_equipment_tab(self):
        """創建設備異常記錄標籤頁"""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text=self.lang_manager.get_text("common.equipment", "設備異常"))
        tab_frame.columnconfigure(0, weight=1)
        
        # 輸入區域
        input_frame = ttk.LabelFrame(tab_frame, text="設備異常輸入", padding="15")
        input_frame.grid(row=0, column=0, sticky="ew")
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

        # 設備ID和異常內容
        self.equip_id_label = ttk.Label(input_frame, text=f"{self.lang_manager.get_text('equipment.equipId', '設備ID')}:")
        self.equip_id_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.equip_id_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.equip_id_var, width=30).grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        self.equip_desc_label = ttk.Label(input_frame, text=f"{self.lang_manager.get_text('common.description', '異常內容')}:")
        self.equip_desc_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 5), pady=5)
        self.equip_desc_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.equip_desc_var).grid(row=0, column=3, sticky="ew", pady=5)
        
        # 發生時刻和影響數量
        self.equip_start_time_label = ttk.Label(input_frame, text=f"{self.lang_manager.get_text('equipment.startTime', '發生時刻')}:")
        self.equip_start_time_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.equip_start_time_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.equip_start_time_var, width=30).grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        self.equip_impact_qty_label = ttk.Label(input_frame, text=f"{self.lang_manager.get_text('equipment.impactQty', '影響數量')}:")
        self.equip_impact_qty_label.grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=5)
        self.equip_impact_qty_var = tk.StringVar(value="0")
        ttk.Entry(input_frame, textvariable=self.equip_impact_qty_var).grid(row=1, column=3, sticky="ew", pady=5)
        
        # 對應內容
        self.equip_action_taken_label = ttk.Label(input_frame, text=f"{self.lang_manager.get_text('equipment.actionTaken', '對應內容')}:")
        self.equip_action_taken_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.equip_action_taken_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.equip_action_taken_var).grid(row=2, column=1, columnspan=3, sticky="ew", pady=5)
        
        # 圖片上傳
        self.equip_image_label = ttk.Label(input_frame, text=f"{self.lang_manager.get_text('common.image', '圖片')}:")
        self.equip_image_label.grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=10)
        self.equip_image_path_var = tk.StringVar()
        image_frame = ttk.Frame(input_frame)
        image_frame.grid(row=3, column=1, columnspan=3, sticky="ew", pady=10)
        image_frame.columnconfigure(0, weight=1)

        image_entry = ttk.Entry(image_frame, textvariable=self.equip_image_path_var, state="readonly")
        image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.browse_btn = ttk.Button(
            image_frame,
            text=self.lang_manager.get_text("common.browse", "瀏覽"),
            command=self.browse_equipment_image
        )
        self.browse_btn.grid(row=0, column=1, sticky="e")
        
        # 添加記錄按鈕
        self.add_equipment_btn = ttk.Button(
            input_frame,
            text=self.lang_manager.get_text("common.add", "添加記錄"),
            command=self.add_equipment_log
        )
        self.add_equipment_btn.grid(row=4, column=3, sticky=tk.E, pady=(10, 0))
    
    def create_lot_log_tab(self):
        """創建異常批次記錄標籤頁"""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text=self.lang_manager.get_text("common.lots", "異常批次"))
        tab_frame.columnconfigure(0, weight=1)

        # 輸入區域
        input_frame = ttk.LabelFrame(tab_frame, text="異常批次輸入", padding="15")
        input_frame.grid(row=0, column=0, sticky="ew")
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # 批號和異常內容
        self.lot_id_label = ttk.Label(input_frame, text=f"{self.lang_manager.get_text('lot.lotId', '批號')}:")
        self.lot_id_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.lot_id_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.lot_id_var, width=30).grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        self.lot_desc_label = ttk.Label(input_frame, text=f"{self.lang_manager.get_text('common.description', '異常內容')}:")
        self.lot_desc_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 5), pady=5)
        self.lot_desc_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.lot_desc_var).grid(row=0, column=3, sticky="ew", pady=5)
        
        # 處置狀況和特記事項
        self.lot_status_label = ttk.Label(input_frame, text=f"{self.lang_manager.get_text('lot.status', '處置狀況')}:")
        self.lot_status_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.lot_status_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.lot_status_var, width=30).grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        self.lot_notes_label = ttk.Label(input_frame, text=f"{self.lang_manager.get_text('common.notes', '特記事項')}:")
        self.lot_notes_label.grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=5)
        self.lot_notes_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.lot_notes_var).grid(row=1, column=3, sticky="ew", pady=5)
        
        # 添加記錄按鈕
        self.add_lot_btn = ttk.Button(
            input_frame,
            text=self.lang_manager.get_text("common.add", "添加記錄"),
            command=self.add_lot_log
        )
        self.add_lot_btn.grid(row=2, column=3, sticky=tk.E, pady=(10, 0))
    
    def create_master_data_tab(self):
        """創建基本資料管理標籤頁"""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text=self.lang_manager.get_text("navigation.masterData", "基本資料管理"))
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(1, weight=1)

        self.master_data_frame = ttk.LabelFrame(tab_frame, text=self.lang_manager.get_text("navigation.masterData", "基本資料管理"), padding="15")
        self.master_data_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.master_data_frame.columnconfigure(0, weight=1)
        self.master_data_frame.rowconfigure(1, weight=1)

        # 區域管理介面
        area_management_frame = ttk.LabelFrame(self.master_data_frame, text="區域管理", padding="10")
        area_management_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        area_management_frame.columnconfigure(1, weight=1)

        self.area_input_label = ttk.Label(area_management_frame, text=f"{self.lang_manager.get_text('common.area', '區域')}:")
        self.area_input_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.area_name_var = tk.StringVar()
        self.area_entry = ttk.Entry(area_management_frame, textvariable=self.area_name_var, width=40)
        self.area_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)

        # CRUD 按鈕
        button_frame = ttk.Frame(area_management_frame)
        button_frame.grid(row=0, column=2, sticky="e", padx=(0, 5))

        self.add_area_btn = ttk.Button(button_frame, text=self.lang_manager.get_text("common.create", "新增"), command=self.add_area)
        self.add_area_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.update_area_btn = ttk.Button(button_frame, text=self.lang_manager.get_text("common.update", "更新"), command=self.update_area)
        self.update_area_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.delete_area_btn = ttk.Button(button_frame, text=self.lang_manager.get_text("common.delete", "刪除"), command=self.delete_area)
        self.delete_area_btn.pack(side=tk.LEFT)

        # 區域列表顯示
        self.area_tree = ttk.Treeview(self.master_data_frame, columns=("AreaName",), show="headings", selectmode="browse")
        self.area_tree.heading("AreaName", text=self.lang_manager.get_text("common.area", "區域"))
        self.area_tree.column("AreaName", width=200, anchor=tk.W)
        self.area_tree.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        # 滾動條
        scrollbar = ttk.Scrollbar(self.master_data_frame, orient="vertical", command=self.area_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(10, 0))
        self.area_tree.configure(yscrollcommand=scrollbar.set)

        self.area_tree.bind("<<TreeviewSelect>>", self.on_area_select)
        self.populate_area_list()

    def populate_area_list(self):
        """填充區域列表"""
        for i in self.area_tree.get_children():
            self.area_tree.delete(i)
        for area in self.master_data.get("areas", []):
            self.area_tree.insert("", "end", values=(area,))

    def add_area(self):
        """新增區域"""
        new_area = self.area_name_var.get().strip()
        if new_area and new_area not in self.master_data.get("areas", []):
            self.master_data.setdefault("areas", []).append(new_area)
            self.save_master_data()
            self.populate_area_list()
            self.area_name_var.set("")
            messagebox.showinfo(self.lang_manager.get_text("common.success", "成功"), f"區域 '{new_area}' 已新增。")
            self.update_daily_report_tab_language() # 更新日報表的區域下拉選單
        elif new_area:
            messagebox.showwarning(self.lang_manager.get_text("common.error", "錯誤"), "區域已存在。")
        else:
            messagebox.showwarning(self.lang_manager.get_text("common.error", "錯誤"), "區域名稱不能為空。")

    def update_area(self):
        """更新選定的區域"""
        selected_item = self.area_tree.focus()
        if not selected_item:
            messagebox.showwarning(self.lang_manager.get_text("common.error", "錯誤"), "請選擇一個要更新的區域。")
            return

        old_area = self.area_tree.item(selected_item)['values'][0]
        new_area = self.area_name_var.get().strip()

        if not new_area:
            messagebox.showwarning(self.lang_manager.get_text("common.error", "錯誤"), "區域名稱不能為空。")
            return
        
        if new_area in self.master_data.get("areas", []) and new_area != old_area:
            messagebox.showwarning(self.lang_manager.get_text("common.error", "錯誤"), "新區域名稱已存在。")
            return

        if old_area in self.master_data["areas"]:
            index = self.master_data["areas"].index(old_area)
            self.master_data["areas"][index] = new_area
            self.save_master_data()
            self.populate_area_list()
            self.area_name_var.set("")
            messagebox.showinfo(self.lang_manager.get_text("common.success", "成功"), f"區域 '{old_area}' 已更新為 '{new_area}'。")
            self.update_daily_report_tab_language() # 更新日報表的區域下拉選單
        else:
            messagebox.showerror(self.lang_manager.get_text("common.error", "錯誤"), "找不到要更新的區域。")

    def delete_area(self):
        """刪除選定的區域"""
        selected_item = self.area_tree.focus()
        if not selected_item:
            messagebox.showwarning(self.lang_manager.get_text("common.error", "錯誤"), "請選擇一個要刪除的區域。")
            return

        area_to_delete = self.area_tree.item(selected_item)['values'][0]
        if messagebox.askyesno(
            self.lang_manager.get_text("common.confirm", "確認"),
            f"確定要刪除區域 '{area_to_delete}' 嗎？"
        ):
            if area_to_delete in self.master_data.get("areas", []):
                self.master_data["areas"].remove(area_to_delete)
                self.save_master_data()
                self.populate_area_list()
                self.area_name_var.set("")
                messagebox.showinfo(self.lang_manager.get_text("common.success", "成功"), f"區域 '{area_to_delete}' 已刪除。")
                self.update_daily_report_tab_language() # 更新日報表的區域下拉選單
            else:
                messagebox.showerror(self.lang_manager.get_text("common.error", "錯誤"), "找不到要刪除的區域。")

    def on_area_select(self, event):
        """當區域列表中的項目被選中時觸發"""
        selected_item = self.area_tree.focus()
        if selected_item:
            area_name = self.area_tree.item(selected_item)['values'][0]
            self.area_name_var.set(area_name)

    def update_summary(self):
        """更新總結內容"""
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, "系統總結報告\n")
        self.summary_text.insert(tk.END, "="*30 + "\n")
        self.summary_text.insert(tk.END, f"當前語言: {self.lang_manager.get_current_language()}\n")
        self.summary_text.insert(tk.END, f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.summary_text.insert(tk.END, f"日報表數量: 0\n")
        self.summary_text.insert(tk.END, f"設備異常記錄數: 0\n")
        self.summary_text.insert(tk.END, f"批次異常記錄數: 0\n")
        self.summary_text.insert(tk.END, "\n系統狀態: 正常運行")

    def save_daily_report(self):
        """保存日報表"""
        try:
            # 這裡會實現保存邏輯到後端 API
            # 目前僅顯示確認對話框
            messagebox.showinfo(
                self.lang_manager.get_text("common.success", "成功"),
                f"報表已保存!\n日期: {self.date_var.get()}\n班別: {self.shift_var.get()}\n區域: {self.area_var.get()}"
            )
        except Exception as e:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                f"{self.lang_manager.get_text('common.saveFailed', '保存失敗')}: {str(e)}"
            )

    def save_attendance_record(self):
        """保存出勤記錄 - 實現正社員和契約社員同時記錄的功能"""
        try:
            # 驗證數據
            attendance_data = self.attendance_section.get_data()
            if not self.attendance_section.validate_attendance_data():
                return  # 數據驗證失敗，不繼續保存

            # 在實際實現中，這會調用後端API保存數據
            # 目前僅顯示保存確認對話框
            messagebox.showinfo(
                self.lang_manager.get_text("common.success", "成功"),
                f"出勤記錄已保存!\n" +
                f"{self.lang_manager.get_text('attendance.regular', '正社員')}: 定員 {attendance_data['regular']['scheduled']}, 出勤 {attendance_data['regular']['present']}, 欠勤 {attendance_data['regular']['absent']}\n" +
                f"{self.lang_manager.get_text('attendance.contractor', '契約社員')}: 定員 {attendance_data['contractor']['scheduled']}, 出勤 {attendance_data['contractor']['present']}, 欠勤 {attendance_data['contractor']['absent']}"
            )
        except Exception as e:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                f"{self.lang_manager.get_text('common.saveFailed', '保存失敗')}: {str(e)}"
            )

    def browse_equipment_image(self):
        """瀏覽設備圖片"""
        file_path = filedialog.askopenfilename(
            title=self.lang_manager.get_text("common.selectImage", "選擇圖片"),
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            # 在實際實現中，這會上傳文件到服務器，但目前僅顯示文件路徑
            self.equip_image_path_var.set(file_path)

    def add_equipment_log(self):
        """添加設備異常記錄"""
        if not self.equip_id_var.get().strip() or not self.equip_desc_var.get().strip():
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                self.lang_manager.get_text("equipment.requireFields", "設備ID和異常內容是必填字段")
            )
            return

        # 在實際實現中，這會調用後端API保存數據
        # 目前僅顯示確認對話框
        messagebox.showinfo(
            self.lang_manager.get_text("common.success", "成功"),
            self.lang_manager.get_text("equipment.recordAdded", "設備異常記錄已添加")
        )

    def add_lot_log(self):
        """添加異常批次記錄"""
        if not self.lot_id_var.get().strip() or not self.lot_desc_var.get().strip():
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                self.lang_manager.get_text("lot.requireFields", "批號和異常內容是必填字段")
            )
            return

        # 在實際實現中，這會調用後端API保存數據
        # 目前僅顯示確認對話框
        messagebox.showinfo(
            self.lang_manager.get_text("common.success", "成功"),
            self.lang_manager.get_text("lot.recordAdded", "異常批次記錄已添加")
        )


def main():
    """主函數"""
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
