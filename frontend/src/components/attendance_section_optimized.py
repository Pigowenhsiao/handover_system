"""
優化版出勤記錄界面組件
改善了布局、添加了視覺提示和即時計算功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from frontend.src.utils.attendance_helpers import (
    compute_attendance_totals,
    validate_attendance_values,
)
from frontend.src.utils.theme_helpers import ThemeColors


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
        return ThemeColors.get_colors(is_dark=False)

    def _is_dark_theme(self):
        return getattr(self.app_instance, "theme_mode", "light") == "dark"

    def _apply_styles(self):
        style = ttk.Style()
        colors = self._get_theme_colors()
        is_dark = self._is_dark_theme()

        bg_colors = ThemeColors.get_status_bg_colors(is_dark)
        fg_colors = ThemeColors.get_status_fg_colors(is_dark)

        style.configure("Good.TFrame", background=bg_colors["good"])
        style.configure("Warning.TFrame", background=bg_colors["warning"])
        style.configure("Danger.TFrame", background=bg_colors["danger"])

        style.configure(
            "Good.TLabel", background=bg_colors["good"], foreground=fg_colors["good"]
        )
        style.configure(
            "Warning.TLabel",
            background=bg_colors["warning"],
            foreground=fg_colors["warning"],
        )
        style.configure(
            "Danger.TLabel",
            background=bg_colors["danger"],
            foreground=fg_colors["danger"],
        )

        style.configure("Modified.TEntry", fieldbackground=bg_colors["modified"])
        style.configure(
            "Save.TButton",
            font=("TkDefaultFont", 10, "bold"),
            background=colors["success"],
            foreground="white",
        )

    def apply_theme(self):
        self._apply_styles()
        colors = self._get_theme_colors()
        if self._widget_alive(getattr(self, "info_label", None)):
            self.info_label.configure(foreground=colors.get("text_secondary", "gray"))
        if self._widget_alive(getattr(self, "total_present_label", None)):
            self.total_present_label.configure(
                foreground=colors.get("success", "#4CAF50")
            )
        if self._widget_alive(getattr(self, "total_absent_label", None)):
            self.total_absent_label.configure(foreground=colors.get("error", "#F44336"))
        if self._widget_alive(getattr(self, "regular_status_canvas", None)):
            self.regular_status_canvas.configure(
                background=colors.get("surface", "#FFFFFF")
            )
        if self._widget_alive(getattr(self, "contractor_status_canvas", None)):
            self.contractor_status_canvas.configure(
                background=colors.get("surface", "#FFFFFF")
            )
        for txt in (
            getattr(self, "overtime_regular_notes_text", None),
            getattr(self, "overtime_contract_notes_text", None),
        ):
            if self._widget_alive(txt):
                text_bg = colors.get("surface", "#FFFFFF")
                text_fg = colors.get("text_primary", "#212121")
                if self._is_dark_theme():
                    text_bg = colors.get("surface", "#1E1E1E")
                    text_fg = colors.get("text_primary", "#E6E6E6")
                txt.configure(
                    background=text_bg, foreground=text_fg, insertbackground=text_fg
                )
        self.update_status_indicator()
        self.calculate_rates()

    def _get_rate_colors(self, rate):
        return ThemeColors.get_status_colors(rate, self._is_dark_theme())

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
                "attendance.info", "💡 提示：出勤率 = 出勤人數 ÷ 定員人數 × 100%"
            ),
            font=("TkDefaultFont", 9, "italic"),
            foreground="gray",
        )
        self.info_label.pack(side="left")

        # 數據狀態指示器
        self.status_label = ttk.Label(
            info_frame,
            text="",  # 空表示未變更
            font=("TkDefaultFont", 9, "bold"),
        )
        self.status_label.pack(side="right")

        # 主要內容區 - 左右分欄
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill="both", expand=True)

        # 左側：正社員
        self.left_frame = ttk.LabelFrame(
            content_frame,
            text=self.lang_manager.get_text(
                "attendance.regular_staff", "正社員 (Regular Staff)"
            ),
            padding="15",
        )
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # 右側：契約社員
        self.right_frame = ttk.LabelFrame(
            content_frame,
            text=self.lang_manager.get_text(
                "attendance.contractor_staff", "契約社員 (Contractor Staff)"
            ),
            padding="15",
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
            style="Accent.TButton",
        )
        self.validate_btn.pack(side="left")

        # 中間：即時統計
        self.stats_frame = ttk.LabelFrame(
            action_frame,
            text=self.lang_manager.get_text("attendance.statistics", "統計"),
        )
        self.stats_frame.pack(side="left", padx=(20, 0), fill="x", expand=True)

        self.setup_statistics_section()

        # 右側：儲存按鈕
        self.save_btn = ttk.Button(
            action_frame,
            text=self.lang_manager.get_text("common.save", "儲存"),
            command=self.save_attendance_data,
            style="Save.TButton",
        )
        self.save_btn.pack(side="right")

        # 設定按鈕樣式
        try:
            style = ttk.Style()
            colors = self._get_theme_colors()
            style.configure("Accent.TButton", font=("TkDefaultFont", 10, "bold"))
            style.configure(
                "Save.TButton",
                font=("TkDefaultFont", 10, "bold"),
                background=colors.get("success", "#4caf50"),
                foreground="white",
            )
        except Exception:
            pass

    def setup_overtime_section(self):
        """?"-??r?S???-??,?.?????YY"""
        self.overtime_frame = ttk.LabelFrame(
            self.main_frame,
            text=self.lang_manager.get_text("attendance.overtime_title", "?S???-"),
            padding="10",
        )
        self.overtime_frame.pack(fill="x", pady=(10, 0))

        # Regular staff overtime
        self.overtime_regular_title = ttk.Label(
            self.overtime_frame,
            text=self.lang_manager.get_text(
                "attendance.overtime_regular", "Regular Staff"
            ),
        )
        self.overtime_regular_title.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.overtime_regular_count_var = tk.StringVar(value="")
        self.overtime_regular_count_entry = ttk.Entry(
            self.overtime_frame,
            textvariable=self.overtime_regular_count_var,
            width=10,
            justify="right",
        )
        self.overtime_regular_count_entry.grid(row=0, column=1, sticky="w")
        self.overtime_regular_count_entry.bind(
            "<KeyRelease>", lambda e: self.on_data_change("overtime")
        )

        self.overtime_regular_notes_label = ttk.Label(
            self.overtime_frame,
            text=self.lang_manager.get_text("attendance.overtime_notes", "Notes"),
        )
        self.overtime_regular_notes_label.grid(
            row=1, column=0, sticky="nw", padx=(0, 10), pady=(6, 0)
        )

        self.overtime_regular_notes_text = tk.Text(
            self.overtime_frame, width=60, height=3, wrap="word"
        )
        self.overtime_regular_notes_text.grid(
            row=1, column=1, columnspan=3, sticky="ew", pady=(6, 0)
        )
        self.overtime_regular_notes_text.bind(
            "<KeyRelease>", lambda e: self.on_data_change("overtime")
        )

        # Contractor staff overtime
        self.overtime_contract_title = ttk.Label(
            self.overtime_frame,
            text=self.lang_manager.get_text(
                "attendance.overtime_contract", "Contract Staff"
            ),
        )
        self.overtime_contract_title.grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=(10, 0)
        )

        self.overtime_contract_count_var = tk.StringVar(value="")
        self.overtime_contract_count_entry = ttk.Entry(
            self.overtime_frame,
            textvariable=self.overtime_contract_count_var,
            width=10,
            justify="right",
        )
        self.overtime_contract_count_entry.grid(
            row=2, column=1, sticky="w", pady=(10, 0)
        )
        self.overtime_contract_count_entry.bind(
            "<KeyRelease>", lambda e: self.on_data_change("overtime")
        )

        self.overtime_contract_notes_label = ttk.Label(
            self.overtime_frame,
            text=self.lang_manager.get_text("attendance.overtime_notes", "Notes"),
        )
        self.overtime_contract_notes_label.grid(
            row=3, column=0, sticky="nw", padx=(0, 10), pady=(6, 0)
        )

        self.overtime_contract_notes_text = tk.Text(
            self.overtime_frame, width=60, height=3, wrap="word"
        )
        self.overtime_contract_notes_text.grid(
            row=3, column=1, columnspan=3, sticky="ew", pady=(6, 0)
        )
        self.overtime_contract_notes_text.bind(
            "<KeyRelease>", lambda e: self.on_data_change("overtime")
        )

        self.overtime_frame.columnconfigure(1, weight=1)

    def setup_staff_section(self, parent, staff_type):
        """設置員工區段（正社員或契約社員）"""
        # 定員
        scheduled_label = ttk.Label(
            parent, text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:"
        )
        scheduled_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10))

        scheduled_var = tk.StringVar(value="0")
        scheduled_entry = ttk.Entry(
            parent, textvariable=scheduled_var, width=12, justify="right"
        )
        scheduled_entry.grid(row=0, column=1, sticky="w", pady=(0, 10))
        scheduled_entry.bind("<KeyRelease>", lambda e: self.on_data_change(staff_type))
        scheduled_entry.bind("<KeyRelease>", lambda e: self.calculate_rates(), add="+")
        scheduled_entry.bind(
            "<KeyRelease>", lambda e: self._recalc_absent(staff_type), add="+"
        )

        # 出勤
        present_label = ttk.Label(
            parent, text=f"{self.lang_manager.get_text('common.present', '出勤')}:"
        )
        present_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 10))

        present_var = tk.StringVar(value="0")
        present_entry = ttk.Entry(
            parent, textvariable=present_var, width=12, justify="right"
        )
        present_entry.grid(row=1, column=1, sticky="w", pady=(0, 10))
        present_entry.bind("<KeyRelease>", lambda e: self.on_data_change(staff_type))
        present_entry.bind("<KeyRelease>", lambda e: self.calculate_rates(), add="+")
        present_entry.bind(
            "<KeyRelease>", lambda e: self._recalc_absent(staff_type), add="+"
        )

        # 欠勤
        absent_label = ttk.Label(
            parent, text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:"
        )
        absent_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 10))

        absent_var = tk.StringVar(value="0")
        absent_entry = ttk.Entry(
            parent, textvariable=absent_var, width=12, justify="right"
        )
        absent_entry.grid(row=2, column=1, sticky="w", pady=(0, 10))
        absent_entry.bind("<KeyRelease>", lambda e: self.on_data_change(staff_type))
        absent_entry.bind("<KeyRelease>", lambda e: self.calculate_rates(), add="+")

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
            rate_frame, text="0%", font=("TkDefaultFont", 16, "bold"), foreground="gray"
        )
        rate_label.pack(pady=(5, 10))

        # 狀態指示燈
        status_canvas = tk.Canvas(rate_frame, width=20, height=20, highlightthickness=0)
        status_canvas.create_oval(2, 2, 18, 18, fill="gray", outline="")
        status_canvas.pack()

        # 理由
        reason_label = ttk.Label(
            parent, text=f"{self.lang_manager.get_text('common.reason', '理由')}:"
        )
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
        }

    def setup_statistics_section(self):
        """設置統計區域"""
        # 總定員
        self.total_scheduled_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text("attendance.total_scheduled", "總定員:"),
        )
        self.total_scheduled_title.grid(row=0, column=0, sticky="w")
        self.total_scheduled_label = ttk.Label(
            self.stats_frame, text="0", font=("TkDefaultFont", 10, "bold")
        )
        self.total_scheduled_label.grid(row=0, column=1, sticky="e", padx=(10, 20))

        # 總出勤
        self.total_present_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text("attendance.total_present", "總出勤:"),
        )
        self.total_present_title.grid(row=0, column=2, sticky="w")
        self.total_present_label = ttk.Label(
            self.stats_frame,
            text="0",
            font=("TkDefaultFont", 10, "bold"),
            foreground="#2e7d32",
        )
        self.total_present_label.grid(row=0, column=3, sticky="e", padx=(10, 20))

        # 總欠勤
        self.total_absent_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text("attendance.total_absent", "總欠勤:"),
        )
        self.total_absent_title.grid(row=0, column=4, sticky="w")
        self.total_absent_label = ttk.Label(
            self.stats_frame,
            text="0",
            font=("TkDefaultFont", 10, "bold"),
            foreground="#c62828",
        )
        self.total_absent_label.grid(row=0, column=5, sticky="e")

        # 加班統計
        self.overtime_regular_total_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text(
                "attendance.overtime_regular_total", "Regular OT:"
            ),
        )
        self.overtime_regular_total_title.grid(row=0, column=6, sticky="w")
        self.overtime_regular_total_label = ttk.Label(
            self.stats_frame, text="0", font=("TkDefaultFont", 10, "bold")
        )
        self.overtime_regular_total_label.grid(
            row=0, column=7, sticky="e", padx=(10, 20)
        )

        self.overtime_contract_total_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text(
                "attendance.overtime_contract_total", "Contract OT:"
            ),
        )
        self.overtime_contract_total_title.grid(row=0, column=8, sticky="w")
        self.overtime_contract_total_label = ttk.Label(
            self.stats_frame, text="0", font=("TkDefaultFont", 10, "bold")
        )
        self.overtime_contract_total_label.grid(
            row=0, column=9, sticky="e", padx=(10, 20)
        )

        self.overtime_total_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text(
                "attendance.overtime_total", "Overtime Total:"
            ),
        )
        self.overtime_total_title.grid(row=0, column=10, sticky="w")
        self.overtime_total_label = ttk.Label(
            self.stats_frame, text="0", font=("TkDefaultFont", 10, "bold")
        )
        self.overtime_total_label.grid(row=0, column=11, sticky="e")

        # 整體出勤率
        self.overall_rate_title = ttk.Label(
            self.stats_frame,
            text=self.lang_manager.get_text("attendance.overall_rate", "整體出勤率:"),
        )
        self.overall_rate_title.grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.overall_rate_label = ttk.Label(
            self.stats_frame, text="0%", font=("TkDefaultFont", 12, "bold")
        )
        self.overall_rate_label.grid(row=1, column=1, sticky="e", pady=(5, 0))

    def update_language(self):
        """更新語系後重新套用文字"""
        if not self._widget_alive(self.main_frame):
            return
        self.info_label.config(
            text=self.lang_manager.get_text(
                "attendance.info", "Attendance rate = Present / Scheduled x 100%"
            )
        )
        self.left_frame.config(
            text=self.lang_manager.get_text("attendance.regular_staff", "Regular Staff")
        )
        self.right_frame.config(
            text=self.lang_manager.get_text(
                "attendance.contractor_staff", "Contract Staff"
            )
        )
        self.validate_btn.config(
            text=self.lang_manager.get_text("attendance.validate", "Validate")
        )
        self.stats_frame.config(
            text=self.lang_manager.get_text("attendance.statistics", "Statistics")
        )
        self.save_btn.config(text=self.lang_manager.get_text("common.save", "Save"))

        self.overtime_frame.config(
            text=self.lang_manager.get_text("attendance.overtime_title", "Overtime")
        )
        self.overtime_regular_title.config(
            text=self.lang_manager.get_text(
                "attendance.overtime_regular", "Regular Staff"
            )
        )
        self.overtime_regular_notes_label.config(
            text=self.lang_manager.get_text("attendance.overtime_notes", "Notes")
        )
        self.overtime_contract_title.config(
            text=self.lang_manager.get_text(
                "attendance.overtime_contract", "Contract Staff"
            )
        )
        self.overtime_contract_notes_label.config(
            text=self.lang_manager.get_text("attendance.overtime_notes", "Notes")
        )

        for staff_type, labels in self.staff_labels.items():
            labels["scheduled"].config(
                text=f"{self.lang_manager.get_text('common.scheduled', 'Scheduled')}:"
            )
            labels["present"].config(
                text=f"{self.lang_manager.get_text('common.present', 'Present')}:"
            )
            labels["absent"].config(
                text=f"{self.lang_manager.get_text('common.absent', 'Absent')}:"
            )
            labels["reason"].config(
                text=f"{self.lang_manager.get_text('common.reason', 'Reason')}:"
            )
            labels["rate"].config(
                text=self.lang_manager.get_text("attendance.rate", "Attendance Rate")
            )

        self.total_scheduled_title.config(
            text=self.lang_manager.get_text(
                "attendance.total_scheduled", "Total Scheduled:"
            )
        )
        self.total_present_title.config(
            text=self.lang_manager.get_text(
                "attendance.total_present", "Total Present:"
            )
        )
        self.total_absent_title.config(
            text=self.lang_manager.get_text("attendance.total_absent", "Total Absent:")
        )
        self.overtime_regular_total_title.config(
            text=self.lang_manager.get_text(
                "attendance.overtime_regular_total", "Regular OT:"
            )
        )
        self.overtime_contract_total_title.config(
            text=self.lang_manager.get_text(
                "attendance.overtime_contract_total", "Contract OT:"
            )
        )
        self.overtime_total_title.config(
            text=self.lang_manager.get_text(
                "attendance.overtime_total", "Overtime Total:"
            )
        )
        self.overall_rate_title.config(
            text=self.lang_manager.get_text(
                "attendance.overall_rate", "Overall Attendance Rate:"
            )
        )
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
        if staff_type == "overtime":
            self.update_overtime_stats()

    def update_status_indicator(self):
        """更新狀態指示器"""
        if self.data_modified:
            colors = self._get_theme_colors()
            self.status_label.config(
                text=self.lang_manager.get_text("attendance.unsaved", "⚠️ 未儲存"),
                foreground=colors.get("warning", "#ff9800"),
            )
        else:
            self.status_label.config(text="")

    def calculate_rates(self):
        """計算出勤率"""
        try:
            # 計算正社員出勤率
            regular_scheduled = int(self.regular_scheduled_var.get() or 0)
            regular_present = int(self.regular_present_var.get() or 0)
            regular_rate = (
                (regular_present / regular_scheduled * 100)
                if regular_scheduled > 0
                else 0
            )

            # 計算契約社員出勤率
            contractor_scheduled = int(self.contractor_scheduled_var.get() or 0)
            contractor_present = int(self.contractor_present_var.get() or 0)
            contractor_rate = (
                (contractor_present / contractor_scheduled * 100)
                if contractor_scheduled > 0
                else 0
            )

            # 更新顯示
            self.regular_rate_label.config(text=f"{regular_rate:.1f}%")
            self.contractor_rate_label.config(text=f"{contractor_rate:.1f}%")

            # 更新顏色和狀態指示燈
            self.update_rate_display("regular", regular_rate)
            self.update_rate_display("contractor", contractor_rate)

            # 更新總計
            self.update_totals(
                regular_scheduled,
                regular_present,
                contractor_scheduled,
                contractor_present,
            )
            self.update_overtime_stats()

        except (ValueError, ZeroDivisionError):
            pass

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
        totals = compute_attendance_totals(
            reg_scheduled, reg_present, con_scheduled, con_present
        )

        self.total_scheduled_label.config(text=f"{totals['total_scheduled']:,}")
        self.total_present_label.config(text=f"{totals['total_present']:,}")
        self.total_absent_label.config(text=f"{totals['total_absent']:,}")

        # 整體出勤率
        overall_rate = totals["overall_rate"]
        self.overall_rate_label.config(text=f"{overall_rate:.1f}%")

        self.overall_rate_label.config(
            foreground=self._get_overall_rate_color(overall_rate)
        )

    def _get_overtime_counts(self):
        reg_raw = (self.overtime_regular_count_var.get() or "").strip()
        con_raw = (self.overtime_contract_count_var.get() or "").strip()
        try:
            reg_count = int(reg_raw) if reg_raw else 0
        except ValueError:
            reg_count = 0
        try:
            con_count = int(con_raw) if con_raw else 0
        except ValueError:
            con_count = 0
        return reg_count, con_count, reg_count + con_count

    def update_overtime_stats(self):
        """更新加班統計顯示"""
        reg_count, con_count, total_count = self._get_overtime_counts()
        self.overtime_regular_total_label.config(text=self.format_number(reg_count))
        self.overtime_contract_total_label.config(text=self.format_number(con_count))
        self.overtime_total_label.config(text=self.format_number(total_count))

    def _recalc_absent(self, staff_type):
        """依據排班與出勤自動計算缺席人數"""
        try:
            if staff_type == "regular":
                scheduled = int(self.regular_scheduled_var.get() or 0)
                present = int(self.regular_present_var.get() or 0)
                target = self.regular_absent_var
            else:
                scheduled = int(self.contractor_scheduled_var.get() or 0)
                present = int(self.contractor_present_var.get() or 0)
                target = self.contractor_absent_var
        except ValueError:
            return
        new_absent = max(scheduled - present, 0)
        if target.get() != str(new_absent):
            target.set(str(new_absent))
            self.on_data_change(staff_type)

    def format_number(self, value):
        """格式化數字（千位分隔符）"""
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return str(value)

    def validate_attendance_data(self):
        """?c-?-%????<??,?"s?s,??^??+??"""
        try:
            # ?????-?,?"s
            regular_scheduled = int(self.regular_scheduled_var.get() or "0")
            regular_present = int(self.regular_present_var.get() or "0")
            regular_absent = int(self.regular_absent_var.get() or "0")

            contractor_scheduled = int(self.contractor_scheduled_var.get() or "0")
            contractor_present = int(self.contractor_present_var.get() or "0")
            contractor_absent = int(self.contractor_absent_var.get() or "0")

            reg_ot_raw = (self.overtime_regular_count_var.get() or "").strip()
            con_ot_raw = (self.overtime_contract_count_var.get() or "").strip()
            reg_ot = int(reg_ot_raw) if reg_ot_raw else 0
            con_ot = int(con_ot_raw) if con_ot_raw else 0

            errors = validate_attendance_values(
                {
                    "scheduled": regular_scheduled,
                    "present": regular_present,
                    "absent": regular_absent,
                },
                {
                    "scheduled": contractor_scheduled,
                    "present": contractor_present,
                    "absent": contractor_absent,
                },
                {"regular": reg_ot, "contract": con_ot},
                self.lang_manager.get_text,
            )

            # ??_???????zo
            if errors:
                error_msg = "\n".join(errors)
                messagebox.showwarning(
                    self.lang_manager.get_text(
                        "attendance.validation_failed", "Validation failed"
                    ),
                    error_msg,
                )
                return False
            else:
                # ?"^?r-????<??Z?
                regular_rate = (
                    (regular_present / regular_scheduled * 100)
                    if regular_scheduled > 0
                    else 0
                )
                contractor_rate = (
                    (contractor_present / contractor_scheduled * 100)
                    if contractor_scheduled > 0
                    else 0
                )

                success_msg = "\n\n".join(
                    [
                        self.lang_manager.get_text(
                            "attendance.validation_summary_intro",
                            "Summary of attendance validation:",
                        ),
                        self.lang_manager.get_text(
                            "attendance.validation_summary_regular",
                            "Regular staff: scheduled {scheduled}, present {present}, absent {absent}, attendance rate {rate:.1f}%",
                        ).format(
                            scheduled=self.format_number(regular_scheduled),
                            present=self.format_number(regular_present),
                            absent=self.format_number(regular_absent),
                            rate=regular_rate,
                        ),
                        self.lang_manager.get_text(
                            "attendance.validation_summary_contractor",
                            "Contract staff: scheduled {scheduled}, present {present}, absent {absent}, attendance rate {rate:.1f}%",
                        ).format(
                            scheduled=self.format_number(contractor_scheduled),
                            present=self.format_number(contractor_present),
                            absent=self.format_number(contractor_absent),
                            rate=contractor_rate,
                        ),
                    ]
                )

                messagebox.showinfo(
                    self.lang_manager.get_text(
                        "attendance.validation_success", "Validation passed"
                    ),
                    success_msg,
                )
                return True

        except ValueError:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "?O_???"),
                self.lang_manager.get_text(
                    "attendance.invalid_numbers", "??<????????,?.?s,????~_?o%?^?,?--"
                ),
            )
            return False

    def save_attendance_data(self):
        """儲存出勤數據"""
        if hasattr(self.app_instance, "ensure_report_context"):
            if not self.app_instance.ensure_report_context():
                return
        if self.validate_attendance_data():
            if hasattr(self.app_instance, "save_attendance_entries"):
                if not self.app_instance.save_attendance_entries(
                    self.get_attendance_data()
                ):
                    return
            self.data_modified = False
            self.update_status_indicator()

            messagebox.showinfo(
                self.lang_manager.get_text("common.success", "成功"),
                self.lang_manager.get_text("attendance.saved", "出勤數據已儲存"),
            )

    def get_attendance_data(self):
        """?????-??%?????<??,?"s"""
        reg_notes = self.overtime_regular_notes_text.get("1.0", "end").strip()
        con_notes = self.overtime_contract_notes_text.get("1.0", "end").strip()
        reg_ot_raw = (self.overtime_regular_count_var.get() or "").strip()
        con_ot_raw = (self.overtime_contract_count_var.get() or "").strip()
        return {
            "regular": {
                "scheduled": int(self.regular_scheduled_var.get() or "0"),
                "present": int(self.regular_present_var.get() or "0"),
                "absent": int(self.regular_absent_var.get() or "0"),
                "reason": self.regular_reason_var.get(),
            },
            "contractor": {
                "scheduled": int(self.contractor_scheduled_var.get() or "0"),
                "present": int(self.contractor_present_var.get() or "0"),
                "absent": int(self.contractor_absent_var.get() or "0"),
                "reason": self.contractor_reason_var.get(),
            },
            "overtime": {
                "regular": {
                    "count": int(reg_ot_raw) if reg_ot_raw else 0,
                    "notes": reg_notes,
                },
                "contract": {
                    "count": int(con_ot_raw) if con_ot_raw else 0,
                    "notes": con_notes,
                },
            },
        }

    def set_attendance_data(self, data):
        """?"-??r????<??,?"s"""
        if "regular" in data:
            regular_data = data["regular"]
            self.regular_scheduled_var.set(str(regular_data.get("scheduled", 0)))
            self.regular_present_var.set(str(regular_data.get("present", 0)))
            self.regular_absent_var.set(str(regular_data.get("absent", 0)))
            self.regular_reason_var.set(regular_data.get("reason", ""))

        if "contractor" in data:
            contractor_data = data["contractor"]
            self.contractor_scheduled_var.set(str(contractor_data.get("scheduled", 0)))
            self.contractor_present_var.set(str(contractor_data.get("present", 0)))
            self.contractor_absent_var.set(str(contractor_data.get("absent", 0)))
            self.contractor_reason_var.set(contractor_data.get("reason", ""))

        overtime_data = data.get("overtime", {}) or {}
        reg_ot = overtime_data.get("regular", {}) or {}
        con_ot = overtime_data.get("contract", {}) or {}

        reg_count = reg_ot.get("count", "")
        con_count = con_ot.get("count", "")
        self.overtime_regular_count_var.set(
            "" if reg_count in ("", None) else str(reg_count)
        )
        self.overtime_contract_count_var.set(
            "" if con_count in ("", None) else str(con_count)
        )

        if self._widget_alive(getattr(self, "overtime_regular_notes_text", None)):
            self.overtime_regular_notes_text.delete("1.0", "end")
            if reg_ot.get("notes"):
                self.overtime_regular_notes_text.insert("1.0", reg_ot.get("notes"))

        if self._widget_alive(getattr(self, "overtime_contract_notes_text", None)):
            self.overtime_contract_notes_text.delete("1.0", "end")
            if con_ot.get("notes"):
                self.overtime_contract_notes_text.insert("1.0", con_ot.get("notes"))

        # ????-??"^?r-
        self.calculate_rates()
        self.update_overtime_stats()
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

        self.overtime_regular_count_var.set("")
        self.overtime_contract_count_var.set("")
        self.overtime_regular_notes_text.delete("1.0", "end")
        self.overtime_contract_notes_text.delete("1.0", "end")

        self.data_modified = False
        self.calculate_rates()
        self.update_overtime_stats()
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
                "common.save": "儲存",
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
        "regular": {"scheduled": 50, "present": 45, "absent": 5, "reason": "病假"},
        "contractor": {"scheduled": 30, "present": 28, "absent": 2, "reason": "事假"},
    }
    attendance.set_attendance_data(test_data)

    root.mainloop()


if __name__ == "__main__":
    test_optimized_attendance()
