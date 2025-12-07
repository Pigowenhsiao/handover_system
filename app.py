from __future__ import annotations

import csv
import os
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from auth import verify_password, hash_password
from models import (
    AttendanceEntry,
    DailyReport,
    EquipmentLog,
    LotLog,
    SessionLocal,
    ShiftOption,
    AreaOption,
    User,
    init_db,
)

# 版本資訊
VERSION = "v0.3.2-桌面多語"

# 語言資源
LANGS = {"ja": "日本語", "en": "English", "zh": "繁體中文"}
TEXTS: Dict[str, Dict[str, str]] = {
    "title": {"ja": "電子引き継ぎシステム（デスクトップ版）", "en": "Handover System (Desktop)", "zh": "電子交接本系統（桌面版）"},
    "login_title": {"ja": "電子引き継ぎシステム", "en": "Handover System", "zh": "電子交接本系統"},
    "login_username": {"ja": "ユーザー名", "en": "Username", "zh": "帳號"},
    "login_password": {"ja": "パスワード", "en": "Password", "zh": "密碼"},
    "login_button": {"ja": "ログイン", "en": "Login", "zh": "登入"},
    "login_fail": {"ja": "ログイン失敗", "en": "Login Failed", "zh": "登入失敗"},
    "login_empty": {"ja": "ユーザー名とパスワードを入力してください。", "en": "Username and password cannot be empty.", "zh": "帳號與密碼不可為空。"},
    "login_wrong": {"ja": "ユーザー名またはパスワードが正しくありません。", "en": "Invalid username or password.", "zh": "帳號或密碼錯誤。"},
    "db_error": {"ja": "データベースエラー：", "en": "Database error: ", "zh": "資料庫錯誤："},
    "logout": {"ja": "ログアウト", "en": "Logout", "zh": "登出"},
    "tab_daily": {"ja": "日報入力", "en": "Daily Entry", "zh": "填寫日報"},
    "tab_report": {"ja": "レポート", "en": "Reports", "zh": "報表"},
    "tab_user": {"ja": "ユーザー管理", "en": "User Management", "zh": "使用者管理"},
    "base_info": {"ja": "基本情報", "en": "Basic Info", "zh": "基礎資訊"},
    "date_label": {"ja": "日付 YYYY-MM-DD", "en": "Date YYYY-MM-DD", "zh": "日期 YYYY-MM-DD"},
    "shift_label": {"ja": "シフト", "en": "Shift", "zh": "班別"},
    "area_label": {"ja": "エリア", "en": "Area", "zh": "區域"},
    "attendance": {"ja": "出勤状況", "en": "Attendance", "zh": "出勤狀況"},
    "att_category": {"ja": "区分", "en": "Category", "zh": "分類"},
    "att_scheduled": {"ja": "定員", "en": "Scheduled", "zh": "定員"},
    "att_present": {"ja": "出勤", "en": "Present", "zh": "出勤"},
    "att_absent": {"ja": "欠勤", "en": "Absent", "zh": "欠勤"},
    "att_reason": {"ja": "理由", "en": "Reason", "zh": "理由"},
    "equipment": {"ja": "設備異常", "en": "Equipment Issues", "zh": "設備異常"},
    "equip_id": {"ja": "設備番号", "en": "Equipment ID", "zh": "設備番号"},
    "equip_desc": {"ja": "異常内容", "en": "Description", "zh": "異常內容"},
    "equip_start": {"ja": "発生時刻", "en": "Start Time", "zh": "發生時刻"},
    "equip_impact": {"ja": "影響数量", "en": "Impact Qty", "zh": "影響數量"},
    "equip_action": {"ja": "対応内容", "en": "Action Taken", "zh": "對應內容"},
    "equip_image": {"ja": "画像パス", "en": "Image Path", "zh": "圖片路徑"},
    "lot": {"ja": "異常ロット", "en": "Abnormal LOT", "zh": "本日異常批次"},
    "lot_id_col": {"ja": "ロット", "en": "Lot ID", "zh": "批號"},
    "lot_desc": {"ja": "異常内容", "en": "Description", "zh": "異常內容"},
    "lot_status": {"ja": "処置状況", "en": "Status", "zh": "處置狀況"},
    "lot_notes": {"ja": "特記事項", "en": "Notes", "zh": "特記事項"},
    "summary": {"ja": "サマリー", "en": "Summary", "zh": "總結"},
    "import_excel": {"ja": "Excel 取り込み（準備中）", "en": "Import Excel (coming soon)", "zh": "匯入 Excel（即將提供）"},
    "submit": {"ja": "送信", "en": "Submit", "zh": "提交"},
    "save_update": {"ja": "保存/更新", "en": "Save / Update", "zh": "存檔/更新"},
    "confirm_upload": {"ja": "確認アップロード", "en": "Confirm Upload", "zh": "確認上傳"},
    "clear_form": {"ja": "クリア", "en": "Clear", "zh": "清空"},
    "load_existing": {"ja": "既存読み込み", "en": "Load Existing", "zh": "載入既有資料"},
    "add": {"ja": "追加", "en": "Add", "zh": "新增"},
    "success": {"ja": "成功", "en": "Success", "zh": "成功"},
    "submit_ok": {"ja": "送信しました。", "en": "Submitted successfully.", "zh": "提交成功！"},
    "submit_updated": {"ja": "更新しました。", "en": "Updated successfully.", "zh": "更新成功！"},
    "error": {"ja": "エラー", "en": "Error", "zh": "錯誤"},
    "empty_data": {"ja": "データがありません", "en": "No data found", "zh": "查無資料"},
    "report_att": {"ja": "人員出勤レポート", "en": "Attendance Report", "zh": "人員出勤報表"},
    "report_equip": {"ja": "設備異常レポート", "en": "Equipment Report", "zh": "設備異常報表"},
    "report_lot": {"ja": "異常LOTレポート", "en": "LOT Report", "zh": "異常 LOT 報表"},
    "period_type": {"ja": "期間タイプ", "en": "Period Type", "zh": "期間類型"},
    "period_header": {"ja": "期間", "en": "Period", "zh": "期間"},
    "count_label": {"ja": "件数", "en": "Count", "zh": "筆數"},
    "rate_label": {"ja": "出勤率(%)", "en": "Attendance Rate (%)", "zh": "出勤率(%)"},
    "debug_label": {"ja": "デバッグ", "en": "DEBUG", "zh": "DEBUG"},
    "dbg_reset_att": {"ja": "出勤行をリセット", "en": "Reset attendance rows", "zh": "重置出勤列"},
    "dbg_select_att": {"ja": "選択出勤: {id}", "en": "Selected attendance: {id}", "zh": "選取出勤列: {id}"},
    "dbg_btn_edit": {"ja": "ボタン編集: {id}", "en": "Edit via button: {id}", "zh": "按鈕編輯: {id}"},
    "dbg_dbl_edit": {"ja": "ダブルクリック編集: {id}", "en": "Edit via double click: {id}", "zh": "雙擊編輯: {id}"},
    "dbg_update_att": {"ja": "更新: {id}", "en": "Updated: {id}", "zh": "更新出勤: {id}"},
    "dbg_no_select": {"ja": "編集対象が未選択", "en": "No row selected", "zh": "未選取任何列"},
    "err_select_row": {"ja": "編集する行を選択してください。", "en": "Please select a row to edit.", "zh": "請先選擇要編輯的列。"},
    "start_date": {"ja": "開始日 YYYY-MM-DD", "en": "Start Date YYYY-MM-DD", "zh": "起始日 YYYY-MM-DD"},
    "end_date": {"ja": "終了日 YYYY-MM-DD", "en": "End Date YYYY-MM-DD", "zh": "結束日 YYYY-MM-DD"},
    "search": {"ja": "検索", "en": "Search", "zh": "查詢"},
    "export_csv": {"ja": "CSV出力", "en": "Export CSV", "zh": "匯出 CSV"},
    "confirm_delete": {"ja": "削除してもよろしいですか？", "en": "Are you sure to delete?", "zh": "確定要刪除？"},
    "user": {"ja": "ユーザー", "en": "User", "zh": "使用者"},
    "role": {"ja": "権限", "en": "Role", "zh": "角色"},
    "password": {"ja": "パスワード", "en": "Password", "zh": "密碼"},
    "add_user": {"ja": "ユーザー追加", "en": "Add User", "zh": "新增使用者"},
    "reset_pw": {"ja": "パスワード初期化", "en": "Reset Password", "zh": "重設密碼"},
    "delete_user": {"ja": "ユーザー削除", "en": "Delete User", "zh": "刪除使用者"},
    "option_title": {"ja": "シフト・エリア管理", "en": "Shift & Area Management", "zh": "班別與區域管理"},
    "shift_list": {"ja": "シフト一覧", "en": "Shift List", "zh": "班別列表"},
    "area_list": {"ja": "エリア一覧", "en": "Area List", "zh": "區域列表"},
    "name": {"ja": "名称", "en": "Name", "zh": "名稱"},
    "update": {"ja": "更新", "en": "Update", "zh": "修改"},
    "delete": {"ja": "削除", "en": "Delete", "zh": "刪除"},
    "lang_label": {"ja": "言語", "en": "Language", "zh": "語言"},
    "actions_section": {"ja": "操作", "en": "Actions", "zh": "操作"},
    "summary_key": {"ja": "主要設備アウトプット", "en": "Key Machine Output", "zh": "主要設備產出"},
    "summary_issues": {"ja": "主要問題", "en": "Key Issues", "zh": "主要問題"},
    "summary_counter": {"ja": "対策", "en": "Countermeasures", "zh": "對策"},
}

class HandoverApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.lang: str = "ja"
        self.title(f"{self._t('title')} {VERSION}")
        self.geometry("1100x720")
        self.resizable(True, True)
        self.session_user: Optional[Dict[str, str]] = None
        self.shift_options: List[str] = []
        self.area_options: List[str] = []
        self.current_report_id: Optional[int] = None
        self.att_selected_id: Optional[str] = None
        self.debug_var = tk.StringVar(value="")  # 用於畫面上顯示偵錯資訊
        init_db()
        self._load_options()
        self._build_login()

    def _t(self, key: str) -> str:
        return TEXTS.get(key, {}).get(self.lang, TEXTS.get(key, {}).get("zh", key))

    def _build_login(self) -> None:
        self.login_frame = ttk.Frame(self)
        self.login_frame.pack(expand=True)

        self.lang_var = tk.StringVar(value=self.lang)
        lang_frame = ttk.Frame(self.login_frame)
        lang_frame.grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Label(lang_frame, text=self._t("lang_label")).pack(side="left", padx=5)
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=list(LANGS.keys()), state="readonly", width=8)
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
        ttk.Label(top_bar, text=f"版本：{VERSION}").pack(side="left", padx=10, pady=5)
        ttk.Label(top_bar, text=f"{self._t('user')}：{self.session_user['username']}（{self.session_user['role']}）").pack(side="left", padx=10, pady=5)
        ttk.Button(top_bar, text=self._t("logout"), command=self._logout).pack(side="right", padx=10)
        lang_frame = ttk.Frame(top_bar)
        lang_frame.pack(side="right", padx=10)
        ttk.Label(lang_frame, text=self._t("lang_label")).pack(side="left", padx=5)
        self.lang_var = tk.StringVar(value=self.lang)
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=list(LANGS.keys()), state="readonly", width=8)
        lang_combo.pack(side="left")
        lang_combo.bind("<<ComboboxSelected>>", self._switch_language)

        # Debug 信息顯示
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

    def _logout(self) -> None:
        self.session_user = None
        for widget in self.winfo_children():
            widget.destroy()
        self._build_login()

    def _clear_tree(self, tree: ttk.Treeview) -> None:
        for item in tree.get_children():
            tree.delete(item)

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
        self.lang = self.lang_var.get()
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

    # ================= 報表：出勤 =================
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

        self.att_report_tree = ttk.Treeview(
            self.att_tab,
            columns=("period", "scheduled", "present", "absent", "rate"),
            show="headings",
            height=12,
        )
        att_headers = [
            self._t("period_header"),
            self._t("att_scheduled"),
            self._t("att_present"),
            self._t("att_absent"),
            self._t("rate_label"),
        ]
        for col, text in zip(self.att_report_tree["columns"], att_headers):
            self.att_report_tree.heading(col, text=text)
            self.att_report_tree.column(col, width=140)
        self.att_report_tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.att_chart_frame = ttk.LabelFrame(self.att_tab, text="出勤率趨勢")
        self.att_chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def _load_attendance_report(self) -> None:
        mode = self.att_mode_var.get()
        start_str = self.att_start_var.get().strip()
        end_str = self.att_end_var.get().strip()
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else None
        except ValueError:
            messagebox.showerror(self._t("error"), "日期格式應為 YYYY-MM-DD")
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
                    "date": rep.date,
                    "scheduled": att.scheduled_count,
                    "present": att.present_count,
                    "absent": att.absent_count,
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
            grouped = df.groupby("date", as_index=False).sum()
            grouped["period"] = grouped["date"].astype(str)
        elif mode == "週":
            df["week_start"] = df["date"].apply(start_of_week)
            grouped = df.groupby("week_start", as_index=False).sum()
            grouped["period"] = grouped["week_start"].astype(str)
        elif mode == "月":
            df["month"] = df["date"].apply(lambda d: d.strftime("%Y-%m"))
            grouped = df.groupby("month", as_index=False).sum()
            grouped["period"] = grouped["month"]
        else:  # 自訂
            grouped = df.groupby("date", as_index=False).sum()
            grouped["period"] = grouped["date"].astype(str)

        grouped["rate"] = grouped.apply(lambda r: "" if r["scheduled"] == 0 else round(r["present"] * 100 / r["scheduled"], 1), axis=1)

        self._clear_tree(self.att_report_tree)
        for _, r in grouped.iterrows():
            self.att_report_tree.insert("", "end", values=(r["period"], r["scheduled"], r["present"], r["absent"], r["rate"]))

        # Chart
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.plot(grouped["period"], [r if r != "" else 0 for r in grouped["rate"]], marker="o")
        ax.set_ylabel("出勤率(%)")
        ax.set_xlabel("期間")
        ax.set_title("出勤率趨勢")
        ax.grid(True, linestyle="--", alpha=0.4)
        plt.xticks(rotation=45, ha="right")
        self._embed_chart(self.att_chart_frame, "att_chart_canvas", fig)

    def _export_attendance_csv(self) -> None:
        rows = [self.att_report_tree.item(i, "values") for i in self.att_report_tree.get_children()]
        if not rows:
            messagebox.showinfo(self._t("success"), "沒有資料可匯出")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="匯出出勤報表")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["期間", "應出勤", "實際出勤", "缺勤", "出勤率(%)"])
                for row in rows:
                    writer.writerow(row)
            messagebox.showinfo("匯出", "匯出成功")
        except Exception as exc:
            messagebox.showerror("匯出失敗", f"{exc}")

    # ================= 報表：設備異常 =================
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

        agg_frame = ttk.LabelFrame(self.equip_tab, text="彙總")
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

        self.equip_chart_frame = ttk.LabelFrame(self.equip_tab, text="設備異常趨勢")
        self.equip_chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def _load_equipment_report(self) -> None:
        mode = self.equip_mode_var.get()
        start_str = self.equip_start_var.get().strip()
        end_str = self.equip_end_var.get().strip()
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else None
        except ValueError:
            messagebox.showerror("錯誤", "日期格式應為 YYYY-MM-DD")
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
        ax.set_ylabel("筆數")
        ax.set_xlabel("期間")
        ax.set_title("設備異常趨勢")
        plt.xticks(rotation=45, ha="right")
        self._embed_chart(self.equip_chart_frame, "equip_chart_canvas", fig)

    def _export_equipment_csv(self) -> None:
        rows = [self.equip_tree_detail.item(i, "values") for i in self.equip_tree_detail.get_children()]
        if not rows:
            messagebox.showinfo("匯出", "沒有資料可匯出")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="匯出設備異常報表")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["日期", "區域", "設備", "異常內容", "影響數量", "對應內容"])
                for row in rows:
                    writer.writerow(row)
            messagebox.showinfo("匯出", "匯出成功")
        except Exception as exc:
            messagebox.showerror("匯出失敗", f"{exc}")

    # ================= 報表：異常 LOT =================
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

        agg_frame = ttk.LabelFrame(self.lot_tab, text="彙總")
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

        self.lot_chart_frame = ttk.LabelFrame(self.lot_tab, text="異常 LOT 趨勢")
        self.lot_chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def _load_lot_report(self) -> None:
        mode = self.lot_mode_var.get()
        start_str = self.lot_start_var.get().strip()
        end_str = self.lot_end_var.get().strip()
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else None
        except ValueError:
            messagebox.showerror("錯誤", "日期格式應為 YYYY-MM-DD")
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
        ax.set_ylabel("筆數")
        ax.set_xlabel("期間")
        ax.set_title("異常 LOT 趨勢")
        plt.xticks(rotation=45, ha="right")
        self._embed_chart(self.lot_chart_frame, "lot_chart_canvas", fig)

    def _export_lot_csv(self) -> None:
        rows = [self.lot_tree_detail.item(i, "values") for i in self.lot_tree_detail.get_children()]
        if not rows:
            messagebox.showinfo("匯出", "沒有資料可匯出")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="匯出異常 LOT 報表")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["日期", "區域", "批號", "異常內容", "處置狀況", "特記事項"])
                for row in rows:
                    writer.writerow(row)
            messagebox.showinfo("匯出", "匯出成功")
        except Exception as exc:
            messagebox.showerror("匯出失敗", f"{exc}")

    # Daily tab
    def _build_daily_tab(self) -> None:
        # 可捲動容器，避免小螢幕時按鈕被擠出畫面
        container = ttk.Frame(self.daily_frame)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container)
        vbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.daily_scroll = ttk.Frame(canvas)
        self.daily_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.daily_scroll, anchor="nw")
        canvas.configure(yscrollcommand=vbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")

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

        # Actions (固定在畫面底部，便於找到)
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
            messagebox.showerror(self._t("error"), "日期格式需為 YYYY-MM-DD")
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
            # auto-select first row to reduce空選擇狀況
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

        ttk.Button(dialog, text="確定", command=confirm).grid(row=5, column=0, columnspan=2, pady=10)

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
            messagebox.showerror(self._t("error"), "日期格式需為 YYYY-MM-DD")
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
                if not messagebox.askyesno(self._t("confirm_upload"), "是否確認上傳全部欄位（含總結）？"):
                    return
                if self.current_report_id:
                    report = db.query(DailyReport).filter(DailyReport.id == self.current_report_id).first()
                else:
                    report = (
                        db.query(DailyReport)
                        .filter(
                            DailyReport.date == report_date,
                            DailyReport.shift == self.shift_var.get(),
                            DailyReport.area == self.area_var.get(),
                        )
                        .first()
                    )
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

        self.report_notebook.add(self.att_tab, text=self._t("report_att"))
        self.report_notebook.add(self.equip_tab, text=self._t("report_equip"))
        self.report_notebook.add(self.lot_tab, text=self._t("report_lot"))

        self._build_attendance_report_tab()
        self._build_equipment_report_tab()
        self._build_lot_report_tab()

    def _load_reports(self) -> None:
        pass

    def _export_csv(self) -> None:
        pass

    # User management tab
    def _build_user_tab(self) -> None:
        frame = ttk.Frame(self.user_frame)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.user_tree = ttk.Treeview(frame, columns=("id", "username", "role"), show="headings")
        for col, text in zip(self.user_tree["columns"], ["ID", "帳號", "角色"]):
            self.user_tree.heading(col, text=text)
            self.user_tree.column(col, width=120)
        self.user_tree.pack(side="left", fill="both", expand=True)
        ttk.Scrollbar(frame, orient="vertical", command=self.user_tree.yview).pack(side="left", fill="y")

        form = ttk.Frame(frame)
        form.pack(side="right", fill="y", padx=10)
        ttk.Label(form, text="帳號").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(form, text="密碼").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(form, text="角色").grid(row=2, column=0, padx=5, pady=5)
        self.new_user_var = tk.StringVar()
        self.new_pass_var = tk.StringVar()
        self.new_role_var = tk.StringVar(value="user")
        ttk.Entry(form, textvariable=self.new_user_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(form, textvariable=self.new_pass_var, show="*").grid(row=1, column=1, padx=5, pady=5)
        ttk.Combobox(form, textvariable=self.new_role_var, values=["user", "admin"], state="readonly").grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(form, text="新增使用者", command=self._add_user).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(form, text="重設密碼", command=self._reset_password).grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(form, text="刪除使用者", command=self._delete_user).grid(row=5, column=0, columnspan=2, pady=5)

        self._refresh_users()

        # Option management (shift/area)
        option_frame = ttk.LabelFrame(self.user_frame, text="班別與區域管理")
        option_frame.pack(fill="both", expand=True, padx=10, pady=10)
        shift_frame = ttk.Frame(option_frame)
        shift_frame.pack(side="left", fill="both", expand=True, padx=5)
        area_frame = ttk.Frame(option_frame)
        area_frame.pack(side="left", fill="both", expand=True, padx=5)

        # Shift
        ttk.Label(shift_frame, text="班別列表").pack(anchor="w")
        self.shift_tree = ttk.Treeview(shift_frame, columns=("id", "name"), show="headings", height=6)
        for col, text in zip(self.shift_tree["columns"], ["ID", "班別名稱"]):
            self.shift_tree.heading(col, text=text)
            self.shift_tree.column(col, width=80 if col == "id" else 150)
        self.shift_tree.pack(fill="both", expand=True)
        ttk.Scrollbar(shift_frame, orient="vertical", command=self.shift_tree.yview).pack(side="right", fill="y")
        self.shift_tree.bind("<<TreeviewSelect>>", lambda e: self._on_shift_select())

        shift_form = ttk.Frame(shift_frame)
        shift_form.pack(fill="x", pady=5)
        ttk.Label(shift_form, text="名稱").grid(row=0, column=0, padx=5, pady=2)
        self.shift_name_var = tk.StringVar()
        ttk.Entry(shift_form, textvariable=self.shift_name_var, width=18).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(shift_form, text="新增", command=self._add_shift_option).grid(row=1, column=0, padx=5, pady=2)
        ttk.Button(shift_form, text="修改", command=self._update_shift_option).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(shift_form, text="刪除", command=self._delete_shift_option).grid(row=1, column=2, padx=5, pady=2)

        # Area
        ttk.Label(area_frame, text="區域列表").pack(anchor="w")
        self.area_tree = ttk.Treeview(area_frame, columns=("id", "name"), show="headings", height=6)
        for col, text in zip(self.area_tree["columns"], ["ID", "區域名稱"]):
            self.area_tree.heading(col, text=text)
            self.area_tree.column(col, width=80 if col == "id" else 150)
        self.area_tree.pack(fill="both", expand=True)
        ttk.Scrollbar(area_frame, orient="vertical", command=self.area_tree.yview).pack(side="right", fill="y")
        self.area_tree.bind("<<TreeviewSelect>>", lambda e: self._on_area_select())

        area_form = ttk.Frame(area_frame)
        area_form.pack(fill="x", pady=5)
        ttk.Label(area_form, text="名稱").grid(row=0, column=0, padx=5, pady=2)
        self.area_name_var = tk.StringVar()
        ttk.Entry(area_form, textvariable=self.area_name_var, width=18).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(area_form, text="新增", command=self._add_area_option).grid(row=1, column=0, padx=5, pady=2)
        ttk.Button(area_form, text="修改", command=self._update_area_option).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(area_form, text="刪除", command=self._delete_area_option).grid(row=1, column=2, padx=5, pady=2)

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
