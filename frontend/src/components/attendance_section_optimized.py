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
        
        # 創建界面
        self.setup_ui()
        self.setup_styles()
    
    def setup_styles(self):
        """設置自定義樣式"""
        style = ttk.Style()
        
        # 定義顏色方案
        style.configure("Good.TFrame", background="#e8f5e9")
        style.configure("Warning.TFrame", background="#fff3e0")
        style.configure("Danger.TFrame", background="#ffebee")
        
        style.configure("Good.TLabel", background="#e8f5e9", foreground="#2e7d32")
        style.configure("Warning.TLabel", background="#fff3e0", foreground="#ef6c00")
        style.configure("Danger.TLabel", background="#ffebee", foreground="#c62828")
        
        style.configure("Modified.TEntry", fieldbackground="#fff9c4")
    
    def setup_ui(self):
        """設置優化版界面"""
        # 創建主框架，使用左右分欄
        self.main_frame = ttk.Frame(self.parent, padding="10")
        
        # 頂部資訊欄
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill="x", pady=(0, 15))
        
        self.info_label = ttk.Label(
            info_frame,
            text="💡 提示：出勤率 = 出勤人數 ÷ 定員人數 × 100%",
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
        left_frame = ttk.LabelFrame(
            content_frame,
            text=self.lang_manager.get_text("attendance.regular_staff", "正社員 (Regular Staff)"),
            padding="15"
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # 右側：契約社員
        right_frame = ttk.LabelFrame(
            content_frame,
            text=self.lang_manager.get_text("attendance.contractor_staff", "契約社員 (Contractor Staff)"),
            padding="15"
        )
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # 配置網格權重
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # 設置左側內容
        self.setup_staff_section(left_frame, "regular")
        
        # 設置右側內容
        self.setup_staff_section(right_frame, "contractor")
        
        # 底部操作區
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill="x", pady=(15, 0))
        
        # 左側：驗證按鈕
        validate_btn = ttk.Button(
            action_frame,
            text=self.lang_manager.get_text("attendance.validate", "驗證數據"),
            command=self.validate_attendance_data,
            style="Accent.TButton"
        )
        validate_btn.pack(side="left")
        
        # 中間：即時統計
        self.stats_frame = ttk.LabelFrame(action_frame, text=self.lang_manager.get_text("attendance.statistics", "統計"))
        self.stats_frame.pack(side="left", padx=(20, 0), fill="x", expand=True)
        
        self.setup_statistics_section()
        
        # 右側：儲存按鈕
        save_btn = ttk.Button(
            action_frame,
            text=self.lang_manager.get_text("common.save", "儲存"),
            command=self.save_attendance_data,
            style="Save.TButton"
        )
        save_btn.pack(side="right")
        
        # 設定按鈕樣式
        try:
            style = ttk.Style()
            style.configure("Accent.TButton", font=("TkDefaultFont", 10, "bold"))
            style.configure("Save.TButton", font=("TkDefaultFont", 10, "bold"), background="#4caf50")
        except:
            pass
    
    def setup_staff_section(self, parent, staff_type):
        """設置員工區段（正社員或契約社員）"""
        # 定員
        ttk.Label(parent, text=f"{self.lang_manager.get_text('common.scheduled', '定員')}:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10)
        )
        
        scheduled_var = tk.StringVar(value="0")
        scheduled_entry = ttk.Entry(parent, textvariable=scheduled_var, width=12, justify="right")
        scheduled_entry.grid(row=0, column=1, sticky="w", pady=(0, 10))
        scheduled_entry.bind("<KeyRelease>", lambda e: self.on_data_change(staff_type))
        scheduled_entry.bind("<KeyRelease>", lambda e: self.calculate_rates(), add="+")
        
        # 出勤
        ttk.Label(parent, text=f"{self.lang_manager.get_text('common.present', '出勤')}:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 10)
        )
        
        present_var = tk.StringVar(value="0")
        present_entry = ttk.Entry(parent, textvariable=present_var, width=12, justify="right")
        present_entry.grid(row=1, column=1, sticky="w", pady=(0, 10))
        present_entry.bind("<KeyRelease>", lambda e: self.on_data_change(staff_type))
        present_entry.bind("<KeyRelease>", lambda e: self.calculate_rates(), add="+")
        
        # 欠勤
        ttk.Label(parent, text=f"{self.lang_manager.get_text('common.absent', '欠勤')}:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 10)
        )
        
        absent_var = tk.StringVar(value="0")
        absent_entry = ttk.Entry(parent, textvariable=absent_var, width=12, justify="right")
        absent_entry.grid(row=2, column=1, sticky="w", pady=(0, 10))
        absent_entry.bind("<KeyRelease>", lambda e: self.on_data_change(staff_type))
        absent_entry.bind("<KeyRelease>", lambda e: self.calculate_rates(), add="+")
        
        # 出勤率指示器
        rate_frame = ttk.Frame(parent)
        rate_frame.grid(row=0, column=2, rowspan=3, sticky="ns", padx=(15, 0))
        
        ttk.Label(rate_frame, text=self.lang_manager.get_text("attendance.rate", "出勤率"), font=("TkDefaultFont", 9, "bold")).pack()
        
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
        ttk.Label(parent, text=f"{self.lang_manager.get_text('common.reason', '理由')}:").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=(10, 0)
        )
        
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
    
    def setup_statistics_section(self):
        """設置統計區域"""
        # 總定員
        ttk.Label(self.stats_frame, text="總定員:").grid(row=0, column=0, sticky="w")
        self.total_scheduled_label = ttk.Label(self.stats_frame, text="0", font=("TkDefaultFont", 10, "bold"))
        self.total_scheduled_label.grid(row=0, column=1, sticky="e", padx=(10, 20))
        
        # 總出勤
        ttk.Label(self.stats_frame, text="總出勤:").grid(row=0, column=2, sticky="w")
        self.total_present_label = ttk.Label(self.stats_frame, text="0", font=("TkDefaultFont", 10, "bold"), foreground="#2e7d32")
        self.total_present_label.grid(row=0, column=3, sticky="e", padx=(10, 20))
        
        # 總欠勤
        ttk.Label(self.stats_frame, text="總欠勤:").grid(row=0, column=4, sticky="w")
        self.total_absent_label = ttk.Label(self.stats_frame, text="0", font=("TkDefaultFont", 10, "bold"), foreground="#c62828")
        self.total_absent_label.grid(row=0, column=5, sticky="e")
        
        # 整體出勤率
        ttk.Label(self.stats_frame, text="整體出勤率:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.overall_rate_label = ttk.Label(
            self.stats_frame,
            text="0%",
            font=("TkDefaultFont", 12, "bold")
        )
        self.overall_rate_label.grid(row=1, column=1, sticky="e", pady=(5, 0))
    
    def on_data_change(self, staff_type):
        """當數據變更時調用"""
        self.data_modified = True
        self.update_status_indicator()
    
    def update_status_indicator(self):
        """更新狀態指示器"""
        if self.data_modified:
            self.status_label.config(
                text="⚠️ 未儲存",
                foreground="#ff9800"
            )
        else:
            self.status_label.config(text="")
    
    def calculate_rates(self):
        """計算出勤率"""
        try:
            # 計算正社員出勤率
            regular_scheduled = int(self.regular_scheduled_var.get() or 0)
            regular_present = int(self.regular_present_var.get() or 0)
            regular_rate = (regular_present / regular_scheduled * 100) if regular_scheduled > 0 else 0
            
            # 計算契約社員出勤率
            contractor_scheduled = int(self.contractor_scheduled_var.get() or 0)
            contractor_present = int(self.contractor_present_var.get() or 0)
            contractor_rate = (contractor_present / contractor_scheduled * 100) if contractor_scheduled > 0 else 0
            
            # 更新顯示
            self.regular_rate_label.config(text=f"{regular_rate:.1f}%")
            self.contractor_rate_label.config(text=f"{contractor_rate:.1f}%")
            
            # 更新顏色和狀態指示燈
            self.update_rate_display("regular", regular_rate)
            self.update_rate_display("contractor", contractor_rate)
            
            # 更新總計
            self.update_totals(regular_scheduled, regular_present, contractor_scheduled, contractor_present)
            
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
        
        # 根據出勤率設定顏色
        if rate >= 90:
            color = "#2e7d32"  # 綠色 - 優秀
            light_color = "#4caf50"
        elif rate >= 80:
            color = "#f57c00"  # 橙色 - 良好
            light_color = "#ff9800"
        elif rate >= 60:
            color = "#0288d1"  # 藍色 - 一般
            light_color = "#03a9f4"
        else:
            color = "#c62828"  # 紅色 - 警告
            light_color = "#f44336"
        
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
        
        # 整體出勤率顏色
        if overall_rate >= 85:
            self.overall_rate_label.config(foreground="#2e7d32")
        elif overall_rate >= 70:
            self.overall_rate_label.config(foreground="#f57c00")
        else:
            self.overall_rate_label.config(foreground="#c62828")
    
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
            
            # 驗證規則
            errors = []
            
            # 驗證正社員
            if regular_present + regular_absent > regular_scheduled:
                errors.append(f"正社員：出勤({regular_present}) + 欠勤({regular_absent}) > 定員({regular_scheduled})")
            
            if regular_present < 0 or regular_absent < 0 or regular_scheduled < 0:
                errors.append("正社員：人數不能為負數")
            
            # 驗證契約社員
            if contractor_present + contractor_absent > contractor_scheduled:
                errors.append(f"契約社員：出勤({contractor_present}) + 欠勤({contractor_absent}) > 定員({contractor_scheduled})")
            
            if contractor_present < 0 or contractor_absent < 0 or contractor_scheduled < 0:
                errors.append("契約社員：人數不能為負數")
            
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
                
                success_msg = (
                    f"✅ 所有出勤數據輸入合理。\n\n"
                    f"正社員: 定員 {self.format_number(regular_scheduled)}, "
                    f"出勤 {self.format_number(regular_present)}, "
                    f"欠勤 {self.format_number(regular_absent)}, "
                    f"出勤率 {regular_rate:.1f}%\n\n"
                    f"契約社員: 定員 {self.format_number(contractor_scheduled)}, "
                    f"出勤 {self.format_number(contractor_present)}, "
                    f"欠勤 {self.format_number(contractor_absent)}, "
                    f"出勤率 {contractor_rate:.1f}%"
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
        if self.validate_attendance_data():
            self.data_modified = False
            self.update_status_indicator()
            
            messagebox.showinfo(
                self.lang_manager.get_text("common.success", "成功"),
                self.lang_manager.get_text("attendance.saved", "出勤數據已儲存")
            )
    
    def get_attendance_data(self):
        """獲取當前出勤數據"""
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
