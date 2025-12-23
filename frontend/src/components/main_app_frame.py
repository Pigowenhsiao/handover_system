"""
主應用程序界面組件
包含電子交接本系統的主要界面元素
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime

from frontend.src.components.language_selector import LanguageSelector, MultiLanguageLabel, MultiLanguageButton
from frontend.src.i18n.language_manager import LanguageManager


class MainApplicationFrame:
    """
    主應用程序界面框架
    包含導航、標題和內容區域
    """
    
    def __init__(self, parent, lang_manager):
        self.parent = parent
        self.lang_manager = lang_manager
        
        # 創建主界面
        self.setup_ui()
    
    def setup_ui(self):
        """設置主界面元素"""
        # 頂部框架 - 包含標題和語言選擇
        self.top_frame = ttk.Frame(self.parent)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 標題
        self.title_label = MultiLanguageLabel(
            self.top_frame,
            text_key="header.title",
            default_text="電子交接系統",
            font=("TkDefaultFont", 16, "bold")
        )
        self.title_label.get_widget().pack(side=tk.LEFT)
        
        # 語言選擇器
        self.lang_selector = LanguageSelector(
            self.top_frame,
            self.lang_manager,
            callback=self.on_language_changed
        )
        self.lang_selector.get_widget().pack(side=tk.RIGHT)
        
        # 中間內容框架
        self.content_frame = ttk.Frame(self.parent)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 創建內容界面
        self.create_content_area()
        
        # 底部狀態欄
        self.status_bar = ttk.Label(
            self.parent,
            text="就緒",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_content_area(self):
        """創建內容區域"""
        # 創建筆記本組件（分頁界面）
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 創建各個標籤頁
        self.create_daily_report_tab()
        self.create_attendance_tab()
        self.create_equipment_tab()
        self.create_lot_tab()
        self.create_summary_tab()
        self.create_admin_tab()
    
    def create_daily_report_tab(self):
        """創建日報表標籤頁"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="日報表")
        
        # 日期選擇
        date_frame = ttk.LabelFrame(tab_frame, text="日期與班別")
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 日期
        ttk.Label(date_frame, text="日期:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.date_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 班別
        ttk.Label(date_frame, text="班別:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.shift_var = tk.StringVar(value="Day")
        shift_combo = ttk.Combobox(
            date_frame,
            textvariable=self.shift_var,
            values=sorted(["Day", "Night"], key=str.lower),
            state="readonly"
        )
        shift_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 區域
        ttk.Label(date_frame, text="區域:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.area_var = tk.StringVar(value="etching_D")
        area_combo = ttk.Combobox(
            date_frame,
            textvariable=self.area_var,
            values=sorted(["etching_D", "etching_E", "litho", "thin_film"], key=str.lower),
            state="readonly"
        )
        area_combo.grid(row=0, column=5, sticky=tk.W, padx=5, pady=5)
        
        # 基本信息
        basic_frame = ttk.LabelFrame(tab_frame, text="基本資訊")
        basic_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(basic_frame, text="Key Machine Output:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.key_output_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.key_output_var, width=60).grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # 配置列權重以便擴展
        basic_frame.columnconfigure(1, weight=1)
    
    def create_attendance_tab(self):
        """創建出勤記錄標籤頁"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="出勤記錄")
        
        # 正社員出勤記錄
        regular_frame = ttk.LabelFrame(tab_frame, text="正社員 (Regular Staff)")
        regular_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(regular_frame, text="定員:").grid(row=0, column=0, padx=5, pady=5)
        self.regular_scheduled_var = tk.StringVar(value="0")
        ttk.Entry(regular_frame, textvariable=self.regular_scheduled_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(regular_frame, text="出勤:").grid(row=0, column=2, padx=5, pady=5)
        self.regular_present_var = tk.StringVar(value="0")
        ttk.Entry(regular_frame, textvariable=self.regular_present_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(regular_frame, text="欠勤:").grid(row=0, column=4, padx=5, pady=5)
        self.regular_absent_var = tk.StringVar(value="0")
        ttk.Entry(regular_frame, textvariable=self.regular_absent_var, width=10).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(regular_frame, text="理由:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.regular_reason_var = tk.StringVar()
        ttk.Entry(regular_frame, textvariable=self.regular_reason_var, width=60).grid(row=1, column=1, columnspan=5, sticky=tk.EW, padx=5, pady=5)
        
        # 配置列權重
        regular_frame.columnconfigure(1, weight=1)
        
        # 契約社員出勤記錄
        contractor_frame = ttk.LabelFrame(tab_frame, text="契約社員 (Contractor Staff)")
        contractor_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(contractor_frame, text="定員:").grid(row=0, column=0, padx=5, pady=5)
        self.contractor_scheduled_var = tk.StringVar(value="0")
        ttk.Entry(contractor_frame, textvariable=self.contractor_scheduled_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(contractor_frame, text="出勤:").grid(row=0, column=2, padx=5, pady=5)
        self.contractor_present_var = tk.StringVar(value="0")
        ttk.Entry(contractor_frame, textvariable=self.contractor_present_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(contractor_frame, text="欠勤:").grid(row=0, column=4, padx=5, pady=5)
        self.contractor_absent_var = tk.StringVar(value="0")
        ttk.Entry(contractor_frame, textvariable=self.contractor_absent_var, width=10).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(contractor_frame, text="理由:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.contractor_reason_var = tk.StringVar()
        ttk.Entry(contractor_frame, textvariable=self.contractor_reason_var, width=60).grid(row=1, column=1, columnspan=5, sticky=tk.EW, padx=5, pady=5)
        
        # 配置列權重
        contractor_frame.columnconfigure(1, weight=1)
    
    def create_equipment_tab(self):
        """創建設備異常記錄標籤頁"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="設備異常")
        
        # 設備號碼
        ttk.Label(tab_frame, text="設備號碼:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.equip_id_var = tk.StringVar()
        ttk.Entry(tab_frame, textvariable=self.equip_id_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 發生時刻
        ttk.Label(tab_frame, text="發生時刻:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.start_time_var = tk.StringVar()
        ttk.Entry(tab_frame, textvariable=self.start_time_var, width=20).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 影響數量
        ttk.Label(tab_frame, text="影響數量:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.impact_qty_var = tk.StringVar(value="0")
        ttk.Entry(tab_frame, textvariable=self.impact_qty_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 異常內容
        ttk.Label(tab_frame, text="異常內容:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_text = tk.Text(tab_frame, height=4, width=60)
        self.desc_text.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        # 對應內容
        ttk.Label(tab_frame, text="對應內容:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_text = tk.Text(tab_frame, height=4, width=60)
        self.action_text.grid(row=3, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        # 圖片上傳
        ttk.Label(tab_frame, text="異常圖片:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.image_path_var = tk.StringVar()
        ttk.Entry(tab_frame, textvariable=self.image_path_var, width=50, state="readonly").grid(row=4, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(tab_frame, text="瀏覽", command=self.browse_image).grid(row=4, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 配置列權重
        tab_frame.columnconfigure(1, weight=1)
    
    def create_lot_tab(self):
        """創建異常批次記錄標籤頁"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="異常批次")
        
        # 批號
        ttk.Label(tab_frame, text="批號:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.lot_id_var = tk.StringVar()
        ttk.Entry(tab_frame, textvariable=self.lot_id_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 異常內容
        ttk.Label(tab_frame, text="異常內容:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.lot_desc_text = tk.Text(tab_frame, height=4, width=60)
        self.lot_desc_text.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # 處置狀況
        ttk.Label(tab_frame, text="處置狀況:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.lot_status_var = tk.StringVar()
        ttk.Entry(tab_frame, textvariable=self.lot_status_var, width=60).grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # 特記事項
        ttk.Label(tab_frame, text="特記事項:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.lot_notes_text = tk.Text(tab_frame, height=4, width=60)
        self.lot_notes_text.grid(row=3, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # 配置列權重
        tab_frame.columnconfigure(1, weight=1)
    
    def create_summary_tab(self):
        """創建總結標籤頁"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="總結")
        
        # Key Issues
        ttk.Label(tab_frame, text="Key Issues:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.key_issues_text = tk.Text(tab_frame, height=6, width=80)
        self.key_issues_text.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # Countermeasures
        ttk.Label(tab_frame, text="Countermeasures:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.countermeasures_text = tk.Text(tab_frame, height=6, width=80)
        self.countermeasures_text.grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # 配置權重
        tab_frame.columnconfigure(0, weight=1)
    
    def create_admin_tab(self):
        """創建管理員標籤頁"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="管理員")
        
        # 用戶管理
        user_mgmt_frame = ttk.LabelFrame(tab_frame, text="用戶管理")
        user_mgmt_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(user_mgmt_frame, text="用戶列表", command=self.show_users).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(user_mgmt_frame, text="新增用戶", command=self.add_user).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(user_mgmt_frame, text="編輯用戶", command=self.edit_user).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(user_mgmt_frame, text="刪除用戶", command=self.delete_user).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 翻譯管理
        translation_mgmt_frame = ttk.LabelFrame(tab_frame, text="翻譯管理")
        translation_mgmt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 翻譯列表
        columns = ("Key", "Japanese", "Chinese", "English")
        self.translation_tree = ttk.Treeview(translation_mgmt_frame, columns=columns, show="headings", height=15)
        
        # 定義列標題
        self.translation_tree.heading("Key", text="鍵")
        self.translation_tree.heading("Japanese", text="日本語")
        self.translation_tree.heading("Chinese", text="中文")
        self.translation_tree.heading("English", text="English")
        
        # 設置列寬
        self.translation_tree.column("Key", width=150)
        self.translation_tree.column("Japanese", width=150)
        self.translation_tree.column("Chinese", width=150)
        self.translation_tree.column("English", width=150)
        
        # 滾動條
        scrollbar = ttk.Scrollbar(translation_mgmt_frame, orient=tk.VERTICAL, command=self.translation_tree.yview)
        self.translation_tree.configure(yscrollcommand=scrollbar.set)
        
        self.translation_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def browse_image(self):
        """瀏覽圖片文件"""
        file_path = filedialog.askopenfilename(
            title="選擇圖片文件",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # 在實際應用中，這會上傳文件到服務器
            # 此處僅存儲本地路徑以示範功能
            self.image_path_var.set(file_path)
    
    def on_language_changed(self, new_lang_code):
        """語言變更時的回調函數"""
        # 更新界面中的所有標籤和按鈕文本
        self.update_ui_language()
        
        # 更新狀態欄
        lang_names = {"ja": "日本語", "en": "English", "zh": "中文"}
        current_lang_name = lang_names.get(new_lang_code, new_lang_code)
        self.status_bar.config(text=f"當前語言: {current_lang_name}")
    
    def update_ui_language(self):
        """根據當前語言更新界面文本"""
        # 此處需要更新所有界面元素的文本
        # 因為我們使用了 MultiLanguageLabel 組件，只需通知它們更新
        pass
    
    def show_users(self):
        """顯示用戶列表"""
        messagebox.showinfo("用戶管理", "用戶列表功能")
    
    def add_user(self):
        """新增用戶"""
        messagebox.showinfo("用戶管理", "新增用戶功能")
    
    def edit_user(self):
        """編輯用戶"""
        messagebox.showinfo("用戶管理", "編輯用戶功能")
    
    def delete_user(self):
        """刪除用戶"""
        messagebox.showinfo("用戶管理", "刪除用戶功能")
