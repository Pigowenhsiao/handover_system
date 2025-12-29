"""
優化版出勤記錄界面組件
改善了布局、添加了視覺提示和即時計算功能
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class AttendanceSectionOptimized:
    """
    優化版出勤記錄界面組件
    特點：
    - 左右分欄布局（正社員左，契約社員右）
    - 即時出勤率計算
    - 色彩提示（根據出勤率）
    - 數字格式化（千位分隔符）
    - 數據變更標記
    """
    
    def __init__(self, parent, lang_manager, app_instance):
        """
        初始化出勤記錄組件
        
        Args:
            parent: 父組件
            lang_manager: 語言管理器實例
            app_instance: 主應用程式實例
        """
        self.parent = parent
        self.lang_manager = lang_manager
        self.app_instance = app_instance
        
        # 追蹤數據變更狀態
        self.data_modified = False
        self.original_data = {}
        self.staff_labels = {}
        
        # 創建界面
        self.setup_ui()
        self.setup_styles()
    
    def setup_styles(self):
        """設置自定義樣式"""
        self.apply_theme()

    def _get_theme_colors(self):
        if self.app_instance and hasattr(self.app_instance, "COLORS"):
            return self.app_instance.COLORS
        return {
            "primary": "#1976D2",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#F44336",
            "text_primary": "#212121",
            "text_secondary": "#757575",
            "surface": "#FFFFFF",
        }

    def _is_dark_theme(self):
        return getattr(self.app_instance, "theme_mode", "light") == "dark"

    def _apply_styles(self):
        style = ttk.Style()
        colors = self._get_theme_colors()

        if self._is_dark_theme():
            good_bg = "#1f2b1f"
            warning_bg = "#332414"
            danger_bg = "#2d1b1b"
            modified_bg = "#3d3a1a"
            good_fg = colors["success"]
            warning_fg = colors["warning"]
            danger_fg = colors["error"]
        else:
            good_bg = "#e8f5e9"
            warning_bg = "#fff3e0"
            danger_bg = "#ffebee"
            modified_bg = "#fff9c4"
            good_fg = "#2e7d32"
            warning_fg = "#ef6c00"
            danger_fg = "#c62828"

        style.configure("Good.TFrame", background=good_bg)
        style.configure("Warning.TFrame", background=warning_bg)
        style.configure("Danger.TFrame", background=danger_bg)

        style.configure("Good.TLabel", background=good_bg, foreground=good_fg)
        style.configure("Warning.TLabel", background=warning_bg, foreground=warning_fg)
        style.configure("Danger.TLabel", background=danger_bg, foreground=danger_fg)

        style.configure("Modified.TEntry", fieldbackground=modified_bg)
        style.configure("Save.TButton", font=("TkDefaultFont", 10, "bold"), background=colors["success"], foreground="white")

    def apply_theme(self):
        self._apply_styles()
        colors = self._get_theme_colors()
        if self._widget_alive(getattr(self, "info_label", None)):
            self.info_label.configure(foreground=colors.get("text_secondary", "gray"))
        if self._widget_alive(getattr(self, "total_present_label", None)):
            self.total_present_label.configure(foreground=colors.get("success", "#4CAF50"))
        if self._widget_alive(getattr(self, "total_absent_label", None)):
            self.total_absent_label.configure(foreground=colors.get("error", "#F44336"))
        if self._widget_alive(getattr(self, "regular_status_canvas", None)):
            self.regular_status_canvas.configure(background=colors.get("surface", "#FFFFFF"))
        if self._widget_alive(getattr(self, "contractor_status_canvas", None)):
            self.contractor_status_canvas.configure(background=colors.get("surface", "#FFFFFF"))
        if self._widget_alive(getattr(self, "overtime_notes_text", None)):
            text_bg = colors.get("surface", "#FFFFFF")
            text_fg = colors.get("text_primary", "#212121")
            if self._is_dark_theme():
                text_bg = colors.get("surface", "#1E1E1E")
                text_fg = colors.get("text_primary", "#E6E6E6")
            self.overtime_notes_text.configure(
                background=text_bg,
                foreground=text_fg,
                insertbackground=text_fg,
            )
        self.update_status_indicator()
        self.calculate_rates()

    def _get_rate_colors(self, rate):
        colors = self._get_theme_colors()
        if self._is_dark_theme():
            if rate >= 90:
                return colors["success"], colors["success"]
            if rate >= 80:
                return colors["warning"], colors["warning"]
            if rate >= 60:
                return colors["primary"], colors["primary"]
            return colors["error"], colors["error"]

        if rate >= 90:
            return "#2e7d32", "#4caf50"
        if rate >= 80:
            return "#f57c00", "#ff9800"
        if rate >= 60:
            return "#0288d1", "#03a9f4"
        return "#c62828", "#f44336"

    def _get_overall_rate_color(self, rate):
        colors = self._get_theme_colors()
        if self._is_dark_theme():
            if rate >= 85:
                return colors["success"]
            if rate >= 70:
                return colors["warning"]
            return colors["error"]

        if rate >= 85:
            return "#2e7d32"
        if rate >= 70:
            return "#f57c00"
        return "#c62828"
    
    def setup_ui(self):
        """設置優化版界面"""
        # 創建主框架，使用左右分欄
        self.main_frame = ttk.Frame(self.parent, padding="10")
        
        # 頂部資訊欄
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill="x", pady=(0, 15))
        
        self.info_label = ttk.Label(
            info_frame,
            text=self.lang_manager.get_text(
                "attendance.info",
                "💡 提示：出勤率 = 出勤人數 ÷ 定員人數 × 100%"
            ),
            font=("TkDefaultFont", 9, "italic"),
            foreground="gray"
        )
        self.info_label.pack(side="left")
        
        # 數據狀態指示器
        self.status_label = ttk.Label(
            info_frame,
            text="",  # 空表示未變更
            font=("TkDefaultFont", 9, "bold")
        )
        self.status_label.pack(side="right")
        
        # 主要內容區 - 左右分欄
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # 左側：正社員
        self.left_frame = ttk.LabelFrame(
            content_frame,
            text=self.lang_manager.get_text("attendance.regular_staff", "正社員 (Regular Staff)"),
            padding="15"
        )
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # 右側：契約社員
        self.right_frame = ttk.LabelFrame(
            content_frame,
            text=self.lang_manager.get_text("attendance.contractor_staff", "契約社員 (Contractor Staff)"),
            padding="15"
        )
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        
        # 配置網格權重
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # 設置左側內容
        self.setup_staff_section(self.left_frame, "regular")
        
        # 設置右側內容
        self.setup_staff_section(self.right_frame, "contractor")

        # 加班區塊
        self.setup_overtime_section()

        # 底部操作區
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill="x", pady=(15, 0))
        
        # 左側：驗證按鈕
        self.validate_btn = ttk.Button(
            action_frame,
            text=self.lang_manager.get_text("attendance.validate", "驗證數據"),
            command=self.validate_attendance_data,
            style="Accent.TButton"
        )
        self.validate_btn.pack(side="left")
        
        # 中間：即時統計
        self.stats_frame = ttk.LabelFrame(action_frame, text=self.lang_manager.get_text("attendance.statistics", "統計"))
        self.stats_frame.pack(side="left", padx=(20, 0), fill="x", expand=True)
        
        self.setup_statistics_section()
        
        # 右側：儲存按鈕
        self.save_btn = ttk.Button(
            action_frame,
            text=self.lang_manager.get_text("common.save", "儲存"),
            command=self.save_attendance_data,
            style="Save.TButton"
        )
        self.save_btn.pack(side="right")
        
        # 設定按鈕樣式
        try:
            style = ttk.Style()
            colors = self._get_theme_colors()
            style.configure("Accent.TButton", font=("TkDefaultFont", 10, "bold"))
            style.configure("Save.TButton", font=("TkDefaultFont", 10, "bold"), background=colors.get("success", "#4caf50"), foreground="white")
        except Exception:
            pass

    def setup_overtime_section(self):
        """設置加班輸入區域"""
        self.overtime_frame = ttk.LabelFrame(
            self.main_frame,
            text=self.lang_manager.get_text("attendance.overtime_title", "加班"),
            padding="10"
        )
        self.overtime_frame.pack(fill="x", pady=(10, 0))

        self.overtime_category_label = ttk.Label(
            self.overtime_frame,
            text=f"{self.lang_manager.get_text('attendance.overtime_category', '類別')}:"
        )
        self.overtime_category_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 6))

        self.overtime_category_var = tk.StringVar(value="")
        self.overtime_category_code = ""
        self.overtime_category_combo = ttk.Combobox(
            self.overtime_frame,
            textvariable=self.overtime_category_var,
            width=18,
            state="readonly"
        )
        self.overtime_category_combo.grid(row=0, column=1, sticky="w", pady=(0, 6))
        self.overtime_category_combo.bind("<<ComboboxSelected>>", self._on_overtime_category_change)

        self.overtime_count_label = ttk.Label(
            self.overtime_frame,
            text=f"{self.lang_manager.get_text('attendance.overtime_count', '人數')}:"
        )
        self.overtime_count_label.grid(row=0, column=2, sticky="w", padx=(20, 10), pady=(0, 6))

        self.overtime_count_var = tk.StringVar(value="")
        self.overtime_count_entry = ttk.Entry(
            self.overtime_frame,
            textvariable=self.overtime_count_var,
            width=10,
            justify="right"
        )
        self.overtime_count_entry.grid(row=0, column=3, sticky="w", pady=(0, 6))
        self.overtime_count_entry.bind("<KeyRelease>", lambda e: self.on_data_change("overtime"))

        self.overtime_notes_label = ttk.Label(
            self.overtime_frame,
            text=f"{self.lang_manager.get_text('attendance.overtime_notes', '備註')}:"
        )
        self.overtime_notes_label.grid(row=1, column=0, sticky="nw", padx=(0, 10))

        self.overtime_notes_text = tk.Text(
            self.overtime_frame,
            width=60,
            height=3,
            wrap="word"
        )
        self.overtime_notes_text.grid(row=1, column=1, columnspan=3, sticky="ew")
        self.overtime_notes_text.bind("<KeyRelease>", lambda e: self.on_data_change("overtime"))

        self.overtime_frame.columnconfigure(1, weight=1)
        self._update_overtime_category_values()

    def setup_staff_section(self, parent, staff_type):
        """設置員工區段（正社員或契約社員）"""
        # 定員
        scheduled_label = ttk.Label(parent, text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:")
        scheduled_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
        
        scheduled_var = tk.StringVar(value="0")
        scheduled_entry = ttk.Entry(parent, textvariable=scheduled_var, width=12, justify="right")
        scheduled_entry.grid(row=0, column=1, sticky="w", pady=(0, 10))
        scheduled_entry.bind("<KeyRelease>", lambda e: self.on_data_change(staff_type))
        scheduled_entry.bind("<KeyRelease>", lambda e: self.calculate_rates(), add="+")
        
        # 出勤
        present_label = ttk.Label(parent, text=f"{self.lang_manager.get_text('common.present', '出勤')}:")
        present_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
        
        present_var = tk.StringVar(value="0")
        present_entry = ttk.Entry(parent, textvariable=present_var, width=12, justify="right")
        present_entry.grid(row=1, column=1, sticky="w", pady=(0, 10))
        present_entry.bind("<KeyRelease>", lambda e: self.on_data_change(staff_type))
        present_entry.bind("<KeyRelease>", lambda e: self.calculate_rates(), add="+")
        
        # 欠勤
        absent_label = ttk.Label(parent, text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:")
        absent_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
        
        absent_var = tk.StringVar(value="0")
        absent_entry = ttk.Entry(parent, textvariable=absent_var, width=12, justify="right", state="readonly")
        absent_entry.grid(row=2, column=1, sticky="w", pady=(0, 10))
        # 缺勤由系統自動計算，避免手動輸入
        
        # 出勤率指示器
        rate_frame = ttk.Frame(parent)
        rate_frame.grid(row=0, column=2, rowspan=3, sticky="ns", padx=(15, 0))
        
        rate_title_label = ttk.Label(
            rate_frame,
            text=self.lang_manager.get_text("attendance.rate", "出勤率"),
            font=("TkDefaultFont", 9, "bold"),
        )
        rate_title_label.pack()
        
        rate_label = ttk.Label(
            rate_frame,
            text="0%",
            font=("TkDefaultFont", 16, "bold"),
            foreground="gray"
        )
        rate_label.pack(pady=(5, 10))
        
        # 狀態指示燈
        status_canvas = tk.Canvas(rate_frame, width=20, height=20, highlightthickness=0)
        status_canvas.create_oval(2, 2, 18, 18, fill="gray", outline="")
        status_canvas.pack()
        
        # 理由
        reason_label = ttk.Label(parent, text=f"{self.lang_manager.get_text('common.reason', '理由')}:")
        reason_label.grid(row=3, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        
        reason_var = tk.StringVar()
        reason_entry = ttk.Entry(parent, textvariable=reason_var, width=35)
        reason_entry.grid(row=3, column=1, columnspan=2, sticky="ew", pady=(10, 0))
        reason_entry.bind("<KeyRelease>", lambda e: self.on_data_change(staff_type))
        
        # 存儲變數
        if staff_type == "regular":
            self.regular_scheduled_var = scheduled_var
            self.regular_present_var = present_var
            self.regular_absent_var = absent_var
            self.regular_reason_var = reason_var
            self.regular_rate_label = rate_label
            self.regular_status_canvas = status_canvas
        else:
            self.contractor_scheduled_var = scheduled_var
            self.contractor_present_var = present_var
            self.contractor_absent_var = absent_var
            self.contractor_reason_var = reason_var
            self.contractor_rate_label = rate_label
            self.contractor_status_canvas = status_canvas

        self.staff_labels[staff_type] = {
            "scheduled": scheduled_label,
            "present": present_label,
            "absent": absent_label,
            "reason": reason_label,
            "rate": rate_title_label,
            "absent_var": absent_var,
            "absent_entry": absent_entry,
        }
    
    def setup_statistics_section(self):
        """設置統計區域"""
        # 總定員
        self.total_scheduled_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text("attendance.total_scheduled", "總定員:")
        )
        self.total_scheduled_title.grid(row=0, column=0, sticky="w")
        self.total_scheduled_label = ttk.Label(self.stats_frame, text="0", font=("TkDefaultFont", 10, "bold"))
        self.total_scheduled_label.grid(row=0, column=1, sticky="e", padx=(10, 20))
        
        # 總出勤
        self.total_present_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text("attendance.total_present", "總出勤:")
        )
        self.total_present_title.grid(row=0, column=2, sticky="w")
        self.total_present_label = ttk.Label(self.stats_frame, text="0", font=("TkDefaultFont", 10, "bold"), foreground="#2e7d32")
        self.total_present_label.grid(row=0, column=3, sticky="e", padx=(10, 20))
        
        # 總欠勤
        self.total_absent_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text("attendance.total_absent", "總欠勤:")
        )
        self.total_absent_title.grid(row=0, column=4, sticky="w")
        self.total_absent_label = ttk.Label(self.stats_frame, text="0", font=("TkDefaultFont", 10, "bold"), foreground="#c62828")
        self.total_absent_label.grid(row=0, column=5, sticky="e")
        
        # 整體出勤率
        self.overall_rate_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text("attendance.overall_rate", "整體出勤率:")
        )
        self.overall_rate_title.grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.overall_rate_label = ttk.Label(
            self.stats_frame,
            text="0%",
            font=("TkDefaultFont", 12, "bold")
        )
        self.overall_rate_label.grid(row=1, column=1, sticky="e", pady=(5, 0))

    def update_language(self):
        """更新語言文字"""
        if not self._widget_alive(self.main_frame):
            return
        self.info_label.config(
            text=self.lang_manager.get_text(
                "attendance.info",
                "💡 提示：出勤率 = 出勤人數 ÷ 定員人數 × 100%"
            )
        )
        self.left_frame.config(text=self.lang_manager.get_text("attendance.regular_staff", "正社員 (Regular Staff)"))
        self.right_frame.config(text=self.lang_manager.get_text("attendance.contractor_staff", "契約社員 (Contractor Staff)"))
        self.validate_btn.config(text=self.lang_manager.get_text("attendance.validate", "驗證數據"))
        self.stats_frame.config(text=self.lang_manager.get_text("attendance.statistics", "統計"))
        self.save_btn.config(text=self.lang_manager.get_text("common.save", "儲存"))

        self.overtime_frame.config(text=self.lang_manager.get_text("attendance.overtime_title", "加班"))
        self.overtime_category_label.config(
            text=f"{self.lang_manager.get_text('attendance.overtime_category', '類別')}:"
        )
        self.overtime_count_label.config(
            text=f"{self.lang_manager.get_text('attendance.overtime_count', '人數')}:"
        )
        self.overtime_notes_label.config(
            text=f"{self.lang_manager.get_text('attendance.overtime_notes', '備註')}:"
        )
        self._update_overtime_category_values()

        for staff_type, labels in self.staff_labels.items():
            labels["scheduled"].config(text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:")
            labels["present"].config(text=f"{self.lang_manager.get_text('common.present', '出勤')}:")
            labels["absent"].config(text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:")
            labels["reason"].config(text=f"{self.lang_manager.get_text('common.reason', '理由')}:")
            labels["rate"].config(text=self.lang_manager.get_text("attendance.rate", "出勤率"))

        self.total_scheduled_title.config(text=self.lang_manager.get_text("attendance.total_scheduled", "總定員:"))
        self.total_present_title.config(text=self.lang_manager.get_text("attendance.total_present", "總出勤:"))
        self.total_absent_title.config(text=self.lang_manager.get_text("attendance.total_absent", "總欠勤:"))
        self.overall_rate_title.config(text=self.lang_manager.get_text("attendance.overall_rate", "整體出勤率:"))
        self.update_status_indicator()

    def _widget_alive(self, widget):
        try:
            return widget is not None and widget.winfo_exists()
        except Exception:
            return False
    
    def on_data_change(self, staff_type):
        """當數據變更時調用"""
        self.data_modified = True
        self.update_status_indicator()
    
    def update_status_indicator(self):
        """???????"""
        if self.data_modified:
            colors = self._get_theme_colors()
            self.status_label.config(
                text=self.lang_manager.get_text("attendance.unsaved", "?? ???"),
                foreground=colors.get("warning", "#ff9800"),
            )
        else:
            self.status_label.config(text="")

    def _update_absent_display(self, staff_type, scheduled, present):
        labels = self.staff_labels.get(staff_type, {})
        absent_var = labels.get("absent_var")
        absent_label = labels.get("absent")
        if absent_var is None or absent_label is None:
            return 0
        absent = scheduled - present
        absent_var.set(str(absent))
        colors = self._get_theme_colors()
        normal_color = colors.get("text_primary", "#212121")
        danger_color = colors.get("error", "#F44336")
        absent_label.config(foreground=danger_color if absent < 0 else normal_color)
        return absent

    def calculate_rates(self):
        """?????"""
        try:
            regular_scheduled = int(self.regular_scheduled_var.get() or 0)
            regular_present = int(self.regular_present_var.get() or 0)
            regular_rate = (regular_present / regular_scheduled * 100) if regular_scheduled > 0 else 0
            self._update_absent_display("regular", regular_scheduled, regular_present)

            contractor_scheduled = int(self.contractor_scheduled_var.get() or 0)
            contractor_present = int(self.contractor_present_var.get() or 0)
            contractor_rate = (contractor_present / contractor_scheduled * 100) if contractor_scheduled > 0 else 0
            self._update_absent_display("contractor", contractor_scheduled, contractor_present)

            self.regular_rate_label.config(text=f"{regular_rate:.1f}%")
            self.contractor_rate_label.config(text=f"{contractor_rate:.1f}%")

            self.update_rate_display("regular", regular_rate)
            self.update_rate_display("contractor", contractor_rate)

            self.update_totals(regular_scheduled, regular_present, contractor_scheduled, contractor_present)
        except (ValueError, ZeroDivisionError):
            pass

    def _get_overtime_category_labels(self):

        return {
            "Regular": self.lang_manager.get_text("attendance.overtime_regular", "正社員"),
            "Contract": self.lang_manager.get_text("attendance.overtime_contract", "契約社員"),
        }

    def _update_overtime_category_values(self):
        if not self._widget_alive(getattr(self, "overtime_category_combo", None)):
            return
        labels = self._get_overtime_category_labels()
        values = sorted(labels.values())
        self.overtime_category_combo["values"] = [""] + values

        if self.overtime_category_code:
            self.overtime_category_var.set(labels.get(self.overtime_category_code, self.overtime_category_code))
        else:
            self.overtime_category_var.set("")

    def _on_overtime_category_change(self, _event=None):
        selection = self.overtime_category_var.get()
        if not selection:
            self.overtime_category_code = ""
            self.on_data_change("overtime")
            return
        for code, label in self._get_overtime_category_labels().items():
            if selection == label:
                self.overtime_category_code = code
                self.on_data_change("overtime")
                return
        self.overtime_category_code = selection
        self.on_data_change("overtime")

    def _get_overtime_notes(self):
        if not self._widget_alive(getattr(self, "overtime_notes_text", None)):
            return ""
        return self.overtime_notes_text.get("1.0", "end").strip()

    def _set_overtime_notes(self, notes):
        if not self._widget_alive(getattr(self, "overtime_notes_text", None)):
            return
        self.overtime_notes_text.delete("1.0", "end")
        if notes:
            self.overtime_notes_text.insert("1.0", notes)

    def update_rate_display(self, staff_type, rate):
        """更新出勤率顯示（顏色和狀態燈）"""
        if staff_type == "regular":
            label = self.regular_rate_label
            canvas = self.regular_status_canvas
        else:
            label = self.contractor_rate_label
            canvas = self.contractor_status_canvas
        
        color, light_color = self._get_rate_colors(rate)
        
        label.config(foreground=color)
        
        # 更新狀態指示燈
        canvas.delete("all")
        canvas.create_oval(2, 2, 18, 18, fill=light_color, outline="")
    
    def update_totals(self, reg_scheduled, reg_present, con_scheduled, con_present):
        """更新總計統計"""
        total_scheduled = reg_scheduled + con_scheduled
        total_present = reg_present + con_present
        total_absent = (reg_scheduled - reg_present) + (con_scheduled - con_present)
        
        self.total_scheduled_label.config(text=f"{total_scheduled:,}")
        self.total_present_label.config(text=f"{total_present:,}")
        self.total_absent_label.config(text=f"{total_absent:,}")
        
        # 整體出勤率
        overall_rate = (total_present / total_scheduled * 100) if total_scheduled > 0 else 0
        self.overall_rate_label.config(text=f"{overall_rate:.1f}%")
        
        self.overall_rate_label.config(foreground=self._get_overall_rate_color(overall_rate))
    
    def format_number(self, value):
        """格式化數字（千位分隔符）"""
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return str(value)
    
    def validate_attendance_data(self):
        """驗證出勤數據的合理性"""
        try:
            # 獲取數據
            regular_scheduled = int(self.regular_scheduled_var.get() or "0")
            regular_present = int(self.regular_present_var.get() or "0") 
            regular_absent = int(self.regular_absent_var.get() or "0")
            
            contractor_scheduled = int(self.contractor_scheduled_var.get() or "0")
            contractor_present = int(self.contractor_present_var.get() or "0")
            contractor_absent = int(self.contractor_absent_var.get() or "0")

            overtime_count_raw = (self.overtime_count_var.get() or "").strip()
            overtime_count = 0
            if overtime_count_raw:
                overtime_count = int(overtime_count_raw)

            # 驗證規則
            errors = []
            
            # 驗證正社員
            if regular_present + regular_absent > regular_scheduled:
                errors.append(
                    self.lang_manager.get_text(
                        "attendance.error_regular_exceeds",
                        "正社員：出勤({present}) + 欠勤({absent}) > 定員({scheduled})"
                    ).format(present=regular_present, absent=regular_absent, scheduled=regular_scheduled)
                )
            
            if regular_present < 0 or regular_absent < 0 or regular_scheduled < 0:
                errors.append(self.lang_manager.get_text("attendance.error_regular_negative", "正社員：人數不能為負數"))
            
            # 驗證契約社員
            if contractor_present + contractor_absent > contractor_scheduled:
                errors.append(
                    self.lang_manager.get_text(
                        "attendance.error_contractor_exceeds",
                        "契約社員：出勤({present}) + 欠勤({absent}) > 定員({scheduled})"
                    ).format(present=contractor_present, absent=contractor_absent, scheduled=contractor_scheduled)
                )
            
            if contractor_present < 0 or contractor_absent < 0 or contractor_scheduled < 0:
                errors.append(self.lang_manager.get_text("attendance.error_contractor_negative", "契約社員：人數不能為負數"))

            if overtime_count < 0:
                errors.append(self.lang_manager.get_text("attendance.error_overtime_negative", "加班人數不能為負數"))

            # 顯示結果
            if errors:
                error_msg = "\n".join(errors)
                messagebox.showwarning(
                    self.lang_manager.get_text("attendance.validation_failed", "驗證失敗"),
                    error_msg
                )
                return False
            else:
                # 計算出勤率
                regular_rate = (regular_present / regular_scheduled * 100) if regular_scheduled > 0 else 0
                contractor_rate = (contractor_present / contractor_scheduled * 100) if contractor_scheduled > 0 else 0
                
                success_msg = "\n\n".join(
                    [
                        self.lang_manager.get_text(
                            "attendance.validation_summary_intro",
                            "✅ 所有出勤數據輸入合理。"
                        ),
                        self.lang_manager.get_text(
                            "attendance.validation_summary_regular",
                            "正社員: 定員 {scheduled}, 出勤 {present}, 欠勤 {absent}, 出勤率 {rate:.1f}%"
                        ).format(
                            scheduled=self.format_number(regular_scheduled),
                            present=self.format_number(regular_present),
                            absent=self.format_number(regular_absent),
                            rate=regular_rate,
                        ),
                        self.lang_manager.get_text(
                            "attendance.validation_summary_contractor",
                            "契約社員: 定員 {scheduled}, 出勤 {present}, 欠勤 {absent}, 出勤率 {rate:.1f}%"
                        ).format(
                            scheduled=self.format_number(contractor_scheduled),
                            present=self.format_number(contractor_present),
                            absent=self.format_number(contractor_absent),
                            rate=contractor_rate,
                        ),
                    ]
                )
                
                messagebox.showinfo(
                    self.lang_manager.get_text("attendance.validation_success", "驗證成功"),
                    success_msg
                )
                return True
                
        except ValueError:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                self.lang_manager.get_text("attendance.invalid_numbers", "請確保輸入的都是有效數字")
            )
            return False
    
    def save_attendance_data(self):
        """儲存出勤數據"""
        if hasattr(self.app_instance, "ensure_report_context"):
            if not self.app_instance.ensure_report_context():
                return
        if self.validate_attendance_data():
            if hasattr(self.app_instance, "save_attendance_entries"):
                if not self.app_instance.save_attendance_entries(self.get_attendance_data()):
                    return
            self.data_modified = False
            self.update_status_indicator()

            messagebox.showinfo(
                self.lang_manager.get_text("common.success", "成功"),
                self.lang_manager.get_text("attendance.saved", "出勤數據已儲存")
            )
    
    def get_attendance_data(self):
        """獲取當前出勤數據"""
        overtime_count_raw = (self.overtime_count_var.get() or "").strip()
        overtime_count = int(overtime_count_raw) if overtime_count_raw else 0
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
            },
            "overtime": {
                "category": self.overtime_category_code or "",
                "count": overtime_count,
                "notes": self._get_overtime_notes(),
            },
        }
    
    def set_attendance_data(self, data):
        """設置出勤數據"""
        if 'regular' in data:
            regular_data = data['regular']
            self.regular_scheduled_var.set(str(regular_data.get('scheduled', 0)))
            self.regular_present_var.set(str(regular_data.get('present', 0)))
            self.regular_absent_var.set(str(regular_data.get('absent', 0)))
            self.regular_reason_var.set(regular_data.get('reason', ''))
        
        if 'contractor' in data:
            contractor_data = data['contractor']
            self.contractor_scheduled_var.set(str(contractor_data.get('scheduled', 0)))
            self.contractor_present_var.set(str(contractor_data.get('present', 0)))
            self.contractor_absent_var.set(str(contractor_data.get('absent', 0)))
            self.contractor_reason_var.set(contractor_data.get('reason', ''))

        overtime_data = data.get("overtime", {})
        self.overtime_category_code = overtime_data.get("category", "") or ""
        self._update_overtime_category_values()
        overtime_count = overtime_data.get("count", "")
        self.overtime_count_var.set("" if overtime_count in ("", None) else str(overtime_count))
        self._set_overtime_notes(overtime_data.get("notes", ""))

        # 重新計算
        self.calculate_rates()
        self.data_modified = False
        self.update_status_indicator()
    
    def get_widget(self):
        """獲取組件主框架"""
        return self.main_frame
    
    def clear_data(self):
        """清除所有數據"""
        self.regular_scheduled_var.set("0")
        self.regular_present_var.set("0")
        self.regular_absent_var.set("0")
        self.regular_reason_var.set("")
        
        self.contractor_scheduled_var.set("0")
        self.contractor_present_var.set("0")
        self.contractor_absent_var.set("0")
        self.contractor_reason_var.set("")

        self.overtime_category_code = ""
        self.overtime_category_var.set("")
        self.overtime_count_var.set("")
        self._set_overtime_notes("")

        self.data_modified = False
        self.calculate_rates()
        self.update_status_indicator()


# 測試函數
def test_optimized_attendance():
    """測試優化版出勤組件"""
    root = tk.Tk()
    root.title("測試優化版出勤記錄介面")
    root.geometry("800x600")
    
    # 模擬語言管理器
    class MockLangManager:
        def get_text(self, key, default):
            translations = {
                "common.scheduled": "定員",
                "common.present": "出勤",
                "common.absent": "欠勤",
                "common.reason": "理由",
                "attendance.regular_staff": "正社員 (Regular Staff)",
                "attendance.contractor_staff": "契約社員 (Contractor Staff)",
                "attendance.rate": "出勤率",
                "attendance.validate": "驗證數據",
                "attendance.validation_success": "驗證成功",
                "attendance.statistics": "統計",
                "common.success": "成功",
                "common.save": "儲存"
            }
            return translations.get(key, default)
        
        def get_current_language(self):
            return "zh"
    
    # 模擬應用實例
    class MockApp:
        pass
    
    # 創建組件
    attendance = AttendanceSectionOptimized(root, MockLangManager(), MockApp())
    attendance.get_widget().pack(fill="both", expand=True, padx=20, pady=20)
    
    # 設置測試數據
    test_data = {
        "regular": {
            "scheduled": 50,
            "present": 45,
            "absent": 5,
            "reason": "病假"
        },
        "contractor": {
            "scheduled": 30,
            "present": 28,
            "absent": 2,
            "reason": "事假"
        }
    }
    attendance.set_attendance_data(test_data)
    
    root.mainloop()


if __name__ == "__main__":
    test_optimized_attendance()
