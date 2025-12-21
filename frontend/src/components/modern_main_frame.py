"""
現代化主應用程序界面框架
採用側邊導航、卡片式設計、現代色彩方案
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from collections import defaultdict
import calendar
import json
import os
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import rcParams
from sqlalchemy.orm import joinedload

# 導入現有組件
from frontend.src.components.language_selector import LanguageSelector
from frontend.main import LanguageManager
from frontend.src.components.admin_section import UserManagementSection, TranslationManagementSection, MasterDataSection
from frontend.src.components.attendance_section_optimized import AttendanceSectionOptimized
from auth import verify_password
from models import (
    DelayEntry,
    SummaryActualEntry,
    SessionLocal,
    User,
    DailyReport,
    AttendanceEntry,
    EquipmentLog,
    LotLog,
    ShiftOption,
    AreaOption,
    get_database_path,
)


class ModernMainFrame:
    """
    現代化主應用框架
    採用 Material Design 設計理念
    """
    
    LIGHT_COLORS = {
        'primary': '#1976D2',      # 主色 - 藍色
        'primary_dark': '#1565C0',
        'primary_light': '#E3F2FD',
        'accent': '#FF9800',       # 強調色 - 橙色
        'background': '#FAFAFA',   # 背景色
        'surface': '#FFFFFF',      # 表面色
        'text_primary': '#212121', # 主要文字
        'text_secondary': '#757575', # 次要文字
        'divider': '#E0E0E0',      # 分割線
        'success': '#4CAF50',      # 成功色
        'warning': '#FF9800',      # 警告色
        'error': '#F44336',        # 錯誤色
        'sidebar': '#2C3E50',      # 側邊欄背景
        'sidebar_active': '#3498DB' # 側邊欄激活項
    }
    DARK_COLORS = {
        'primary': '#4C8DFF',
        'primary_dark': '#1E6BD6',
        'primary_light': '#90CAF9',
        'accent': '#FFB74D',
        'background': '#121212',
        'surface': '#1E1E1E',
        'text_primary': '#E6E6E6',
        'text_secondary': '#B0B0B0',
        'divider': '#2A2A2A',
        'success': '#66BB6A',
        'warning': '#FFA726',
        'error': '#EF5350',
        'sidebar': '#111827',
        'sidebar_active': '#1F2937'
    }
    COLORS = LIGHT_COLORS
    
    def __init__(self, parent, lang_manager):
        self.parent = parent
        self.lang_manager = lang_manager
        self.current_user = None
        self.sidebar_collapsed = False
        self._global_i18n = []
        self._page_i18n = []
        self._nav_items = []
        self.theme_mode = self._load_theme_mode()
        self.COLORS = dict(self.DARK_COLORS if self.theme_mode == "dark" else self.LIGHT_COLORS)
        ModernMainFrame.COLORS = self.COLORS
        self._text_widgets = []
        self._canvas_widgets = []
        self.report_context = {"date": "", "shift": "", "area": ""}
        self.saved_context = {"date": "", "shift": "", "area": ""}
        self.report_is_saved = False
        self.active_report_id = None
        self.nav_locked = True
        self.layout = {
            "page_pad": 24,
            "section_pad": 20,
            "card_pad": 20,
            "row_pad": 12,
            "field_gap": 16,
        }
        self.delay_pending_records = []
        self.summary_pending_records = []
        self.summary_dashboard_data = None
        self._cjk_font_ready = False
        self.shift_options = ["Day", "Night"]
        self.area_options = ["etching_D", "etching_E", "litho", "thin_film"]
        
        # 配置現代化樣式
        self.setup_modern_styles()
        
        # 創建界面
        self.setup_login_ui()
        self.setup_ui()

        # 先顯示登入畫面
        self._show_login_screen()

    def _t(self, key, default):
        return self.lang_manager.get_text(key, default)

    def _register_text(self, widget, key, default, scope="global"):
        entry = {"widget": widget, "key": key, "default": default}
        if scope == "page":
            self._page_i18n.append(entry)
        else:
            self._global_i18n.append(entry)
        widget.config(text=self._t(key, default))

    def _apply_i18n(self):
        for entry in self._global_i18n + self._page_i18n:
            widget = entry["widget"]
            if widget.winfo_exists():
                widget.config(text=self._t(entry["key"], entry["default"]))

    def _clear_page_i18n(self):
        self._page_i18n = []

    def _set_status(self, key, default):
        self.status_label.config(text=self._t(key, default))

    def _update_auth_ui(self):
        has_nav = hasattr(self, "nav_buttons")
        if self.current_user:
            username = self.current_user.get("username", "")
            role = self.current_user.get("role", "")
            label = self._t("auth.logged_in_as", "👤 {username} ({role})")
            self.user_info_label.config(text=label.format(username=username, role=role))
            self.auth_button.config(text=self._t("header.logout", "登出"))
            if has_nav and "admin" in self.nav_buttons:
                self.nav_buttons["admin"].config(state="normal")
        else:
            self.user_info_label.config(text=self._t("auth.not_logged_in", "未登入"))
            self.auth_button.config(text=self._t("header.login", "登入"))
            if has_nav and "admin" in self.nav_buttons:
                self.nav_buttons["admin"].config(state="disabled")

    def _clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def _load_settings_data(self):
        path = self._settings_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_settings_data(self, data):
        path = self._settings_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def _load_theme_mode(self):
        data = self._load_settings_data()
        theme = data.get("theme")
        return theme if theme in ("light", "dark") else "light"

    def _persist_theme_setting(self):
        data = self._load_settings_data()
        data["theme"] = self.theme_mode
        self._save_settings_data(data)

    def _register_text_widget(self, widget):
        self._text_widgets.append(widget)
        self._apply_text_widget_colors(widget)

    def _register_canvas_widget(self, widget, bg_key):
        self._canvas_widgets.append({"widget": widget, "bg_key": bg_key})
        widget.configure(background=self.COLORS[bg_key])

    def _apply_text_widget_colors(self, widget):
        colors = self.COLORS
        widget.configure(
            background=colors['surface'],
            foreground=colors['text_primary'],
            insertbackground=colors['text_primary'],
            selectbackground=colors['primary_dark'],
            selectforeground='white',
        )

    def _apply_theme_to_fixed_widgets(self):
        colors = self.COLORS
        if hasattr(self, "main_title"):
            self.main_title.configure(foreground=colors['primary'], background=colors['surface'])
        if hasattr(self, "subtitle"):
            self.subtitle.configure(foreground=colors['text_secondary'], background=colors['surface'])
        if hasattr(self, "user_info_label"):
            self.user_info_label.configure(foreground=colors['text_secondary'], background=colors['surface'])
        if hasattr(self, "status_label"):
            self.status_label.configure(foreground=colors['text_secondary'], background=colors['surface'])
        if hasattr(self, "status_info_label"):
            self.status_info_label.configure(foreground=colors['text_secondary'], background=colors['surface'])
        if hasattr(self, "sidebar_title"):
            self.sidebar_title.configure(background=colors['sidebar'], foreground='white')
        if hasattr(self, "sidebar_version_label"):
            self.sidebar_version_label.configure(background=colors['sidebar'], foreground=colors['text_secondary'])
        if hasattr(self, "summary_hint_label"):
            self.summary_hint_label.configure(foreground=colors['text_secondary'])

        for entry in self._canvas_widgets:
            widget = entry["widget"]
            if widget.winfo_exists():
                widget.configure(background=colors[entry["bg_key"]])

        for widget in self._text_widgets:
            if widget.winfo_exists():
                self._apply_text_widget_colors(widget)

        if hasattr(self, "status_indicator") and hasattr(self, "status_indicator_id"):
            self.status_indicator.itemconfigure(self.status_indicator_id, fill=colors['success'])

        if hasattr(self, "summary_pie_canvas") and self.summary_pie_canvas:
            self.summary_pie_canvas.get_tk_widget().configure(background=colors['surface'])
        if hasattr(self, "summary_bar_canvas") and self.summary_bar_canvas:
            self.summary_bar_canvas.get_tk_widget().configure(background=colors['surface'])

        popup = getattr(self, "_calendar_popup", None)
        if popup is not None and popup.winfo_exists():
            popup.configure(background=colors['background'])

    def _update_theme_toggle_label(self):
        if not hasattr(self, "theme_toggle_btn"):
            return
        if self.theme_mode == "dark":
            key = "theme.switchToLight"
            default = "切換明亮模式"
        else:
            key = "theme.switchToDark"
            default = "切換黑暗模式"
        self.theme_toggle_btn.configure(text=self._t(key, default))

    def toggle_theme(self):
        next_theme = "dark" if self.theme_mode == "light" else "light"
        self.apply_theme(next_theme)

    def apply_theme(self, theme_mode):
        if theme_mode == self.theme_mode:
            return
        if theme_mode not in ("light", "dark"):
            return
        self.theme_mode = theme_mode
        self._persist_theme_setting()
        self.COLORS = dict(self.DARK_COLORS if theme_mode == "dark" else self.LIGHT_COLORS)
        ModernMainFrame.COLORS = self.COLORS
        self.setup_modern_styles()
        self._apply_theme_to_fixed_widgets()
        self._update_theme_toggle_label()
        if hasattr(self, "attendance_section") and self.attendance_section:
            self.attendance_section.apply_theme()
        if self.summary_dashboard_data is not None:
            self._render_summary_charts(self.summary_dashboard_data)
    
    def setup_modern_styles(self):
        """設置現代化樣式"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        
        # 配置顏色
        colors = self.COLORS

        # 基礎樣式
        style.configure('TFrame', background=colors['surface'])
        style.configure('TLabel', background=colors['surface'], foreground=colors['text_primary'])
        style.configure('TButton',
                       background=colors['surface'],
                       foreground=colors['text_primary'],
                       padding=(10, 6),
                       font=('Segoe UI', 9))
        style.map('TButton',
                 background=[('active', colors['primary_light']),
                            ('pressed', colors['primary_dark'])],
                 foreground=[('active', colors['text_primary'])])
        style.configure('TEntry',
                       fieldbackground=colors['surface'],
                       foreground=colors['text_primary'],
                       padding=(6, 4))
        style.configure('TCombobox',
                       fieldbackground=colors['surface'],
                       foreground=colors['text_primary'])
        style.map('TCombobox',
                 fieldbackground=[('readonly', colors['surface'])],
                 foreground=[('readonly', colors['text_primary'])])
        style.configure('TCheckbutton',
                       background=colors['surface'],
                       foreground=colors['text_primary'])
        style.configure('TRadiobutton',
                       background=colors['surface'],
                       foreground=colors['text_primary'])
        style.configure('TLabelframe',
                       background=colors['surface'],
                       foreground=colors['text_primary'])
        style.configure('TLabelframe.Label',
                       background=colors['surface'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 10, 'bold'))
        style.configure('Treeview',
                       background=colors['surface'],
                       fieldbackground=colors['surface'],
                       foreground=colors['text_primary'],
                       rowheight=24)
        style.configure('Treeview.Heading',
                       background=colors['background'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 9, 'bold'))
        style.map('Treeview',
                 background=[('selected', colors['primary_dark'])],
                 foreground=[('selected', 'white')])
        
        # 框架樣式
        style.configure('Modern.TFrame', background=colors['background'])
        style.configure('Sidebar.TFrame', background=colors['sidebar'])
        style.configure('MainContent.TFrame', background=colors['background'])
        style.configure('Card.TFrame', background=colors['surface'], relief='flat')
        style.configure('Toolbar.TFrame', background=colors['surface'], relief='flat')
        
        # 按鈕樣式
        style.configure('Primary.TButton',
                       background=colors['primary'],
                       foreground='white',
                       padding=(15, 8),
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Accent.TButton',
                       background=colors['accent'],
                       foreground='white',
                       padding=(10, 6),
                       font=('Segoe UI', 9, 'bold'))
        
        style.configure('Sidebar.TButton',
                       background=colors['sidebar'],
                       foreground='white',
                       padding=(15, 12),
                       font=('Segoe UI', 10),
                       anchor='w')

        style.configure('SidebarActive.TButton',
                       background=colors['sidebar_active'],
                       foreground='white',
                       padding=(15, 12),
                       font=('Segoe UI', 10, 'bold'),
                       anchor='w')

        style.configure('Toolbar.TButton',
                       background=colors['surface'],
                       foreground=colors['text_primary'],
                       padding=(10, 6),
                       font=('Segoe UI', 9, 'bold'))
        style.map('Toolbar.TButton',
                 background=[('active', colors['primary_light']),
                            ('pressed', colors['primary_dark'])],
                 foreground=[('active', colors['text_primary'])])
        
        style.map('Sidebar.TButton',
                 background=[('active', colors['sidebar_active']),
                            ('pressed', colors['primary_dark'])],
                 foreground=[('active', 'white')])
        
        # 標籤樣式
        style.configure('Title.TLabel',
                       font=('Segoe UI', 24, 'bold'),
                       foreground=colors['text_primary'],
                       background=colors['background'])
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 14),
                       foreground=colors['text_secondary'],
                       background=colors['background'])

        style.configure('Context.TLabel',
                       font=('Segoe UI', 10, 'bold'),
                       foreground=colors['text_secondary'],
                       background=colors['background'])
        
        style.configure('CardTitle.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=colors['text_primary'],
                       background=colors['surface'])
        
        style.configure('Sidebar.TLabel',
                       font=('Segoe UI', 11),
                       foreground='white',
                       background=colors['sidebar'])
        
        # 筆記本樣式
        style.configure('Modern.TNotebook', background=colors['background'])
        style.configure('Modern.TNotebook.Tab',
                       font=('Segoe UI', 10),
                       padding=(15, 8),
                       background=colors['surface'])
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', colors['primary_dark'])],
                 foreground=[('selected', 'white')])
        
        # 輸入框樣式
        style.configure('Modern.TEntry',
                       fieldbackground=colors['surface'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 10),
                       padding=(8, 5))
        
        # 進度條樣式
        style.configure('Horizontal.TProgressbar',
                       background=colors['primary'],
                       troughcolor=colors['background'],
                       thickness=8)
        
        # 分隔線樣式
        style.configure('Line.TSeparator', background=colors['divider'])

    def setup_login_ui(self):
        """設置登入畫面"""
        self.login_container = ttk.Frame(self.parent, style='Modern.TFrame')

        wrapper = ttk.Frame(self.login_container, style='Modern.TFrame')
        wrapper.pack(fill='both', expand=True)

        card = ttk.Frame(wrapper, style='Card.TFrame')
        card.place(relx=0.5, rely=0.5, anchor='center')

        title_label = ttk.Label(card, style='CardTitle.TLabel')
        self._register_text(title_label, "login.title", "登入系統", scope="global")
        title_label.grid(row=0, column=0, columnspan=2, sticky='w', padx=30, pady=(25, 5))

        subtitle_label = ttk.Label(card, style='Subtitle.TLabel')
        self._register_text(subtitle_label, "login.subtitle", "請輸入帳號與密碼", scope="global")
        subtitle_label.grid(row=1, column=0, columnspan=2, sticky='w', padx=30, pady=(0, 20))

        username_label = ttk.Label(card, font=('Segoe UI', 10))
        self._register_text(username_label, "common.username", "使用者名稱", scope="global")
        username_label.grid(row=2, column=0, sticky='w', padx=30, pady=(0, 10))
        self.login_username_var = tk.StringVar()
        self.login_username_entry = ttk.Entry(card, textvariable=self.login_username_var, style='Modern.TEntry', width=28)
        self.login_username_entry.grid(row=2, column=1, sticky='ew', padx=(10, 30), pady=(0, 10))

        password_label = ttk.Label(card, font=('Segoe UI', 10))
        self._register_text(password_label, "common.password", "密碼", scope="global")
        password_label.grid(row=3, column=0, sticky='w', padx=30, pady=(0, 10))
        self.login_password_var = tk.StringVar()
        self.login_password_entry = ttk.Entry(card, textvariable=self.login_password_var, show="*", style='Modern.TEntry', width=28)
        self.login_password_entry.grid(row=3, column=1, sticky='ew', padx=(10, 30), pady=(0, 10))
        self.login_password_entry.bind("<Return>", lambda event: self.attempt_login())

        lang_frame = ttk.Frame(card, style='Card.TFrame')
        lang_frame.grid(row=4, column=0, columnspan=2, sticky='w', padx=30, pady=(5, 15))
        self.login_lang_selector = LanguageSelector(lang_frame, self.lang_manager, callback=self.on_language_changed)
        self.login_lang_selector.get_widget().pack(side='left')

        self.login_button = ttk.Button(card, style='Primary.TButton', command=self.attempt_login)
        self._register_text(self.login_button, "header.login", "登入", scope="global")
        self.login_button.grid(row=5, column=0, columnspan=2, sticky='ew', padx=30, pady=(0, 25))

        card.columnconfigure(1, weight=1)
    
    def setup_ui(self):
        """設置現代化界面"""
        # 主容器
        self.main_container = ttk.Frame(self.parent, style='Modern.TFrame')
        self.main_container.pack(fill='both', expand=True)
        
        # 創建頂部工具欄
        self.create_top_toolbar()
        
        # 創建側邊導航欄
        self.create_sidebar()
        self._update_auth_ui()
        
        # 創建主內容區域
        self.create_main_content()
        
        # 創建狀態欄
        self.create_status_bar()

    def _show_login_screen(self):
        if hasattr(self, "main_container"):
            self.main_container.pack_forget()
        self.login_container.pack(fill='both', expand=True)
        if hasattr(self, "login_username_entry"):
            self.login_username_entry.focus_set()

    def _show_main_ui(self):
        self.login_container.pack_forget()
        self.main_container.pack(fill='both', expand=True)
    
    def create_top_toolbar(self):
        """創建頂部工具欄"""
        toolbar = ttk.Frame(self.main_container, height=60, style='Toolbar.TFrame')
        toolbar.pack(fill='x', padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        # Logo/標題容器
        title_container = ttk.Frame(toolbar, style='Toolbar.TFrame')
        title_container.pack(side='left', padx=20)
        
        # 主標題
        self.main_title = ttk.Label(
            title_container,
            font=('Segoe UI', 18, 'bold'),
            foreground=self.COLORS['primary'],
            background=self.COLORS['surface']
        )
        self._register_text(self.main_title, "header.title", "電子交接系統")
        self.main_title.pack(side='left')
        
        # 副標題
        self.subtitle = ttk.Label(
            title_container,
            font=('Segoe UI', 9),
            foreground=self.COLORS['text_secondary'],
            background=self.COLORS['surface']
        )
        self._register_text(self.subtitle, "header.subtitle", "Handover Management System")
        self.subtitle.pack(side='left', padx=(10, 0))
        
        # 右側工具區
        tool_container = ttk.Frame(toolbar, style='Toolbar.TFrame')
        tool_container.pack(side='right', padx=20)
        
        # 使用者資訊
        self.user_info_label = ttk.Label(
            tool_container,
            font=('Segoe UI', 10),
            foreground=self.COLORS['text_secondary'],
            background=self.COLORS['surface']
        )
        self.user_info_label.pack(side='left', padx=(0, 15))
        
        # 語言選擇器
        self.lang_selector = LanguageSelector(
            tool_container,
            self.lang_manager,
            callback=self.on_language_changed
        )
        self.lang_selector.get_widget().pack(side='left', padx=(0, 10))

        # 主題切換
        self.theme_toggle_btn = ttk.Button(
            tool_container,
            style='Toolbar.TButton',
            command=self.toggle_theme
        )
        self.theme_toggle_btn.pack(side='left', padx=(0, 10))
        self._update_theme_toggle_label()
        
        # 登出/登入按鈕
        self.auth_button = ttk.Button(
            tool_container,
            style='Accent.TButton',
            command=self.toggle_auth,
            width=12
        )
        self.auth_button.pack(side='left')
        self._update_auth_ui()
    
    def create_sidebar(self):
        """創建側邊導航欄"""
        self.sidebar_frame = ttk.Frame(self.main_container, width=220, style='Sidebar.TFrame')
        self.sidebar_frame.pack(side='left', fill='y', padx=0, pady=0)
        self.sidebar_frame.pack_propagate(False)
        
        # 側邊欄標題
        self.sidebar_title = ttk.Label(
            self.sidebar_frame,
            font=('Segoe UI', 12, 'bold'),
            foreground='white',
            background=self.COLORS['sidebar']
        )
        self._register_text(self.sidebar_title, "navigation.menuTitle", "導航選單")
        self.sidebar_title.pack(pady=(20, 10), padx=20, anchor='w')
        
        # 導航按鈕
        self.nav_buttons = {}
        
        self._nav_items = [
            ('daily_report', '📋', "navigation.dailyReport", "日報表"),
            ('attendance', '👥', "navigation.attendance", "出勤記錄"),
            ('equipment', '⚙️', "navigation.equipment", "設備異常"),
            ('lot', '📦', "navigation.lot", "異常批次"),
            ('summary', '📊', "navigation.summary", "總結"),
            ('abnormal_history', '🗂️', "navigation.abnormalHistory", "異常歷史"),
            ('delay_list', '⏱️', "navigation.delayList", "延遲清單"),
            ('summary_actual', '🧾', "navigation.summaryActual", "Summary Actual"),
            ('admin', '⚙️', "navigation.admin", "系統管理")
        ]

        for item_id, icon, text_key, text_default in self._nav_items:
            btn = ttk.Button(
                self.sidebar_frame,
                text=f"{icon} {self._t(text_key, text_default)}",
                style='Sidebar.TButton',
                command=lambda page=item_id: self.show_page(page),
                width=20
            )
            btn.pack(fill='x', padx=10, pady=2)
            self.nav_buttons[item_id] = btn
            
            # 添加懸停效果提示
            self.add_tooltip(btn, text_key, text_default)
        
        # 側邊欄底部資訊
        separator = ttk.Separator(self.sidebar_frame, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=(20, 10))
        
        self.sidebar_version_label = ttk.Label(
            self.sidebar_frame,
            font=('Segoe UI', 8),
            foreground='white',
            background=self.COLORS['sidebar']
        )
        self._register_text(self.sidebar_version_label, "header.version", "Version 2.0")
        self.sidebar_version_label.pack(side='bottom', pady=(0, 10), padx=20, anchor='w')
        
        # 收合/展開按鈕
        self.toggle_sidebar_btn = ttk.Button(
            self.sidebar_frame,
            text="◀",
            width=3,
            command=self.toggle_sidebar
        )
        self._position_sidebar_toggle()
        self._set_navigation_locked(self.nav_locked)
    
    def create_main_content(self):
        """創建主內容區域"""
        # 內容容器
        self.content_container = ttk.Frame(self.main_container, style='MainContent.TFrame')
        self.content_container.pack(side='left', fill='both', expand=True, padx=0, pady=0)
        
        # 內容區域（使用 Card 設計）
        self.content_frame = ttk.Frame(self.content_container, style='Modern.TFrame')
        self.content_frame.pack(fill='both', expand=True, padx=self.layout["page_pad"], pady=self.layout["page_pad"])
        
        # 頁面標題
        self.page_header = ttk.Frame(self.content_frame, style='Modern.TFrame')
        self.page_header.pack(fill='x', pady=(0, 20))
        
        self.page_title = ttk.Label(
            self.page_header,
            text="",
            style='Title.TLabel'
        )
        self.page_title.pack(side='left')
        
        self.page_subtitle = ttk.Label(
            self.page_header,
            text="",
            style='Subtitle.TLabel'
        )
        self.page_subtitle.pack(side='left', padx=(10, 0))

        self.context_label = ttk.Label(
            self.page_header,
            text="",
            style='Context.TLabel'
        )
        self.context_label.pack(side='right')
        
        # 分隔線
        separator = ttk.Separator(self.content_frame, orient='horizontal', style='Line.TSeparator')
        separator.pack(fill='x', pady=(0, 20))
        
        # 內容區（動態載入）
        self.page_content = ttk.Frame(self.content_frame, style='Modern.TFrame')
        self.page_content.pack(fill='both', expand=True)
        
        # 初始化各個頁面
        self.pages = {}
        self.current_page = None
    
    def create_status_bar(self):
        """創建狀態欄"""
        self.status_frame = ttk.Frame(self.main_container, height=30, style='Toolbar.TFrame')
        self.status_frame.pack(side='bottom', fill='x', pady=0)
        self.status_frame.pack_propagate(False)
        
        self.status_label = ttk.Label(
            self.status_frame,
            font=('Segoe UI', 9),
            foreground=self.COLORS['text_secondary'],
            background=self.COLORS['surface']
        )
        self.status_label.pack(side='left', padx=20)
        self._set_status("status.ready", "就緒")

        self.status_info_label = ttk.Label(
            self.status_frame,
            font=('Segoe UI', 9),
            foreground=self.COLORS['text_secondary'],
            background=self.COLORS['surface']
        )
        self.status_info_label.pack(side='right', padx=(0, 10))
        self._update_status_bar_info()

        # 狀態指示器
        self.status_indicator = tk.Canvas(self.status_frame, width=12, height=12, highlightthickness=0)
        self._register_canvas_widget(self.status_indicator, "surface")
        self.status_indicator_id = self.status_indicator.create_oval(1, 1, 11, 11, fill=self.COLORS['success'], outline="")
        self.status_indicator.pack(side='right', padx=20)

    def _update_status_bar_info(self):
        if not hasattr(self, "status_info_label"):
            return
        version_text = self._t("header.version", "Version 2.2")
        db_label = self._t("settings.databasePath", "Database Path:")
        db_path = str(get_database_path())
        info_text = f"{version_text} | {db_label} {db_path} | Create by Pigo Hsiao"
        self.status_info_label.config(text=info_text)
    
    def show_page(self, page_id):
        """顯示指定頁面"""
        if self.nav_locked and page_id != 'daily_report':
            messagebox.showwarning(
                self._t("context.basicInfoRequiredTitle", "尚未儲存基本資訊"),
                self._t("context.basicInfoRequiredBody", "請先在日報表儲存日期、班別、區域後再使用其他功能。")
            )
            return
        # 清除現有內容
        for widget in self.page_content.winfo_children():
            widget.destroy()
        self._clear_page_i18n()
        
        # 更新導航按鈕狀態
        self.update_nav_buttons(page_id)
        
        # 根據頁面ID創建內容
        if page_id == 'daily_report':
            self.create_daily_report_page()
        elif page_id == 'attendance':
            self.create_attendance_page()
        elif page_id == 'equipment':
            self.create_equipment_page()
        elif page_id == 'lot':
            self.create_lot_page()
        elif page_id == 'summary':
            self.create_summary_page()
        elif page_id == 'abnormal_history':
            self.create_abnormal_history_page()
        elif page_id == 'delay_list':
            self.create_delay_list_page()
        elif page_id == 'summary_actual':
            self.create_summary_actual_page()
        elif page_id == 'admin':
            self.create_admin_page()
        
        self.current_page = page_id
        self._update_report_context_label()
    
    def update_nav_buttons(self, active_page):
        """更新導航按鈕狀態"""
        for page_id, button in self.nav_buttons.items():
            if page_id == active_page:
                button.state(['pressed'])
                # 突出顯示活動按鈕
                button.configure(style='SidebarActive.TButton')
            else:
                button.state(['!pressed'])
                button.configure(style='Sidebar.TButton')
    
    def create_daily_report_page(self):
        """創建日報表頁面"""
        self._register_text(self.page_title, "pages.dailyReport.title", "日報表", scope="page")
        self._register_text(self.page_subtitle, "pages.dailyReport.subtitle", "記錄每日生產交接資訊", scope="page")
        
        # 日期與班別卡片
        date_card = self.create_card(self.page_content, '📅', "cards.dateShift", "日期與班別資訊")
        date_card.pack(fill='x', padx=0, pady=(0, 20))
        
        # 表單布局
        form_frame = ttk.Frame(date_card, style='Card.TFrame')
        form_frame.pack(fill='x', padx=self.layout["card_pad"], pady=self.layout["card_pad"])
        
        # 日期
        date_label = ttk.Label(form_frame, font=('Segoe UI', 10))
        self._register_text(date_label, "fields.date", "📅 日期:", scope="page")
        date_label.grid(row=0, column=0, sticky='w', padx=0, pady=self.layout["row_pad"])
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_frame = ttk.Frame(form_frame, style='Card.TFrame')
        date_frame.grid(row=0, column=1, sticky='ew', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        self._create_date_picker(date_frame, self.date_var, width=18)
        
        self._load_shift_area_options()

        # 班別
        shift_values = self._build_shift_display_options()
        self.shift_values = shift_values
        self.shift_combo = self.create_form_row(
            form_frame, 1,
            "fields.shift", "⏰ 班別:",
            'shift',
            widget_type='combo',
            var_name='shift_var',
            values=shift_values,
            default=shift_values[0] if shift_values else ""
        )
        
        # 區域
        self.area_combo = self.create_form_row(
            form_frame, 2,
            "fields.area", "🏭 區域:",
            'area',
            widget_type='combo',
            var_name='area_var',
            values=self.area_options,
            default=self.area_options[0] if self.area_options else ""
        )

        basic_action_frame = ttk.Frame(form_frame, style='Card.TFrame')
        basic_action_frame.grid(row=3, column=0, columnspan=2, sticky='w', pady=(10, 0))
        basic_save_btn = ttk.Button(basic_action_frame, style='Primary.TButton', command=self.save_basic_info)
        self._register_text(basic_save_btn, "actions.saveBasicInfo", "💾 儲存基本資訊", scope="page")
        basic_save_btn.pack(side='left')

        self.date_var.trace_add("write", lambda *_: self._sync_report_context_from_form())
        self.shift_var.trace_add("write", lambda *_: self._sync_report_context_from_form())
        self.area_var.trace_add("write", lambda *_: self._sync_report_context_from_form())
        self._sync_report_context_from_form()
        
        # 基本信息卡片
        basic_card = self.create_card(self.page_content, '📝', "cards.basicSummary", "基本資訊與摘要")
        basic_card.pack(fill='both', expand=True, padx=0, pady=(0, 20))
        
        # Key Machine Output
        key_output_label = ttk.Label(basic_card, style='CardTitle.TLabel')
        self._register_text(key_output_label, "summary.keyOutput", "🔑 Key Machine Output:", scope="page")
        key_output_label.pack(anchor='w', padx=self.layout["card_pad"], pady=(20, 5))
        self.key_output_text = tk.Text(basic_card, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'], wrap="word")
        self._register_text_widget(self.key_output_text)
        self.key_output_text.pack(fill='x', padx=self.layout["card_pad"], pady=(0, 15))
        
        # Key Issues
        key_issues_label = ttk.Label(basic_card, style='CardTitle.TLabel')
        self._register_text(key_issues_label, "summary.issues", "⚠️ Key Issues:", scope="page")
        key_issues_label.pack(anchor='w', padx=self.layout["card_pad"], pady=(15, 5))
        self.key_issues_text = tk.Text(basic_card, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'], wrap="word")
        self._register_text_widget(self.key_issues_text)
        self.key_issues_text.pack(fill='x', padx=self.layout["card_pad"], pady=(0, 15))
        
        # Countermeasures
        counter_label = ttk.Label(basic_card, style='CardTitle.TLabel')
        self._register_text(counter_label, "summary.countermeasures", "✅ Countermeasures:", scope="page")
        counter_label.pack(anchor='w', padx=self.layout["card_pad"], pady=(15, 5))
        self.countermeasures_text = tk.Text(basic_card, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'], wrap="word")
        self._register_text_widget(self.countermeasures_text)
        self.countermeasures_text.pack(fill='x', padx=self.layout["card_pad"], pady=(0, 20))
        
        # 操作按鈕
        button_frame = ttk.Frame(basic_card, style='Card.TFrame')
        button_frame.pack(fill='x', padx=self.layout["card_pad"], pady=(0, 20))
        
        save_btn = ttk.Button(button_frame, style='Primary.TButton', command=self.save_daily_report)
        self._register_text(save_btn, "actions.saveDailyReport", "💾 儲存日報", scope="page")
        save_btn.pack(side='left')
        reset_btn = ttk.Button(button_frame, style='Accent.TButton', command=self.reset_daily_report)
        self._register_text(reset_btn, "actions.resetDailyReport", "🔄 重置", scope="page")
        reset_btn.pack(side='left', padx=(10, 0))
    
    def create_card(self, parent, emoji, title_key, title_default):
        """創建卡片容器"""
        card = ttk.Frame(parent, style='Card.TFrame')
        
        # 卡片標題
        title_frame = ttk.Frame(card, style='Card.TFrame')
        title_frame.pack(fill='x', padx=20, pady=(15, 0))
        
        title_label = ttk.Label(title_frame, style='CardTitle.TLabel')
        self._register_text(title_label, title_key, f"{emoji} {title_default}", scope="page")
        title_label.pack(side='left')
        
        # 分隔線
        sep = ttk.Separator(card, orient='horizontal', style='Line.TSeparator')
        sep.pack(fill='x', padx=20, pady=(10, 0))
        
        # 記錄卡片以便後續引用
        setattr(self, f"{title_default.lower().replace(' ', '_').replace('/', '_')}_card", card)
        
        return card
    
    def create_form_row(self, parent, row, label_key, label_default, field_name, widget_type='entry', **kwargs):
        """創建表單行"""
        label = ttk.Label(parent, font=('Segoe UI', 10))
        self._register_text(label, label_key, label_default, scope="page")
        label.grid(row=row, column=0, sticky='w', padx=0, pady=self.layout["row_pad"])
        
        widget = None
        if widget_type == 'entry':
            var = tk.StringVar(value=kwargs.get('default', ''))
            setattr(self, kwargs['var_name'], var)
            widget = ttk.Entry(parent, textvariable=var, style='Modern.TEntry', width=30)
            widget.grid(row=row, column=1, sticky='ew', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        elif widget_type == 'combo':
            var = tk.StringVar(value=kwargs.get('default', ''))
            setattr(self, kwargs['var_name'], var)
            widget = ttk.Combobox(
                parent,
                textvariable=var,
                values=kwargs['values'],
                state='readonly',
                font=('Segoe UI', 10),
                width=28
            )
            widget.grid(row=row, column=1, sticky='ew', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        parent.columnconfigure(1, weight=1)
        return widget

    def _load_shift_area_options(self):
        shift_defaults = ["Day", "Night"]
        area_defaults = ["etching_D", "etching_E", "litho", "thin_film"]
        try:
            with SessionLocal() as db:
                shifts = [opt.name for opt in db.query(ShiftOption).order_by(ShiftOption.id).all()]
                areas = [opt.name for opt in db.query(AreaOption).order_by(AreaOption.id).all()]
            self.shift_options = shifts or shift_defaults
            self.area_options = areas or area_defaults
        except Exception:
            self.shift_options = shift_defaults
            self.area_options = area_defaults

    def _build_shift_display_options(self):
        day_label = self._t("shift.day", "Day")
        night_label = self._t("shift.night", "Night")
        code_map = {}
        display_map = {}
        display_values = []
        for code in self.shift_options:
            if code == "Day":
                display = day_label
            elif code == "Night":
                display = night_label
            else:
                display = code
            code_map[display] = code
            display_map[code] = display
            display_values.append(display)
        self.shift_code_map = code_map
        self.shift_display_map = display_map
        return display_values

    def _get_month_date_range(self):
        today = datetime.now().date()
        start = today.replace(day=1)
        return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

    def _format_shift_display(self, shift_code):
        if not shift_code:
            return ""
        self._load_shift_area_options()
        self._build_shift_display_options()
        return self.shift_display_map.get(shift_code, shift_code)

    def _update_abnormal_filter_options(self):
        if not hasattr(self, "abnormal_shift_combo") or not hasattr(self, "abnormal_area_combo"):
            return
        if not self.abnormal_shift_combo.winfo_exists() or not self.abnormal_area_combo.winfo_exists():
            return
        self._load_shift_area_options()
        all_labels = {"全部", "All", "すべて"}

        current_display = self.abnormal_shift_var.get().strip()
        current_code = None
        if current_display and current_display not in all_labels:
            current_code = self.shift_code_map.get(current_display, current_display)

        shift_values = self._build_shift_display_options()
        all_label = self._t("common.all", "全部")
        self.abnormal_shift_combo["values"] = [all_label] + shift_values
        if current_code and current_code in self.shift_display_map:
            self.abnormal_shift_var.set(self.shift_display_map[current_code])
        else:
            self.abnormal_shift_var.set(all_label)

        current_area = self.abnormal_area_var.get().strip()
        self.abnormal_area_combo["values"] = [all_label] + self.area_options
        if current_area in self.area_options:
            self.abnormal_area_var.set(current_area)
        else:
            self.abnormal_area_var.set(all_label)

    def _create_date_picker(self, parent, var, width=16):
        entry = ttk.Entry(parent, textvariable=var, style='Modern.TEntry', width=width, state='readonly')
        entry.pack(side='left', fill='x', expand=True)
        button = ttk.Button(parent, text="📅", width=3, command=lambda: self._open_calendar_popup(var))
        button.pack(side='left', padx=(6, 0))
        entry.bind("<Button-1>", lambda _e: self._open_calendar_popup(var))
        return entry, button

    def _open_calendar_popup(self, target_var):
        if hasattr(self, "_calendar_popup") and self._calendar_popup is not None:
            if self._calendar_popup.winfo_exists():
                self._calendar_popup.destroy()
            self._calendar_popup = None

        current = target_var.get().strip()
        today = datetime.now().date()
        try:
            base_date = datetime.strptime(current, "%Y-%m-%d").date() if current else today
        except ValueError:
            base_date = today

        popup = tk.Toplevel(self.parent)
        popup.title(self._t("common.selectDate", "選擇日期"))
        popup.resizable(False, False)
        popup.transient(self.parent)
        popup.configure(background=self.COLORS['background'])
        self._calendar_popup = popup

        header = ttk.Frame(popup, padding=(10, 10, 10, 0))
        header.pack(fill='x')

        current_year = tk.IntVar(value=base_date.year)
        current_month = tk.IntVar(value=base_date.month)

        month_label = ttk.Label(header, font=('Segoe UI', 11, 'bold'))
        month_label.pack(side='left', padx=(10, 0))

        def update_title():
            year = current_year.get()
            month = current_month.get()
            month_label.config(text=f"{year}-{month:02d}")

        def change_month(delta):
            year = current_year.get()
            month = current_month.get() + delta
            if month < 1:
                month = 12
                year -= 1
            elif month > 12:
                month = 1
                year += 1
            current_year.set(year)
            current_month.set(month)
            render_days()

        prev_btn = ttk.Button(header, text="◀", width=3, command=lambda: change_month(-1))
        prev_btn.pack(side='left')
        next_btn = ttk.Button(header, text="▶", width=3, command=lambda: change_month(1))
        next_btn.pack(side='left', padx=(5, 0))

        body = ttk.Frame(popup, padding=10)
        body.pack(fill='both', expand=True)

        weekdays = [
            self._t("calendar.mon", "一"),
            self._t("calendar.tue", "二"),
            self._t("calendar.wed", "三"),
            self._t("calendar.thu", "四"),
            self._t("calendar.fri", "五"),
            self._t("calendar.sat", "六"),
            self._t("calendar.sun", "日"),
        ]

        for idx, day_label in enumerate(weekdays):
            ttk.Label(body, text=day_label).grid(row=0, column=idx, padx=4, pady=2)

        days_frame = ttk.Frame(body)
        days_frame.grid(row=1, column=0, columnspan=7)

        def render_days():
            for child in days_frame.winfo_children():
                child.destroy()
            update_title()
            year = current_year.get()
            month = current_month.get()
            cal = calendar.Calendar(firstweekday=0)
            weeks = cal.monthdayscalendar(year, month)
            for r, week in enumerate(weeks):
                for c, day in enumerate(week):
                    if day == 0:
                        ttk.Label(days_frame, text=" ").grid(row=r, column=c, padx=2, pady=2)
                        continue

                    def select_date(d=day):
                        target_var.set(f"{year}-{month:02d}-{d:02d}")
                        if popup.winfo_exists():
                            popup.destroy()
                        self._calendar_popup = None

                    btn = ttk.Button(days_frame, text=str(day), width=3, command=select_date)
                    btn.grid(row=r, column=c, padx=2, pady=2)

        render_days()

        def on_close():
            if popup.winfo_exists():
                popup.destroy()
            self._calendar_popup = None

        popup.protocol("WM_DELETE_WINDOW", on_close)
    
    def create_attendance_page(self):
        """創建出勤記錄頁面"""
        self._register_text(self.page_title, "pages.attendance.title", "出勤記錄", scope="page")
        self._register_text(self.page_subtitle, "pages.attendance.subtitle", "記錄正社員與契約社員出勤資訊", scope="page")
        
        # 使用優化版出勤組件
        self.attendance_section = AttendanceSectionOptimized(self.page_content, self.lang_manager, self)
        self.attendance_section.get_widget().pack(fill='both', expand=True)
        if self.active_report_id:
            self._load_attendance_entries()
    
    def create_equipment_page(self):
        """創建設備異常頁面"""
        self._register_text(self.page_title, "pages.equipment.title", "設備異常", scope="page")
        self._register_text(self.page_subtitle, "pages.equipment.subtitle", "記錄設備異常與處理資訊", scope="page")
        
        card = self.create_card(self.page_content, '⚙️', "cards.equipmentRecord", "設備異常記錄")
        card.pack(fill='both', expand=True)
        
        # 表單
        form_frame = ttk.Frame(card, style='Card.TFrame')
        form_frame.pack(fill='both', expand=True, padx=self.layout["card_pad"], pady=self.layout["card_pad"])
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        
        # 設備號碼
        equip_id_label = ttk.Label(form_frame, font=('Segoe UI', 10))
        self._register_text(equip_id_label, "equipment.equipId", "設備號碼:", scope="page")
        equip_id_label.grid(row=0, column=0, sticky='w', pady=self.layout["row_pad"])
        self.equip_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.equip_id_var, style='Modern.TEntry').grid(
            row=0, column=1, sticky='ew', padx=self.layout["field_gap"], pady=self.layout["row_pad"]
        )
        
        # 發生時刻
        start_time_label = ttk.Label(form_frame, font=('Segoe UI', 10))
        self._register_text(start_time_label, "equipment.startTime", "發生時刻:", scope="page")
        start_time_label.grid(row=0, column=2, sticky='w', pady=self.layout["row_pad"])
        self.start_time_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.start_time_var, style='Modern.TEntry').grid(
            row=0, column=3, sticky='ew', padx=self.layout["field_gap"], pady=self.layout["row_pad"]
        )
        
        # 影響數量
        impact_label = ttk.Label(form_frame, font=('Segoe UI', 10))
        self._register_text(impact_label, "equipment.impactQty", "影響數量:", scope="page")
        impact_label.grid(row=1, column=0, sticky='w', pady=self.layout["row_pad"])
        self.impact_qty_var = tk.StringVar(value='0')
        ttk.Entry(form_frame, textvariable=self.impact_qty_var, style='Modern.TEntry').grid(
            row=1, column=1, sticky='ew', padx=self.layout["field_gap"], pady=self.layout["row_pad"]
        )
        
        # 異常內容
        desc_label = ttk.Label(form_frame, font=('Segoe UI', 10))
        self._register_text(desc_label, "common.description", "異常內容:", scope="page")
        desc_label.grid(row=2, column=0, sticky='w', pady=self.layout["row_pad"])
        self.equip_desc_text = tk.Text(form_frame, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'], wrap="word")
        self._register_text_widget(self.equip_desc_text)
        self.equip_desc_text.grid(row=2, column=1, columnspan=3, sticky='ew', padx=self.layout["field_gap"], pady=self.layout["row_pad"])
        
        # 對應內容
        action_label = ttk.Label(form_frame, font=('Segoe UI', 10))
        self._register_text(action_label, "equipment.actionTaken", "對應內容:", scope="page")
        action_label.grid(row=3, column=0, sticky='w', pady=self.layout["row_pad"])
        self.action_text = tk.Text(form_frame, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'], wrap="word")
        self._register_text_widget(self.action_text)
        self.action_text.grid(row=3, column=1, columnspan=3, sticky='ew', padx=self.layout["field_gap"], pady=self.layout["row_pad"])
        
        # 圖片上傳
        image_frame = ttk.Frame(form_frame, style='Card.TFrame')
        image_frame.grid(row=4, column=0, columnspan=4, sticky='ew', padx=0, pady=self.layout["row_pad"])
        image_frame.columnconfigure(1, weight=1)
        
        image_label = ttk.Label(image_frame, font=('Segoe UI', 10))
        self._register_text(image_label, "common.image", "異常圖片:", scope="page")
        image_label.pack(side='left')
        self.image_path_var = tk.StringVar()
        ttk.Entry(image_frame, textvariable=self.image_path_var, state='readonly', style='Modern.TEntry').pack(side='left', padx=self.layout["field_gap"], fill='x', expand=True)
        browse_btn = ttk.Button(image_frame, style='Accent.TButton', command=self.browse_image)
        self._register_text(browse_btn, "common.browse", "瀏覽...", scope="page")
        browse_btn.pack(side='left')
        
        # 按鈕
        button_frame = ttk.Frame(card, style='Card.TFrame')
        button_frame.pack(fill='x', padx=self.layout["card_pad"], pady=(0, 20))
        
        add_btn = ttk.Button(button_frame, style='Primary.TButton', command=self.add_equipment_record)
        self._register_text(add_btn, "actions.addEquipment", "➕ 添加記錄", scope="page")
        add_btn.pack(side='left')
        history_btn = ttk.Button(button_frame, style='Accent.TButton', command=self.view_equipment_history)
        self._register_text(history_btn, "actions.viewEquipmentHistory", "📋 查看歷史", scope="page")
        history_btn.pack(side='left', padx=10)
    
    def create_lot_page(self):
        """創建異常批次頁面"""
        self._register_text(self.page_title, "pages.lot.title", "異常批次", scope="page")
        self._register_text(self.page_subtitle, "pages.lot.subtitle", "記錄批次異常與處置狀況", scope="page")
        
        card = self.create_card(self.page_content, '📦', "cards.lotRecord", "異常批次記錄")
        card.pack(fill='both', expand=True)
        
        form_frame = ttk.Frame(card, style='Card.TFrame')
        form_frame.pack(fill='both', expand=True, padx=self.layout["card_pad"], pady=self.layout["card_pad"])
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        
        # 批號
        lot_id_label = ttk.Label(form_frame, font=('Segoe UI', 10))
        self._register_text(lot_id_label, "lot.lotId", "批號:", scope="page")
        lot_id_label.grid(row=0, column=0, sticky='w', pady=self.layout["row_pad"])
        self.lot_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.lot_id_var, style='Modern.TEntry').grid(
            row=0, column=1, sticky='ew', padx=self.layout["field_gap"], pady=self.layout["row_pad"]
        )
        
        # 異常內容
        lot_desc_label = ttk.Label(form_frame, font=('Segoe UI', 10))
        self._register_text(lot_desc_label, "common.description", "異常內容:", scope="page")
        lot_desc_label.grid(row=1, column=0, sticky='w', pady=self.layout["row_pad"])
        self.lot_desc_text = tk.Text(form_frame, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'], wrap="word")
        self._register_text_widget(self.lot_desc_text)
        self.lot_desc_text.grid(row=1, column=1, columnspan=3, sticky='ew', padx=self.layout["field_gap"], pady=self.layout["row_pad"])
        
        # 處置狀況
        status_label = ttk.Label(form_frame, font=('Segoe UI', 10))
        self._register_text(status_label, "lot.status", "處置狀況:", scope="page")
        status_label.grid(row=2, column=0, sticky='w', pady=self.layout["row_pad"])
        self.lot_status_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.lot_status_var, style='Modern.TEntry').grid(
            row=2, column=1, sticky='ew', padx=self.layout["field_gap"], pady=self.layout["row_pad"]
        )
        
        # 特記事項
        notes_label = ttk.Label(form_frame, font=('Segoe UI', 10))
        self._register_text(notes_label, "lot.notes", "特記事項:", scope="page")
        notes_label.grid(row=3, column=0, sticky='w', pady=self.layout["row_pad"])
        self.lot_notes_text = tk.Text(form_frame, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'], wrap="word")
        self._register_text_widget(self.lot_notes_text)
        self.lot_notes_text.grid(row=3, column=1, columnspan=3, sticky='ew', padx=self.layout["field_gap"], pady=self.layout["row_pad"])
        
        # 按鈕
        button_frame = ttk.Frame(card, style='Card.TFrame')
        button_frame.pack(fill='x', padx=self.layout["card_pad"], pady=(0, 20))
        
        add_btn = ttk.Button(button_frame, style='Primary.TButton', command=self.add_lot_record)
        self._register_text(add_btn, "actions.addLot", "➕ 添加批次", scope="page")
        add_btn.pack(side='left')
        list_btn = ttk.Button(button_frame, style='Accent.TButton', command=self.view_lot_list)
        self._register_text(list_btn, "actions.viewLotList", "📋 批次列表", scope="page")
        list_btn.pack(side='left', padx=10)
    
    def create_summary_page(self):
        """創建總結頁面"""
        self._register_text(self.page_title, "pages.summary.title", "出勤統計", scope="page")
        self._register_text(self.page_subtitle, "pages.summary.subtitle", "依日期區間彙整出勤資訊", scope="page")

        self._summary_scroll_setup()
        control_card = self.create_card(self.summary_scroll_frame, '👥', "cards.attendanceSummary", "出勤統計")
        control_card.pack(fill='x', pady=(0, 20))

        control_frame = ttk.Frame(control_card, style='Card.TFrame')
        control_frame.pack(fill='x', padx=self.layout["card_pad"], pady=self.layout["card_pad"])

        start_label = ttk.Label(control_frame, font=('Segoe UI', 10))
        self._register_text(start_label, "summaryDashboard.startDate", "統計開始日期", scope="page")
        start_label.grid(row=0, column=0, sticky='w', pady=self.layout["row_pad"])
        self.summary_dash_start_var = tk.StringVar()
        start_frame = ttk.Frame(control_frame, style='Card.TFrame')
        start_frame.grid(row=0, column=1, sticky='w', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        self._create_date_picker(start_frame, self.summary_dash_start_var, width=14)

        end_label = ttk.Label(control_frame, font=('Segoe UI', 10))
        self._register_text(end_label, "summaryDashboard.endDate", "統計結束日期", scope="page")
        end_label.grid(row=0, column=2, sticky='w', padx=(20, 0), pady=self.layout["row_pad"])
        self.summary_dash_end_var = tk.StringVar()
        end_frame = ttk.Frame(control_frame, style='Card.TFrame')
        end_frame.grid(row=0, column=3, sticky='w', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        self._create_date_picker(end_frame, self.summary_dash_end_var, width=14)

        confirm_btn = ttk.Button(control_frame, style='Primary.TButton', command=self._load_summary_dashboard)
        self._register_text(confirm_btn, "summaryDashboard.confirm", "確定", scope="page")
        confirm_btn.grid(row=0, column=4, padx=(20, 0), pady=self.layout["row_pad"])

        self.summary_hint_label = ttk.Label(control_frame, font=('Segoe UI', 9), foreground=self.COLORS['text_secondary'])
        self._register_text(self.summary_hint_label, "summaryDashboard.hint", "選擇日期區間後按下確定以產生統計結果", scope="page")
        self.summary_hint_label.grid(row=1, column=0, columnspan=5, sticky='w')

        start_default, end_default = self._get_month_date_range()
        self.summary_dash_start_var.set(start_default)
        self.summary_dash_end_var.set(end_default)

        table_card = self.create_card(self.summary_scroll_frame, '📋', "cards.attendanceTable", "出勤統計表")
        table_card.pack(fill='both', expand=True, pady=(0, 20))

        table_frame = ttk.Frame(table_card, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=self.layout["card_pad"], pady=self.layout["card_pad"])

        cols = (
            "date",
            "area",
            "author",
            "regular_present",
            "regular_absent",
            "contract_present",
            "contract_absent",
            "notes",
        )
        self.summary_dash_columns = cols
        self.summary_dash_header_keys = [
            ("common.date", "日期"),
            ("common.area", "區域"),
            ("common.author", "填寫者"),
            ("summaryDashboard.regularPresent", "正職出勤"),
            ("summaryDashboard.regularAbsent", "正職缺勤"),
            ("summaryDashboard.contractPresent", "契約出勤"),
            ("summaryDashboard.contractAbsent", "契約缺勤"),
            ("common.notes", "備註"),
        ]

        self.summary_dash_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=12)
        self._update_summary_dashboard_headers()
        self.summary_dash_tree.pack(side='left', fill='both', expand=True)
        table_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.summary_dash_tree.yview)
        self.summary_dash_tree.configure(yscrollcommand=table_scroll.set)
        table_scroll.pack(side="right", fill="y")

        charts_card = self.create_card(self.summary_scroll_frame, '📊', "cards.attendanceCharts", "出勤圖表")
        charts_card.pack(fill='both', expand=True)

        charts_frame = ttk.Frame(charts_card, style='Card.TFrame')
        charts_frame.pack(fill='both', expand=True, padx=self.layout["card_pad"], pady=self.layout["card_pad"])
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.columnconfigure(1, weight=1)

        self.summary_pie_frame = ttk.Frame(charts_frame, style='Card.TFrame')
        self.summary_pie_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        self.summary_bar_frame = ttk.Frame(charts_frame, style='Card.TFrame')
        self.summary_bar_frame.grid(row=0, column=1, sticky='nsew')

        self.summary_pie_canvas = None
        self.summary_bar_canvas = None
        self.summary_dashboard_data = None
        self._render_summary_charts(None)

    def create_abnormal_history_page(self):
        """創建異常歷史查詢頁面"""
        self._register_text(self.page_title, "pages.abnormalHistory.title", "異常歷史查詢", scope="page")
        self._register_text(self.page_subtitle, "pages.abnormalHistory.subtitle", "查詢設備異常與異常批次歷史", scope="page")

        self._abnormal_scroll_setup()
        control_card = self.create_card(self.abnormal_scroll_frame, '🗂️', "cards.abnormalHistorySearch", "異常歷史查詢")
        control_card.pack(fill='x', pady=(0, 20))

        control_frame = ttk.Frame(control_card, style='Card.TFrame')
        control_frame.pack(fill='x', padx=self.layout["card_pad"], pady=self.layout["card_pad"])

        start_label = ttk.Label(control_frame, font=('Segoe UI', 10))
        self._register_text(start_label, "abnormalHistory.startDate", "統計開始日期", scope="page")
        start_label.grid(row=0, column=0, sticky='w', pady=self.layout["row_pad"])
        self.abnormal_start_var = tk.StringVar()
        start_frame = ttk.Frame(control_frame, style='Card.TFrame')
        start_frame.grid(row=0, column=1, sticky='w', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        self._create_date_picker(start_frame, self.abnormal_start_var, width=14)

        end_label = ttk.Label(control_frame, font=('Segoe UI', 10))
        self._register_text(end_label, "abnormalHistory.endDate", "統計結束日期", scope="page")
        end_label.grid(row=0, column=2, sticky='w', padx=(20, 0), pady=self.layout["row_pad"])
        self.abnormal_end_var = tk.StringVar()
        end_frame = ttk.Frame(control_frame, style='Card.TFrame')
        end_frame.grid(row=0, column=3, sticky='w', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        self._create_date_picker(end_frame, self.abnormal_end_var, width=14)

        search_btn = ttk.Button(control_frame, style='Primary.TButton', command=self._load_abnormal_history)
        self._register_text(search_btn, "common.search", "搜尋", scope="page")
        search_btn.grid(row=0, column=4, padx=(20, 0), pady=self.layout["row_pad"])

        shift_label = ttk.Label(control_frame, font=('Segoe UI', 10))
        self._register_text(shift_label, "fields.shift", "⏰ 班別:", scope="page")
        shift_label.grid(row=1, column=0, sticky='w', pady=self.layout["row_pad"])
        self.abnormal_shift_var = tk.StringVar()
        self.abnormal_shift_combo = ttk.Combobox(control_frame, textvariable=self.abnormal_shift_var, state='readonly', width=16)
        self.abnormal_shift_combo.grid(row=1, column=1, sticky='w', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])

        area_label = ttk.Label(control_frame, font=('Segoe UI', 10))
        self._register_text(area_label, "fields.area", "🏭 區域:", scope="page")
        area_label.grid(row=1, column=2, sticky='w', padx=(20, 0), pady=self.layout["row_pad"])
        self.abnormal_area_var = tk.StringVar()
        self.abnormal_area_combo = ttk.Combobox(control_frame, textvariable=self.abnormal_area_var, state='readonly', width=16)
        self.abnormal_area_combo.grid(row=1, column=3, sticky='w', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])

        start_default, end_default = self._get_month_date_range()
        self.abnormal_start_var.set(start_default)
        self.abnormal_end_var.set(end_default)
        self._update_abnormal_filter_options()

        equipment_card = self.create_card(self.abnormal_scroll_frame, '⚙️', "cards.abnormalEquipmentHistory", "設備異常歷史")
        equipment_card.pack(fill='both', expand=True, pady=(0, 20))

        equipment_frame = ttk.Frame(equipment_card, style='Card.TFrame')
        equipment_frame.pack(fill='both', expand=True, padx=self.layout["card_pad"], pady=self.layout["card_pad"])

        eq_cols = (
            "date",
            "shift",
            "area",
            "author",
            "equip_id",
            "description",
            "start_time",
            "impact_qty",
            "action_taken",
            "image_path",
        )
        self.abnormal_equipment_columns = eq_cols
        self.abnormal_equipment_header_keys = [
            ("common.date", "日期"),
            ("common.shift", "班別"),
            ("common.area", "區域"),
            ("common.author", "填寫者"),
            ("equipment.equipId", "設備號碼"),
            ("common.description", "異常內容"),
            ("equipment.startTime", "發生時刻"),
            ("equipment.impactQty", "影響數量"),
            ("equipment.actionTaken", "對應內容"),
            ("common.image", "異常圖片"),
        ]

        self.abnormal_equipment_tree = ttk.Treeview(equipment_frame, columns=eq_cols, show="headings", height=8)
        self._update_abnormal_history_headers()
        self.abnormal_equipment_tree.pack(side='left', fill='both', expand=True)
        eq_scroll = ttk.Scrollbar(equipment_frame, orient="vertical", command=self.abnormal_equipment_tree.yview)
        self.abnormal_equipment_tree.configure(yscrollcommand=eq_scroll.set)
        eq_scroll.pack(side="right", fill="y")

        lot_card = self.create_card(self.abnormal_scroll_frame, '📦', "cards.abnormalLotHistory", "異常批次歷史")
        lot_card.pack(fill='both', expand=True)

        lot_frame = ttk.Frame(lot_card, style='Card.TFrame')
        lot_frame.pack(fill='both', expand=True, padx=self.layout["card_pad"], pady=self.layout["card_pad"])

        lot_cols = (
            "date",
            "shift",
            "area",
            "author",
            "lot_id",
            "description",
            "status",
            "notes",
        )
        self.abnormal_lot_columns = lot_cols
        self.abnormal_lot_header_keys = [
            ("common.date", "日期"),
            ("common.shift", "班別"),
            ("common.area", "區域"),
            ("common.author", "填寫者"),
            ("lot.lotId", "批號"),
            ("common.description", "異常內容"),
            ("lot.status", "處置狀況"),
            ("lot.notes", "特記事項"),
        ]

        self.abnormal_lot_tree = ttk.Treeview(lot_frame, columns=lot_cols, show="headings", height=8)
        self._update_abnormal_history_headers()
        self.abnormal_lot_tree.pack(side='left', fill='both', expand=True)
        lot_scroll = ttk.Scrollbar(lot_frame, orient="vertical", command=self.abnormal_lot_tree.yview)
        self.abnormal_lot_tree.configure(yscrollcommand=lot_scroll.set)
        lot_scroll.pack(side="right", fill="y")

        self._load_abnormal_history()

    def _abnormal_scroll_setup(self):
        self.abnormal_scroll_canvas = tk.Canvas(
            self.page_content,
            background=self.COLORS['background'],
            highlightthickness=0
        )
        self._register_canvas_widget(self.abnormal_scroll_canvas, "background")
        self.abnormal_scroll_canvas.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(self.page_content, orient="vertical", command=self.abnormal_scroll_canvas.yview)
        scroll.pack(side="right", fill="y")
        self.abnormal_scroll_canvas.configure(yscrollcommand=scroll.set)
        self.abnormal_scroll_frame = ttk.Frame(self.abnormal_scroll_canvas, style='Modern.TFrame')
        self.abnormal_scroll_window = self.abnormal_scroll_canvas.create_window(
            (0, 0),
            window=self.abnormal_scroll_frame,
            anchor="nw"
        )

        def _on_frame_config(_event):
            self.abnormal_scroll_canvas.configure(scrollregion=self.abnormal_scroll_canvas.bbox("all"))

        def _on_canvas_config(event):
            self.abnormal_scroll_canvas.itemconfigure(self.abnormal_scroll_window, width=event.width)

        self.abnormal_scroll_frame.bind("<Configure>", _on_frame_config)
        self.abnormal_scroll_canvas.bind("<Configure>", _on_canvas_config)
        self._bind_canvas_mousewheel(self.abnormal_scroll_frame, self.abnormal_scroll_canvas)

    def _summary_scroll_setup(self):
        self.summary_scroll_canvas = tk.Canvas(
            self.page_content,
            background=self.COLORS['background'],
            highlightthickness=0
        )
        self._register_canvas_widget(self.summary_scroll_canvas, "background")
        self.summary_scroll_canvas.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(self.page_content, orient="vertical", command=self.summary_scroll_canvas.yview)
        scroll.pack(side="right", fill="y")
        self.summary_scroll_canvas.configure(yscrollcommand=scroll.set)
        self.summary_scroll_frame = ttk.Frame(self.summary_scroll_canvas, style='Modern.TFrame')
        self.summary_scroll_window = self.summary_scroll_canvas.create_window(
            (0, 0),
            window=self.summary_scroll_frame,
            anchor="nw"
        )

        def _on_frame_config(_event):
            self.summary_scroll_canvas.configure(scrollregion=self.summary_scroll_canvas.bbox("all"))

        def _on_canvas_config(event):
            self.summary_scroll_canvas.itemconfigure(self.summary_scroll_window, width=event.width)

        self.summary_scroll_frame.bind("<Configure>", _on_frame_config)
        self.summary_scroll_canvas.bind("<Configure>", _on_canvas_config)
        self._bind_canvas_mousewheel(self.summary_scroll_frame, self.summary_scroll_canvas)

    def _bind_canvas_mousewheel(self, widget, canvas):
        def _on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        def _on_enter(_event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

        def _on_leave(_event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        widget.bind("<Enter>", _on_enter)
        widget.bind("<Leave>", _on_leave)

    def _update_summary_dashboard_headers(self):
        if not hasattr(self, "summary_dash_tree"):
            return
        for col, (key, default) in zip(self.summary_dash_columns, self.summary_dash_header_keys):
            self.summary_dash_tree.heading(col, text=self._t(key, default))
        widths = {
            "date": 110,
            "area": 120,
            "author": 140,
            "regular_present": 90,
            "regular_absent": 90,
            "contract_present": 90,
            "contract_absent": 90,
            "notes": 260,
        }
        anchors = {
            "date": "center",
            "area": "center",
            "author": "center",
            "regular_present": "center",
            "regular_absent": "center",
            "contract_present": "center",
            "contract_absent": "center",
            "notes": "w",
        }
        for col in self.summary_dash_columns:
            self.summary_dash_tree.column(col, width=widths.get(col, 100), stretch=(col == "notes"), anchor=anchors.get(col, "center"))

    def _update_abnormal_history_headers(self):
        if hasattr(self, "abnormal_equipment_tree"):
            for col, (key, default) in zip(self.abnormal_equipment_columns, self.abnormal_equipment_header_keys):
                self.abnormal_equipment_tree.heading(col, text=self._t(key, default))
            widths = {
                "date": 100,
                "shift": 80,
                "area": 110,
                "author": 120,
                "equip_id": 110,
                "description": 200,
                "start_time": 100,
                "impact_qty": 80,
                "action_taken": 180,
                "image_path": 160,
            }
            for col in self.abnormal_equipment_columns:
                self.abnormal_equipment_tree.column(
                    col,
                    width=widths.get(col, 100),
                    stretch=col in ("description", "action_taken", "image_path"),
                    anchor="w" if col in ("description", "action_taken", "image_path") else "center",
                )
        if hasattr(self, "abnormal_lot_tree"):
            for col, (key, default) in zip(self.abnormal_lot_columns, self.abnormal_lot_header_keys):
                self.abnormal_lot_tree.heading(col, text=self._t(key, default))
            widths = {
                "date": 100,
                "shift": 80,
                "area": 110,
                "author": 120,
                "lot_id": 100,
                "description": 200,
                "status": 140,
                "notes": 180,
            }
            for col in self.abnormal_lot_columns:
                self.abnormal_lot_tree.column(
                    col,
                    width=widths.get(col, 100),
                    stretch=col in ("description", "status", "notes"),
                    anchor="w" if col in ("description", "status", "notes") else "center",
                )

    def _build_attendance_notes(self, regular_reason, contract_reason):
        parts = []
        regular_label = self._t("attendance.regular_short", "正職")
        contract_label = self._t("attendance.contractor_short", "契約")
        if regular_reason:
            parts.append(f"{regular_label}: {regular_reason}")
        if contract_reason:
            parts.append(f"{contract_label}: {contract_reason}")
        return " / ".join(parts)

    def _load_summary_dashboard(self):
        if not hasattr(self, "summary_dash_tree"):
            return
        self._clear_tree(self.summary_dash_tree)
        start = self.summary_dash_start_var.get().strip()
        end = self.summary_dash_end_var.get().strip()
        if not start or not end:
            messagebox.showwarning(
                self._t("common.warning", "提醒"),
                self._t("summaryDashboard.missingRange", "請先選擇統計開始日期與結束日期。")
            )
            self.summary_dashboard_data = None
            self._render_summary_charts(None)
            return
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning(
                self._t("common.warning", "提醒"),
                self._t("errors.invalidDateFormat", "日期格式需為 YYYY-MM-DD")
            )
            self.summary_dashboard_data = None
            self._render_summary_charts(None)
            return
        if end_date < start_date:
            messagebox.showwarning(
                self._t("common.warning", "提醒"),
                self._t("summaryDashboard.invalidRange", "結束日期不可早於開始日期。")
            )
            self.summary_dashboard_data = None
            self._render_summary_charts(None)
            return

        try:
            with SessionLocal() as db:
                reports = (
                    db.query(DailyReport)
                    .options(joinedload(DailyReport.author))
                    .filter(DailyReport.date >= start_date, DailyReport.date <= end_date)
                    .order_by(DailyReport.date, DailyReport.area)
                    .all()
                )
                if not reports:
                    self.summary_dashboard_data = None
                    self._render_summary_charts(None)
                    messagebox.showinfo(
                        self._t("common.info", "資訊"),
                        self._t("common.emptyData", "查無資料")
                    )
                    return
                report_ids = [report.id for report in reports]
                attendance_rows = (
                    db.query(AttendanceEntry)
                    .filter(AttendanceEntry.report_id.in_(report_ids))
                    .all()
                )

            attendance_by_report = {}
            for report in reports:
                attendance_by_report[report.id] = {
                    "regular": {"present": 0, "absent": 0, "reason": ""},
                    "contract": {"present": 0, "absent": 0, "reason": ""},
                }

            for row in attendance_rows:
                category = (row.category or "").lower()
                bucket = "regular" if category.startswith("reg") else "contract"
                target = attendance_by_report.get(row.report_id)
                if not target:
                    continue
                slot = target[bucket]
                slot["present"] += int(row.present_count or 0)
                slot["absent"] += int(row.absent_count or 0)
                reason = (row.reason or "").strip()
                if reason:
                    if slot["reason"]:
                        slot["reason"] = f"{slot['reason']} / {reason}"
                    else:
                        slot["reason"] = reason

            total_present = 0
            total_absent = 0
            daily_counts = defaultdict(lambda: {"regular": 0, "contract": 0, "present": 0, "absent": 0})

            for report in reports:
                data = attendance_by_report.get(report.id, {})
                regular = data.get("regular", {})
                contract = data.get("contract", {})
                regular_present = regular.get("present", 0)
                regular_absent = regular.get("absent", 0)
                contract_present = contract.get("present", 0)
                contract_absent = contract.get("absent", 0)
                notes = self._build_attendance_notes(regular.get("reason", ""), contract.get("reason", ""))
                author_name = report.author.username if report.author else ""

                self.summary_dash_tree.insert(
                    "",
                    "end",
                    values=(
                        report.date.strftime("%Y-%m-%d"),
                        report.area,
                        author_name,
                        regular_present,
                        regular_absent,
                        contract_present,
                        contract_absent,
                        notes,
                    ),
                )

                total_present += regular_present + contract_present
                total_absent += regular_absent + contract_absent
                daily_counts[report.date]["regular"] += regular_present
                daily_counts[report.date]["contract"] += contract_present
                daily_counts[report.date]["present"] += regular_present + contract_present
                daily_counts[report.date]["absent"] += regular_absent + contract_absent

            daily_series = []
            for date_key in sorted(daily_counts.keys()):
                daily_series.append(
                    {
                        "date": date_key,
                        "regular": daily_counts[date_key]["regular"],
                        "contract": daily_counts[date_key]["contract"],
                        "present": daily_counts[date_key]["present"],
                        "absent": daily_counts[date_key]["absent"],
                    }
                )

            self.summary_dashboard_data = {
                "total_present": total_present,
                "total_absent": total_absent,
                "daily_series": daily_series,
            }
            self._render_summary_charts(self.summary_dashboard_data)
        except Exception as exc:
            self.summary_dashboard_data = None
            self._render_summary_charts(None)
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("summaryDashboard.loadFailed", "統計載入失敗：{error}").format(error=exc)
            )

    def _load_abnormal_history(self):
        if not hasattr(self, "abnormal_equipment_tree") or not hasattr(self, "abnormal_lot_tree"):
            return
        self._clear_tree(self.abnormal_equipment_tree)
        self._clear_tree(self.abnormal_lot_tree)

        start = self.abnormal_start_var.get().strip()
        end = self.abnormal_end_var.get().strip()
        if not start or not end:
            messagebox.showwarning(
                self._t("common.warning", "提醒"),
                self._t("abnormalHistory.missingRange", "請先選擇統計開始日期與結束日期。")
            )
            return
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning(
                self._t("common.warning", "提醒"),
                self._t("errors.invalidDateFormat", "日期格式需為 YYYY-MM-DD")
            )
            return
        if end_date < start_date:
            messagebox.showwarning(
                self._t("common.warning", "提醒"),
                self._t("abnormalHistory.invalidRange", "結束日期不可早於開始日期。")
            )
            return

        try:
            with SessionLocal() as db:
                all_label = self._t("common.all", "全部")
                shift_display = self.abnormal_shift_var.get().strip()
                area_value = self.abnormal_area_var.get().strip()
                shift_code = None
                if shift_display and shift_display not in {"全部", "All", "すべて", all_label}:
                    shift_code = self.shift_code_map.get(shift_display, shift_display)
                if area_value in {"全部", "All", "すべて", all_label}:
                    area_value = None

                equipment_query = (
                    db.query(EquipmentLog)
                    .join(DailyReport)
                    .options(joinedload(EquipmentLog.report).joinedload(DailyReport.author))
                    .filter(DailyReport.date >= start_date, DailyReport.date <= end_date)
                )
                if shift_code:
                    equipment_query = equipment_query.filter(DailyReport.shift == shift_code)
                if area_value:
                    equipment_query = equipment_query.filter(DailyReport.area == area_value)
                equipment_rows = equipment_query.order_by(DailyReport.date.desc(), DailyReport.area, EquipmentLog.id).all()

                lot_query = (
                    db.query(LotLog)
                    .join(DailyReport)
                    .options(joinedload(LotLog.report).joinedload(DailyReport.author))
                    .filter(DailyReport.date >= start_date, DailyReport.date <= end_date)
                )
                if shift_code:
                    lot_query = lot_query.filter(DailyReport.shift == shift_code)
                if area_value:
                    lot_query = lot_query.filter(DailyReport.area == area_value)
                lot_rows = lot_query.order_by(DailyReport.date.desc(), DailyReport.area, LotLog.id).all()

            for row in equipment_rows:
                report = row.report
                if not report:
                    continue
                shift_display = self._format_shift_display(report.shift)
                author_name = report.author.username if report.author else ""
                self.abnormal_equipment_tree.insert(
                    "",
                    "end",
                    values=(
                        report.date.strftime("%Y-%m-%d"),
                        shift_display,
                        report.area,
                        author_name,
                        row.equip_id,
                        row.description,
                        row.start_time,
                        row.impact_qty,
                        row.action_taken,
                        row.image_path or "",
                    ),
                )

            for row in lot_rows:
                report = row.report
                if not report:
                    continue
                shift_display = self._format_shift_display(report.shift)
                author_name = report.author.username if report.author else ""
                self.abnormal_lot_tree.insert(
                    "",
                    "end",
                    values=(
                        report.date.strftime("%Y-%m-%d"),
                        shift_display,
                        report.area,
                        author_name,
                        row.lot_id,
                        row.description,
                        row.status,
                        row.notes,
                    ),
                )

            if not equipment_rows and not lot_rows:
                messagebox.showinfo(
                    self._t("common.info", "資訊"),
                    self._t("common.emptyData", "查無資料")
                )
        except Exception as exc:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("abnormalHistory.loadFailed", "查詢失敗：{error}").format(error=exc)
            )

    def _ensure_cjk_font(self):
        if self._cjk_font_ready:
            return
        candidates = [
            "Noto Sans CJK TC",
            "Noto Sans CJK JP",
            "Noto Sans CJK SC",
            "Noto Sans TC",
            "Noto Sans JP",
            "Microsoft YaHei",
            "PingFang TC",
            "PingFang SC",
            "Heiti TC",
            "Hiragino Sans",
            "Yu Gothic",
            "MS Gothic",
            "IPAexGothic",
            "IPAGothic",
            "SimHei",
            "Arial Unicode MS",
        ]
        rcParams["font.family"] = "sans-serif"
        rcParams["font.sans-serif"] = candidates + ["DejaVu Sans"]
        rcParams["axes.unicode_minus"] = False
        self._cjk_font_ready = True

    def _get_chart_theme(self):
        colors = self.COLORS
        return {
            "face": colors['surface'],
            "grid": colors['divider'],
            "text": colors['text_primary'],
            "line": colors['success'],
            "bar_primary": colors['primary'],
            "bar_accent": colors['accent'],
        }

    def _apply_chart_axes_theme(self, ax, theme):
        ax.set_facecolor(theme["face"])
        ax.tick_params(axis="x", colors=theme["text"])
        ax.tick_params(axis="y", colors=theme["text"])
        ax.title.set_color(theme["text"])
        ax.xaxis.label.set_color(theme["text"])
        ax.yaxis.label.set_color(theme["text"])
        for spine in ax.spines.values():
            spine.set_color(theme["grid"])

    def _clear_summary_charts(self):
        for frame in (getattr(self, "summary_pie_frame", None), getattr(self, "summary_bar_frame", None)):
            if not frame or not frame.winfo_exists():
                continue
            for child in frame.winfo_children():
                child.destroy()
        self.summary_pie_canvas = None
        self.summary_bar_canvas = None

    def _render_summary_charts(self, data):
        self._clear_summary_charts()
        if not data:
            empty_text = self._t("common.emptyData", "查無資料")
            if hasattr(self, "summary_pie_frame"):
                ttk.Label(self.summary_pie_frame, text=empty_text, font=('Segoe UI', 10)).pack(expand=True)
            if hasattr(self, "summary_bar_frame"):
                ttk.Label(self.summary_bar_frame, text=empty_text, font=('Segoe UI', 10)).pack(expand=True)
            return

        self._ensure_cjk_font()
        theme = self._get_chart_theme()

        daily_series = data.get("daily_series", [])
        labels = [item["date"].strftime("%Y-%m-%d") for item in daily_series]
        regular_values = [item["regular"] for item in daily_series]
        contract_values = [item["contract"] for item in daily_series]
        rate_values = []
        for item in daily_series:
            total = item.get("present", 0) + item.get("absent", 0)
            rate_values.append((item.get("present", 0) / total * 100) if total else 0)

        line_fig = Figure(figsize=(4.2, 3.2), dpi=100)
        line_fig.patch.set_facecolor(theme["face"])
        line_ax = line_fig.add_subplot(111)
        self._apply_chart_axes_theme(line_ax, theme)
        line_ax.set_title(self._t("summaryDashboard.rateLineTitle", "出勤率趨勢"))
        if labels:
            x = range(len(labels))
            line_ax.plot(
                list(x),
                rate_values,
                marker="o",
                color=theme["line"],
                label=self._t("summaryDashboard.rateSeries", "出勤率"),
            )
            line_ax.set_xticks(list(x))
            line_ax.set_xticklabels(labels, rotation=45, ha="right")
            line_ax.set_ylabel(self._t("summaryDashboard.rateAxis", "出勤率 (%)"))
            line_ax.set_ylim(0, 100)
            legend = line_ax.legend(loc="upper right")
            legend.get_frame().set_facecolor(theme["face"])
            legend.get_frame().set_edgecolor(theme["grid"])
            for text in legend.get_texts():
                text.set_color(theme["text"])
        else:
            line_ax.text(
                0.5,
                0.5,
                self._t("common.emptyData", "查無資料"),
                ha="center",
                va="center",
                color=theme["text"],
            )
        line_fig.tight_layout()
        self.summary_pie_canvas = FigureCanvasTkAgg(line_fig, master=self.summary_pie_frame)
        self.summary_pie_canvas.draw()
        self.summary_pie_canvas.get_tk_widget().configure(background=theme["face"])
        self.summary_pie_canvas.get_tk_widget().pack(fill='both', expand=True)

        bar_fig = Figure(figsize=(4.6, 3.2), dpi=100)
        bar_fig.patch.set_facecolor(theme["face"])
        bar_ax = bar_fig.add_subplot(111)
        self._apply_chart_axes_theme(bar_ax, theme)
        bar_ax.set_title(self._t("summaryDashboard.countChartTitle", "出勤人數"))

        if labels:
            x = range(len(labels))
            bar_ax.bar(x, regular_values, label=self._t("attendance.regular_short", "正職"), color=theme["bar_primary"])
            bar_ax.bar(
                x,
                contract_values,
                bottom=regular_values,
                label=self._t("attendance.contractor_short", "契約"),
                color=theme["bar_accent"],
            )
            bar_ax.set_xticks(list(x))
            bar_ax.set_xticklabels(labels, rotation=45, ha="right")
            bar_ax.set_ylabel(self._t("summaryDashboard.countAxis", "出勤人數"))
            legend = bar_ax.legend(loc="upper right")
            legend.get_frame().set_facecolor(theme["face"])
            legend.get_frame().set_edgecolor(theme["grid"])
            for text in legend.get_texts():
                text.set_color(theme["text"])
        else:
            bar_ax.text(
                0.5,
                0.5,
                self._t("common.emptyData", "查無資料"),
                ha="center",
                va="center",
                color=theme["text"],
            )
        bar_fig.tight_layout()
        self.summary_bar_canvas = FigureCanvasTkAgg(bar_fig, master=self.summary_bar_frame)
        self.summary_bar_canvas.draw()
        self.summary_bar_canvas.get_tk_widget().configure(background=theme["face"])
        self.summary_bar_canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_delay_list_page(self):
        """創建延遲清單頁面"""
        self._register_text(self.page_title, "pages.delayList.title", "延遲清單", scope="page")
        self._register_text(self.page_subtitle, "pages.delayList.subtitle", "延遲清單匯入與查詢", scope="page")

        control_card = self.create_card(self.page_content, '⏱️', "cards.delayList", "延遲清單")
        control_card.pack(fill='x', padx=0, pady=(0, 20))

        control_frame = ttk.Frame(control_card, style='Card.TFrame')
        control_frame.pack(fill='x', padx=self.layout["card_pad"], pady=self.layout["card_pad"])

        start_label = ttk.Label(control_frame, font=('Segoe UI', 10))
        self._register_text(start_label, "delay.startDate", "起日", scope="page")
        start_label.grid(row=0, column=0, sticky='w', pady=self.layout["row_pad"])
        self.delay_start_var = tk.StringVar()
        start_frame = ttk.Frame(control_frame, style='Card.TFrame')
        start_frame.grid(row=0, column=1, sticky='w', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        self._create_date_picker(start_frame, self.delay_start_var, width=14)

        end_label = ttk.Label(control_frame, font=('Segoe UI', 10))
        self._register_text(end_label, "delay.endDate", "迄日", scope="page")
        end_label.grid(row=0, column=2, sticky='w', padx=(20, 0), pady=self.layout["row_pad"])
        self.delay_end_var = tk.StringVar()
        end_frame = ttk.Frame(control_frame, style='Card.TFrame')
        end_frame.grid(row=0, column=3, sticky='w', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        self._create_date_picker(end_frame, self.delay_end_var, width=14)
        self._apply_report_date_to_filters()

        search_btn = ttk.Button(control_frame, style='Accent.TButton', command=self._load_delay_entries)
        self._register_text(search_btn, "common.search", "搜尋", scope="page")
        search_btn.grid(row=0, column=4, padx=(20, 0), pady=self.layout["row_pad"])

        import_btn = ttk.Button(control_frame, style='Accent.TButton', command=self._import_delay_excel)
        self._register_text(import_btn, "delay.importExcel", "匯入延遲Excel", scope="page")
        import_btn.grid(row=1, column=0, pady=self.layout["row_pad"])

        upload_btn = ttk.Button(control_frame, style='Primary.TButton', command=self._upload_delay_pending)
        self._register_text(upload_btn, "delay.confirmUpload", "確認上傳", scope="page")
        upload_btn.grid(row=1, column=1, padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])

        refresh_btn = ttk.Button(control_frame, style='Accent.TButton', command=self._load_delay_entries)
        self._register_text(refresh_btn, "delay.refresh", "重新整理", scope="page")
        refresh_btn.grid(row=1, column=2, padx=(20, 0), pady=self.layout["row_pad"])

        clear_btn = ttk.Button(
            control_frame,
            style='Accent.TButton',
            command=lambda: self._clear_delay_view(),
        )
        self._register_text(clear_btn, "delay.clear", "清除畫面", scope="page")
        clear_btn.grid(row=1, column=3, padx=(20, 0), pady=self.layout["row_pad"])

        table_card = self.create_card(self.page_content, '📋', "cards.delayListTable", "延遲清單資料")
        table_card.pack(fill='both', expand=True)

        table_frame = ttk.Frame(table_card, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=self.layout["card_pad"], pady=self.layout["card_pad"])

        cols = (
            "id",
            "date",
            "time",
            "reactor",
            "process",
            "lot",
            "wafer",
            "progress",
            "prev_steps",
            "prev_time",
            "severity",
            "action",
            "note",
        )
        self.delay_columns = cols
        self.delay_header_keys = [
            ("common.id", "ID"),
            ("delay.date", "日期"),
            ("delay.time", "時間"),
            ("delay.reactor", "設備"),
            ("delay.process", "製程"),
            ("delay.lot", "批號"),
            ("delay.wafer", "晶圓"),
            ("delay.progress", "進行中"),
            ("delay.prevSteps", "前站"),
            ("delay.prevTime", "前站時間"),
            ("delay.severity", "嚴重度"),
            ("delay.action", "對應內容"),
            ("delay.note", "備註"),
        ]

        self.delay_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)
        self._update_delay_headers()
        self.delay_tree.pack(side='left', fill='both', expand=True)
        delay_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.delay_tree.yview)
        self.delay_tree.configure(yscrollcommand=delay_scroll.set)
        delay_scroll.pack(side="right", fill="y")
        self.delay_tree.bind("<Double-1>", lambda e: self._edit_delay_dialog())

        self._load_delay_entries()

    def create_summary_actual_page(self):
        """創建 Summary Actual 頁面"""
        self._register_text(self.page_title, "pages.summaryActual.title", "Summary Actual", scope="page")
        self._register_text(self.page_subtitle, "pages.summaryActual.subtitle", "Summary Actual 匯入與查詢", scope="page")

        control_card = self.create_card(self.page_content, '🧾', "cards.summaryActual", "Summary Actual")
        control_card.pack(fill='x', padx=0, pady=(0, 20))

        control_frame = ttk.Frame(control_card, style='Card.TFrame')
        control_frame.pack(fill='x', padx=self.layout["card_pad"], pady=self.layout["card_pad"])

        start_label = ttk.Label(control_frame, font=('Segoe UI', 10))
        self._register_text(start_label, "summaryActual.startDate", "日期篩選起日", scope="page")
        start_label.grid(row=0, column=0, sticky='w', pady=self.layout["row_pad"])
        self.summary_start_var = tk.StringVar()
        summary_start_frame = ttk.Frame(control_frame, style='Card.TFrame')
        summary_start_frame.grid(row=0, column=1, sticky='w', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        self._create_date_picker(summary_start_frame, self.summary_start_var, width=14)

        end_label = ttk.Label(control_frame, font=('Segoe UI', 10))
        self._register_text(end_label, "summaryActual.endDate", "日期篩選迄日", scope="page")
        end_label.grid(row=0, column=2, sticky='w', padx=(20, 0), pady=self.layout["row_pad"])
        self.summary_end_var = tk.StringVar()
        summary_end_frame = ttk.Frame(control_frame, style='Card.TFrame')
        summary_end_frame.grid(row=0, column=3, sticky='w', padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])
        self._create_date_picker(summary_end_frame, self.summary_end_var, width=14)
        self._apply_report_date_to_filters()

        search_btn = ttk.Button(control_frame, style='Accent.TButton', command=self._load_summary_actual)
        self._register_text(search_btn, "common.search", "搜尋", scope="page")
        search_btn.grid(row=0, column=4, padx=(20, 0), pady=self.layout["row_pad"])

        import_btn = ttk.Button(control_frame, style='Accent.TButton', command=self._import_summary_actual_excel)
        self._register_text(import_btn, "summaryActual.importExcel", "匯入 Summary Actual", scope="page")
        import_btn.grid(row=1, column=0, pady=self.layout["row_pad"])

        upload_btn = ttk.Button(control_frame, style='Primary.TButton', command=self._upload_summary_pending)
        self._register_text(upload_btn, "summaryActual.confirmUpload", "確認上傳", scope="page")
        upload_btn.grid(row=1, column=1, padx=(self.layout["field_gap"], 0), pady=self.layout["row_pad"])

        clear_btn = ttk.Button(
            control_frame,
            style='Accent.TButton',
            command=self._clear_summary_view,
        )
        self._register_text(clear_btn, "summaryActual.clear", "清除畫面", scope="page")
        clear_btn.grid(row=1, column=2, padx=(20, 0), pady=self.layout["row_pad"])

        table_card = self.create_card(self.page_content, '📋', "cards.summaryActualTable", "Summary Actual 資料")
        table_card.pack(fill='both', expand=True)

        table_frame = ttk.Frame(table_card, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=self.layout["card_pad"], pady=self.layout["card_pad"])

        cols = (
            "id",
            "date",
            "label",
            "plan",
            "completed",
            "in_process",
            "on_track",
            "at_risk",
            "delayed",
            "no_data",
            "scrapped",
        )
        self.summary_columns = cols
        self.summary_header_keys = [
            ("common.id", "ID"),
            ("summaryActual.date", "日期"),
            ("summaryActual.label", "標籤"),
            ("summaryActual.plan", "Plan"),
            ("summaryActual.completed", "Completed"),
            ("summaryActual.inProcess", "In Process"),
            ("summaryActual.onTrack", "On Track"),
            ("summaryActual.atRisk", "At Risk"),
            ("summaryActual.delayed", "Delayed"),
            ("summaryActual.noData", "No Data"),
            ("summaryActual.scrapped", "Scrapped"),
        ]

        self.summary_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)
        self._update_summary_headers()
        self.summary_tree.pack(side='left', fill='both', expand=True)
        summary_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.summary_tree.yview)
        self.summary_tree.configure(yscrollcommand=summary_scroll.set)
        summary_scroll.pack(side="right", fill="y")
        self.summary_tree.bind("<Double-1>", lambda e: self._edit_summary_dialog())

        self._load_summary_actual()
    
    def create_admin_page(self):
        """創建管理員頁面"""
        self._register_text(self.page_title, "pages.admin.title", "系統管理", scope="page")
        self._register_text(self.page_subtitle, "pages.admin.subtitle", "管理使用者、翻譯資源與系統設定", scope="page")
        
        # 創建 Notebook 分頁
        self.admin_notebook = ttk.Notebook(self.page_content, style='Modern.TNotebook')
        self.admin_notebook.pack(fill='both', expand=True)
        
        # 使用者管理分頁
        user_tab = ttk.Frame(self.admin_notebook, style='Modern.TFrame')
        self.admin_notebook.add(user_tab, text=self._t("admin.tabUsers", "👥 使用者管理"))
        
        self.admin_user_mgmt = UserManagementSection(user_tab, self.lang_manager)
        self.admin_user_mgmt.get_widget().pack(fill='both', expand=True, padx=20, pady=20)
        
        # 翻譯管理分頁
        translation_tab = ttk.Frame(self.admin_notebook, style='Modern.TFrame')
        self.admin_notebook.add(translation_tab, text=self._t("admin.tabTranslations", "🌐 翻譯管理"))
        
        self.admin_trans_mgmt = TranslationManagementSection(translation_tab, self.lang_manager)
        self.admin_trans_mgmt.get_widget().pack(fill='both', expand=True, padx=20, pady=20)

        # 班別/區域管理分頁
        master_tab = ttk.Frame(self.admin_notebook, style='Modern.TFrame')
        self.admin_notebook.add(master_tab, text=self._t("admin.tabMasterData", "🧩 班別/區域"))

        self.admin_master_data = MasterDataSection(master_tab, self.lang_manager, on_change=self.refresh_shift_area_options)
        self.admin_master_data.get_widget().pack(fill='both', expand=True, padx=20, pady=20)
        
        # 系統設定分頁
        settings_tab = ttk.Frame(self.admin_notebook, style='Modern.TFrame')
        self.admin_notebook.add(settings_tab, text=self._t("admin.tabSettings", "⚙️ 系統設定"))
        
        self.create_settings_page(settings_tab)
    
    def create_settings_page(self, parent):
        """創建設定頁面"""
        # 資料庫設定
        db_card = self.create_card(parent, '🗄️', "cards.databaseSettings", "資料庫設定")
        db_card.pack(fill='x', padx=20, pady=(20, 10))
        
        db_path_label = ttk.Label(db_card, font=('Segoe UI', 10))
        self._register_text(db_path_label, "settings.databasePath", "資料庫路徑:", scope="page")
        db_path_label.pack(anchor='w', padx=20, pady=(15, 5))
        db_path_frame = ttk.Frame(db_card, style='Card.TFrame')
        db_path_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.db_path_var = tk.StringVar(value=str(get_database_path()))
        ttk.Entry(db_path_frame, textvariable=self.db_path_var, width=50, state='readonly', style='Modern.TEntry').pack(side='left', padx=(0, 10))
        browse_btn = ttk.Button(db_path_frame, style='Accent.TButton')
        self._register_text(browse_btn, "common.browse", "瀏覽...", scope="page")
        browse_btn.pack(side='left')
        
        # 系統設定
        system_card = self.create_card(parent, '⚙️', "cards.systemSettings", "系統設定")
        system_card.pack(fill='x', padx=20, pady=(0, 20))
        
        # 自動備份
        backup_frame = ttk.Frame(system_card, style='Card.TFrame')
        backup_frame.pack(fill='x', padx=20, pady=15)
        
        self.auto_backup_var = tk.BooleanVar(value=True)
        auto_backup_cb = ttk.Checkbutton(backup_frame, variable=self.auto_backup_var)
        self._register_text(auto_backup_cb, "settings.autoBackup", "啟用自動備份", scope="page")
        auto_backup_cb.pack(side='left')
        
        interval_label = ttk.Label(backup_frame, font=('Segoe UI', 10))
        self._register_text(interval_label, "settings.backupInterval", "備份間隔:", scope="page")
        interval_label.pack(side='left', padx=(20, 10))
        self.backup_interval_var = tk.StringVar(value='7')
        ttk.Entry(backup_frame, textvariable=self.backup_interval_var, width=5, style='Modern.TEntry').pack(side='left')
        days_label = ttk.Label(backup_frame, font=('Segoe UI', 10))
        self._register_text(days_label, "settings.days", "天", scope="page")
        days_label.pack(side='left', padx=(5, 10))

        save_btn = ttk.Button(backup_frame, style='Primary.TButton', command=self.save_system_settings)
        self._register_text(save_btn, "settings.saveBackup", "確認", scope="page")
        save_btn.pack(side='left')

        self._load_system_settings()

    def _settings_path(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        return os.path.join(root_dir, "handover_settings.json")

    def _load_system_settings(self):
        data = self._load_settings_data()
        if "auto_backup" in data:
            self.auto_backup_var.set(bool(data["auto_backup"]))
        if "backup_interval_days" in data:
            self.backup_interval_var.set(str(data["backup_interval_days"]))

    def save_system_settings(self):
        try:
            interval = int(self.backup_interval_var.get().strip())
        except ValueError:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("common.invalidNumber", "數字格式無效")
            )
            return
        if interval <= 0:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("settings.invalidBackupInterval", "備份間隔需為正整數")
            )
            return
        data = {
            "auto_backup": bool(self.auto_backup_var.get()),
            "backup_interval_days": interval,
        }
        try:
            merged = self._load_settings_data()
            merged.update(data)
            if not self._save_settings_data(merged):
                raise OSError("settings write failed")
            self._set_status("settings.saved", "✅ 設定已儲存")
            messagebox.showinfo(
                self._t("common.success", "成功"),
                self._t("settings.saved", "✅ 設定已儲存")
            )
        except Exception as exc:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("settings.saveFailed", "設定儲存失敗：{error}").format(error=exc)
            )
    
    def toggle_sidebar(self):
        """收合/展開側邊欄"""
        self.sidebar_collapsed = not self.sidebar_collapsed
        
        if self.sidebar_collapsed:
            self.sidebar_frame.configure(width=60)
            self.toggle_sidebar_btn.configure(text='▶')
            # 隱藏文字
            for btn in self.nav_buttons.values():
                btn.configure(text='')
        else:
            self.sidebar_frame.configure(width=220)
            self.toggle_sidebar_btn.configure(text='◀')
            # 恢復文字
            self.update_nav_text()
        self._position_sidebar_toggle()

    def _position_sidebar_toggle(self):
        width = 60 if self.sidebar_collapsed else 220
        self.toggle_sidebar_btn.place(x=width - 24, y=10)
    
    def update_nav_text(self):
        """更新導航文字"""
        for item_id, icon, text_key, text_default in self._nav_items:
            if item_id in self.nav_buttons:
                if self.sidebar_collapsed:
                    self.nav_buttons[item_id].configure(text="")
                else:
                    label = self._t(text_key, text_default)
                    self.nav_buttons[item_id].configure(text=f"{icon} {label}")

    def _set_navigation_locked(self, locked):
        self.nav_locked = locked
        if not hasattr(self, "nav_buttons"):
            return
        for page_id, button in self.nav_buttons.items():
            if page_id == "daily_report":
                button.configure(state="normal")
            else:
                button.configure(state="disabled" if locked else "normal")
        if not locked:
            self._update_auth_ui()

    def _reset_report_state(self):
        self.report_is_saved = False
        self.active_report_id = None
        self.saved_context = {"date": "", "shift": "", "area": ""}
        self._set_navigation_locked(True)
    
    def toggle_auth(self):
        """切換登入/登出"""
        if self.current_user:
            self.logout()
        else:
            self._show_login_screen()

    def attempt_login(self):
        """登入驗證"""
        username = self.login_username_var.get().strip() if hasattr(self, "login_username_var") else ""
        password = self.login_password_var.get() if hasattr(self, "login_password_var") else ""
        if not username or not password:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("auth.loginMissing", "請輸入帳號與密碼")
            )
            return
        try:
            with SessionLocal() as db:
                user = db.query(User).filter_by(username=username).first()
                if not user or not verify_password(password, user.password_hash):
                    messagebox.showerror(
                        self._t("common.error", "錯誤"),
                        self._t("auth.loginFailed", "帳號或密碼錯誤")
                    )
                    return
                self.current_user = {"id": user.id, "username": user.username, "role": user.role}
            self._update_auth_ui()
            self._reset_report_state()
            self._show_main_ui()
            self.show_page('daily_report')
            self._set_status("status.loginSuccess", "✅ 登入成功")
            self.login_password_var.set("")
        except Exception as exc:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("auth.loginFailedDetail", "登入失敗：{error}").format(error=exc)
            )
    
    def logout(self):
        """登出"""
        self.current_user = None
        self._update_auth_ui()
        self._reset_report_state()
        self._set_status("status.loggedOut", "✅ 已登出")
        self._show_login_screen()
    
    def on_language_changed(self, new_lang_code):
        """語言變更回調"""
        lang_names = {"ja": "日本語", "en": "English", "zh": "中文"}
        current_lang_name = lang_names.get(new_lang_code, new_lang_code)
        self._apply_i18n()
        self.update_nav_text()
        self.lang_selector.update_text()
        self.lang_selector.update_language_display(new_lang_code)
        self._update_theme_toggle_label()
        if hasattr(self, "login_lang_selector"):
            self.login_lang_selector.update_text()
            self.login_lang_selector.update_language_display(new_lang_code)
        self._update_auth_ui()
        self._update_admin_tab_texts()
        if hasattr(self, "attendance_section"):
            self.attendance_section.update_language()
        if hasattr(self, "admin_user_mgmt"):
            self.admin_user_mgmt.update_ui_language()
        if hasattr(self, "admin_trans_mgmt"):
            self.admin_trans_mgmt.update_ui_language()
        if hasattr(self, "admin_master_data"):
            self.admin_master_data.update_ui_language()
        self._update_abnormal_filter_options()
        self._update_shift_values()
        self._sync_report_context_from_form()
        self._update_delay_headers()
        self._update_summary_dashboard_headers()
        self._update_abnormal_history_headers()
        self._update_summary_headers()
        if self.current_page == "summary" and self.summary_dashboard_data:
            self._render_summary_charts(self.summary_dashboard_data)
        self._update_report_context_label()
        self._update_status_bar_info()
        self.status_label.config(text=self._t("status.languageChanged", "🌐 語言已切換至: {language}").format(language=current_lang_name))
        self.update_nav_text()
    
    def add_tooltip(self, widget, text_key, text_default):
        """添加懸停提示"""
        def enter(event):
            self.status_label.config(text=f'💡 {self._t(text_key, text_default)}')
        
        def leave(event):
            self._set_status("status.ready", "就緒")
        
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def _update_admin_tab_texts(self):
        if not hasattr(self, "admin_notebook"):
            return
        tabs = [
            (0, "admin.tabUsers", "👥 使用者管理"),
            (1, "admin.tabTranslations", "🌐 翻譯管理"),
            (2, "admin.tabMasterData", "🧩 班別/區域"),
            (3, "admin.tabSettings", "⚙️ 系統設定"),
        ]
        for index, key, default in tabs:
            try:
                self.admin_notebook.tab(index, text=self._t(key, default))
            except Exception:
                continue

    def _update_shift_values(self):
        if not hasattr(self, "shift_combo") or not hasattr(self, "shift_var"):
            return
        if not self.shift_combo.winfo_exists():
            return
        self._load_shift_area_options()
        current_code = self._get_shift_code()
        new_values = self._build_shift_display_options()
        self.shift_values = new_values
        self.shift_combo["values"] = new_values
        if current_code in self.shift_display_map:
            self.shift_var.set(self.shift_display_map[current_code])
        elif new_values:
            self.shift_var.set(new_values[0])

    def _get_shift_code(self):
        if hasattr(self, "shift_code_map"):
            return self.shift_code_map.get(self.shift_var.get().strip(), self.shift_var.get().strip())
        return self.shift_var.get().strip() if hasattr(self, "shift_var") else ""

    def refresh_shift_area_options(self):
        self._load_shift_area_options()
        if hasattr(self, "shift_combo") and self.shift_combo.winfo_exists():
            current_code = self._get_shift_code()
            new_values = self._build_shift_display_options()
            self.shift_values = new_values
            self.shift_combo["values"] = new_values
            if current_code in self.shift_display_map:
                self.shift_var.set(self.shift_display_map[current_code])
            elif new_values:
                self.shift_var.set(new_values[0])
        if hasattr(self, "area_combo") and self.area_combo.winfo_exists():
            current_area = self.area_var.get().strip() if hasattr(self, "area_var") else ""
            self.area_combo["values"] = self.area_options
            if current_area in self.area_options:
                self.area_var.set(current_area)
            elif self.area_options:
                self.area_var.set(self.area_options[0])
        self._update_abnormal_filter_options()
    
    def add_equipment_record(self):
        """添加設備記錄"""
        if not self.ensure_report_context():
            return
        equip_id = self.equip_id_var.get().strip()
        description = self.equip_desc_text.get("1.0", "end").strip()
        start_time = self.start_time_var.get().strip()
        action_taken = self.action_text.get("1.0", "end").strip()
        image_path = self.image_path_var.get().strip() if hasattr(self, "image_path_var") else ""
        if not equip_id or not description:
            messagebox.showwarning(
                self._t("common.warning", "提醒"),
                self._t("equipment.missingRequired", "請填寫設備號碼與異常內容")
            )
            return
        try:
            impact_qty = int(self.impact_qty_var.get() or 0)
        except ValueError:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("equipment.invalidImpactQty", "影響數量需為數字")
            )
            return
        try:
            with SessionLocal() as db:
                entry = EquipmentLog(
                    report_id=self.active_report_id,
                    equip_id=equip_id,
                    description=description,
                    start_time=start_time,
                    impact_qty=impact_qty,
                    action_taken=action_taken,
                    image_path=image_path or None,
                )
                db.add(entry)
                db.commit()
            self._set_status("status.equipmentAdded", "✅ 設備異常記錄已添加")
            self.equip_id_var.set("")
            self.start_time_var.set("")
            self.impact_qty_var.set("0")
            self.equip_desc_text.delete("1.0", "end")
            self.action_text.delete("1.0", "end")
            if hasattr(self, "image_path_var"):
                self.image_path_var.set("")
        except Exception as exc:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("equipment.saveFailed", "設備異常儲存失敗：{error}").format(error=exc)
            )
    
    def view_equipment_history(self):
        """查看設備歷史"""
        if not self.ensure_report_context():
            return
        try:
            with SessionLocal() as db:
                rows = db.query(EquipmentLog).filter_by(report_id=self.active_report_id).order_by(EquipmentLog.id.desc()).all()
            if not rows:
                messagebox.showinfo(
                    self._t("common.info", "資訊"),
                    self._t("equipment.noHistory", "目前日報沒有設備異常記錄")
                )
                return
            self._open_equipment_history_dialog(rows)
        except Exception as exc:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("equipment.loadFailed", "載入設備異常失敗：{error}").format(error=exc)
            )
    
    def add_lot_record(self):
        """添加批次記錄"""
        if not self.ensure_report_context():
            return
        lot_id = self.lot_id_var.get().strip()
        description = self.lot_desc_text.get("1.0", "end").strip()
        status_text = self.lot_status_var.get().strip()
        notes = self.lot_notes_text.get("1.0", "end").strip()
        if not lot_id or not description:
            messagebox.showwarning(
                self._t("common.warning", "提醒"),
                self._t("lot.missingRequired", "請填寫批號與異常內容")
            )
            return
        try:
            with SessionLocal() as db:
                entry = LotLog(
                    report_id=self.active_report_id,
                    lot_id=lot_id,
                    description=description,
                    status=status_text,
                    notes=notes,
                )
                db.add(entry)
                db.commit()
            self._set_status("status.lotAdded", "✅ 批次異常記錄已添加")
            self.lot_id_var.set("")
            self.lot_status_var.set("")
            self.lot_desc_text.delete("1.0", "end")
            self.lot_notes_text.delete("1.0", "end")
        except Exception as exc:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("lot.saveFailed", "批次異常儲存失敗：{error}").format(error=exc)
            )
    
    def view_lot_list(self):
        """查看批次列表"""
        if not self.ensure_report_context():
            return
        try:
            with SessionLocal() as db:
                rows = db.query(LotLog).filter_by(report_id=self.active_report_id).order_by(LotLog.id.desc()).all()
            if not rows:
                messagebox.showinfo(
                    self._t("common.info", "資訊"),
                    self._t("lot.noHistory", "目前日報沒有批次異常記錄")
                )
                return
            self._open_lot_history_dialog(rows)
        except Exception as exc:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("lot.loadFailed", "載入批次異常失敗：{error}").format(error=exc)
            )

    def _open_history_dialog(self, title, columns, headers, rows, row_builder):
        dialog = tk.Toplevel(self.parent)
        dialog.configure(background=self.COLORS['background'])
        dialog.title(title)
        dialog.geometry("900x420")
        dialog.transient(self.parent)

        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill='both', expand=True)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=14)
        for col, (key, default) in zip(columns, headers):
            tree.heading(col, text=self._t(key, default))
            tree.column(col, width=150, anchor="w")
        tree.pack(side='left', fill='both', expand=True)

        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        for row in rows:
            tree.insert("", "end", values=row_builder(row))

    def _open_equipment_history_dialog(self, rows):
        columns = ("equip_id", "start_time", "impact_qty", "description", "action_taken")
        headers = [
            ("equipment.equipId", "設備號碼"),
            ("equipment.startTime", "發生時刻"),
            ("equipment.impactQty", "影響數量"),
            ("common.description", "異常內容"),
            ("equipment.actionTaken", "對應內容"),
        ]
        self._open_history_dialog(
            self._t("equipment.historyTitle", "設備異常記錄"),
            columns,
            headers,
            rows,
            lambda row: (
                row.equip_id,
                row.start_time,
                row.impact_qty,
                row.description,
                row.action_taken,
            ),
        )

    def _open_lot_history_dialog(self, rows):
        columns = ("lot_id", "description", "status", "notes")
        headers = [
            ("lot.lotId", "批號"),
            ("common.description", "異常內容"),
            ("lot.status", "處置狀況"),
            ("lot.notes", "特記事項"),
        ]
        self._open_history_dialog(
            self._t("lot.historyTitle", "批次異常記錄"),
            columns,
            headers,
            rows,
            lambda row: (
                row.lot_id,
                row.description,
                row.status,
                row.notes,
            ),
        )
    
    def browse_image(self):
        """瀏覽圖片"""
        file_path = filedialog.askopenfilename(
            title=self._t("common.selectImage", "選擇圖片文件"),
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
        )
        if file_path:
            self.image_path_var.set(file_path)
            self.status_label.config(
                text=self._t("status.imageSelected", "📷 已選擇圖片: {filename}").format(
                    filename=os.path.basename(file_path)
                )
            )
    
    def save_basic_info(self):
        """儲存日報基本資訊"""
        report_id = self._save_report(context_only=True)
        if report_id:
            self._set_status("status.basicInfoSaved", "✅ 基本資訊已儲存")
            messagebox.showinfo(
                self._t("common.success", "成功"),
                self._t("status.basicInfoSavedDetail", "基本資訊已儲存（報表 ID: {report_id}）").format(report_id=report_id)
            )

    def save_daily_report(self):
        """儲存日報內容"""
        if not self.ensure_report_context():
            return
        if self._save_report(context_only=False):
            self._set_status("status.dailySaved", "💾 日報已儲存")

    def _save_report(self, context_only=False):
        self._sync_report_context_from_form()
        date_str = self.report_context.get("date", "").strip()
        shift_code = self._get_shift_code()
        area = self.report_context.get("area", "").strip()
        if not date_str or not shift_code or not area:
            messagebox.showwarning(
                self._t("context.missingTitle", "尚未設定日報表"),
                self._t("context.missingBody", "請先在日報表設定日期、班別、區域後再繼續。")
            )
            return None
        try:
            report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("errors.invalidDateFormat", "日期格式需為 YYYY-MM-DD")
            )
            return None
        if not self.current_user:
            messagebox.showwarning(
                self._t("auth.loginRequiredTitle", "尚未登入"),
                self._t("auth.loginRequiredBody", "請先登入後再儲存日報。")
            )
            return None

        key_output = self.key_output_text.get("1.0", "end").strip()
        issues = self.key_issues_text.get("1.0", "end").strip()
        counter = self.countermeasures_text.get("1.0", "end").strip()
        author_id = self.current_user.get("id")

        try:
            with SessionLocal() as db:
                if author_id is None:
                    user = db.query(User).filter_by(username=self.current_user.get("username")).first()
                    if not user:
                        raise ValueError("找不到使用者資料")
                    author_id = user.id
                report = (
                    db.query(DailyReport)
                    .filter_by(date=report_date, shift=shift_code, area=area)
                    .first()
                )
                if report is None:
                    report = DailyReport(
                        date=report_date,
                        shift=shift_code,
                        area=area,
                        author_id=author_id,
                    )
                    db.add(report)
                elif report.author_id != author_id:
                    report.author_id = author_id
                if not context_only:
                    report.summary_key_output = key_output
                    report.summary_issues = issues
                    report.summary_countermeasures = counter
                db.commit()
                db.refresh(report)

            self.active_report_id = report.id
            self.report_is_saved = True
            self.saved_context = {"date": date_str, "shift": shift_code, "area": area}
            self._set_navigation_locked(False)
            return report.id
        except Exception as exc:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("status.basicInfoSaveFailed", "基本資訊儲存失敗：{error}").format(error=exc)
            )
            return None
    
    def reset_daily_report(self):
        """重置日報"""
        if hasattr(self, "date_var"):
            self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        if hasattr(self, "shift_values") and hasattr(self, "shift_var") and self.shift_values:
            self.shift_var.set(self.shift_values[0])
        if hasattr(self, "area_var"):
            self.area_var.set("etching_D")
        if hasattr(self, "key_output_text"):
            self.key_output_text.delete("1.0", "end")
        if hasattr(self, "key_issues_text"):
            self.key_issues_text.delete("1.0", "end")
        if hasattr(self, "countermeasures_text"):
            self.countermeasures_text.delete("1.0", "end")
        self.report_is_saved = False
        self.active_report_id = None
        self.saved_context = {"date": "", "shift": "", "area": ""}
        self._set_navigation_locked(True)
        self._sync_report_context_from_form()
        self._set_status("status.dailyReset", "🔄 日報表單已重置")

    def _sync_report_context_from_form(self):
        date_value = self.date_var.get().strip() if hasattr(self, "date_var") else ""
        shift_display = self.shift_var.get().strip() if hasattr(self, "shift_var") else ""
        area_value = self.area_var.get().strip() if hasattr(self, "area_var") else ""
        self.report_context["date"] = date_value
        self.report_context["shift"] = shift_display
        self.report_context["area"] = area_value
        current_context = {
            "date": date_value,
            "shift": self._get_shift_code(),
            "area": area_value,
        }
        if self.report_is_saved and current_context != self.saved_context:
            self.report_is_saved = False
            self.active_report_id = None
            self._set_navigation_locked(True)
            self._set_status("status.basicInfoLocked", "⚠️ 請先儲存基本資訊")
        self._update_report_context_label()

    def _update_report_context_label(self):
        unknown = self._t("context.unknown", "未設定")
        date = self.report_context.get("date") or unknown
        shift = self.report_context.get("shift") or unknown
        area = self.report_context.get("area") or unknown
        text = self._t("context.currentReport", "目前日報：日期 {date}｜班別 {shift}｜區域 {area}")
        self.context_label.config(text=text.format(date=date, shift=shift, area=area))

    def _apply_report_date_to_filters(self):
        report_date = self.report_context.get("date") or ""
        if report_date:
            if hasattr(self, "delay_start_var") and not self.delay_start_var.get().strip():
                self.delay_start_var.set(report_date)
            if hasattr(self, "delay_end_var") and not self.delay_end_var.get().strip():
                self.delay_end_var.set(report_date)
            if hasattr(self, "summary_start_var") and not self.summary_start_var.get().strip():
                self.summary_start_var.set(report_date)
            if hasattr(self, "summary_end_var") and not self.summary_end_var.get().strip():
                self.summary_end_var.set(report_date)

    def get_report_context(self):
        return dict(self.report_context)

    def ensure_report_context(self):
        if not all(self.report_context.get(key) for key in ("date", "shift", "area")):
            messagebox.showwarning(
                self._t("context.missingTitle", "尚未設定日報表"),
                self._t("context.missingBody", "請先在日報表設定日期、班別、區域後再繼續。")
            )
            return False
        if not self.report_is_saved or not self.active_report_id:
            messagebox.showwarning(
                self._t("context.basicInfoRequiredTitle", "尚未儲存基本資訊"),
                self._t("context.basicInfoRequiredBody", "請先在日報表儲存日期、班別、區域後再使用其他功能。")
            )
            return False
        return True

    def _load_attendance_entries(self):
        if not self.active_report_id or not hasattr(self, "attendance_section"):
            return
        try:
            with SessionLocal() as db:
                rows = db.query(AttendanceEntry).filter_by(report_id=self.active_report_id).all()
            if not rows:
                self.attendance_section.clear_data()
                return
            data = {
                "regular": {"scheduled": 0, "present": 0, "absent": 0, "reason": ""},
                "contractor": {"scheduled": 0, "present": 0, "absent": 0, "reason": ""},
            }
            for row in rows:
                category = row.category.lower()
                if category == "regular":
                    target = "regular"
                else:
                    target = "contractor"
                data[target] = {
                    "scheduled": row.scheduled_count,
                    "present": row.present_count,
                    "absent": row.absent_count,
                    "reason": row.reason or "",
                }
            self.attendance_section.set_attendance_data(data)
        except Exception as exc:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("attendance.loadFailed", "載入出勤資料失敗：{error}").format(error=exc)
            )

    def save_attendance_entries(self, data):
        if not self.ensure_report_context():
            return False
        try:
            with SessionLocal() as db:
                db.query(AttendanceEntry).filter_by(report_id=self.active_report_id).delete(synchronize_session=False)
                entries = [
                    AttendanceEntry(
                        report_id=self.active_report_id,
                        category="Regular",
                        scheduled_count=int(data["regular"]["scheduled"]),
                        present_count=int(data["regular"]["present"]),
                        absent_count=int(data["regular"]["absent"]),
                        reason=data["regular"].get("reason", ""),
                    ),
                    AttendanceEntry(
                        report_id=self.active_report_id,
                        category="Contract",
                        scheduled_count=int(data["contractor"]["scheduled"]),
                        present_count=int(data["contractor"]["present"]),
                        absent_count=int(data["contractor"]["absent"]),
                        reason=data["contractor"].get("reason", ""),
                    ),
                ]
                db.add_all(entries)
                db.commit()
            self._set_status("status.attendanceSaved", "✅ 出勤資料已儲存")
            return True
        except Exception as exc:
            messagebox.showerror(
                self._t("common.error", "錯誤"),
                self._t("attendance.saveFailed", "出勤資料儲存失敗：{error}").format(error=exc)
            )
            return False

    def _update_delay_headers(self):
        if not hasattr(self, "delay_tree"):
            return
        for col, (key, default) in zip(self.delay_columns, self.delay_header_keys):
            self.delay_tree.heading(col, text=self._t(key, default))
            width = 50 if col == "id" else 110
            stretch = False if col == "id" else True
            anchor = "center" if col not in ("note", "action", "progress") else "w"
            self.delay_tree.column(col, width=width, stretch=stretch, anchor=anchor)

    def _update_summary_headers(self):
        if not hasattr(self, "summary_tree"):
            return
        for col, (key, default) in zip(self.summary_columns, self.summary_header_keys):
            self.summary_tree.heading(col, text=self._t(key, default))
            width = 50 if col == "id" else 110
            stretch = False if col == "id" else True
            anchor = "center" if col not in ("label",) else "w"
            self.summary_tree.column(col, width=width, stretch=stretch, anchor=anchor)

    def _clear_delay_view(self):
        if hasattr(self, "delay_tree"):
            self._clear_tree(self.delay_tree)
        self.delay_pending_records = []

    def _clear_summary_view(self):
        if hasattr(self, "summary_tree"):
            self._clear_tree(self.summary_tree)
        self.summary_pending_records = []

    def _render_delay_rows(self, rows, pending=False):
        self._clear_tree(self.delay_tree)
        for idx, row in enumerate(rows):
            if pending:
                row_id = f"P{idx}"
                values = (
                    row_id,
                    row["delay_date"],
                    row["time_range"],
                    row["reactor"],
                    row["process"],
                    row["lot"],
                    row["wafer"],
                    row["progress"],
                    row["prev_steps"],
                    row["prev_time"],
                    row["severity"],
                    row["action"],
                    row["note"],
                )
            else:
                values = (
                    row.id,
                    row.delay_date,
                    row.time_range,
                    row.reactor,
                    row.process,
                    row.lot,
                    row.wafer,
                    row.progress,
                    row.prev_steps,
                    row.prev_time,
                    row.severity,
                    row.action,
                    row.note,
                )
            self.delay_tree.insert("", "end", values=values)

    def _load_delay_entries(self):
        if self.delay_pending_records:
            self._render_delay_rows(self.delay_pending_records, pending=True)
            return
        start = self.delay_start_var.get().strip()
        end = self.delay_end_var.get().strip()
        start_date = end_date = None
        try:
            if start:
                start_date = datetime.strptime(start, "%Y-%m-%d").date()
            if end:
                end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror(self._t("common.error", "錯誤"), self._t("errors.invalidDateFormat", "日期格式需為 YYYY-MM-DD"))
            return
        try:
            with SessionLocal() as db:
                query = db.query(DelayEntry)
                if start_date:
                    query = query.filter(DelayEntry.delay_date >= start_date)
                if end_date:
                    query = query.filter(DelayEntry.delay_date <= end_date)
                rows = query.order_by(DelayEntry.delay_date.desc(), DelayEntry.imported_at.desc()).all()
        except Exception as exc:
            messagebox.showerror(self._t("common.error", "錯誤"), f"{exc}")
            return
        self._render_delay_rows(rows, pending=False)

    def _import_delay_excel(self):
        path = filedialog.askopenfilename(
            title=self._t("delay.importExcel", "匯入延遲Excel"),
            filetypes=[("Excel Files", "*.xlsx;*.xls")],
        )
        if not path:
            return
        try:
            xls = pd.ExcelFile(path)
            sheet_name = xls.sheet_names[0]
            if len(xls.sheet_names) > 1:
                picker = tk.Toplevel(self.parent)
                picker.configure(background=self.COLORS['background'])
                picker.title(self._t("navigation.delayList", "延遲清單"))
                ttk.Label(picker, text=self._t("common.selectSheet", "選擇工作表")).pack(padx=10, pady=5)
                sheet_var = tk.StringVar(value=xls.sheet_names[0])
                combo = ttk.Combobox(picker, textvariable=sheet_var, values=xls.sheet_names, state="readonly")
                combo.pack(padx=10, pady=5)
                chosen = {"name": sheet_name}

                def confirm():
                    chosen["name"] = sheet_var.get()
                    picker.destroy()

                ttk.Button(picker, text=self._t("common.ok", "確定"), command=confirm).pack(pady=8)
                picker.grab_set()
                picker.wait_window()
                sheet_name = chosen["name"]

            df = pd.read_excel(xls, sheet_name=sheet_name, header=1)
        except Exception as exc:
            messagebox.showerror(self._t("common.error", "錯誤"), f"{exc}")
            return

        def find_col(match):
            for col in df.columns:
                c = str(col).lower()
                if match in c:
                    return col
            return None

        col_map = {
            "date": find_col("date"),
            "time": find_col("time"),
            "reactor": find_col("reactor"),
            "process": find_col("process"),
            "lot": find_col("lot"),
            "wafer": find_col("wafer"),
            "progress": find_col("progress"),
            "prev_steps": find_col("previous"),
            "prev_time": find_col("prev"),
            "severity": find_col("severity") or find_col("caution"),
            "action": find_col("action") or find_col("対処"),
            "note": find_col("note") or find_col("備考"),
        }

        records = []
        for _, row in df.iterrows():
            raw_date = row.get(col_map["date"]) if col_map["date"] else None
            parsed_date = pd.to_datetime(raw_date, errors="coerce").date() if pd.notna(raw_date) else None
            if not parsed_date:
                continue

            def sval(key):
                col = col_map.get(key)
                if col is None:
                    return ""
                val = row.get(col)
                if pd.isna(val):
                    return ""
                return str(val).strip()

            records.append(
                {
                    "delay_date": parsed_date,
                    "time_range": sval("time"),
                    "reactor": sval("reactor"),
                    "process": sval("process"),
                    "lot": sval("lot"),
                    "wafer": sval("wafer"),
                    "progress": sval("progress"),
                    "prev_steps": sval("prev_steps"),
                    "prev_time": sval("prev_time"),
                    "severity": sval("severity"),
                    "action": sval("action"),
                    "note": sval("note"),
                }
            )

        if not records:
            messagebox.showinfo(self._t("common.info", "資訊"), self._t("common.emptyData", "查無資料"))
            return

        self.delay_pending_records = records
        self._render_delay_rows(records, pending=True)
        messagebox.showinfo(
            self._t("common.info", "資訊"),
            self._t("delay.importPending", "匯入完成，請確認後再點上傳"),
        )

    def _upload_delay_pending(self):
        if not self.delay_pending_records:
            messagebox.showinfo(self._t("common.info", "資訊"), self._t("common.emptyData", "查無資料"))
            return
        try:
            with SessionLocal() as db:
                unique_dates = {rec["delay_date"] for rec in self.delay_pending_records}
                if unique_dates:
                    db.query(DelayEntry).filter(DelayEntry.delay_date.in_(unique_dates)).delete(synchronize_session=False)
                for rec in self.delay_pending_records:
                    db.add(DelayEntry(**rec))
                db.commit()
            self.delay_pending_records = []
            self._load_delay_entries()
            messagebox.showinfo(self._t("common.success", "成功"), self._t("common.uploadSuccess", "上傳成功"))
        except Exception as exc:
            messagebox.showerror(self._t("common.error", "錯誤"), f"{exc}")

    def _edit_delay_dialog(self):
        sel = self.delay_tree.selection()
        if not sel:
            messagebox.showinfo(self._t("common.info", "資訊"), self._t("common.selectRow", "請先選擇一列"))
            return
        vals = self.delay_tree.item(sel[0], "values")
        if len(vals) < 13:
            return
        (
            row_id,
            d_date,
            d_time,
            reactor,
            process,
            lot,
            wafer,
            progress,
            prev_steps,
            prev_time,
            severity,
            action,
            note,
        ) = vals
        is_pending = isinstance(row_id, str) and str(row_id).startswith("P")
        dlg = tk.Toplevel(self.parent)
        dlg.configure(background=self.COLORS['background'])
        dlg.title(self._t("navigation.delayList", "延遲清單"))
        dlg.columnconfigure(1, weight=1)

        fields = [
            ("date", self._t("delay.date", "日期"), d_date),
            ("time", self._t("delay.time", "時間"), d_time),
            ("reactor", self._t("delay.reactor", "設備"), reactor),
            ("process", self._t("delay.process", "製程"), process),
            ("lot", self._t("delay.lot", "批號"), lot),
            ("wafer", self._t("delay.wafer", "晶圓"), wafer),
            ("progress", self._t("delay.progress", "進行中"), progress),
            ("prev_steps", self._t("delay.prevSteps", "前站"), prev_steps),
            ("prev_time", self._t("delay.prevTime", "前站時間"), prev_time),
            ("severity", self._t("delay.severity", "嚴重度"), severity),
            ("action", self._t("delay.action", "對應內容"), action),
            ("note", self._t("delay.note", "備註"), note),
        ]
        vars_map = {}
        for idx, (key, label, value) in enumerate(fields):
            ttk.Label(dlg, text=label).grid(row=idx, column=0, padx=5, pady=4, sticky="e")
            var = tk.StringVar(value=str(value))
            if key == "date":
                date_frame = ttk.Frame(dlg)
                date_frame.grid(row=idx, column=1, padx=5, pady=4, sticky="ew")
                self._create_date_picker(date_frame, var, width=18)
            else:
                ttk.Entry(dlg, textvariable=var, width=30).grid(row=idx, column=1, padx=5, pady=4, sticky="ew")
            vars_map[key] = var

        def save():
            try:
                if is_pending:
                    idx = int(str(row_id)[1:])
                    if idx < 0 or idx >= len(self.delay_pending_records):
                        messagebox.showerror(self._t("common.error", "錯誤"), self._t("common.selectRow", "請先選擇一列"))
                        return
                    try:
                        new_date = datetime.strptime(vars_map["date"].get().strip(), "%Y-%m-%d").date()
                    except Exception:
                        messagebox.showerror(self._t("common.error", "錯誤"), self._t("errors.invalidDateFormat", "日期格式需為 YYYY-MM-DD"))
                        return
                    rec = self.delay_pending_records[idx]
                    rec.update(
                        {
                            "delay_date": new_date,
                            "time_range": vars_map["time"].get().strip(),
                            "reactor": vars_map["reactor"].get().strip(),
                            "process": vars_map["process"].get().strip(),
                            "lot": vars_map["lot"].get().strip(),
                            "wafer": vars_map["wafer"].get().strip(),
                            "progress": vars_map["progress"].get().strip(),
                            "prev_steps": vars_map["prev_steps"].get().strip(),
                            "prev_time": vars_map["prev_time"].get().strip(),
                            "severity": vars_map["severity"].get().strip(),
                            "action": vars_map["action"].get().strip(),
                            "note": vars_map["note"].get().strip(),
                        }
                    )
                    self._render_delay_rows(self.delay_pending_records, pending=True)
                else:
                    with SessionLocal() as db:
                        row = db.query(DelayEntry).filter(DelayEntry.id == row_id).first()
                        if not row:
                            messagebox.showerror(self._t("common.error", "錯誤"), self._t("common.selectRow", "請先選擇一列"))
                            return
                        try:
                            row.delay_date = datetime.strptime(vars_map["date"].get().strip(), "%Y-%m-%d").date()
                        except Exception:
                            messagebox.showerror(self._t("common.error", "錯誤"), self._t("errors.invalidDateFormat", "日期格式需為 YYYY-MM-DD"))
                            return
                        row.time_range = vars_map["time"].get().strip()
                        row.reactor = vars_map["reactor"].get().strip()
                        row.process = vars_map["process"].get().strip()
                        row.lot = vars_map["lot"].get().strip()
                        row.wafer = vars_map["wafer"].get().strip()
                        row.progress = vars_map["progress"].get().strip()
                        row.prev_steps = vars_map["prev_steps"].get().strip()
                        row.prev_time = vars_map["prev_time"].get().strip()
                        row.severity = vars_map["severity"].get().strip()
                        row.action = vars_map["action"].get().strip()
                        row.note = vars_map["note"].get().strip()
                        db.commit()
                    self._load_delay_entries()
                dlg.destroy()
            except Exception as exc:
                messagebox.showerror(self._t("common.error", "錯誤"), f"{exc}")

        save_btn = ttk.Button(dlg, style='Primary.TButton', command=save)
        self._register_text(save_btn, "common.save", "儲存", scope="page")
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def _load_summary_actual(self):
        self._clear_tree(self.summary_tree)
        start = self.summary_start_var.get().strip()
        end = self.summary_end_var.get().strip()
        start_date = end_date = None
        try:
            if start:
                start_date = datetime.strptime(start, "%Y-%m-%d").date()
            if end:
                end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror(self._t("common.error", "錯誤"), self._t("errors.invalidDateFormat", "日期格式需為 YYYY-MM-DD"))
            return

        def fmt(val):
            return "-" if val == 0 else str(val)

        if self.summary_pending_records:
            for idx, row in enumerate(self.summary_pending_records):
                self.summary_tree.insert(
                    "",
                    "end",
                    values=(
                        f"P{idx}",
                        row["summary_date"],
                        row["label"],
                        fmt(row["plan"]),
                        fmt(row["completed"]),
                        fmt(row["in_process"]),
                        fmt(row["on_track"]),
                        fmt(row["at_risk"]),
                        fmt(row["delayed"]),
                        fmt(row["no_data"]),
                        fmt(row["scrapped"]),
                    ),
                )
            return

        try:
            with SessionLocal() as db:
                query = db.query(SummaryActualEntry)
                if start_date:
                    query = query.filter(SummaryActualEntry.summary_date >= start_date)
                if end_date:
                    query = query.filter(SummaryActualEntry.summary_date <= end_date)
                rows = query.order_by(SummaryActualEntry.summary_date.desc(), SummaryActualEntry.imported_at.desc()).all()
        except Exception as exc:
            messagebox.showerror(self._t("common.error", "錯誤"), f"{exc}")
            return

        for row in rows:
            self.summary_tree.insert(
                "",
                "end",
                values=(
                    row.id,
                    row.summary_date,
                    row.label,
                    fmt(row.plan),
                    fmt(row.completed),
                    fmt(row.in_process),
                    fmt(row.on_track),
                    fmt(row.at_risk),
                    fmt(row.delayed),
                    fmt(row.no_data),
                    fmt(row.scrapped),
                ),
            )

    def _import_summary_actual_excel(self):
        path = filedialog.askopenfilename(
            title=self._t("summaryActual.importExcel", "匯入 Summary Actual"),
            filetypes=[("Excel Files", "*.xlsx;*.xls")],
        )
        if not path:
            return
        try:
            raw_sheet = pd.read_excel(path, sheet_name="Summary(Actual)", header=None)
        except Exception as exc:
            messagebox.showerror(self._t("common.error", "錯誤"), f"{exc}")
            return
        summary_date = None
        if len(raw_sheet) > 1:
            for val in raw_sheet.iloc[1].dropna().tolist():
                parsed = pd.to_datetime(val, errors="coerce")
                if pd.isna(parsed):
                    continue
                summary_date = parsed.date()
                break
        if not summary_date:
            messagebox.showerror(self._t("common.error", "錯誤"), self._t("errors.invalidDateFormat", "日期格式需為 YYYY-MM-DD"))
            return

        try:
            df = pd.read_excel(path, sheet_name="Summary(Actual)", header=2)
        except Exception as exc:
            messagebox.showerror(self._t("common.error", "錯誤"), f"{exc}")
            return

        def norm(col):
            return str(col).strip().lower().replace(" ", "").replace("_", "")

        col_lookup = {norm(c): c for c in df.columns}

        def get_col(key):
            return col_lookup.get(key, None)

        def get_val(row, key):
            col = get_col(key)
            if col is None:
                return 0
            val = row.get(col)
            if pd.isna(val):
                return 0
            try:
                return int(val)
            except Exception:
                try:
                    return int(float(val))
                except Exception:
                    return 0

        records = []
        for _, row in df.iterrows():
            label_val = ""
            if len(df.columns) > 2:
                part_b = row.get(df.columns[1])
                part_c = row.get(df.columns[2])
                label_val = f"{'' if pd.isna(part_b) else str(part_b).strip()} {'' if pd.isna(part_c) else str(part_c).strip()}".strip()
            if not label_val:
                continue
            records.append(
                {
                    "summary_date": summary_date,
                    "label": label_val,
                    "plan": get_val(row, "plan"),
                    "completed": get_val(row, "completed"),
                    "in_process": get_val(row, "inprocess"),
                    "on_track": get_val(row, "ontrack"),
                    "at_risk": get_val(row, "atrisk"),
                    "delayed": get_val(row, "delayed"),
                    "no_data": get_val(row, "nodata"),
                    "scrapped": get_val(row, "scrapped"),
                }
            )

        if not records:
            messagebox.showinfo(self._t("common.info", "資訊"), self._t("common.emptyData", "查無資料"))
            return
        self.summary_pending_records = records
        self._load_summary_actual()
        messagebox.showinfo(
            self._t("common.info", "資訊"),
            self._t("summaryActual.importPending", "匯入完成，請確認後再點上傳"),
        )

    def _upload_summary_pending(self):
        if not self.summary_pending_records:
            messagebox.showinfo(self._t("common.info", "資訊"), self._t("common.emptyData", "查無資料"))
            return
        try:
            with SessionLocal() as db:
                unique_dates = {rec["summary_date"] for rec in self.summary_pending_records}
                if unique_dates:
                    db.query(SummaryActualEntry).filter(SummaryActualEntry.summary_date.in_(unique_dates)).delete(
                        synchronize_session=False
                    )
                for rec in self.summary_pending_records:
                    db.add(SummaryActualEntry(**rec))
                db.commit()
            self.summary_pending_records = []
            self._load_summary_actual()
            messagebox.showinfo(self._t("common.success", "成功"), self._t("common.uploadSuccess", "上傳成功"))
        except Exception as exc:
            messagebox.showerror(self._t("common.error", "錯誤"), f"{exc}")

    def _edit_summary_dialog(self):
        sel = self.summary_tree.selection()
        if not sel:
            messagebox.showinfo(self._t("common.info", "資訊"), self._t("common.selectRow", "請先選擇一列"))
            return
        vals = self.summary_tree.item(sel[0], "values")
        if len(vals) < 10:
            return
        (
            row_id,
            d_date,
            label,
            plan,
            completed,
            in_process,
            on_track,
            at_risk,
            delayed,
            no_data,
            scrapped,
        ) = vals
        is_pending = isinstance(row_id, str) and str(row_id).startswith("P")
        dlg = tk.Toplevel(self.parent)
        dlg.configure(background=self.COLORS['background'])
        dlg.title(self._t("navigation.summaryActual", "Summary Actual"))
        dlg.columnconfigure(1, weight=1)

        fields = [
            ("date", self._t("summaryActual.date", "日期"), d_date),
            ("label", self._t("summaryActual.label", "標籤"), label),
            ("plan", self._t("summaryActual.plan", "Plan"), plan),
            ("completed", self._t("summaryActual.completed", "Completed"), completed),
            ("in_process", self._t("summaryActual.inProcess", "In Process"), in_process),
            ("on_track", self._t("summaryActual.onTrack", "On Track"), on_track),
            ("at_risk", self._t("summaryActual.atRisk", "At Risk"), at_risk),
            ("delayed", self._t("summaryActual.delayed", "Delayed"), delayed),
            ("no_data", self._t("summaryActual.noData", "No Data"), no_data),
            ("scrapped", self._t("summaryActual.scrapped", "Scrapped"), scrapped),
        ]
        vars_map = {}
        for idx, (key, label_text, value) in enumerate(fields):
            ttk.Label(dlg, text=label_text).grid(row=idx, column=0, padx=5, pady=4, sticky="e")
            var = tk.StringVar(value=str(value))
            if key == "date":
                date_frame = ttk.Frame(dlg)
                date_frame.grid(row=idx, column=1, padx=5, pady=4, sticky="ew")
                self._create_date_picker(date_frame, var, width=18)
            else:
                ttk.Entry(dlg, textvariable=var, width=30).grid(row=idx, column=1, padx=5, pady=4, sticky="ew")
            vars_map[key] = var

        def save():
            try:
                if is_pending:
                    idx = int(str(row_id)[1:])
                    if idx < 0 or idx >= len(self.summary_pending_records):
                        messagebox.showerror(self._t("common.error", "錯誤"), self._t("common.selectRow", "請先選擇一列"))
                        return
                    try:
                        new_date = datetime.strptime(vars_map["date"].get().strip(), "%Y-%m-%d").date()
                    except Exception:
                        messagebox.showerror(self._t("common.error", "錯誤"), self._t("errors.invalidDateFormat", "日期格式需為 YYYY-MM-DD"))
                        return
                    rec = self.summary_pending_records[idx]
                    rec["summary_date"] = new_date
                    rec["label"] = vars_map["label"].get().strip()
                    for key in [
                        "plan",
                        "completed",
                        "in_process",
                        "on_track",
                        "at_risk",
                        "delayed",
                        "no_data",
                        "scrapped",
                    ]:
                        try:
                            rec[key] = int(vars_map[key].get().strip() or 0)
                        except Exception:
                            rec[key] = 0
                    self._load_summary_actual()
                else:
                    with SessionLocal() as db:
                        row = db.query(SummaryActualEntry).filter(SummaryActualEntry.id == row_id).first()
                        if not row:
                            messagebox.showerror(self._t("common.error", "錯誤"), self._t("common.selectRow", "請先選擇一列"))
                            return
                        try:
                            row.summary_date = datetime.strptime(vars_map["date"].get().strip(), "%Y-%m-%d").date()
                        except Exception:
                            messagebox.showerror(self._t("common.error", "錯誤"), self._t("errors.invalidDateFormat", "日期格式需為 YYYY-MM-DD"))
                            return
                        row.label = vars_map["label"].get().strip()
                        for key, attr in [
                            ("plan", "plan"),
                            ("completed", "completed"),
                            ("in_process", "in_process"),
                            ("on_track", "on_track"),
                            ("at_risk", "at_risk"),
                            ("delayed", "delayed"),
                            ("no_data", "no_data"),
                            ("scrapped", "scrapped"),
                        ]:
                            try:
                                setattr(row, attr, int(vars_map[key].get().strip() or 0))
                            except Exception:
                                setattr(row, attr, 0)
                        db.commit()
                    self._load_summary_actual()
                dlg.destroy()
            except Exception as exc:
                messagebox.showerror(self._t("common.error", "錯誤"), f"{exc}")

        save_btn = ttk.Button(dlg, style='Primary.TButton', command=save)
        self._register_text(save_btn, "common.save", "儲存", scope="page")
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)


# 測試函數
def test_modern_ui():
    """測試現代化 UI"""
    root = tk.Tk()
    root.title("電子交接系統 - 現代化介面")
    root.geometry("1200x800")
    
    # 模擬語言管理器
    class MockLangManager:
        def __init__(self):
            self.current_lang = "zh"
        
        def get_text(self, key, default):
            return default
        
        def set_language(self, lang):
            self.current_lang = lang
        
        def get_current_language(self):
            return self.current_lang
        
        def get_widget(self):
            return None
    
    # 創建現代化主框架
    lang_manager = MockLangManager()
    modern_frame = ModernMainFrame(root, lang_manager)
    
    root.mainloop()


if __name__ == "__main__":
    test_modern_ui()
