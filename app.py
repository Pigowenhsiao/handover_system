from __future__ import annotations

import csv
import os
from datetime import date, datetime, timedelta
from typing import Callable, Dict, List, Optional

import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
from matplotlib import rcParams, font_manager

matplotlib.use("Agg")

# Configure a CJK-capable font to avoid garbled characters in charts.
def _configure_mpl_font() -> None:
    candidates = [
        "Noto Sans TC",
        "Noto Sans CJK TC",
        "Noto Sans SC",
        "Noto Sans CJK JP",
        "Microsoft JhengHei",
        "Microsoft YaHei",
        "PingFang TC",
        "PingFang SC",
        "SimHei",
        "WenQuanYi Micro Hei",
        "Arial Unicode MS",
    ]
    chosen = None
    for name in candidates:
        try:
            if font_manager.findfont(name, fallback_to_default=False):
                chosen = name
                break
        except Exception:
            continue
    rcParams["font.family"] = "sans-serif"
    if chosen:
        rcParams["font.sans-serif"] = [chosen, "DejaVu Sans", "sans-serif"]
    else:
        rcParams["font.sans-serif"] = ["DejaVu Sans", "sans-serif"]
    rcParams["axes.unicode_minus"] = False


_configure_mpl_font()

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from auth import verify_password, hash_password
from models import (
    AttendanceEntry,
    DailyReport,
    EquipmentLog,
    LotLog,
    DelayEntry,
    SummaryActualEntry,
    SessionLocal,
    ShiftOption,
    AreaOption,
    User,
    init_db,
)

# Version info
VERSION = "v0.3.5-Desktop multi lang version"

# Language resources (restored readable text)
LANGS = {"ja": "日本語", "en": "English", "zh": "中文"}
TEXTS: Dict[str, Dict[str, str]] = {
    "title": {"ja": "引き継ぎシステム（デスクトップ版）", "en": "Handover System (Desktop)", "zh": "交接系統（桌面版）"},
    "login_title": {"ja": "引き継ぎシステム", "en": "Handover System", "zh": "交接系統"},
    "login_username": {"ja": "ユーザー名", "en": "Username", "zh": "帳號"},
    "login_password": {"ja": "パスワード", "en": "Password", "zh": "密碼"},
    "login_button": {"ja": "ログイン", "en": "Login", "zh": "登入"},
    "login_fail": {"ja": "ログイン失敗", "en": "Login Failed", "zh": "登入失敗"},
    "login_empty": {"ja": "ユーザー名とパスワードを入力してください。", "en": "Username and password cannot be empty.", "zh": "帳號與密碼不可空白。"},
    "login_wrong": {"ja": "ユーザー名またはパスワードが違います。", "en": "Invalid username or password.", "zh": "帳號或密碼不正確。"},
    "db_error": {"ja": "データベースエラー：", "en": "Database error: ", "zh": "資料庫錯誤："},
    "logout": {"ja": "ログアウト", "en": "Logout", "zh": "登出"},
    "tab_daily": {"ja": "日報入力", "en": "Daily Entry", "zh": "日常輸入"},
    "tab_report": {"ja": "報表", "en": "Reports", "zh": "報表"},
    "tab_user": {"ja": "ユーザー管理", "en": "User Management", "zh": "使用者管理"},
    "base_info": {"ja": "基本情報", "en": "Basic Info", "zh": "基本資料"},
    "date_label": {"ja": "日付 YYYY-MM-DD", "en": "Date YYYY-MM-DD", "zh": "日期 YYYY-MM-DD"},
    "shift_label": {"ja": "シフト", "en": "Shift", "zh": "班別"},
    "area_label": {"ja": "エリア", "en": "Area", "zh": "區域"},
    "attendance": {"ja": "出勤", "en": "Attendance", "zh": "出勤"},
    "att_category": {"ja": "区分", "en": "Category", "zh": "類別"},
    "att_scheduled": {"ja": "予定", "en": "Scheduled", "zh": "預排"},
    "att_present": {"ja": "出勤", "en": "Present", "zh": "實到"},
    "att_absent": {"ja": "欠勤", "en": "Absent", "zh": "缺勤"},
    "att_reason": {"ja": "理由", "en": "Reason", "zh": "原因"},
    "equipment": {"ja": "設備トラブル", "en": "Equipment Issues", "zh": "設備異常"},
    "equip_id": {"ja": "設備ID", "en": "Equipment ID", "zh": "設備ID"},
    "equip_desc": {"ja": "内容", "en": "Description", "zh": "內容"},
    "equip_start": {"ja": "開始時刻", "en": "Start Time", "zh": "開始時間"},
    "equip_impact": {"ja": "影響数量", "en": "Impact Qty", "zh": "影響數量"},
    "equip_action": {"ja": "対策", "en": "Action Taken", "zh": "處置"},
    "equip_image": {"ja": "画像パス", "en": "Image Path", "zh": "圖片路徑"},
    "lot": {"ja": "異常LOT", "en": "Abnormal LOT", "zh": "異常LOT"},
    "lot_id_col": {"ja": "LOT ID", "en": "Lot ID", "zh": "LOT ID"},
    "lot_desc": {"ja": "内容", "en": "Description", "zh": "內容"},
    "lot_status": {"ja": "状態", "en": "Status", "zh": "狀態"},
    "lot_notes": {"ja": "備考", "en": "Notes", "zh": "備註"},
    "summary": {"ja": "サマリー", "en": "Summary", "zh": "摘要"},
    "import_excel": {"ja": "Excel取込（準備中）", "en": "Import Excel (coming soon)", "zh": "匯入 Excel（稍後提供）"},
    "submit": {"ja": "送信", "en": "Submit", "zh": "送出"},
    "save_update": {"ja": "保存/更新", "en": "Save / Update", "zh": "儲存/更新"},
    "confirm_upload": {"ja": "アップロード確定", "en": "Confirm Upload", "zh": "確認上傳"},
    "clear_form": {"ja": "クリア", "en": "Clear", "zh": "清除"},
    "load_existing": {"ja": "既存データ読込", "en": "Load Existing", "zh": "讀取既有資料"},
    "add": {"ja": "追加", "en": "Add", "zh": "新增"},
    "success": {"ja": "成功", "en": "Success", "zh": "成功"},
    "submit_ok": {"ja": "送信しました。", "en": "Submitted successfully.", "zh": "送出成功。"},
    "submit_updated": {"ja": "更新しました。", "en": "Updated successfully.", "zh": "更新完成。"},
    "error": {"ja": "エラー", "en": "Error", "zh": "錯誤"},
    "empty_data": {"ja": "データが見つかりません", "en": "No data found", "zh": "查無資料"},
    "report_att": {"ja": "出勤レポート", "en": "Attendance Report", "zh": "出勤報表"},
    "report_equip": {"ja": "設備レポート", "en": "Equipment Report", "zh": "設備報表"},
    "report_lot": {"ja": "LOTレポート", "en": "LOT Report", "zh": "LOT 報表"},
    "period_type": {"ja": "集計単位", "en": "Period Type", "zh": "區間種類"},
    "period_header": {"ja": "期間", "en": "Period", "zh": "期間"},
    "count_label": {"ja": "件数", "en": "Count", "zh": "筆數"},
    "rate_label": {"ja": "出勤率(%)", "en": "Attendance Rate (%)", "zh": "出勤率(%)"},
    "debug_label": {"ja": "デバッグ", "en": "DEBUG", "zh": "DEBUG"},
    "dbg_reset_att": {"ja": "出勤行を初期化", "en": "Reset attendance rows", "zh": "重置出勤列"},
    "dbg_select_att": {"ja": "選択中: {id}", "en": "Selected attendance: {id}", "zh": "選擇列: {id}"},
    "dbg_btn_edit": {"ja": "ボタン編集: {id}", "en": "Edit via button: {id}", "zh": "按鈕編輯: {id}"},
    "dbg_dbl_edit": {"ja": "ダブルクリック編集: {id}", "en": "Edit via double click: {id}", "zh": "雙擊編輯: {id}"},
    "dbg_update_att": {"ja": "更新: {id}", "en": "Updated: {id}", "zh": "已更新: {id}"},
    "dbg_no_select": {"ja": "行が選択されていません", "en": "No row selected", "zh": "尚未選取任何列"},
    "err_select_row": {"ja": "編集する行を選択してください。", "en": "Please select a row to edit.", "zh": "請先選擇要編輯的列。"},
    "start_date": {"ja": "開始日 YYYY-MM-DD", "en": "Start Date YYYY-MM-DD", "zh": "起日 YYYY-MM-DD"},
    "end_date": {"ja": "終了日 YYYY-MM-DD", "en": "End Date YYYY-MM-DD", "zh": "迄日 YYYY-MM-DD"},
    "search": {"ja": "検索", "en": "Search", "zh": "查詢"},
    "export_csv": {"ja": "CSV出力", "en": "Export CSV", "zh": "匯出 CSV"},
    "confirm_delete": {"ja": "削除してよいですか？", "en": "Are you sure to delete?", "zh": "確定要刪除嗎？"},
    "delete_success": {"ja": "削除しました", "en": "Deleted successfully", "zh": "刪除成功"},
    "user": {"ja": "ユーザー", "en": "User", "zh": "使用者"},
    "role": {"ja": "権限", "en": "Role", "zh": "角色"},
    "password": {"ja": "パスワード", "en": "Password", "zh": "密碼"},
    "add_user": {"ja": "ユーザー追加", "en": "Add User", "zh": "新增使用者"},
    "reset_pw": {"ja": "パスワードリセット", "en": "Reset Password", "zh": "重設密碼"},
    "delete_user": {"ja": "ユーザー削除", "en": "Delete User", "zh": "刪除使用者"},
    "option_title": {"ja": "シフト・エリア管理", "en": "Shift & Area Management", "zh": "班別/區域管理"},
    "shift_list": {"ja": "シフト一覧", "en": "Shift List", "zh": "班別列表"},
    "area_list": {"ja": "エリア一覧", "en": "Area List", "zh": "區域列表"},
    "name": {"ja": "名称", "en": "Name", "zh": "名稱"},
    "update": {"ja": "更新", "en": "Update", "zh": "更新"},
    "delete": {"ja": "削除", "en": "Delete", "zh": "刪除"},
    "lang_label": {"ja": "言語", "en": "Language", "zh": "語言"},
    "actions_section": {"ja": "操作", "en": "Actions", "zh": "操作"},
    "summary_key": {"ja": "重要設備の出力", "en": "Key Machine Output", "zh": "重要設備產出"},
    "summary_issues": {"ja": "主要課題", "en": "Key Issues", "zh": "關鍵問題"},
    "summary_counter": {"ja": "対策", "en": "Countermeasures", "zh": "對策"},
    "att_chart_title": {"ja": "出勤率トレンド", "en": "Attendance Trend", "zh": "出勤率趨勢"},
    "equip_chart_title": {"ja": "設備異常トレンド", "en": "Equipment Issue Trend", "zh": "設備異常趨勢"},
    "lot_chart_title": {"ja": "異常LOTトレンド", "en": "Abnormal LOT Trend", "zh": "異常 LOT 趨勢"},
    "export": {"ja": "エクスポート", "en": "Export", "zh": "匯出"},
    "export_no_data": {"ja": "出力するデータがありません", "en": "No data to export", "zh": "沒有可匯出的資料"},
    "export_success": {"ja": "エクスポート成功", "en": "Export succeeded", "zh": "匯出成功"},
    "export_fail": {"ja": "エクスポート失敗", "en": "Export failed", "zh": "匯出失敗"},
    "export_att_title": {"ja": "出勤レポート出力", "en": "Export Attendance Report", "zh": "匯出出勤報表"},
    "export_equip_title": {"ja": "設備レポート出力", "en": "Export Equipment Report", "zh": "匯出設備報表"},
    "export_lot_title": {"ja": "LOTレポート出力", "en": "Export LOT Report", "zh": "匯出 LOT 報表"},
    "choose_image": {"ja": "画像選択", "en": "Choose Image", "zh": "選擇圖片"},
    "dialog_add_equip": {"ja": "設備異常の追加", "en": "Add Equipment Issue", "zh": "新增設備異常"},
    "dialog_add_lot": {"ja": "異常LOTの追加", "en": "Add Abnormal LOT", "zh": "新增異常 LOT"},
    "dialog_edit_att": {"ja": "出勤の編集", "en": "Edit Attendance", "zh": "編輯出勤"},
    "edit": {"ja": "編集", "en": "Edit", "zh": "編輯"},
    "version_label": {"ja": "バージョン", "en": "Version", "zh": "版本"},
    "id_label": {"ja": "ID", "en": "ID", "zh": "ID"},
    "shift_name": {"ja": "シフト名", "en": "Shift Name", "zh": "班別名稱"},
    "area_name": {"ja": "エリア名", "en": "Area Name", "zh": "區域名稱"},
    "aggregate": {"ja": "集計", "en": "Aggregate", "zh": "彙總"},
    "info": {"ja": "情報", "en": "Info", "zh": "提示"},
    "duplicate_title": {"ja": "データ重複", "en": "Duplicate Data", "zh": "資料重複"},
    "duplicate_prompt": {"ja": "同じ日付・シフト・エリアのデータが存在します。上書きしますか？", "en": "Data for the same date, shift, and area already exists. Overwrite?", "zh": "同一天同區域同班別的資料已存在，是否覆寫？"},
    "duplicate_skip": {"ja": "保存を中止しました。", "en": "Save skipped.", "zh": "已取消寫入。"},
    "confirm_upload_prompt": {"ja": "全ての欄位（サマリー含む）をアップロードしてよいですか？", "en": "Upload all fields (including summary)?", "zh": "是否確認上傳全部欄位（含總結）？"},
    "detail_title": {"ja": "データ詳細", "en": "Row Details", "zh": "資料明細"},
    "date_format_invalid": {"ja": "日付は YYYY-MM-DD 形式で入力してください", "en": "Date format must be YYYY-MM-DD", "zh": "日期格式需為 YYYY-MM-DD"},
    "dialog_edit_user": {"ja": "ユーザー編集", "en": "Edit User", "zh": "編輯使用者"},
    "dialog_edit_shift": {"ja": "シフト編集", "en": "Edit Shift", "zh": "編輯班別"},
    "dialog_edit_area": {"ja": "エリア編集", "en": "Edit Area", "zh": "編輯區域"},
    "total": {"ja": "合計", "en": "Total", "zh": "總計"},
    "tab_delay": {"ja": "ディレイリスト", "en": "Delay List", "zh": "延遲清單"},
    "import_delay": {"ja": "Delay Excel取込", "en": "Import Delay Excel", "zh": "匯入延遲Excel"},
    "delay_date": {"ja": "日付", "en": "Date", "zh": "日期"},
    "delay_time": {"ja": "時間帯", "en": "Time", "zh": "時間"},
    "delay_reactor": {"ja": "装置", "en": "Reactor", "zh": "設備"},
    "delay_process": {"ja": "工程", "en": "Process", "zh": "製程"},
    "delay_lot": {"ja": "ロット", "en": "Lot", "zh": "批號"},
    "delay_wafer": {"ja": "ウェーハ", "en": "Wafer", "zh": "晶圓"},
    "delay_progress": {"ja": "進行中工程", "en": "In Progress", "zh": "進行中"},
    "delay_prev_steps": {"ja": "前工程", "en": "Previous Steps", "zh": "前站"},
    "delay_prev_time": {"ja": "前工程時間", "en": "Prev Time", "zh": "前站時間"},
    "delay_severity": {"ja": "重要度", "en": "Severity", "zh": "嚴重度"},
    "delay_action": {"ja": "対処内容", "en": "Action", "zh": "對應內容"},
    "delay_note": {"ja": "備考", "en": "Note", "zh": "備註"},
    "tab_summary_actual": {"ja": "Summary Actual", "en": "Summary Actual", "zh": "Summary Actual"},
    "import_summary_actual": {"ja": "Summary Actual 取込", "en": "Import Summary Actual", "zh": "匯入 Summary Actual"},
    "summary_label": {"ja": "ラベル", "en": "Label", "zh": "標籤"},
    "summary_plan": {"ja": "Plan", "en": "Plan", "zh": "Plan"},
    "summary_completed": {"ja": "Completed", "en": "Completed", "zh": "Completed"},
    "summary_in_process": {"ja": "In Process", "en": "In Process", "zh": "In Process"},
    "summary_on_track": {"ja": "On Track", "en": "On Track", "zh": "On Track"},
    "summary_at_risk": {"ja": "At Risk", "en": "At Risk", "zh": "At Risk"},
    "summary_delayed": {"ja": "Delayed", "en": "Delayed", "zh": "Delayed"},
    "summary_no_data": {"ja": "No Data", "en": "No Data", "zh": "No Data"},
    "summary_scrapped": {"ja": "Scrapped", "en": "Scrapped", "zh": "Scrapped"},
    "filter_date": {"ja": "日付フィルタ", "en": "Date Filter", "zh": "日期篩選"},
    "clear_reports": {"ja": "レポート表示をクリア", "en": "Clear Reports", "zh": "清除報表畫面"},
    "number_invalid": {"ja": "数値は整数で入力してください", "en": "Please enter integer values.", "zh": "請輸入整數值。"},
}


class HandoverApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.lang: str = "ja"
        self.title(f"{self._t('title')} {VERSION}")
        self.geometry("1100x720")
        self.resizable(True, True)
        self.minsize(800, 600)
        self.session_user: Optional[Dict[str, str]] = None
        self.shift_options: List[str] = []
        self.area_options: List[str] = []
        self.current_report_id: Optional[int] = None
        self.att_selected_id: Optional[str] = None
        self.debug_var = tk.StringVar(value="")  # used to display debug info on UI
        self.delay_pending_records: List[Dict[str, str]] = []
        self.summary_pending_records: List[Dict[str, str]] = []
        self.att_report_row_map: Dict[str, int] = {}
        self.att_report_row_data: Dict[str, Dict[str, str]] = {}
        
        # Configure styles
        style = ttk.Style()
        style.configure('Delete.TButton', foreground='red')
        
        init_db()
        self._load_options()
        self._build_login()

    def _t(self, key: str) -> str:
        return TEXTS.get(key, {}).get(self.lang, TEXTS.get(key, {}).get("zh", key))

    def _lang_name(self, code: str) -> str:
        return LANGS.get(code, code)

    def _lang_code_from_name(self, name: str) -> str:
        for code, label in LANGS.items():
            if label == name:
                return code
        return name

    def _build_login(self) -> None:
        self.login_frame = ttk.Frame(self)
        self.login_frame.pack(expand=True)

        self.lang_var = tk.StringVar(value=self._lang_name(self.lang))
        lang_frame = ttk.Frame(self.login_frame)
        lang_frame.grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Label(lang_frame, text=self._t("lang_label")).pack(side="left", padx=5)
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=list(LANGS.values()), state="readonly", width=10)
        lang_combo.pack(side="left")
        lang_combo.bind("<<ComboboxSelected>>", self._switch_language)

        ttk.Label(self.login_frame, text=self._t("login_title"), font=("Arial", 18, "bold")).grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Label(self.login_frame, text=self._t("login_username")).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self.login_frame, text=self._t("login_password")).grid(row=3, column=0, sticky="e", padx=5, pady=5)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        ttk.Entry(self.login_frame, textvariable=self.username_var).grid(row=2, column=1, padx=5, pady=5)
        ttk.Entry(self.login_frame, textvariable=self.password_var, show="*").grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(self.login_frame, text=self._t("login_button"), command=self._handle_login).grid(row=4, column=0, columnspan=2, pady=10)

    def _handle_login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            messagebox.showerror(self._t("login_fail"), self._t("login_empty"))
            return
        try:
            with SessionLocal() as db:
                user = db.query(User).filter(User.username == username).first()
                if user and verify_password(password, user.password_hash):
                    self.session_user = {"id": user.id, "username": user.username, "role": user.role}
                else:
                    self.session_user = None
        except Exception as exc:
            messagebox.showerror(self._t("login_fail"), f"{self._t('db_error')}{exc}")
            return

        if self.session_user:
            self.login_frame.destroy()
            self._build_main_ui()
        else:
            messagebox.showerror(self._t("login_fail"), self._t("login_wrong"))

    def _build_main_ui(self) -> None:
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x")
        ttk.Label(top_bar, text=f"{self._t('version_label')}: {VERSION}").pack(side="left", padx=10, pady=5)
        ttk.Label(
            top_bar,
            text=f"{self._t('user')}: {self.session_user['username']} ({self.session_user['role']})",
        ).pack(side="left", padx=10, pady=5)
        ttk.Button(top_bar, text=self._t("logout"), command=self._logout).pack(side="right", padx=10)
        lang_frame = ttk.Frame(top_bar)
        lang_frame.pack(side="right", padx=10)
        ttk.Label(lang_frame, text=self._t("lang_label")).pack(side="left", padx=5)
        self.lang_var = tk.StringVar(value=self._lang_name(self.lang))
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=list(LANGS.values()), state="readonly", width=10)
        lang_combo.pack(side="left")
        lang_combo.bind("<<ComboboxSelected>>", self._switch_language)

        # Debug info display
        debug_frame = ttk.Frame(self)
        debug_frame.pack(fill="x")
        ttk.Label(debug_frame, text=f"{self._t('debug_label')}:").pack(side="left", padx=5)
        self.debug_label = ttk.Label(debug_frame, textvariable=self.debug_var, foreground="blue")
        self.debug_label.pack(side="left", padx=5, pady=2)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.daily_frame = ttk.Frame(self.notebook)
        self.report_frame = ttk.Frame(self.notebook)
        self.user_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.daily_frame, text=self._t("tab_daily"))
        self.notebook.add(self.report_frame, text=self._t("tab_report"))
        if self.session_user.get("role") == "admin":
            self.notebook.add(self.user_frame, text=self._t("tab_user"))

        self._build_daily_tab()
        self._build_report_tab()
        if self.session_user.get("role") == "admin":
            self._build_user_tab()
        self.bind("<Configure>", self._on_resize)

    def _logout(self) -> None:
        self.session_user = None
        for widget in self.winfo_children():
            widget.destroy()
        self._build_login()

    def _clear_tree(self, tree: ttk.Treeview) -> None:
        for item in tree.get_children():
            tree.delete(item)

    def _clear_reports_view(self, target: Optional[str] = None) -> None:
        """Clear report tables; target 可指定 att/equip/lot/delay/summary/all."""
        if target in (None, "all", "delay"):
            self.delay_pending_records = []
        if target in (None, "all", "summary"):
            self.summary_pending_records = []
        if target in (None, "all", "att"):
            if hasattr(self, "att_report_tree"):
                self._clear_tree(self.att_report_tree)
            self.att_report_row_map = {}
            self.att_report_row_data = {}
        if target in (None, "all", "equip"):
            for attr in ["equip_tree_detail", "equip_tree_agg"]:
                if hasattr(self, attr):
                    self._clear_tree(getattr(self, attr))
        if target in (None, "all", "lot"):
            for attr in ["lot_tree_detail", "lot_tree_agg"]:
                if hasattr(self, attr):
                    self._clear_tree(getattr(self, attr))
        if target in (None, "all", "delay"):
            if hasattr(self, "delay_tree"):
                self._clear_tree(self.delay_tree)
        if target in (None, "all", "summary"):
            if hasattr(self, "summary_tree"):
                self._clear_tree(self.summary_tree)

    def _embed_chart(self, frame: ttk.Frame, fig_attr: str, fig: plt.Figure) -> None:
        # Destroy previous canvas if exists
        old = getattr(self, fig_attr, None)
        if old:
            old.get_tk_widget().destroy()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        setattr(self, fig_attr, canvas)

    def _load_options(self) -> None:
        """Load shift/area options from database and keep local copies."""
        try:
            with SessionLocal() as db:
                self.shift_options = [s.name for s in db.query(ShiftOption).order_by(ShiftOption.id).all()]
                self.area_options = [a.name for a in db.query(AreaOption).order_by(AreaOption.id).all()]
        except Exception as exc:
            messagebox.showerror("錯誤", f"讀取班別/區域選項失敗：{exc}")
            self.shift_options = ["Day", "Night"]
            self.area_options = ["etching_D", "etching_E"]

    def _refresh_option_widgets(self) -> None:
        """Sync combo boxes after option changes."""
        if hasattr(self, "shift_combo"):
            self.shift_combo["values"] = self.shift_options
            if self.shift_var.get() not in self.shift_options and self.shift_options:
                self.shift_var.set(self.shift_options[0])
        if hasattr(self, "area_combo"):
            self.area_combo["values"] = self.area_options
            if self.area_var.get() not in self.area_options and self.area_options:
                self.area_var.set(self.area_options[0])

    def _switch_language(self, *_: object) -> None:
        self.lang = self._lang_code_from_name(self.lang_var.get())
        self.title(f"{self._t('title')} {VERSION}")
        for widget in self.winfo_children():
            widget.destroy()
        if self.session_user:
            self._build_main_ui()
        else:
            self._build_login()

    def _log_debug(self, key: str, **kwargs: str) -> None:
        """在畫面上更新偵錯資訊。"""
        tpl = self._t(key)
        try:
            self.debug_var.set(tpl.format(**kwargs))
        except Exception:
            self.debug_var.set(tpl)

    def _on_resize(self, event: tk.Event) -> None:
        """Adaptive resize for daily canvas when window >= 800x600."""
        try:
            width = self.winfo_width()
            height = self.winfo_height()
        except Exception:
            return
        if width < 800 or height < 600:
            return
        if hasattr(self, "daily_canvas") and hasattr(self, "daily_window_id"):
            # Leave small padding for scrollbars/top bars
            new_w = max(200, width - 40)
            new_h = max(200, height - 200)
            self.daily_canvas.config(width=new_w, height=new_h)
            self.daily_canvas.itemconfig(self.daily_window_id, width=new_w)
    def _show_detail_window(
        self,
        tree: ttk.Treeview,
        title: str,
        delete_handler: Optional[Callable[[str, tk.Toplevel], None]] = None,
        can_delete: Optional[Callable[[str], bool]] = None,
    ) -> None:
        """Double-click helper to show a simple detail window for report rows."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo(self._t("info"), self._t("err_select_row"))
            return
        item_id = selection[0]
        cols = tree["columns"]
        values = tree.item(item_id, "values")
        win = tk.Toplevel(self)
        win.title(f"{title} - {self._t('detail_title')}")
        frame = ttk.Frame(win)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        for idx, (col, val) in enumerate(zip(cols, values)):
            label = tree.heading(col).get("text") or col
            ttk.Label(frame, text=label).grid(row=idx, column=0, sticky="e", padx=6, pady=4)
            ttk.Label(frame, text=val, wraplength=420, justify="left").grid(row=idx, column=1, sticky="w", padx=6, pady=4)

        allow_delete = False
        if delete_handler is not None:
            allow_delete = can_delete(item_id) if can_delete else True
        if allow_delete:
            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=len(cols), column=0, columnspan=2, pady=(10, 0))
            ttk.Button(
                btn_frame,
                text=self._t("delete"),
                style="Delete.TButton",
                command=lambda: delete_handler(item_id, win),
            ).pack()

    # ================= Reports: Attendance =================
    def _build_attendance_report_tab(self) -> None:
        control = ttk.Frame(self.att_tab)
        control.pack(fill="x", padx=10, pady=5)

        ttk.Label(control, text=self._t("period_type")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.att_mode_var = tk.StringVar(value="日")
        ttk.Combobox(control, textvariable=self.att_mode_var, values=["日", "週", "月", "自訂"], width=8, state="readonly").grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Label(control, text=self._t("start_date")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ttk.Label(control, text=self._t("end_date")).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.att_start_var = tk.StringVar()
        self.att_end_var = tk.StringVar()
        ttk.Entry(control, textvariable=self.att_start_var, width=12).grid(row=0, column=3, padx=5, pady=5)
        ttk.Entry(control, textvariable=self.att_end_var, width=12).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(control, text=self._t("search"), command=self._load_attendance_report).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(control, text=self._t("export_csv"), command=self._export_attendance_csv).grid(row=0, column=7, padx=5, pady=5)
        ttk.Button(control, text=self._t("clear_reports"), command=lambda: self._clear_reports_view("att")).grid(
            row=0, column=8, padx=5, pady=5
        )

        self.att_report_tree = ttk.Treeview(
            self.att_tab,
            columns=("period", "shift", "area", "scheduled", "present", "absent", "rate"),
            show="headings",
            height=12,
        )
        att_headers = [
            self._t("period_header"),
            self._t("shift_label"),
            self._t("area_label"),
            self._t("att_scheduled"),
            self._t("att_present"),
            self._t("att_absent"),
            self._t("rate_label"),
        ]
        for col, text in zip(self.att_report_tree["columns"], att_headers):
            self.att_report_tree.heading(col, text=text)
            self.att_report_tree.column(col, width=120)
        self.att_report_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.att_report_tree.bind("<Double-1>", self._on_att_report_double_click)

        self.att_chart_frame = ttk.LabelFrame(self.att_tab, text=self._t("att_chart_title"))
        self.att_chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def _load_attendance_report(self) -> None:
        mode = self.att_mode_var.get()
        start_str = self.att_start_var.get().strip()
        end_str = self.att_end_var.get().strip()
        self.att_report_row_map = {}
        self.att_report_row_data = {}
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else None
        except ValueError:
            messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
            return

        try:
            with SessionLocal() as db:
                query = (
                    db.query(AttendanceEntry, DailyReport)
                    .join(DailyReport, AttendanceEntry.report_id == DailyReport.id)
                )
                if start_date:
                    query = query.filter(DailyReport.date >= start_date)
                if end_date:
                    query = query.filter(DailyReport.date <= end_date)
                rows = query.all()
        except Exception as exc:
            messagebox.showerror(self._t("error"), f"{exc}")
            return

        data = []
        for att, rep in rows:
            data.append(
                {
                    "id": att.id,
                    "date": rep.date,
                    "shift": rep.shift,
                    "area": rep.area,
                    "scheduled": att.scheduled_count,
                    "present": att.present_count,
                    "absent": att.absent_count,
                    "reason": att.reason or "",
                }
            )
        if not data:
            self._clear_tree(self.att_report_tree)
            messagebox.showinfo(self._t("success"), self._t("empty_data"))
            return

        df = pd.DataFrame(data)

        def start_of_week(d: date) -> date:
            return d - timedelta(days=d.weekday())

        if mode == "日":
            df["period"] = df["date"]
        elif mode == "週":
            df["period"] = df["date"].apply(start_of_week)
        elif mode == "月":
            df["period"] = df["date"].apply(lambda d: d.strftime("%Y-%m"))
        else:  # custom
            df["period"] = df["date"]

        def calc_rate(scheduled: float, present: float) -> str:
            return "" if scheduled == 0 else round(present * 100 / scheduled, 1)

        # Detailed rows
        df["period_str"] = df["period"].astype(str)
        df["rate"] = df.apply(lambda r: calc_rate(r["scheduled"], r["present"]), axis=1)

        # Sum row per period (ALL/ALL)
        total_rows = (
            df.groupby("period", as_index=False)[["scheduled", "present", "absent"]]
            .sum()
            .assign(shift=self._t("total"), area=self._t("total"))
        )
        total_rows["period_str"] = total_rows["period"].astype(str)
        total_rows["rate"] = total_rows.apply(lambda r: calc_rate(r["scheduled"], r["present"]), axis=1)

        self._clear_tree(self.att_report_tree)
        for _, r in df.iterrows():
            item_id = f"att-{int(r['id'])}"
            self.att_report_tree.insert(
                "",
                "end",
                iid=item_id,
                values=(r["period_str"], r["shift"], r["area"], r["scheduled"], r["present"], r["absent"], r["rate"]),
            )
            self.att_report_row_map[item_id] = int(r["id"])
            self.att_report_row_data[item_id] = {
                "date": str(r["date"]),
                "shift": r["shift"],
                "area": r["area"],
                "scheduled": r["scheduled"],
                "present": r["present"],
                "absent": r["absent"],
                "reason": r.get("reason", ""),
            }
        for idx, r in total_rows.iterrows():
            self.att_report_tree.insert(
                "",
                "end",
                iid=f"total-{idx}-{r['period_str']}",
                values=(r["period_str"], r["shift"], r["area"], r["scheduled"], r["present"], r["absent"], r["rate"]),
            )

        # Chart
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.plot(total_rows["period_str"], [r if r != "" else 0 for r in total_rows["rate"]], marker="o")
        ax.set_ylabel(self._t("rate_label"))
        ax.set_xlabel(self._t("period_header"))
        ax.set_title(self._t("att_chart_title"))
        ax.grid(True, linestyle="--", alpha=0.4)
        plt.xticks(rotation=45, ha="right")
        self._embed_chart(self.att_chart_frame, "att_chart_canvas", fig)

    def _delete_att_report_row(self, item_id: str, window: Optional[tk.Toplevel] = None) -> None:
        """刪除出勤報表中的單筆資料並重載報表。"""
        record_id = self.att_report_row_map.get(item_id)
        if record_id is None:
            messagebox.showinfo(self._t("info"), self._t("err_select_row"))
            return
        if not messagebox.askyesno(self._t("delete"), self._t("confirm_delete")):
            return
        try:
            with SessionLocal() as db:
                entry = db.query(AttendanceEntry).filter(AttendanceEntry.id == record_id).first()
                if not entry:
                    messagebox.showerror(self._t("error"), self._t("err_select_row"))
                    return
                db.delete(entry)
                db.commit()
        except Exception as exc:
            messagebox.showerror(self._t("error"), f"{exc}")
            return
        if window and window.winfo_exists():
            window.destroy()
        self._load_attendance_report()
        messagebox.showinfo(self._t("success"), self._t("delete_success"))

    def _on_att_report_double_click(self, event: tk.Event) -> None:
        """Handle double click on attendance report rows."""
        item_id = self.att_report_tree.identify_row(event.y)
        if not item_id:
            messagebox.showinfo(self._t("info"), self._t("err_select_row"))
            return
        self.att_report_tree.selection_set(item_id)
        if item_id in self.att_report_row_map:
            self._open_att_report_editor(item_id)
        else:
            self._show_detail_window(self.att_report_tree, self._t("report_att"))

    def _open_att_report_editor(self, item_id: str) -> None:
        """Open editable dialog for attendance report detail rows."""
        record_id = self.att_report_row_map.get(item_id)
        if record_id is None:
            messagebox.showerror(self._t("error"), self._t("err_select_row"))
            return
        try:
            with SessionLocal() as db:
                entry = db.query(AttendanceEntry).filter(AttendanceEntry.id == record_id).first()
        except Exception as exc:
            messagebox.showerror(self._t("error"), f"{exc}")
            return
        if not entry:
            messagebox.showerror(self._t("error"), self._t("err_select_row"))
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"{self._t('report_att')} - {self._t('edit')}")

        fields = [
            (self._t("att_scheduled"), entry.scheduled_count),
            (self._t("att_present"), entry.present_count),
            (self._t("att_absent"), entry.absent_count),
            (self._t("att_reason"), entry.reason or ""),
        ]
        entries: List[tk.Entry] = []
        for idx, (label, val) in enumerate(fields):
            ttk.Label(dlg, text=label).grid(row=idx, column=0, padx=6, pady=6, sticky="e")
            ent = ttk.Entry(dlg, width=20)
            ent.insert(0, val)
            ent.grid(row=idx, column=1, padx=6, pady=6)
            entries.append(ent)

        def do_update() -> None:
            try:
                scheduled = int(entries[0].get() or 0)
                present = int(entries[1].get() or 0)
                absent = int(entries[2].get() or 0)
            except ValueError:
                messagebox.showerror(self._t("error"), self._t("number_invalid"))
                return
            reason_val = entries[3].get()
            try:
                with SessionLocal() as db:
                    entry_db = db.query(AttendanceEntry).filter(AttendanceEntry.id == record_id).first()
                    if not entry_db:
                        messagebox.showerror(self._t("error"), self._t("err_select_row"))
                        return
                    entry_db.scheduled_count = scheduled
                    entry_db.present_count = present
                    entry_db.absent_count = absent
                    entry_db.reason = reason_val
                    db.commit()
                dlg.destroy()
                self._load_attendance_report()
                messagebox.showinfo(self._t("success"), self._t("submit_updated"))
            except Exception as exc:
                messagebox.showerror(self._t("error"), f"{exc}")

        btn_frame = ttk.Frame(dlg)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text=self._t("save_update"), command=do_update).pack(side="left", padx=6)
        ttk.Button(
            btn_frame,
            text=self._t("delete"),
            style="Delete.TButton",
            command=lambda: self._delete_att_report_row(item_id, dlg),
        ).pack(side="left", padx=6)

    def _export_attendance_csv(self) -> None:
        rows = [self.att_report_tree.item(i, "values") for i in self.att_report_tree.get_children()]
        if not rows:
            messagebox.showinfo(self._t("export"), self._t("export_no_data"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")], title=self._t("export_att_title")
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        self._t("period_header"),
                        self._t("shift_label"),
                        self._t("area_label"),
                        self._t("att_scheduled"),
                        self._t("att_present"),
                        self._t("att_absent"),
                        self._t("rate_label"),
                    ]
                )
                for row in rows:
                    writer.writerow(row)
            messagebox.showinfo(self._t("export"), self._t("export_success"))
        except Exception as exc:
            messagebox.showerror(self._t("export_fail"), f"{exc}")

    # ================= Reports: Equipment Issues =================
    def _build_equipment_report_tab(self) -> None:
        control = ttk.Frame(self.equip_tab)
        control.pack(fill="x", padx=10, pady=5)
        ttk.Label(control, text=self._t("period_type")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.equip_mode_var = tk.StringVar(value="日")
        ttk.Combobox(control, textvariable=self.equip_mode_var, values=["日", "週", "月", "自訂"], width=8, state="readonly").grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Label(control, text=self._t("start_date")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ttk.Label(control, text=self._t("end_date")).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.equip_start_var = tk.StringVar()
        self.equip_end_var = tk.StringVar()
        ttk.Entry(control, textvariable=self.equip_start_var, width=12).grid(row=0, column=3, padx=5, pady=5)
        ttk.Entry(control, textvariable=self.equip_end_var, width=12).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(control, text=self._t("search"), command=self._load_equipment_report).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(control, text=self._t("export_csv"), command=self._export_equipment_csv).grid(row=0, column=7, padx=5, pady=5)
        ttk.Button(control, text=self._t("clear_reports"), command=lambda: self._clear_reports_view("equip")).grid(
            row=0, column=8, padx=5, pady=5
        )

        self.equip_tree_detail = ttk.Treeview(
            self.equip_tab,
            columns=("date", "area", "equip", "desc", "impact", "action"),
            show="headings",
            height=8,
        )
        equip_headers = [
            self._t("date_label"),
            self._t("area_label"),
            self._t("equip_id"),
            self._t("equip_desc"),
            self._t("equip_impact"),
            self._t("equip_action"),
        ]
        for col, text in zip(self.equip_tree_detail["columns"], equip_headers):
            self.equip_tree_detail.heading(col, text=text)
            self.equip_tree_detail.column(col, width=140)
        self.equip_tree_detail.pack(fill="both", expand=True, padx=10, pady=5)
        self.equip_tree_detail.bind(
            "<Double-1>", lambda e: self._show_detail_window(self.equip_tree_detail, self._t("report_equip"))
        )

        agg_frame = ttk.LabelFrame(self.equip_tab, text=self._t("aggregate"))
        agg_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.equip_tree_agg = ttk.Treeview(
            agg_frame,
            columns=("period", "count"),
            show="headings",
            height=6,
        )
        for col, text in zip(self.equip_tree_agg["columns"], [self._t("period_header"), self._t("count_label")]):
            self.equip_tree_agg.heading(col, text=text)
            self.equip_tree_agg.column(col, width=150)
        self.equip_tree_agg.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        ttk.Scrollbar(agg_frame, orient="vertical", command=self.equip_tree_agg.yview).pack(side="left", fill="y")
        self.equip_tree_agg.bind(
            "<Double-1>", lambda e: self._show_detail_window(self.equip_tree_agg, self._t("report_equip"))
        )

        self.equip_chart_frame = ttk.LabelFrame(self.equip_tab, text=self._t("equip_chart_title"))
        self.equip_chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def _load_equipment_report(self) -> None:
        mode = self.equip_mode_var.get()
        start_str = self.equip_start_var.get().strip()
        end_str = self.equip_end_var.get().strip()
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else None
        except ValueError:
            messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
            return
        try:
            with SessionLocal() as db:
                query = db.query(EquipmentLog, DailyReport).join(DailyReport, EquipmentLog.report_id == DailyReport.id)
                if start_date:
                    query = query.filter(DailyReport.date >= start_date)
                if end_date:
                    query = query.filter(DailyReport.date <= end_date)
                rows = query.all()
        except Exception as exc:
            messagebox.showerror("查詢失敗", f"{exc}")
            return

        detail = []
        for eq, rep in rows:
            detail.append(
                {
                    "date": rep.date,
                    "area": rep.area,
                    "equip": eq.equip_id,
                    "desc": eq.description,
                    "impact": eq.impact_qty,
                    "action": eq.action_taken,
                }
            )
        if not detail:
            self._clear_tree(self.equip_tree_detail)
            self._clear_tree(self.equip_tree_agg)
            messagebox.showinfo("提示", "查無資料")
            return

        df = pd.DataFrame(detail)
        self._clear_tree(self.equip_tree_detail)
        for _, r in df.iterrows():
            self.equip_tree_detail.insert("", "end", values=(r["date"], r["area"], r["equip"], r["desc"], r["impact"], r["action"]))

        def start_of_week(d: date) -> date:
            return d - timedelta(days=d.weekday())

        if mode == "日":
            grouped = df.groupby("date", as_index=False).size()
            grouped["period"] = grouped["date"].astype(str)
        elif mode == "週":
            df["week_start"] = df["date"].apply(start_of_week)
            grouped = df.groupby("week_start", as_index=False).size()
            grouped["period"] = grouped["week_start"].astype(str)
        elif mode == "月":
            df["month"] = df["date"].apply(lambda d: d.strftime("%Y-%m"))
            grouped = df.groupby("month", as_index=False).size()
            grouped["period"] = grouped["month"]
        else:
            grouped = df.groupby("date", as_index=False).size()
            grouped["period"] = grouped["date"].astype(str)

        self._clear_tree(self.equip_tree_agg)
        for _, r in grouped.iterrows():
            self.equip_tree_agg.insert("", "end", values=(r["period"], r["size"]))

        fig, ax = plt.subplots(figsize=(7, 3))
        ax.bar(grouped["period"], grouped["size"])
        ax.set_ylabel(self._t("count_label"))
        ax.set_xlabel(self._t("period_header"))
        ax.set_title(self._t("equip_chart_title"))
        plt.xticks(rotation=45, ha="right")
        self._embed_chart(self.equip_chart_frame, "equip_chart_canvas", fig)

    def _export_equipment_csv(self) -> None:
        rows = [self.equip_tree_detail.item(i, "values") for i in self.equip_tree_detail.get_children()]
        if not rows:
            messagebox.showinfo(self._t("export"), self._t("export_no_data"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")], title=self._t("export_equip_title")
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        self._t("date_label"),
                        self._t("area_label"),
                        self._t("equip_id"),
                        self._t("equip_desc"),
                        self._t("equip_impact"),
                        self._t("equip_action"),
                    ]
                )
                for row in rows:
                    writer.writerow(row)
            messagebox.showinfo(self._t("export"), self._t("export_success"))
        except Exception as exc:
            messagebox.showerror(self._t("export_fail"), f"{exc}")

    # ================= Reports: Abnormal LOT =================
    def _build_lot_report_tab(self) -> None:
        control = ttk.Frame(self.lot_tab)
        control.pack(fill="x", padx=10, pady=5)
        ttk.Label(control, text=self._t("period_type")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.lot_mode_var = tk.StringVar(value="日")
        ttk.Combobox(control, textvariable=self.lot_mode_var, values=["日", "週", "月", "自訂"], width=8, state="readonly").grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Label(control, text=self._t("start_date")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ttk.Label(control, text=self._t("end_date")).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.lot_start_var = tk.StringVar()
        self.lot_end_var = tk.StringVar()
        ttk.Entry(control, textvariable=self.lot_start_var, width=12).grid(row=0, column=3, padx=5, pady=5)
        ttk.Entry(control, textvariable=self.lot_end_var, width=12).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(control, text=self._t("search"), command=self._load_lot_report).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(control, text=self._t("export_csv"), command=self._export_lot_csv).grid(row=0, column=7, padx=5, pady=5)
        ttk.Button(control, text=self._t("clear_reports"), command=lambda: self._clear_reports_view("lot")).grid(
            row=0, column=8, padx=5, pady=5
        )

        self.lot_tree_detail = ttk.Treeview(
            self.lot_tab,
            columns=("date", "area", "lot", "desc", "status", "notes"),
            show="headings",
            height=8,
        )
        lot_headers = [
            self._t("date_label"),
            self._t("area_label"),
            self._t("lot_id_col"),
            self._t("lot_desc"),
            self._t("lot_status"),
            self._t("lot_notes"),
        ]
        for col, text in zip(self.lot_tree_detail["columns"], lot_headers):
            self.lot_tree_detail.heading(col, text=text)
            self.lot_tree_detail.column(col, width=140)
        self.lot_tree_detail.pack(fill="both", expand=True, padx=10, pady=5)
        self.lot_tree_detail.bind(
            "<Double-1>", lambda e: self._show_detail_window(self.lot_tree_detail, self._t("report_lot"))
        )

        agg_frame = ttk.LabelFrame(self.lot_tab, text=self._t("aggregate"))
        agg_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.lot_tree_agg = ttk.Treeview(
            agg_frame,
            columns=("period", "count"),
            show="headings",
            height=6,
        )
        for col, text in zip(self.lot_tree_agg["columns"], [self._t("period_header"), self._t("count_label")]):
            self.lot_tree_agg.heading(col, text=text)
            self.lot_tree_agg.column(col, width=150)
        self.lot_tree_agg.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        ttk.Scrollbar(agg_frame, orient="vertical", command=self.lot_tree_agg.yview).pack(side="left", fill="y")
        self.lot_tree_agg.bind(
            "<Double-1>", lambda e: self._show_detail_window(self.lot_tree_agg, self._t("report_lot"))
        )

        self.lot_chart_frame = ttk.LabelFrame(self.lot_tab, text=self._t("lot_chart_title"))
        self.lot_chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # ================= Reports: Delay List =================
    def _build_delay_tab(self) -> None:
        btn_frame = ttk.Frame(self.delay_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text=self._t("import_delay"), command=self._import_delay_excel).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=self._t("confirm_upload"), command=self._upload_delay_pending).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=self._t("refresh"), command=self._load_delay_entries).pack(side="left", padx=5)

        filter_frame = ttk.Frame(self.delay_tab)
        filter_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(filter_frame, text=self._t("start_date")).grid(row=0, column=0, padx=4, pady=4, sticky="e")
        self.delay_start_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.delay_start_var, width=12).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(filter_frame, text=self._t("end_date")).grid(row=0, column=2, padx=4, pady=4, sticky="e")
        self.delay_end_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.delay_end_var, width=12).grid(row=0, column=3, padx=4, pady=4)
        ttk.Button(filter_frame, text=self._t("search"), command=self._load_delay_entries).grid(row=0, column=4, padx=6, pady=4)
        ttk.Button(filter_frame, text=self._t("clear_reports"), command=lambda: self._clear_reports_view("delay")).grid(
            row=0, column=5, padx=6, pady=4
        )

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
        headers = [
            "ID",
            self._t("delay_date"),
            self._t("delay_time"),
            self._t("delay_reactor"),
            self._t("delay_process"),
            self._t("delay_lot"),
            self._t("delay_wafer"),
            self._t("delay_progress"),
            self._t("delay_prev_steps"),
            self._t("delay_prev_time"),
            self._t("delay_severity"),
            self._t("delay_action"),
            self._t("delay_note"),
        ]
        self.delay_tree = ttk.Treeview(self.delay_tab, columns=cols, show="headings", height=18)
        for col, header in zip(cols, headers):
            self.delay_tree.heading(col, text=header)
            width = 50 if col == "id" else 110
            stretch = False if col == "id" else True
            anchor = "center" if col != "note" and col != "action" and col != "progress" else "w"
            self.delay_tree.column(col, width=width, stretch=stretch, anchor=anchor)
        self.delay_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.delay_tree.bind("<Double-1>", lambda e: self._edit_delay_dialog())
        ttk.Scrollbar(self.delay_tab, orient="vertical", command=self.delay_tree.yview).pack(side="right", fill="y")
        self.delay_tree.configure(yscrollcommand=self.delay_tree.yview)
        self._load_delay_entries()

    def _render_delay_rows(self, rows: List[Dict[str, str]], pending: bool = False) -> None:
        self._clear_tree(self.delay_tree)
        for idx, r in enumerate(rows):
            if pending:
                row_id = f"P{idx}"
                values = (
                    row_id,
                    r["delay_date"],
                    r["time_range"],
                    r["reactor"],
                    r["process"],
                    r["lot"],
                    r["wafer"],
                    r["progress"],
                    r["prev_steps"],
                    r["prev_time"],
                    r["severity"],
                    r["action"],
                    r["note"],
                )
            else:
                row_id = r.id
                values = (
                    r.id,
                    r.delay_date,
                    r.time_range,
                    r.reactor,
                    r.process,
                    r.lot,
                    r.wafer,
                    r.progress,
                    r.prev_steps,
                    r.prev_time,
                    r.severity,
                    r.action,
                    r.note,
                )
            self.delay_tree.insert("", "end", values=values)

    def _load_delay_entries(self) -> None:
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
            messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
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
            messagebox.showerror(self._t("error"), f"{exc}")
            return
        self._render_delay_rows(rows, pending=False)

    def _import_delay_excel(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=r"Z:\\☆Junior Supervisor日報\\Delay_List",
            title=self._t("import_delay"),
            filetypes=[("Excel Files", "*.xlsx;*.xls")],
        )
        if not path:
            return
        try:
            xls = pd.ExcelFile(path)
            sheet_name = xls.sheet_names[0]
            if len(xls.sheet_names) > 1:
                picker = tk.Toplevel(self)
                picker.title(self._t("tab_delay"))
                ttk.Label(picker, text="Select sheet").pack(padx=10, pady=5)
                sheet_var = tk.StringVar(value=xls.sheet_names[0])
                combo = ttk.Combobox(picker, textvariable=sheet_var, values=xls.sheet_names, state="readonly")
                combo.pack(padx=10, pady=5)
                chosen = {"name": sheet_name}

                def confirm():
                    chosen["name"] = sheet_var.get()
                    picker.destroy()

                ttk.Button(picker, text="OK", command=confirm).pack(pady=8)
                picker.grab_set()
                picker.wait_window()
                sheet_name = chosen["name"]

            df = pd.read_excel(xls, sheet_name=sheet_name, header=1)
        except Exception as exc:
            messagebox.showerror(self._t("error"), f"{exc}")
            return

        def find_col(match: str) -> Optional[str]:
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

        records: List[Dict[str, str]] = []
        for _, row in df.iterrows():
            # Use date value from file
            raw_date = row.get(col_map["date"]) if col_map["date"] else None
            parsed_date = pd.to_datetime(raw_date, errors="coerce").date() if pd.notna(raw_date) else None
            if not parsed_date:
                continue
            def sval(key: str) -> str:
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
            messagebox.showinfo(self._t("info"), self._t("empty_data"))
            return

        self.delay_pending_records = records
        self._render_delay_rows(records, pending=True)
        messagebox.showinfo(self._t("info"), self._t("import_delay") + " OK，請確認後再點上傳")

    def _upload_delay_pending(self) -> None:
        if not self.delay_pending_records:
            messagebox.showinfo(self._t("info"), self._t("empty_data"))
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
            messagebox.showinfo(self._t("success"), self._t("submit_ok"))
        except Exception as exc:
            messagebox.showerror(self._t("error"), f"{exc}")

    # ================= Reports: Summary Actual =================
    def _build_summary_actual_tab(self) -> None:
        control = ttk.Frame(self.summary_actual_tab)
        control.pack(fill="x", padx=10, pady=5)
        ttk.Label(control, text=self._t("filter_date")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.summary_start_var = tk.StringVar()
        ttk.Entry(control, textvariable=self.summary_start_var, width=12).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(control, text=self._t("end_date")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.summary_end_var = tk.StringVar()
        ttk.Entry(control, textvariable=self.summary_end_var, width=12).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(control, text=self._t("search"), command=self._load_summary_actual).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(control, text=self._t("import_summary_actual"), command=self._import_summary_actual_excel).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(control, text=self._t("confirm_upload"), command=self._upload_summary_pending).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(control, text=self._t("clear_reports"), command=lambda: self._clear_reports_view("summary")).grid(
            row=0, column=7, padx=5, pady=5
        )

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
        headers = [
            "ID",
            self._t("delay_date"),
            self._t("summary_label"),
            self._t("summary_plan"),
            self._t("summary_completed"),
            self._t("summary_in_process"),
            self._t("summary_on_track"),
            self._t("summary_at_risk"),
            self._t("summary_delayed"),
            self._t("summary_no_data"),
            self._t("summary_scrapped"),
        ]
        self.summary_tree = ttk.Treeview(self.summary_actual_tab, columns=cols, show="headings", height=16)
        for col, header in zip(cols, headers):
            self.summary_tree.heading(col, text=header)
            width = 50 if col == "id" else 110
            stretch = False if col == "id" else True
            anchor = "center" if col not in ("label",) else "w"
            self.summary_tree.column(col, width=width, stretch=stretch, anchor=anchor)
        self.summary_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.summary_tree.bind(
            "<Double-1>", lambda e: self._edit_summary_dialog()
        )
        ttk.Scrollbar(self.summary_actual_tab, orient="vertical", command=self.summary_tree.yview).pack(side="right", fill="y")
        self.summary_tree.configure(yscrollcommand=self.summary_tree.yview)
        self._load_summary_actual()

    def _load_summary_actual(self) -> None:
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
            messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
            return

        def fmt(v: int) -> str:
            return "-" if v == 0 else str(v)

        if self.summary_pending_records:
            for idx, r in enumerate(self.summary_pending_records):
                self.summary_tree.insert(
                    "",
                    "end",
                    values=(
                        f"P{idx}",
                        r["summary_date"],
                        r["label"],
                        fmt(r["plan"]),
                        fmt(r["completed"]),
                        fmt(r["in_process"]),
                        fmt(r["on_track"]),
                        fmt(r["at_risk"]),
                        fmt(r["delayed"]),
                        fmt(r["no_data"]),
                        fmt(r["scrapped"]),
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
            messagebox.showerror(self._t("error"), f"{exc}")
            return
        for r in rows:
            self.summary_tree.insert(
                "",
                "end",
                values=(
                    r.id,
                    r.summary_date,
                    r.label,
                    fmt(r.plan),
                    fmt(r.completed),
                    fmt(r.in_process),
                    fmt(r.on_track),
                    fmt(r.at_risk),
                    fmt(r.delayed),
                    fmt(r.no_data),
                    fmt(r.scrapped),
                ),
            )

    def _import_summary_actual_excel(self) -> None:
        path = filedialog.askopenfilename(
            title=self._t("import_summary_actual"),
            filetypes=[("Excel Files", "*.xlsx;*.xls")],
        )
        if not path:
            return
        try:
            # Read entire sheet without header to get date row (row index 1)
            raw_sheet = pd.read_excel(path, sheet_name="Summary(Actual)", header=None)
        except Exception as exc:
            messagebox.showerror(self._t("error"), f"{exc}")
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
            messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
            return

        try:
            df = pd.read_excel(path, sheet_name="Summary(Actual)", header=2)
        except Exception as exc:
            messagebox.showerror(self._t("error"), f"{exc}")
            return

        # Normalize column names
        def norm(col: str) -> str:
            return str(col).strip().lower().replace(" ", "").replace("_", "")

        col_lookup = {norm(c): c for c in df.columns}

        def get_col(key: str) -> Optional[str]:
            return col_lookup.get(key, None)

        def get_val(row, key: str) -> int:
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

        records: List[Dict[str, object]] = []
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
            messagebox.showinfo(self._t("info"), self._t("empty_data"))
            return
        self.summary_pending_records = records
        self._load_summary_actual()
        messagebox.showinfo(self._t("info"), self._t("import_summary_actual") + " OK，請確認後再點上傳")

    def _upload_summary_pending(self) -> None:
        if not self.summary_pending_records:
            messagebox.showinfo(self._t("info"), self._t("empty_data"))
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
            messagebox.showinfo(self._t("success"), self._t("submit_ok"))
        except Exception as exc:
            messagebox.showerror(self._t("error"), f"{exc}")

    def _edit_delay_dialog(self) -> None:
        sel = self.delay_tree.selection()
        if not sel:
            messagebox.showinfo(self._t("info"), self._t("err_select_row"))
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
        if hasattr(self, "_delay_edit_win") and self._delay_edit_win and self._delay_edit_win.winfo_exists():
            self._delay_edit_win.destroy()
        dlg = tk.Toplevel(self)
        self._delay_edit_win = dlg
        dlg.title(self._t("tab_delay"))
        fields = [
            ("date", d_date),
            ("time", d_time),
            ("reactor", reactor),
            ("process", process),
            ("lot", lot),
            ("wafer", wafer),
            ("progress", progress),
            ("prev_steps", prev_steps),
            ("prev_time", prev_time),
            ("severity", severity),
            ("action", action),
            ("note", note),
        ]
        vars_map = {}
        for idx, (k, v) in enumerate(fields):
            ttk.Label(dlg, text=k).grid(row=idx, column=0, padx=5, pady=4, sticky="e")
            var = tk.StringVar(value=str(v))
            ttk.Entry(dlg, textvariable=var, width=30).grid(row=idx, column=1, padx=5, pady=4, sticky="w")
            vars_map[k] = var

        def save() -> None:
            try:
                if is_pending:
                    idx = int(str(row_id)[1:])
                    if idx < 0 or idx >= len(self.delay_pending_records):
                        messagebox.showerror(self._t("error"), self._t("err_select_row"))
                        return
                    try:
                        new_date = datetime.strptime(vars_map["date"].get().strip(), "%Y-%m-%d").date()
                    except Exception:
                        messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
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
                            messagebox.showerror(self._t("error"), self._t("err_select_row"))
                            return
                        try:
                            row.delay_date = datetime.strptime(vars_map["date"].get().strip(), "%Y-%m-%d").date()
                        except Exception:
                            messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
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
                messagebox.showerror(self._t("error"), f"{exc}")

        ttk.Button(dlg, text=self._t("save_update"), command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)
        dlg.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, "_delay_edit_win", None), dlg.destroy()))

    def _edit_summary_dialog(self) -> None:
        sel = self.summary_tree.selection()
        if not sel:
            messagebox.showinfo(self._t("info"), self._t("err_select_row"))
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
        if hasattr(self, "_summary_edit_win") and self._summary_edit_win and self._summary_edit_win.winfo_exists():
            self._summary_edit_win.destroy()
        dlg = tk.Toplevel(self)
        self._summary_edit_win = dlg
        dlg.title(self._t("tab_summary_actual"))

        fields = [
            ("date", d_date),
            ("label", label),
            ("plan", plan),
            ("completed", completed),
            ("in_process", in_process),
            ("on_track", on_track),
            ("at_risk", at_risk),
            ("delayed", delayed),
            ("no_data", no_data),
            ("scrapped", scrapped),
        ]
        vars_map = {}
        for idx, (k, v) in enumerate(fields):
            ttk.Label(dlg, text=k).grid(row=idx, column=0, padx=5, pady=4, sticky="e")
            var = tk.StringVar(value=str(v))
            ttk.Entry(dlg, textvariable=var, width=30).grid(row=idx, column=1, padx=5, pady=4, sticky="w")
            vars_map[k] = var

        def save() -> None:
            try:
                if is_pending:
                    idx = int(str(row_id)[1:])
                    if idx < 0 or idx >= len(self.summary_pending_records):
                        messagebox.showerror(self._t("error"), self._t("err_select_row"))
                        return
                    try:
                        new_date = datetime.strptime(vars_map["date"].get().strip(), "%Y-%m-%d").date()
                    except Exception:
                        messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
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
                            messagebox.showerror(self._t("error"), self._t("err_select_row"))
                            return
                        try:
                            row.summary_date = datetime.strptime(vars_map["date"].get().strip(), "%Y-%m-%d").date()
                        except Exception:
                            messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
                            return
                        row.label = vars_map["label"].get().strip()
                        for k_attr in [
                            ("plan", "plan"),
                            ("completed", "completed"),
                            ("in_process", "in_process"),
                            ("on_track", "on_track"),
                            ("at_risk", "at_risk"),
                            ("delayed", "delayed"),
                            ("no_data", "no_data"),
                            ("scrapped", "scrapped"),
                        ]:
                            key, attr = k_attr
                            try:
                                setattr(row, attr, int(vars_map[key].get().strip() or 0))
                            except Exception:
                                setattr(row, attr, 0)
                        db.commit()
                    self._load_summary_actual()
                dlg.destroy()
            except Exception as exc:
                messagebox.showerror(self._t("error"), f"{exc}")

        ttk.Button(dlg, text=self._t("save_update"), command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)
        dlg.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, "_summary_edit_win", None), dlg.destroy()))
    def _load_lot_report(self) -> None:
        mode = self.lot_mode_var.get()
        start_str = self.lot_start_var.get().strip()
        end_str = self.lot_end_var.get().strip()
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else None
        except ValueError:
            messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
            return
        try:
            with SessionLocal() as db:
                query = db.query(LotLog, DailyReport).join(DailyReport, LotLog.report_id == DailyReport.id)
                if start_date:
                    query = query.filter(DailyReport.date >= start_date)
                if end_date:
                    query = query.filter(DailyReport.date <= end_date)
                rows = query.all()
        except Exception as exc:
            messagebox.showerror("查詢失敗", f"{exc}")
            return

        detail = []
        for lot, rep in rows:
            detail.append(
                {
                    "date": rep.date,
                    "area": rep.area,
                    "lot": lot.lot_id,
                    "desc": lot.description,
                    "status": lot.status,
                    "notes": lot.notes,
                }
            )
        if not detail:
            self._clear_tree(self.lot_tree_detail)
            self._clear_tree(self.lot_tree_agg)
            messagebox.showinfo("提示", "查無資料")
            return

        df = pd.DataFrame(detail)
        self._clear_tree(self.lot_tree_detail)
        for _, r in df.iterrows():
            self.lot_tree_detail.insert("", "end", values=(r["date"], r["area"], r["lot"], r["desc"], r["status"], r["notes"]))

        def start_of_week(d: date) -> date:
            return d - timedelta(days=d.weekday())

        if mode == "日":
            grouped = df.groupby("date", as_index=False).size()
            grouped["period"] = grouped["date"].astype(str)
        elif mode == "週":
            df["week_start"] = df["date"].apply(start_of_week)
            grouped = df.groupby("week_start", as_index=False).size()
            grouped["period"] = grouped["week_start"].astype(str)
        elif mode == "月":
            df["month"] = df["date"].apply(lambda d: d.strftime("%Y-%m"))
            grouped = df.groupby("month", as_index=False).size()
            grouped["period"] = grouped["month"]
        else:
            grouped = df.groupby("date", as_index=False).size()
            grouped["period"] = grouped["date"].astype(str)

        self._clear_tree(self.lot_tree_agg)
        for _, r in grouped.iterrows():
            self.lot_tree_agg.insert("", "end", values=(r["period"], r["size"]))

        fig, ax = plt.subplots(figsize=(7, 3))
        ax.bar(grouped["period"], grouped["size"])
        ax.set_ylabel(self._t("count_label"))
        ax.set_xlabel(self._t("period_header"))
        ax.set_title(self._t("lot_chart_title"))
        plt.xticks(rotation=45, ha="right")
        self._embed_chart(self.lot_chart_frame, "lot_chart_canvas", fig)

    def _export_lot_csv(self) -> None:
        rows = [self.lot_tree_detail.item(i, "values") for i in self.lot_tree_detail.get_children()]
        if not rows:
            messagebox.showinfo(self._t("export"), self._t("export_no_data"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")], title=self._t("export_lot_title")
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        self._t("date_label"),
                        self._t("area_label"),
                        self._t("lot_id_col"),
                        self._t("lot_desc"),
                        self._t("lot_status"),
                        self._t("lot_notes"),
                    ]
                )
                for row in rows:
                    writer.writerow(row)
            messagebox.showinfo(self._t("export"), self._t("export_success"))
        except Exception as exc:
            messagebox.showerror(self._t("export_fail"), f"{exc}")

    # Daily tab
    def _build_daily_tab(self) -> None:
        # Scrollable container to prevent buttons being clipped on small screens
        container = ttk.Frame(self.daily_frame)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container)
        vbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        hbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        self.daily_scroll = ttk.Frame(canvas)
        self.daily_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self.daily_window_id = canvas.create_window((0, 0), window=self.daily_scroll, anchor="nw")
        self.daily_canvas = canvas
        canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        hbar.pack(side="bottom", fill="x")
        vbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        info_frame = ttk.LabelFrame(self.daily_scroll, text=self._t("base_info"))
        info_frame.pack(fill="x", padx=10, pady=5)

        self.date_var = tk.StringVar(value=str(date.today()))
        self.shift_var = tk.StringVar(value=self.shift_options[0] if self.shift_options else "")
        self.area_var = tk.StringVar(value=self.area_options[0] if self.area_options else "")

        ttk.Label(info_frame, text=self._t("date_label")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(info_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(info_frame, text=self._t("shift_label")).grid(row=0, column=2, padx=5, pady=5)
        self.shift_combo = ttk.Combobox(info_frame, textvariable=self.shift_var, values=self.shift_options, width=10, state="readonly")
        self.shift_combo.grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(info_frame, text=self._t("area_label")).grid(row=0, column=4, padx=5, pady=5)
        self.area_combo = ttk.Combobox(info_frame, textvariable=self.area_var, values=self.area_options, width=12, state="readonly")
        self.area_combo.grid(row=0, column=5, padx=5, pady=5)

        # Attendance
        att_frame = ttk.LabelFrame(self.daily_scroll, text=self._t("attendance"))
        att_frame.pack(fill="x", padx=10, pady=5)
        self.att_tree_daily = ttk.Treeview(
            att_frame,
            columns=("category", "scheduled", "present", "absent", "reason"),
            show="headings",
            height=3,
            selectmode="browse",
        )
        att_headers = [
            self._t("att_category"),
            self._t("att_scheduled"),
            self._t("att_present"),
            self._t("att_absent"),
            self._t("att_reason"),
        ]
        for col, text in zip(self.att_tree_daily["columns"], att_headers):
            self.att_tree_daily.heading(col, text=text)
            self.att_tree_daily.column(col, width=100)
        self.att_tree_daily.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        att_scroll = ttk.Scrollbar(att_frame, orient="vertical", command=self.att_tree_daily.yview)
        self.att_tree_daily.configure(yscroll=att_scroll.set)
        att_scroll.pack(side="right", fill="y")
        self.att_tree_daily.bind("<Double-1>", self._edit_attendance_row)
        self.att_tree_daily.bind("<<TreeviewSelect>>", self._on_att_select)

        # Prepopulate
        self._reset_attendance_default()

        att_btns = ttk.Frame(att_frame)
        att_btns.pack(side="right", padx=5, pady=5)
        ttk.Button(att_btns, text="編輯", command=self._edit_selected_attendance).pack(fill="x", pady=2)

        # Equipment logs
        equip_frame = ttk.LabelFrame(self.daily_scroll, text=self._t("equipment"))
        equip_frame.pack(fill="x", padx=10, pady=5)
        self.equip_tree = ttk.Treeview(
            equip_frame,
            columns=("equip_id", "description", "start_time", "impact_qty", "action_taken", "image_path"),
            show="headings",
            height=4,
        )
        equip_headers = [
            self._t("equip_id"),
            self._t("equip_desc"),
            self._t("equip_start"),
            self._t("equip_impact"),
            self._t("equip_action"),
            self._t("equip_image"),
        ]
        for col, text in zip(self.equip_tree["columns"], equip_headers):
            self.equip_tree.heading(col, text=text)
            self.equip_tree.column(col, width=120)
        self.equip_tree.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Scrollbar(equip_frame, orient="vertical", command=self.equip_tree.yview).pack(side="right", fill="y")
        ttk.Button(equip_frame, text=self._t("add"), command=self._add_equipment_dialog).pack(side="right", padx=5, pady=5)

        # Lot logs
        lot_frame = ttk.LabelFrame(self.daily_scroll, text=self._t("lot"))
        lot_frame.pack(fill="x", padx=10, pady=5)
        self.lot_tree = ttk.Treeview(
            lot_frame,
            columns=("lot_id", "description", "status", "notes"),
            show="headings",
            height=4,
        )
        lot_headers = [
            self._t("lot_id_col"),
            self._t("lot_desc"),
            self._t("lot_status"),
            self._t("lot_notes"),
        ]
        for col, text in zip(self.lot_tree["columns"], lot_headers):
            self.lot_tree.heading(col, text=text)
            self.lot_tree.column(col, width=150)
        self.lot_tree.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Scrollbar(lot_frame, orient="vertical", command=self.lot_tree.yview).pack(side="right", fill="y")
        ttk.Button(lot_frame, text=self._t("add"), command=self._add_lot_dialog).pack(side="right", padx=5, pady=5)

        # Summary
        summary_frame = ttk.LabelFrame(self.daily_scroll, text=self._t("summary"))
        summary_frame.pack(fill="x", padx=10, pady=5)
        self.summary_key = tk.Text(summary_frame, height=4)
        self.summary_issues = tk.Text(summary_frame, height=4)
        self.summary_counter = tk.Text(summary_frame, height=4)
        ttk.Label(summary_frame, text=self._t("summary_key")).grid(row=0, column=0, sticky="w")
        ttk.Label(summary_frame, text=self._t("summary_issues")).grid(row=0, column=1, sticky="w")
        ttk.Label(summary_frame, text=self._t("summary_counter")).grid(row=0, column=2, sticky="w")
        self.summary_key.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.summary_issues.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.summary_counter.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        for i in range(3):
            summary_frame.columnconfigure(i, weight=1)

        # Actions (fixed near bottom for easy access)
        action_frame = ttk.LabelFrame(self.daily_scroll, text=self._t("actions_section"))
        action_frame.pack(fill="x", padx=10, pady=10)
        buttons = [
            (self._t("load_existing"), self._load_existing_report),
            (self._t("import_excel"), self._import_placeholder),
            (self._t("clear_form"), self._clear_form),
            (self._t("confirm_upload"), self._save_report),
        ]
        for idx, (label, handler) in enumerate(buttons):
            btn = ttk.Button(action_frame, text=label, command=handler)
            btn.grid(row=0, column=idx, padx=8, pady=6, sticky="w")
        for i in range(len(buttons)):
            action_frame.columnconfigure(i, weight=1)

    def _import_placeholder(self) -> None:
        messagebox.showinfo("匯入", "匯入功能將依指定格式完成後提供。")

    def _clear_form(self) -> None:
        self.current_report_id = None
        self.date_var.set(str(date.today()))
        if self.shift_options:
            self.shift_var.set(self.shift_options[0])
        if self.area_options:
            self.area_var.set(self.area_options[0])
        self._reset_attendance_default()
        for tree in [self.equip_tree, self.lot_tree]:
            for item in tree.get_children():
                tree.delete(item)
        self.summary_key.delete("1.0", tk.END)
        self.summary_issues.delete("1.0", tk.END)
        self.summary_counter.delete("1.0", tk.END)
        self.att_selected_id = None

    def _load_existing_report(self) -> None:
        """Load report by date+shift+area if exists."""
        try:
            report_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
            return
        try:
            with SessionLocal() as db:
                report = (
                    db.query(DailyReport)
                    .filter(
                        DailyReport.date == report_date,
                        DailyReport.shift == self.shift_var.get(),
                        DailyReport.area == self.area_var.get(),
                    )
                    .first()
                )
                if not report:
                    messagebox.showinfo(self._t("success"), self._t("empty_data"))
                    self.current_report_id = None
                    return
                self.current_report_id = report.id
                # populate fields
                self._reset_attendance_default()
                for item in self.equip_tree.get_children():
                    self.equip_tree.delete(item)
                for item in self.lot_tree.get_children():
                    self.lot_tree.delete(item)
                self.summary_key.delete("1.0", tk.END)
                self.summary_issues.delete("1.0", tk.END)
                self.summary_counter.delete("1.0", tk.END)

                atts = db.query(AttendanceEntry).filter(AttendanceEntry.report_id == report.id).all()
                if atts:
                    for item in self.att_tree_daily.get_children():
                        self.att_tree_daily.delete(item)
                for a in atts:
                    self.att_tree_daily.insert("", "end", values=(a.category, a.scheduled_count, a.present_count, a.absent_count, a.reason))
                equips = db.query(EquipmentLog).filter(EquipmentLog.report_id == report.id).all()
                for e in equips:
                    self.equip_tree.insert(
                        "",
                        "end",
                        values=(e.equip_id, e.description, e.start_time, e.impact_qty, e.action_taken, e.image_path or ""),
                    )
                lots = db.query(LotLog).filter(LotLog.report_id == report.id).all()
                for l in lots:
                    self.lot_tree.insert("", "end", values=(l.lot_id, l.description, l.status, l.notes))
                self.summary_key.insert("1.0", report.summary_key_output)
                self.summary_issues.insert("1.0", report.summary_issues)
                self.summary_counter.insert("1.0", report.summary_countermeasures)
                messagebox.showinfo(self._t("success"), "已載入舊資料，可修改後存檔。")
        except Exception as exc:
            messagebox.showerror(self._t("error"), f"載入失敗：{exc}")

    def _add_equipment_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("新增設備異常")
        entries: Dict[str, tk.Entry] = {}
        labels = ["設備番号", "異常內容", "發生時刻", "影響數量", "對應內容", "圖片檔路徑"]
        keys = ["equip_id", "description", "start_time", "impact_qty", "action_taken", "image_path"]
        for i, (lbl, key) in enumerate(zip(labels, keys)):
            ttk.Label(dialog, text=lbl).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            ent = ttk.Entry(dialog, width=40)
            ent.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = ent

        def select_image() -> None:
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")])
            if path:
                entries["image_path"].delete(0, tk.END)
                entries["image_path"].insert(0, path)

        ttk.Button(dialog, text="選擇圖片", command=select_image).grid(row=5, column=2, padx=5, pady=5)

        def confirm() -> None:
            values = [entries[k].get() for k in keys]
            self.equip_tree.insert("", "end", values=values)
            dialog.destroy()

        ttk.Button(dialog, text="新增", command=confirm).grid(row=6, column=0, columnspan=3, pady=10)

    def _add_lot_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("新增異常批次")
        labels = ["批號", "異常內容", "處置狀況", "特記事項"]
        entries: List[tk.Entry] = []
        for i, lbl in enumerate(labels):
            ttk.Label(dialog, text=lbl).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            ent = ttk.Entry(dialog, width=40)
            ent.grid(row=i, column=1, padx=5, pady=5)
            entries.append(ent)

        def confirm() -> None:
            values = [e.get() for e in entries]
            self.lot_tree.insert("", "end", values=values)
            dialog.destroy()

        ttk.Button(dialog, text="新增", command=confirm).grid(row=4, column=0, columnspan=2, pady=10)

    def _collect_attendance(self) -> List[Dict[str, str]]:
        data = []
        for item in self.att_tree_daily.get_children():
            vals = self.att_tree_daily.item(item, "values")
            data.append(
                {
                    "category": vals[0],
                    "scheduled_count": vals[1],
                    "present_count": vals[2],
                    "absent_count": vals[3],
                    "reason": vals[4],
                }
            )
        return data

    def _reset_attendance_default(self) -> None:
        for item in self.att_tree_daily.get_children():
            self.att_tree_daily.delete(item)
        self.att_tree_daily.insert("", "end", values=("正社員", 0, 0, 0, ""))
        self.att_tree_daily.insert("", "end", values=("契約/派遣", 0, 0, 0, ""))
        self.att_selected_id = None
        self._log_debug("dbg_reset_att")

    def _edit_attendance_row(self, event: tk.Event) -> None:
        item_id = self.att_tree_daily.identify_row(event.y)
        if item_id:
            self.att_tree_daily.selection_set(item_id)
            self.att_selected_id = item_id
            self._log_debug("dbg_dbl_edit", id=item_id)
            self._open_attendance_editor(item_id)

    def _get_att_selected(self) -> Optional[str]:
        sel = self.att_tree_daily.selection()
        if sel:
            return sel[0]
        if self.att_selected_id:
            return self.att_selected_id
        focus = self.att_tree_daily.focus()
        if focus:
            return focus
        children = self.att_tree_daily.get_children()
        if children:
        # auto-select first row to reduce empty selection cases
            self.att_tree_daily.selection_set(children[0])
            self.att_selected_id = children[0]
            return children[0]
        return None

    def _edit_selected_attendance(self) -> None:
        item_id = self._get_att_selected()
        self._log_debug("dbg_btn_edit", id=item_id or "None")
        if not item_id:
            messagebox.showinfo(self._t("error"), self._t("err_select_row"))
            self._log_debug("dbg_no_select")
            return
        self.att_tree_daily.selection_set(item_id)
        self.att_selected_id = item_id
        self._open_attendance_editor(item_id)

    def _on_att_select(self, _: tk.Event) -> None:
        sel = self.att_tree_daily.selection()
        if sel:
            self.att_selected_id = sel[0]
            self._log_debug("dbg_select_att", id=self.att_selected_id)
    def _open_attendance_editor(self, item_id: str) -> None:
        vals = list(self.att_tree_daily.item(item_id, "values"))
        # pad to 5 columns if needed
        while len(vals) < 5:
            vals.append("")
        dialog = tk.Toplevel(self)
        dialog.title("出勤編輯")
        labels = ["分類", "定員", "出勤", "欠勤", "理由"]
        entries: List[tk.Entry] = []
        for i, (lbl, val) in enumerate(zip(labels, vals)):
            ttk.Label(dialog, text=lbl).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            ent = ttk.Entry(dialog, width=30)
            ent.insert(0, val)
            ent.grid(row=i, column=1, padx=5, pady=5)
            entries.append(ent)

        def confirm() -> None:
            new_vals = [e.get() for e in entries]
            self.att_tree_daily.item(item_id, values=new_vals)
            self._log_debug("dbg_update_att", id=item_id)
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="確定", command=confirm).pack(side="left", padx=5)

    def _collect_equipment(self) -> List[Dict[str, str]]:
        data = []
        for item in self.equip_tree.get_children():
            vals = self.equip_tree.item(item, "values")
            data.append(
                {
                    "equip_id": vals[0],
                    "description": vals[1],
                    "start_time": vals[2],
                    "impact_qty": vals[3],
                    "action_taken": vals[4],
                    "image_path": vals[5] if len(vals) > 5 else None,
                }
            )
        return data

    def _collect_lots(self) -> List[Dict[str, str]]:
        data = []
        for item in self.lot_tree.get_children():
            vals = self.lot_tree.item(item, "values")
            data.append(
                {
                    "lot_id": vals[0],
                    "description": vals[1],
                    "status": vals[2],
                    "notes": vals[3],
                }
            )
        return data

    def _save_report(self) -> None:
        try:
            report_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror(self._t("error"), self._t("date_format_invalid"))
            return

        attendance = self._collect_attendance()
        equipment = self._collect_equipment()
        lots = self._collect_lots()

        # Basic validation
        for idx, row in enumerate(attendance):
            for field in ["scheduled_count", "present_count", "absent_count"]:
                try:
                    val = int(row[field] or 0)
                    if val < 0:
                        messagebox.showerror(self._t("error"), f"出勤第 {idx+1} 列 {field} 不可為負數")
                        return
                    row[field] = val
                except ValueError:
                    messagebox.showerror(self._t("error"), f"出勤第 {idx+1} 列 {field} 需為數字")
                    return
        for idx, row in enumerate(equipment):
            try:
                val = int(row["impact_qty"] or 0)
                if val < 0:
                    messagebox.showerror(self._t("error"), f"設備異常第 {idx+1} 列影響數量不可為負數")
                    return
                row["impact_qty"] = val
            except ValueError:
                messagebox.showerror(self._t("error"), f"設備異常第 {idx+1} 列影響數量需為數字")
                return

        key_output = self.summary_key.get("1.0", tk.END).strip()
        issues = self.summary_issues.get("1.0", tk.END).strip()
        counter = self.summary_counter.get("1.0", tk.END).strip()

        try:
            with SessionLocal() as db:
                is_update = False
                if not messagebox.askyesno(self._t("confirm_upload"), self._t("confirm_upload_prompt")):
                    return
                report = None
                if self.current_report_id:
                    report = db.query(DailyReport).filter(DailyReport.id == self.current_report_id).first()
                if not report:
                    report = (
                        db.query(DailyReport)
                        .filter(
                            DailyReport.date == report_date,
                            DailyReport.shift == self.shift_var.get(),
                            DailyReport.area == self.area_var.get(),
                        )
                        .first()
                    )
                    if report and not messagebox.askyesno(self._t("duplicate_title"), self._t("duplicate_prompt")):
                        messagebox.showinfo(self._t("info"), self._t("duplicate_skip"))
                        return
                if report:
                    is_update = True
                    report.date = report_date
                    report.shift = self.shift_var.get()
                    report.area = self.area_var.get()
                    report.summary_key_output = key_output
                    report.summary_issues = issues
                    report.summary_countermeasures = counter
                    report.author_id = self.session_user["id"]
                    db.query(AttendanceEntry).filter(AttendanceEntry.report_id == report.id).delete()
                    db.query(EquipmentLog).filter(EquipmentLog.report_id == report.id).delete()
                    db.query(LotLog).filter(LotLog.report_id == report.id).delete()
                else:
                    report = DailyReport(
                        date=report_date,
                        shift=self.shift_var.get(),
                        area=self.area_var.get(),
                        author_id=self.session_user["id"],
                        summary_key_output=key_output,
                        summary_issues=issues,
                        summary_countermeasures=counter,
                    )
                    db.add(report)
                    db.flush()
                    self.current_report_id = report.id

                for row in attendance:
                    db.add(
                        AttendanceEntry(
                            report_id=report.id,
                            category=row["category"],
                            scheduled_count=row["scheduled_count"],
                            present_count=row["present_count"],
                            absent_count=row["absent_count"],
                            reason=row["reason"],
                        )
                    )
                for row in equipment:
                    db.add(
                        EquipmentLog(
                            report_id=report.id,
                            equip_id=row["equip_id"],
                            description=row["description"],
                            start_time=row["start_time"],
                            impact_qty=row["impact_qty"],
                            action_taken=row["action_taken"],
                            image_path=row["image_path"],
                        )
                    )
                for row in lots:
                    db.add(
                        LotLog(
                            report_id=report.id,
                            lot_id=row["lot_id"],
                            description=row["description"],
                            status=row["status"],
                            notes=row["notes"],
                        )
                    )

                db.commit()
                self.current_report_id = report.id
            messagebox.showinfo(self._t("success"), self._t("submit_updated") if is_update else self._t("submit_ok"))
        except Exception as exc:
            messagebox.showerror(self._t("error"), f"提交失敗：{exc}")

    # Report tab
    def _build_report_tab(self) -> None:
        self.report_notebook = ttk.Notebook(self.report_frame)
        self.report_notebook.pack(fill="both", expand=True)

        self.att_tab = ttk.Frame(self.report_notebook)
        self.equip_tab = ttk.Frame(self.report_notebook)
        self.lot_tab = ttk.Frame(self.report_notebook)
        self.delay_tab = ttk.Frame(self.report_notebook)
        self.summary_actual_tab = ttk.Frame(self.report_notebook)

        self.report_notebook.add(self.att_tab, text=self._t("report_att"))
        self.report_notebook.add(self.equip_tab, text=self._t("report_equip"))
        self.report_notebook.add(self.lot_tab, text=self._t("report_lot"))
        self.report_notebook.add(self.delay_tab, text=self._t("tab_delay"))
        self.report_notebook.add(self.summary_actual_tab, text=self._t("tab_summary_actual"))

        self._build_attendance_report_tab()
        self._build_equipment_report_tab()
        self._build_lot_report_tab()
        self._build_delay_tab()
        self._build_summary_actual_tab()

    def _load_reports(self) -> None:
        pass

    def _export_csv(self) -> None:
        pass

    # User management tab
    def _build_user_tab(self) -> None:
        frame = ttk.Frame(self.user_frame)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.user_tree = ttk.Treeview(frame, columns=("id", "username", "role"), show="headings")
        for col, text in zip(
            self.user_tree["columns"], [self._t("id_label"), self._t("login_username"), self._t("role")]
        ):
            self.user_tree.heading(col, text=text)
            self.user_tree.column(col, width=120)
        self.user_tree.pack(side="left", fill="both", expand=True)
        ttk.Scrollbar(frame, orient="vertical", command=self.user_tree.yview).pack(side="left", fill="y")
        self.user_tree.bind("<Double-1>", lambda e: self._edit_user_dialog())

        form = ttk.Frame(frame)
        form.pack(side="right", fill="y", padx=10)
        ttk.Label(form, text=self._t("login_username")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(form, text=self._t("password")).grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(form, text=self._t("role")).grid(row=2, column=0, padx=5, pady=5)
        self.new_user_var = tk.StringVar()
        self.new_pass_var = tk.StringVar()
        self.new_role_var = tk.StringVar(value="user")
        ttk.Entry(form, textvariable=self.new_user_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(form, textvariable=self.new_pass_var, show="*").grid(row=1, column=1, padx=5, pady=5)
        ttk.Combobox(form, textvariable=self.new_role_var, values=["user", "admin"], state="readonly").grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(form, text=self._t("add_user"), command=self._add_user).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(form, text=self._t("reset_pw"), command=self._reset_password).grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(form, text=self._t("delete_user"), command=self._delete_user).grid(row=5, column=0, columnspan=2, pady=5)

        self._refresh_users()

        # Option management (shift/area)
        option_frame = ttk.LabelFrame(self.user_frame, text=self._t("option_title"))
        option_frame.pack(fill="both", expand=True, padx=10, pady=10)
        shift_frame = ttk.Frame(option_frame)
        shift_frame.pack(side="left", fill="both", expand=True, padx=5)
        area_frame = ttk.Frame(option_frame)
        area_frame.pack(side="left", fill="both", expand=True, padx=5)

        # Shift
        ttk.Label(shift_frame, text=self._t("shift_list")).pack(anchor="w")
        self.shift_tree = ttk.Treeview(shift_frame, columns=("id", "name"), show="headings", height=6)
        for col, text in zip(self.shift_tree["columns"], [self._t("id_label"), self._t("shift_name")]):
            self.shift_tree.heading(col, text=text)
            self.shift_tree.column(col, width=80 if col == "id" else 150)
        self.shift_tree.pack(fill="both", expand=True)
        ttk.Scrollbar(shift_frame, orient="vertical", command=self.shift_tree.yview).pack(side="right", fill="y")
        self.shift_tree.bind("<<TreeviewSelect>>", lambda e: self._on_shift_select())
        self.shift_tree.bind("<Double-1>", lambda e: self._edit_shift_dialog())

        shift_form = ttk.Frame(shift_frame)
        shift_form.pack(fill="x", pady=5)
        ttk.Label(shift_form, text=self._t("name")).grid(row=0, column=0, padx=5, pady=2)
        self.shift_name_var = tk.StringVar()
        ttk.Entry(shift_form, textvariable=self.shift_name_var, width=18).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(shift_form, text=self._t("add"), command=self._add_shift_option).grid(row=1, column=0, padx=5, pady=2)
        ttk.Button(shift_form, text=self._t("update"), command=self._update_shift_option).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(shift_form, text=self._t("delete"), command=self._delete_shift_option).grid(row=1, column=2, padx=5, pady=2)

        # Area
        ttk.Label(area_frame, text=self._t("area_list")).pack(anchor="w")
        self.area_tree = ttk.Treeview(area_frame, columns=("id", "name"), show="headings", height=6)
        for col, text in zip(self.area_tree["columns"], [self._t("id_label"), self._t("area_name")]):
            self.area_tree.heading(col, text=text)
            self.area_tree.column(col, width=80 if col == "id" else 150)
        self.area_tree.pack(fill="both", expand=True)
        ttk.Scrollbar(area_frame, orient="vertical", command=self.area_tree.yview).pack(side="right", fill="y")
        self.area_tree.bind("<<TreeviewSelect>>", lambda e: self._on_area_select())
        self.area_tree.bind("<Double-1>", lambda e: self._edit_area_dialog())

        area_form = ttk.Frame(area_frame)
        area_form.pack(fill="x", pady=5)
        ttk.Label(area_form, text=self._t("name")).grid(row=0, column=0, padx=5, pady=2)
        self.area_name_var = tk.StringVar()
        ttk.Entry(area_form, textvariable=self.area_name_var, width=18).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(area_form, text=self._t("add"), command=self._add_area_option).grid(row=1, column=0, padx=5, pady=2)
        ttk.Button(area_form, text=self._t("update"), command=self._update_area_option).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(area_form, text=self._t("delete"), command=self._delete_area_option).grid(row=1, column=2, padx=5, pady=2)

        self._refresh_shift_options()
        self._refresh_area_options()

    def _refresh_users(self) -> None:
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        with SessionLocal() as db:
            users = db.query(User).all()
            for u in users:
                self.user_tree.insert("", "end", values=(u.id, u.username, u.role))

    def _add_user(self) -> None:
        username = self.new_user_var.get().strip()
        password = self.new_pass_var.get()
        role = self.new_role_var.get()
        if not username or not password:
            messagebox.showerror("錯誤", "帳號與密碼不可為空")
            return
        try:
            with SessionLocal() as db:
                exists = db.query(User).filter(User.username == username).first()
                if exists:
                    messagebox.showerror("錯誤", "帳號已存在")
                    return
                user = User(username=username, password_hash=hash_password(password), role=role)
                db.add(user)
                db.commit()
            self._refresh_users()
            messagebox.showinfo("成功", "已新增使用者")
        except Exception as exc:
            messagebox.showerror("錯誤", f"新增失敗：{exc}")

    def _reset_password(self) -> None:
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "請先選擇使用者")
            return
        item = self.user_tree.item(selected[0])
        user_id = item["values"][0]
        new_pw = self.new_pass_var.get()
        if not new_pw:
            messagebox.showerror("錯誤", "請輸入新密碼")
            return
        try:
            with SessionLocal() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    messagebox.showerror("錯誤", "找不到使用者")
                    return
                user.password_hash = hash_password(new_pw)
                db.commit()
            messagebox.showinfo("成功", "密碼已更新")
            self.new_pass_var.set("")
        except Exception as exc:
            messagebox.showerror("錯誤", f"更新失敗：{exc}")

    def _delete_user(self) -> None:
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "請先選擇使用者")
            return
        item = self.user_tree.item(selected[0])
        user_id = item["values"][0]
        if not messagebox.askyesno("確認", "確定要刪除該使用者？"):
            return
        try:
            with SessionLocal() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    messagebox.showerror("錯誤", "找不到使用者")
                    return
                db.delete(user)
                db.commit()
            self._refresh_users()
            messagebox.showinfo("成功", "已刪除使用者")
        except Exception as exc:
            messagebox.showerror("錯誤", f"刪除失敗：{exc}")

    def _edit_user_dialog(self) -> None:
        sel = self.user_tree.selection()
        if not sel:
            messagebox.showinfo(self._t("info"), self._t("err_select_row"))
            return
        vals = self.user_tree.item(sel[0], "values")
        if len(vals) < 3:
            return
        user_id, username, role = vals
        if hasattr(self, "_user_edit_win") and self._user_edit_win and self._user_edit_win.winfo_exists():
            self._user_edit_win.destroy()
        dlg = tk.Toplevel(self)
        self._user_edit_win = dlg
        dlg.title(self._t("dialog_edit_user"))
        ttk.Label(dlg, text=self._t("login_username")).grid(row=0, column=0, padx=6, pady=6, sticky="e")
        name_var = tk.StringVar(value=username)
        ttk.Entry(dlg, textvariable=name_var).grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(dlg, text=self._t("password")).grid(row=1, column=0, padx=6, pady=6, sticky="e")
        pw_var = tk.StringVar()
        ttk.Entry(dlg, textvariable=pw_var, show="*").grid(row=1, column=1, padx=6, pady=6)
        ttk.Label(dlg, text=self._t("role")).grid(row=2, column=0, padx=6, pady=6, sticky="e")
        role_var = tk.StringVar(value=role)
        ttk.Combobox(dlg, textvariable=role_var, values=["user", "admin"], state="readonly").grid(row=2, column=1, padx=6, pady=6)

        def save() -> None:
            new_name = name_var.get().strip()
            new_pw = pw_var.get()
            new_role = role_var.get()
            if not new_name:
                messagebox.showerror(self._t("error"), self._t("login_empty"))
                return
            try:
                with SessionLocal() as db:
                    exists = db.query(User).filter(User.username == new_name, User.id != user_id).first()
                    if exists:
                        messagebox.showerror(self._t("error"), self._t("login_wrong"))
                        return
                    user = db.query(User).filter(User.id == user_id).first()
                    if not user:
                        messagebox.showerror(self._t("error"), self._t("err_select_row"))
                        return
                    user.username = new_name
                    user.role = new_role
                    if new_pw:
                        user.password_hash = hash_password(new_pw)
                    db.commit()
                self._refresh_users()
                messagebox.showinfo(self._t("success"), self._t("submit_updated"))
                dlg.destroy()
            except Exception as exc:
                messagebox.showerror(self._t("error"), f"{exc}")

        dlg.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, "_user_edit_win", None), dlg.destroy()))
        ttk.Button(dlg, text=self._t("save_update"), command=save).grid(row=3, column=0, columnspan=2, pady=10)

    # Shift/Area option management
    def _refresh_shift_options(self) -> None:
        try:
            with SessionLocal() as db:
                options = db.query(ShiftOption).order_by(ShiftOption.id).all()
        except Exception as exc:
            messagebox.showerror("錯誤", f"讀取班別失敗：{exc}")
            return
        self.shift_options = [o.name for o in options]
        for item in self.shift_tree.get_children():
            self.shift_tree.delete(item)
        for opt in options:
            self.shift_tree.insert("", "end", values=(opt.id, opt.name))
        self.shift_name_var.set("")
        self._refresh_option_widgets()

    def _refresh_area_options(self) -> None:
        try:
            with SessionLocal() as db:
                options = db.query(AreaOption).order_by(AreaOption.id).all()
        except Exception as exc:
            messagebox.showerror("錯誤", f"讀取區域失敗：{exc}")
            return
        self.area_options = [o.name for o in options]
        for item in self.area_tree.get_children():
            self.area_tree.delete(item)
        for opt in options:
            self.area_tree.insert("", "end", values=(opt.id, opt.name))
        self.area_name_var.set("")
        self._refresh_option_widgets()

    def _edit_shift_dialog(self) -> None:
        sel = self.shift_tree.selection()
        if not sel:
            messagebox.showinfo(self._t("info"), self._t("err_select_row"))
            return
        vals = self.shift_tree.item(sel[0], "values")
        if len(vals) < 2:
            return
        opt_id, name = vals
        if hasattr(self, "_shift_edit_win") and self._shift_edit_win and self._shift_edit_win.winfo_exists():
            self._shift_edit_win.destroy()
        dlg = tk.Toplevel(self)
        self._shift_edit_win = dlg
        dlg.title(self._t("dialog_edit_shift"))
        ttk.Label(dlg, text=self._t("shift_name")).grid(row=0, column=0, padx=6, pady=6, sticky="e")
        name_var = tk.StringVar(value=name)
        ttk.Entry(dlg, textvariable=name_var).grid(row=0, column=1, padx=6, pady=6)

        def save() -> None:
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showerror(self._t("error"), self._t("name"))
                return
            try:
                with SessionLocal() as db:
                    option = db.query(ShiftOption).filter(ShiftOption.id == opt_id).first()
                    if not option:
                        messagebox.showerror(self._t("error"), self._t("err_select_row"))
                        return
                    existing = db.query(ShiftOption).filter(ShiftOption.name == new_name, ShiftOption.id != opt_id).first()
                    if existing:
                        messagebox.showerror(self._t("error"), self._t("duplicate_title"))
                        return
                    option.name = new_name
                    db.commit()
                self._refresh_shift_options()
                messagebox.showinfo(self._t("success"), self._t("submit_updated"))
                dlg.destroy()
            except Exception as exc:
                messagebox.showerror(self._t("error"), f"{exc}")

        dlg.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, "_shift_edit_win", None), dlg.destroy()))
        ttk.Button(dlg, text=self._t("save_update"), command=save).grid(row=1, column=0, columnspan=2, pady=10)

    def _edit_area_dialog(self) -> None:
        sel = self.area_tree.selection()
        if not sel:
            messagebox.showinfo(self._t("info"), self._t("err_select_row"))
            return
        vals = self.area_tree.item(sel[0], "values")
        if len(vals) < 2:
            return
        opt_id, name = vals
        if hasattr(self, "_area_edit_win") and self._area_edit_win and self._area_edit_win.winfo_exists():
            self._area_edit_win.destroy()
        dlg = tk.Toplevel(self)
        self._area_edit_win = dlg
        dlg.title(self._t("dialog_edit_area"))
        ttk.Label(dlg, text=self._t("area_name")).grid(row=0, column=0, padx=6, pady=6, sticky="e")
        name_var = tk.StringVar(value=name)
        ttk.Entry(dlg, textvariable=name_var).grid(row=0, column=1, padx=6, pady=6)

        def save() -> None:
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showerror(self._t("error"), self._t("name"))
                return
            try:
                with SessionLocal() as db:
                    option = db.query(AreaOption).filter(AreaOption.id == opt_id).first()
                    if not option:
                        messagebox.showerror(self._t("error"), self._t("err_select_row"))
                        return
                    existing = db.query(AreaOption).filter(AreaOption.name == new_name, AreaOption.id != opt_id).first()
                    if existing:
                        messagebox.showerror(self._t("error"), self._t("duplicate_title"))
                        return
                    option.name = new_name
                    db.commit()
                self._refresh_area_options()
                messagebox.showinfo(self._t("success"), self._t("submit_updated"))
                dlg.destroy()
            except Exception as exc:
                messagebox.showerror(self._t("error"), f"{exc}")

        dlg.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, "_area_edit_win", None), dlg.destroy()))
        ttk.Button(dlg, text=self._t("save_update"), command=save).grid(row=1, column=0, columnspan=2, pady=10)

    def _on_shift_select(self) -> None:
        sel = self.shift_tree.selection()
        if sel:
            vals = self.shift_tree.item(sel[0], "values")
            if len(vals) >= 2:
                self.shift_name_var.set(vals[1])

    def _on_area_select(self) -> None:
        sel = self.area_tree.selection()
        if sel:
            vals = self.area_tree.item(sel[0], "values")
            if len(vals) >= 2:
                self.area_name_var.set(vals[1])

    def _add_shift_option(self) -> None:
        name = self.shift_name_var.get().strip()
        if not name:
            messagebox.showerror("錯誤", "班別名稱不可為空")
            return
        try:
            with SessionLocal() as db:
                if db.query(ShiftOption).filter(ShiftOption.name == name).first():
                    messagebox.showerror("錯誤", "班別名稱已存在")
                    return
                db.add(ShiftOption(name=name))
                db.commit()
            self._refresh_shift_options()
            messagebox.showinfo("成功", "已新增班別")
        except Exception as exc:
            messagebox.showerror("錯誤", f"新增失敗：{exc}")

    def _update_shift_option(self) -> None:
        sel = self.shift_tree.selection()
        if not sel:
            messagebox.showinfo("提示", "請先選擇班別")
            return
        name = self.shift_name_var.get().strip()
        if not name:
            messagebox.showerror("錯誤", "班別名稱不可為空")
            return
        item_vals = self.shift_tree.item(sel[0], "values")
        opt_id = item_vals[0]
        try:
            with SessionLocal() as db:
                option = db.query(ShiftOption).filter(ShiftOption.id == opt_id).first()
                if not option:
                    messagebox.showerror("錯誤", "找不到班別")
                    return
                existing = db.query(ShiftOption).filter(ShiftOption.name == name, ShiftOption.id != opt_id).first()
                if existing:
                    messagebox.showerror("錯誤", "班別名稱已存在")
                    return
                option.name = name
                db.commit()
            self._refresh_shift_options()
            messagebox.showinfo("成功", "班別已更新")
        except Exception as exc:
            messagebox.showerror("錯誤", f"更新失敗：{exc}")

    def _delete_shift_option(self) -> None:
        sel = self.shift_tree.selection()
        if not sel:
            messagebox.showinfo("提示", "請先選擇班別")
            return
        item_vals = self.shift_tree.item(sel[0], "values")
        opt_id = item_vals[0]
        if not messagebox.askyesno("確認", "確定刪除該班別？"):
            return
        try:
            with SessionLocal() as db:
                option = db.query(ShiftOption).filter(ShiftOption.id == opt_id).first()
                if not option:
                    messagebox.showerror("錯誤", "找不到班別")
                    return
                db.delete(option)
                db.commit()
            self._refresh_shift_options()
            messagebox.showinfo("成功", "班別已刪除")
        except Exception as exc:
            messagebox.showerror("錯誤", f"刪除失敗：{exc}")

    def _add_area_option(self) -> None:
        name = self.area_name_var.get().strip()
        if not name:
            messagebox.showerror("錯誤", "區域名稱不可為空")
            return
        try:
            with SessionLocal() as db:
                if db.query(AreaOption).filter(AreaOption.name == name).first():
                    messagebox.showerror("錯誤", "區域名稱已存在")
                    return
                db.add(AreaOption(name=name))
                db.commit()
            self._refresh_area_options()
            messagebox.showinfo("成功", "已新增區域")
        except Exception as exc:
            messagebox.showerror("錯誤", f"新增失敗：{exc}")

    def _update_area_option(self) -> None:
        sel = self.area_tree.selection()
        if not sel:
            messagebox.showinfo("提示", "請先選擇區域")
            return
        name = self.area_name_var.get().strip()
        if not name:
            messagebox.showerror("錯誤", "區域名稱不可為空")
            return
        item_vals = self.area_tree.item(sel[0], "values")
        opt_id = item_vals[0]
        try:
            with SessionLocal() as db:
                option = db.query(AreaOption).filter(AreaOption.id == opt_id).first()
                if not option:
                    messagebox.showerror("錯誤", "找不到區域")
                    return
                existing = db.query(AreaOption).filter(AreaOption.name == name, AreaOption.id != opt_id).first()
                if existing:
                    messagebox.showerror("錯誤", "區域名稱已存在")
                    return
                option.name = name
                db.commit()
            self._refresh_area_options()
            messagebox.showinfo("成功", "區域已更新")
        except Exception as exc:
            messagebox.showerror("錯誤", f"更新失敗：{exc}")

    def _delete_area_option(self) -> None:
        sel = self.area_tree.selection()
        if not sel:
            messagebox.showinfo("提示", "請先選擇區域")
            return
        item_vals = self.area_tree.item(sel[0], "values")
        opt_id = item_vals[0]
        if not messagebox.askyesno("確認", "確定刪除該區域？"):
            return
        try:
            with SessionLocal() as db:
                option = db.query(AreaOption).filter(AreaOption.id == opt_id).first()
                if not option:
                    messagebox.showerror("錯誤", "找不到區域")
                    return
                db.delete(option)
                db.commit()
            self._refresh_area_options()
            messagebox.showinfo("成功", "區域已刪除")
        except Exception as exc:
            messagebox.showerror("錯誤", f"刪除失敗：{exc}")


if __name__ == "__main__":
    app = HandoverApp()
    app.mainloop()
