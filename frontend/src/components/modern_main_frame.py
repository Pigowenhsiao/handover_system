"""
現代化主應用程序界面框架
採用側邊導航、卡片式設計、現代色彩方案
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os

# 導入現有組件
from frontend.src.components.language_selector import LanguageSelector
from frontend.main import LanguageManager
from frontend.src.components.admin_section import UserManagementSection, TranslationManagementSection
from frontend.src.components.attendance_section_optimized import AttendanceSectionOptimized


class ModernMainFrame:
    """
    現代化主應用框架
    採用 Material Design 設計理念
    """
    
    COLORS = {
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
    
    def __init__(self, parent, lang_manager):
        self.parent = parent
        self.lang_manager = lang_manager
        self.current_user = None
        self.sidebar_collapsed = False
        
        # 配置現代化樣式
        self.setup_modern_styles()
        
        # 創建界面
        self.setup_ui()
        
        # 初始化第一個頁面
        self.show_page('daily_report')
    
    def setup_modern_styles(self):
        """設置現代化樣式"""
        style = ttk.Style()
        
        # 配置顏色
        colors = self.COLORS
        
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
        
        # 輸入框樣式
        style.configure('Modern.TEntry',
                       fieldbackground=colors['surface'],
                       font=('Segoe UI', 10),
                       padding=(8, 5))
        
        # 進度條樣式
        style.configure('Horizontal.TProgressbar',
                       background=colors['primary'],
                       troughcolor=colors['background'],
                       thickness=8)
        
        # 分隔線樣式
        style.configure('Line.TSeparator', background=colors['divider'])
    
    def setup_ui(self):
        """設置現代化界面"""
        # 主容器
        self.main_container = ttk.Frame(self.parent, style='Modern.TFrame')
        self.main_container.pack(fill='both', expand=True)
        
        # 創建頂部工具欄
        self.create_top_toolbar()
        
        # 創建側邊導航欄
        self.create_sidebar()
        
        # 創建主內容區域
        self.create_main_content()
        
        # 創建狀態欄
        self.create_status_bar()
    
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
            text="電子交接系統",
            font=('Segoe UI', 18, 'bold'),
            foreground=self.COLORS['primary'],
            background=self.COLORS['surface']
        )
        self.main_title.pack(side='left')
        
        # 副標題
        self.subtitle = ttk.Label(
            title_container,
            text="Handover Management System",
            font=('Segoe UI', 9),
            foreground=self.COLORS['text_secondary'],
            background=self.COLORS['surface']
        )
        self.subtitle.pack(side='left', padx=(10, 0))
        
        # 右側工具區
        tool_container = ttk.Frame(toolbar, style='Toolbar.TFrame')
        tool_container.pack(side='right', padx=20)
        
        # 使用者資訊
        self.user_info_label = ttk.Label(
            tool_container,
            text="未登入",
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
        
        # 登出/登入按鈕
        self.auth_button = ttk.Button(
            tool_container,
            text="登入",
            style='Accent.TButton',
            command=self.toggle_auth,
            width=12
        )
        self.auth_button.pack(side='left')
    
    def create_sidebar(self):
        """創建側邊導航欄"""
        self.sidebar_frame = ttk.Frame(self.main_container, width=220, style='Sidebar.TFrame')
        self.sidebar_frame.pack(side='left', fill='y', padx=0, pady=0)
        self.sidebar_frame.pack_propagate(False)
        
        # 側邊欄標題
        sidebar_title = ttk.Label(
            self.sidebar_frame,
            text="導航選單",
            font=('Segoe UI', 12, 'bold'),
            foreground='white',
            background=self.COLORS['sidebar']
        )
        sidebar_title.pack(pady=(20, 10), padx=20, anchor='w')
        
        # 導航按鈕
        self.nav_buttons = {}
        
        nav_items = [
            ('daily_report', '📋', '日報表', 'Daily Report'),
            ('attendance', '👥', '出勤記錄', 'Attendance'),
            ('equipment', '⚙️', '設備異常', 'Equipment'),
            ('lot', '📦', '異常批次', 'Lot/批次'),
            ('summary', '📊', '總結', 'Summary'),
            ('admin', '⚙️', '系統管理', 'Admin')
        ]
        
        for item_id, icon, text_zh, text_en in nav_items:
            btn = ttk.Button(
                self.sidebar_frame,
                text=f"{icon} {text_zh}",
                style='Sidebar.TButton',
                command=lambda page=item_id: self.show_page(page),
                width=20
            )
            btn.pack(fill='x', padx=10, pady=2)
            self.nav_buttons[item_id] = btn
            
            # 添加懸停效果提示
            self.add_tooltip(btn, text_en)
        
        # 側邊欄底部資訊
        separator = ttk.Separator(self.sidebar_frame, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=(20, 10))
        
        version_label = ttk.Label(
            self.sidebar_frame,
            text="Version 2.0",
            font=('Segoe UI', 8),
            foreground='white',
            background=self.COLORS['sidebar']
        )
        version_label.pack(side='bottom', pady=(0, 10), padx=20, anchor='w')
        
        # 收合/展開按鈕
        self.toggle_sidebar_btn = ttk.Button(
            self.sidebar_frame,
            text="◀",
            width=3,
            command=self.toggle_sidebar
        )
        self.toggle_sidebar_btn.place(x=180, y=10)
    
    def create_main_content(self):
        """創建主內容區域"""
        # 內容容器
        self.content_container = ttk.Frame(self.main_container, style='MainContent.TFrame')
        self.content_container.pack(side='left', fill='both', expand=True, padx=0, pady=0)
        
        # 內容區域（使用 Card 設計）
        self.content_frame = ttk.Frame(self.content_container, style='Modern.TFrame')
        self.content_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
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
            text="就緒",
            font=('Segoe UI', 9),
            foreground=self.COLORS['text_secondary'],
            background=self.COLORS['surface']
        )
        self.status_label.pack(side='left', padx=20)
        
        # 狀態指示器
        self.status_indicator = tk.Canvas(self.status_frame, width=12, height=12, highlightthickness=0)
        self.status_indicator.create_oval(1, 1, 11, 11, fill=self.COLORS['success'], outline="")
        self.status_indicator.pack(side='right', padx=20)
    
    def show_page(self, page_id):
        """顯示指定頁面"""
        # 清除現有內容
        for widget in self.page_content.winfo_children():
            widget.destroy()
        
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
        elif page_id == 'admin':
            self.create_admin_page()
        
        self.current_page = page_id
    
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
        self.page_title.config(text='日報表')
        self.page_subtitle.config(text='記錄每日生產交接資訊')
        
        # 日期與班別卡片
        date_card = self.create_card(self.page_content, '📅', '日期與班別資訊')
        date_card.pack(fill='x', padx=0, pady=(0, 20))
        
        # 表單布局
        form_frame = ttk.Frame(date_card, style='Card.TFrame')
        form_frame.pack(fill='x', padx=20, pady=20)
        
        # 日期
        self.create_form_row(
            form_frame, 0,
            '📅 日期:', 'date',
            widget_type='entry',
            var_name='date_var',
            default=datetime.now().strftime("%Y-%m-%d")
        )
        
        # 班別
        self.create_form_row(
            form_frame, 1,
            '⏰ 班別:', 'shift',
            widget_type='combo',
            var_name='shift_var',
            values=["Day", "Night"],
            default="Day"
        )
        
        # 區域
        self.create_form_row(
            form_frame, 2,
            '🏭 區域:', 'area',
            widget_type='combo',
            var_name='area_var',
            values=["etching_D", "etching_E", "litho", "thin_film"],
            default="etching_D"
        )
        
        # 基本信息卡片
        basic_card = self.create_card(self.page_content, '📝', '基本資訊與摘要')
        basic_card.pack(fill='both', expand=True, padx=0, pady=(0, 20))
        
        # Key Machine Output
        ttk.Label(basic_card, text='🔑 Key Machine Output:', style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        self.key_output_text = tk.Text(basic_card, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'])
        self.key_output_text.pack(fill='x', padx=20, pady=(0, 15))
        
        # Key Issues
        ttk.Label(basic_card, text='⚠️ Key Issues:', style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(15, 5))
        self.key_issues_text = tk.Text(basic_card, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'])
        self.key_issues_text.pack(fill='x', padx=20, pady=(0, 15))
        
        # Countermeasures
        ttk.Label(basic_card, text='✅ Countermeasures:', style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(15, 5))
        self.countermeasures_text = tk.Text(basic_card, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'])
        self.countermeasures_text.pack(fill='x', padx=20, pady=(0, 20))
        
        # 操作按鈕
        button_frame = ttk.Frame(basic_card, style='Card.TFrame')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text='💾 儲存日報', style='Primary.TButton', command=self.save_daily_report).pack(side='left')
        ttk.Button(button_frame, text='🔄 重置', style='Accent.TButton', command=self.reset_daily_report).pack(side='left', padx=(10, 0))
    
    def create_card(self, parent, emoji, title):
        """創建卡片容器"""
        card = ttk.Frame(parent, style='Card.TFrame')
        
        # 卡片標題
        title_frame = ttk.Frame(card, style='Card.TFrame')
        title_frame.pack(fill='x', padx=20, pady=(15, 0))
        
        title_label = ttk.Label(title_frame, text=f"{emoji} {title}", style='CardTitle.TLabel')
        title_label.pack(side='left')
        
        # 分隔線
        sep = ttk.Separator(card, orient='horizontal', style='Line.TSeparator')
        sep.pack(fill='x', padx=20, pady=(10, 0))
        
        # 記錄卡片以便後續引用
        setattr(self, f"{title.lower().replace(' ', '_').replace('/', '_')}_card", card)
        
        return card
    
    def create_form_row(self, parent, row, label_text, field_name, widget_type='entry', **kwargs):
        """創建表單行"""
        ttk.Label(parent, text=label_text, font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', padx=0, pady=15)
        
        if widget_type == 'entry':
            var = tk.StringVar(value=kwargs.get('default', ''))
            setattr(self, kwargs['var_name'], var)
            widget = ttk.Entry(parent, textvariable=var, style='Modern.TEntry', width=30)
            widget.grid(row=row, column=1, sticky='w', padx=(20, 0), pady=15)
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
            widget.grid(row=row, column=1, sticky='w', padx=(20, 0), pady=15)
    
    def create_attendance_page(self):
        """創建出勤記錄頁面"""
        self.page_title.config(text='出勤記錄')
        self.page_subtitle.config(text='記錄正社員與契約社員出勤資訊')
        
        # 使用優化版出勤組件
        attendance_section = AttendanceSectionOptimized(self.page_content, self.lang_manager, self)
        attendance_section.get_widget().pack(fill='both', expand=True)
    
    def create_equipment_page(self):
        """創建設備異常頁面"""
        self.page_title.config(text='設備異常')
        self.page_subtitle.config(text='記錄設備異常與處理資訊')
        
        card = self.create_card(self.page_content, '⚙️', '設備異常記錄')
        card.pack(fill='both', expand=True)
        
        # 表單
        form_frame = ttk.Frame(card, style='Card.TFrame')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 設備號碼
        ttk.Label(form_frame, text='設備號碼:', font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=10)
        self.equip_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.equip_id_var, style='Modern.TEntry', width=30).grid(row=0, column=1, sticky='w', padx=20, pady=10)
        
        # 發生時刻
        ttk.Label(form_frame, text='發生時刻:', font=('Segoe UI', 10)).grid(row=0, column=2, sticky='w', pady=10)
        self.start_time_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.start_time_var, style='Modern.TEntry', width=30).grid(row=0, column=3, sticky='w', padx=20, pady=10)
        
        # 影響數量
        ttk.Label(form_frame, text='影響數量:', font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=10)
        self.impact_qty_var = tk.StringVar(value='0')
        ttk.Entry(form_frame, textvariable=self.impact_qty_var, style='Modern.TEntry', width=30).grid(row=1, column=1, sticky='w', padx=20, pady=10)
        
        # 異常內容
        ttk.Label(form_frame, text='異常內容:', font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', pady=10)
        self.equip_desc_text = tk.Text(form_frame, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'])
        self.equip_desc_text.grid(row=2, column=1, columnspan=3, sticky='ew', padx=20, pady=10)
        
        # 對應內容
        ttk.Label(form_frame, text='對應內容:', font=('Segoe UI', 10)).grid(row=3, column=0, sticky='w', pady=10)
        self.action_text = tk.Text(form_frame, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'])
        self.action_text.grid(row=3, column=1, columnspan=3, sticky='ew', padx=20, pady=10)
        
        # 圖片上傳
        image_frame = ttk.Frame(form_frame, style='Card.TFrame')
        image_frame.grid(row=4, column=0, columnspan=4, sticky='w', padx=0, pady=10)
        
        ttk.Label(image_frame, text='異常圖片:', font=('Segoe UI', 10)).pack(side='left')
        self.image_path_var = tk.StringVar()
        ttk.Entry(image_frame, textvariable=self.image_path_var, width=40, state='readonly', style='Modern.TEntry').pack(side='left', padx=20)
        ttk.Button(image_frame, text='瀏覽...', style='Accent.TButton', command=self.browse_image).pack(side='left')
        
        # 按鈕
        button_frame = ttk.Frame(card, style='Card.TFrame')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text='➕ 添加記錄', style='Primary.TButton', command=self.add_equipment_record).pack(side='left')
        ttk.Button(button_frame, text='📋 查看歷史', style='Accent.TButton', command=self.view_equipment_history).pack(side='left', padx=10)
    
    def create_lot_page(self):
        """創建異常批次頁面"""
        self.page_title.config(text='異常批次')
        self.page_subtitle.config(text='記錄批次異常與處置狀況')
        
        card = self.create_card(self.page_content, '📦', '異常批次記錄')
        card.pack(fill='both', expand=True)
        
        form_frame = ttk.Frame(card, style='Card.TFrame')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 批號
        ttk.Label(form_frame, text='批號:', font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=10)
        self.lot_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.lot_id_var, style='Modern.TEntry', width=30).grid(row=0, column=1, sticky='w', padx=20, pady=10)
        
        # 異常內容
        ttk.Label(form_frame, text='異常內容:', font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=10)
        self.lot_desc_text = tk.Text(form_frame, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'])
        self.lot_desc_text.grid(row=1, column=1, columnspan=3, sticky='ew', padx=20, pady=10)
        
        # 處置狀況
        ttk.Label(form_frame, text='處置狀況:', font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', pady=10)
        self.lot_status_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.lot_status_var, style='Modern.TEntry', width=30).grid(row=2, column=1, sticky='w', padx=20, pady=10)
        
        # 特記事項
        ttk.Label(form_frame, text='特記事項:', font=('Segoe UI', 10)).grid(row=3, column=0, sticky='w', pady=10)
        self.lot_notes_text = tk.Text(form_frame, height=4, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'])
        self.lot_notes_text.grid(row=3, column=1, columnspan=3, sticky='ew', padx=20, pady=10)
        
        # 按鈕
        button_frame = ttk.Frame(card, style='Card.TFrame')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text='➕ 添加批次', style='Primary.TButton', command=self.add_lot_record).pack(side='left')
        ttk.Button(button_frame, text='📋 批次列表', style='Accent.TButton', command=self.view_lot_list).pack(side='left', padx=10)
    
    def create_summary_page(self):
        """創建總結頁面"""
        self.page_title.config(text='總結')
        self.page_subtitle.config(text='記錄每日總結與分析')
        
        card = self.create_card(self.page_content, '📊', '工作總結')
        card.pack(fill='both', expand=True)
        
        # Key Issues
        ttk.Label(card, text='⚠️ Key Issues (關鍵問題):', style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        self.summary_key_issues_text = tk.Text(card, height=6, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'])
        self.summary_key_issues_text.pack(fill='x', padx=20, pady=(0, 15))
        
        # Countermeasures
        ttk.Label(card, text='✅ Countermeasures (對策):', style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(15, 5))
        self.summary_countermeasures_text = tk.Text(card, height=6, font=('Segoe UI', 10), relief='flat', bg=self.COLORS['surface'])
        self.summary_countermeasures_text.pack(fill='x', padx=20, pady=(0, 20))
        
        # 統計資訊卡片
        stats_card = self.create_card(self.page_content, '📈', '今日統計')
        stats_card.pack(fill='x')
        
        stats_frame = ttk.Frame(stats_card, style='Card.TFrame')
        stats_frame.pack(fill='x', padx=20, pady=20)
        
        # 今日報表數、出勤率等統計
        stat_items = [
            ('📋', '今日報表', '5', '份'),
            ('👥', '平均出勤率', '92.5', '%'),
            ('⚠️', '設備異常', '3', '件'),
            ('📦', '批次異常', '1', '件')
        ]
        
        for i, (emoji, label, value, unit) in enumerate(stat_items):
            frame = ttk.Frame(stats_frame, style='Card.TFrame')
            frame.grid(row=0, column=i, padx=10, pady=0)
            
            ttk.Label(frame, text=emoji, font=('Segoe UI', 24)).pack()
            ttk.Label(frame, text=label, font=('Segoe UI', 10), foreground=self.COLORS['text_secondary']).pack()
            ttk.Label(frame, text=value, font=('Segoe UI', 18, 'bold'), foreground=self.COLORS['primary']).pack()
            ttk.Label(frame, text=unit, font=('Segoe UI', 9), foreground=self.COLORS['text_secondary']).pack()
    
    def create_admin_page(self):
        """創建管理員頁面"""
        self.page_title.config(text='系統管理')
        self.page_subtitle.config(text='管理使用者、翻譯資源與系統設定')
        
        # 創建 Notebook 分頁
        admin_notebook = ttk.Notebook(self.page_content, style='Modern.TNotebook')
        admin_notebook.pack(fill='both', expand=True)
        
        # 使用者管理分頁
        user_tab = ttk.Frame(admin_notebook, style='Modern.TFrame')
        admin_notebook.add(user_tab, text='👥 使用者管理')
        
        user_mgmt = UserManagementSection(user_tab, self.lang_manager)
        user_mgmt.get_widget().pack(fill='both', expand=True, padx=20, pady=20)
        
        # 翻譯管理分頁
        translation_tab = ttk.Frame(admin_notebook, style='Modern.TFrame')
        admin_notebook.add(translation_tab, text='🌐 翻譯管理')
        
        trans_mgmt = TranslationManagementSection(translation_tab, self.lang_manager)
        trans_mgmt.get_widget().pack(fill='both', expand=True, padx=20, pady=20)
        
        # 系統設定分頁
        settings_tab = ttk.Frame(admin_notebook, style='Modern.TFrame')
        admin_notebook.add(settings_tab, text='⚙️ 系統設定')
        
        self.create_settings_page(settings_tab)
    
    def create_settings_page(self, parent):
        """創建設定頁面"""
        # 資料庫設定
        db_card = self.create_card(parent, '🗄️', '資料庫設定')
        db_card.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(db_card, text='資料庫路徑:', font=('Segoe UI', 10)).pack(anchor='w', padx=20, pady=(15, 5))
        db_path_frame = ttk.Frame(db_card, style='Card.TFrame')
        db_path_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.db_path_var = tk.StringVar(value='handover_system.db')
        ttk.Entry(db_path_frame, textvariable=self.db_path_var, width=50, state='readonly', style='Modern.TEntry').pack(side='left', padx=(0, 10))
        ttk.Button(db_path_frame, text='瀏覽...', style='Accent.TButton').pack(side='left')
        
        # 系統設定
        system_card = self.create_card(parent, '⚙️', '系統設定')
        system_card.pack(fill='x', padx=20, pady=(0, 20))
        
        # 自動備份
        backup_frame = ttk.Frame(system_card, style='Card.TFrame')
        backup_frame.pack(fill='x', padx=20, pady=15)
        
        self.auto_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_frame, text='啟用自動備份', variable=self.auto_backup_var).pack(side='left')
        
        ttk.Label(backup_frame, text='備份間隔:', font=('Segoe UI', 10)).pack(side='left', padx=(20, 10))
        self.backup_interval_var = tk.StringVar(value='7')
        ttk.Entry(backup_frame, textvariable=self.backup_interval_var, width=5, style='Modern.TEntry').pack(side='left')
        ttk.Label(backup_frame, text='天', font=('Segoe UI', 10)).pack(side='left', padx=(5, 0))
    
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
    
    def update_nav_text(self):
        """更新導航文字"""
        nav_items = {
            'daily_report': '📋 日報表',
            'attendance': '👥 出勤記錄',
            'equipment': '⚙️ 設備異常',
            'lot': '📦 異常批次',
            'summary': '📊 總結',
            'admin': '⚙️ 系統管理'
        }
        
        for page_id, btn in self.nav_buttons.items():
            btn.configure(text=nav_items[page_id])
    
    def toggle_auth(self):
        """切換登入/登出"""
        if self.current_user:
            self.logout()
        else:
            self.login()
    
    def login(self):
        """登入"""
        try:
            from frontend.src.components.password_change_dialog import PasswordChangeDialog
            
            # 模擬登入
            self.current_user = {'username': 'Admin', 'role': 'admin'}
            self.user_info_label.config(text=f"👤 {self.current_user['username']} ({self.current_user['role']})")
            self.auth_button.config(text='登出')
            self.status_label.config(text='✅ 登入成功')
            
            # 啟用管理員功能
            if self.current_user['role'] == 'admin':
                self.nav_buttons['admin'].config(state='normal')
            
        except ImportError:
            messagebox.showerror("錯誤", "登入功能暫時無法使用")
    
    def logout(self):
        """登出"""
        self.current_user = None
        self.user_info_label.config(text="未登入")
        self.auth_button.config(text='登入')
        self.status_label.config(text='✅ 已登出')
        self.nav_buttons['admin'].config(state='disabled')
        self.show_page('daily_report')
    
    def on_language_changed(self, new_lang_code):
        """語言變更回調"""
        lang_names = {"ja": "日本語", "en": "English", "zh": "中文"}
        current_lang_name = lang_names.get(new_lang_code, new_lang_code)
        self.status_label.config(text=f'🌐 語言已切換至: {current_lang_name}')
        self.update_nav_text()
    
    def add_tooltip(self, widget, text):
        """添加懸停提示"""
        def enter(event):
            self.status_label.config(text=f'💡 {text}')
        
        def leave(event):
            self.status_label.config(text='就緒')
        
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
    
    def add_equipment_record(self):
        """添加設備記錄"""
        self.status_label.config(text='✅ 設備異常記錄已添加')
    
    def view_equipment_history(self):
        """查看設備歷史"""
        self.status_label.config(text='📋 正在載入設備異常歷史...')
    
    def add_lot_record(self):
        """添加批次記錄"""
        self.status_label.config(text='✅ 批次異常記錄已添加')
    
    def view_lot_list(self):
        """查看批次列表"""
        self.status_label.config(text='📋 正在載入批次異常列表...')
    
    def browse_image(self):
        """瀏覽圖片"""
        file_path = filedialog.askopenfilename(
            title="選擇圖片文件",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
        )
        if file_path:
            self.image_path_var.set(file_path)
            self.status_label.config(text=f'📷 已選擇圖片: {os.path.basename(file_path)}')
    
    def save_daily_report(self):
        """儲存日報"""
        self.status_label.config(text='💾 日報已儲存')
    
    def reset_daily_report(self):
        """重置日報"""
        self.status_label.config(text='🔄 日報表單已重置')


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
