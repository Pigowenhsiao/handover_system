"""
系統管理員界面組件
包含使用者管理和翻譯資源管理功能
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
from auth import hash_password
from models import SessionLocal, ShiftOption, AreaOption, User
from frontend.src.utils.table_helpers import (
    attach_vertical_scrollbar,
    configure_treeview_columns,
)
from frontend.src.utils.ui_helpers import build_button_row, create_labeled_input
from frontend.src.utils.crud_helpers import (
    create_crud_manager,
    create_treeview_select_handler,
)


class UserManagementSection:
    """
    使用者管理界面組件
    提供管理員管理系統使用者的功能
    """

    def __init__(self, parent, lang_manager, current_user=None):
        """
        初始化使用者管理組件

        Args:
            parent: 父組件
            lang_manager: 語言管理器實例
        """
        self.parent = parent
        self.lang_manager = lang_manager
        self.current_user = current_user or {}
        self._admin_controls = []

        # 創建界面
        self.setup_ui()

    def setup_ui(self):
        """設置界面元素"""
        # 主框架
        self.main_frame = ttk.LabelFrame(self.parent, text="使用者管理", padding="10")

        # 輸入框架
        self.input_frame = ttk.LabelFrame(
            self.main_frame, text="新增/編輯使用者", padding="5"
        )
        self.input_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # 使用者名稱
        self.username_label, self.username_entry, self.username_var = (
            create_labeled_input(
                self.input_frame,
                0,
                "使用者名稱:",
                width=20,
                label_padx=(0, 5),
                label_pady=2,
                field_pady=2,
            )
        )

        # 電子郵件
        self.email_label, self.email_entry, self.email_var = create_labeled_input(
            self.input_frame,
            0,
            "電子郵件:",
            label_column=2,
            field_column=3,
            width=30,
            label_padx=(10, 5),
            label_pady=2,
            field_pady=2,
        )

        # 密碼
        self.password_label, self.password_entry, self.password_var = (
            create_labeled_input(
                self.input_frame,
                1,
                "密碼:",
                width=20,
                label_padx=(0, 5),
                label_pady=2,
                field_pady=2,
                widget_kwargs={"show": "*"},
            )
        )

        # 角色
        self.role_var = tk.StringVar(value="user")
        self.active_var = tk.BooleanVar(value=True)
        self.role_label, self.role_combo, _ = create_labeled_input(
            self.input_frame,
            1,
            "角色:",
            label_column=2,
            field_column=3,
            variable=self.role_var,
            widget_type="combo",
            values=sorted(["user", "admin"]),
            width=18,
            label_padx=(10, 5),
            label_pady=2,
            field_pady=2,
        )

        # 按鈕框架
        button_specs = [
            {
                "key": "create",
                "options": {"text": "新增使用者", "command": self.create_user},
                "pack": {"padx": (0, 5)},
            },
            {
                "key": "update",
                "options": {
                    "text": "更新使用者",
                    "command": self.update_user,
                    "state": tk.DISABLED,
                },
                "pack": {"padx": (0, 5)},
            },
            {
                "key": "delete",
                "options": {
                    "text": "刪除使用者",
                    "command": self.delete_user,
                    "state": tk.DISABLED,
                },
            },
            {
                "key": "reset_password",
                "options": {
                    "text": "重設密碼",
                    "command": self.reset_password,
                    "state": tk.DISABLED,
                },
                "pack": {"padx": (5, 10)},
            },
            {
                "key": "reset",
                "options": {"text": "重置", "command": self.reset_fields},
                "pack": {"padx": (10, 0)},
            },
        ]
        button_frame, buttons = build_button_row(self.input_frame, button_specs)
        button_frame.grid(row=2, column=0, columnspan=4, pady=5)

        self.create_button = buttons["create"]
        self.update_button = buttons["update"]
        self.delete_button = buttons["delete"]
        self.reset_password_btn = buttons["reset_password"]
        self.reset_button = buttons["reset"]

        self._admin_controls.append(
            ("create", self.create_button, self.create_button.pack_info())
        )
        self._admin_controls.append(
            ("delete", self.delete_button, self.delete_button.pack_info())
        )
        self._admin_controls.append(
            (
                "reset_password",
                self.reset_password_btn,
                self.reset_password_btn.pack_info(),
            )
        )

        # 使用者列表框架
        self.list_frame = ttk.LabelFrame(
            self.main_frame, text="使用者列表", padding="5"
        )
        self.list_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        # 創建表格
        columns = ("ID", "Username", "Email", "Role", "Active", "Created At")
        self.tree = ttk.Treeview(
            self.list_frame, columns=columns, show="headings", height=8
        )

        # 定義表頭
        headers = {
            "ID": "ID",
            "Username": "使用者名稱",
            "Email": "電子郵件",
            "Role": "角色",
            "Active": "啟用",
            "Created At": "創建時間",
        }

        widths = {
            "Username": 100,
            "Email": 150,
            "Role": 80,
            "__default__": 100,
        }
        configure_treeview_columns(self.tree, columns, headers, widths)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        attach_vertical_scrollbar(self.list_frame, self.tree)

        # 綁定表格選擇事件
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # 更新界面語言
        self.update_ui_language()
        self._apply_access_control()
        self.load_users()

    def set_current_user(self, current_user):
        self.current_user = current_user or {}
        if not self._ui_ready():
            return
        self._apply_access_control()

    def _is_admin(self):
        return bool(self.current_user and self.current_user.get("role") == "admin")

    def _ui_ready(self):
        if not hasattr(self, "main_frame"):
            return False
        try:
            return bool(self.main_frame.winfo_exists())
        except tk.TclError:
            return False

    def _widget_alive(self, widget):
        try:
            return widget is not None and widget.winfo_exists()
        except Exception:
            return False

    def _apply_access_control(self):
        if not self._ui_ready():
            return
        if not hasattr(self, "role_combo"):
            return
        if self._is_admin():
            for _, btn, pack_info in self._admin_controls:
                if not btn.winfo_exists():
                    continue
                if not btn.winfo_ismapped():
                    btn.pack(**pack_info)
                btn.config(state=tk.NORMAL)
            if self.role_combo.winfo_exists():
                self.role_combo.config(state="readonly")
            if self.username_entry.winfo_exists():
                self.username_entry.config(state="normal")
        else:
            if self.role_combo.winfo_exists():
                self.role_combo.set("user")
                self.role_combo.config(state=tk.DISABLED)
            if self.username_entry.winfo_exists():
                self.username_entry.config(state="readonly")
            if self.create_button.winfo_exists():
                self.create_button.config(state=tk.NORMAL)
            if self.delete_button.winfo_exists():
                self.delete_button.config(state=tk.NORMAL)
            if self.reset_password_btn.winfo_exists():
                self.reset_password_btn.config(state=tk.NORMAL)

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            with SessionLocal() as db:
                users = db.query(User).order_by(User.username).all()
            for user in users:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        user.id,
                        user.username,
                        "",
                        user.role,
                        "是",
                        "",
                    ),
                )
        except Exception as exc:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                self.lang_manager.get_text(
                    "admin.loadUsersFailed", "載入使用者資料失敗：{error}"
                ).format(error=exc),
            )

    def update_ui_language(self):
        if not self._widget_alive(getattr(self, "main_frame", None)):
            return
        """根據當前語言更新界面標示"""
        # 更新框架標題
        self.main_frame.config(
            text=self.lang_manager.get_text("admin.userManagement", "使用者管理")
        )
        self.input_frame.config(
            text=self.lang_manager.get_text("admin.addEditUser", "新增/編輯使用者")
        )
        self.list_frame.config(
            text=self.lang_manager.get_text("admin.userList", "使用者列表")
        )

        # 更新標籤文本
        self.username_label.config(
            text=f"{self.lang_manager.get_text('common.username', '使用者名稱')}:"
        )
        self.email_label.config(
            text=f"{self.lang_manager.get_text('common.email', '電子郵件')}:"
        )
        self.password_label.config(
            text=f"{self.lang_manager.get_text('common.password', '密碼')}:"
        )
        self.role_label.config(
            text=f"{self.lang_manager.get_text('common.role', '角色')}:"
        )

        # 更新按鈕文本
        self.create_button.config(
            text=self.lang_manager.get_text("common.create", "新增")
        )
        self.update_button.config(
            text=self.lang_manager.get_text("common.update", "更新")
        )
        self.delete_button.config(
            text=self.lang_manager.get_text("common.delete", "刪除")
        )
        self.reset_password_btn.config(
            text=self.lang_manager.get_text("admin.resetPassword", "重設密碼")
        )
        self.reset_button.config(
            text=self.lang_manager.get_text("common.reset", "重置")
        )

        # 更新表格標頭
        headers = {
            "ID": self.lang_manager.get_text("common.id", "ID"),
            "Username": self.lang_manager.get_text("common.username", "使用者名稱"),
            "Email": self.lang_manager.get_text("common.email", "電子郵件"),
            "Role": self.lang_manager.get_text("common.role", "角色"),
            "Active": self.lang_manager.get_text("common.active", "啟用"),
            "Created At": self.lang_manager.get_text("common.createdAt", "創建時間"),
        }

        for col in self.tree["columns"]:
            self.tree.heading(col, text=headers.get(col, col))

    def create_user(self):
        """創建新使用者"""
        if not self._is_admin():
            messagebox.showwarning(
                self.lang_manager.get_text("common.warning", "Warning"),
                self.lang_manager.get_text(
                    "admin.permissionDenied", "Permission denied"
                ),
            )
            return

        # 驗證輸入字段
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                self.lang_manager.get_text(
                    "admin.requiredFields", "使用者名稱和密碼是必填字段"
                ),
            )
            return

        try:
            with SessionLocal() as db:
                if db.query(User).filter_by(username=username).first():
                    messagebox.showwarning(
                        self.lang_manager.get_text("common.warning", "警告"),
                        self.lang_manager.get_text(
                            "admin.userExists", "使用者名稱已存在"
                        ),
                    )
                    return
                user = User(
                    username=username,
                    password_hash=hash_password(password),
                    role=self.role_var.get(),
                )
                db.add(user)
                db.commit()
            self.reset_fields()
            self.load_users()
            messagebox.showinfo(
                self.lang_manager.get_text("common.success", "成功"),
                self.lang_manager.get_text("admin.userCreated", "使用者已創建"),
            )
        except Exception as exc:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                self.lang_manager.get_text(
                    "admin.userCreateFailed", "新增使用者失敗：{error}"
                ).format(error=exc),
            )

    def update_user(self):
        """更新選定的使用者"""
        if not self._is_admin():
            selection = self.tree.selection()
            if selection:
                item_values = self.tree.item(selection[0])["values"]
                if item_values and self.current_user.get("username") != item_values[1]:
                    messagebox.showwarning(
                        self.lang_manager.get_text("common.warning", "Warning"),
                        self.lang_manager.get_text(
                            "admin.permissionDenied", "Permission denied"
                        ),
                    )
                    return

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                self.lang_manager.get_text("common.warning", "警告"),
                self.lang_manager.get_text(
                    "admin.selectUserToUpdate", "請先選擇要更新的使用者"
                ),
            )
            return

        try:
            item_id = self.tree.item(selection[0])["values"][0]
            username = self.username_var.get().strip()
            if not username:
                messagebox.showwarning(
                    self.lang_manager.get_text("common.warning", "警告"),
                    self.lang_manager.get_text(
                        "admin.requiredFields", "使用者名稱和密碼是必填字段"
                    ),
                )
                return
            role = self.role_var.get().strip() or "user"
            if not self._is_admin():
                role = "user"
            password = self.password_var.get().strip()

            with SessionLocal() as db:
                user = db.query(User).filter(User.id == item_id).first()
                if not user:
                    messagebox.showerror(
                        self.lang_manager.get_text("common.error", "錯誤"),
                        self.lang_manager.get_text(
                            "admin.userNotFound", "找不到使用者"
                        ),
                    )
                    return
                if user.username != username:
                    if (
                        db.query(User)
                        .filter(User.username == username, User.id != item_id)
                        .first()
                    ):
                        messagebox.showwarning(
                            self.lang_manager.get_text("common.warning", "警告"),
                            self.lang_manager.get_text(
                                "admin.userExists", "使用者名稱已存在"
                            ),
                        )
                        return
                user.username = username
                user.role = role
                if password:
                    user.password_hash = hash_password(password)
                db.commit()
            self.reset_fields()
            self.load_users()
            messagebox.showinfo(
                self.lang_manager.get_text("common.success", "成功"),
                self.lang_manager.get_text("admin.userUpdated", "使用者已更新"),
            )
        except Exception as e:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                f"{self.lang_manager.get_text('common.updateFailed', '更新失敗')}: {str(e)}",
            )

    def delete_user(self):
        """刪除選定的使用者"""
        if not self._is_admin():
            messagebox.showwarning(
                self.lang_manager.get_text("common.warning", "Warning"),
                self.lang_manager.get_text(
                    "admin.permissionDenied", "Permission denied"
                ),
            )
            return

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                self.lang_manager.get_text("common.warning", "警告"),
                self.lang_manager.get_text(
                    "admin.selectUserToDelete", "請先選擇要刪除的使用者"
                ),
            )
            return

        # 確認對話框
        result = messagebox.askyesno(
            self.lang_manager.get_text("common.confirm", "確認"),
            self.lang_manager.get_text(
                "admin.confirmDeleteUser", "確定要刪除此使用者嗎？"
            ),
        )

        if result:
            try:
                item_id = self.tree.item(selection[0])["values"][0]
                with SessionLocal() as db:
                    user = db.query(User).filter(User.id == item_id).first()
                    if not user:
                        messagebox.showerror(
                            self.lang_manager.get_text("common.error", "錯誤"),
                            self.lang_manager.get_text(
                                "admin.userNotFound", "找不到使用者"
                            ),
                        )
                        return
                    db.delete(user)
                    db.commit()
                self.reset_fields()
                self.load_users()
                messagebox.showinfo(
                    self.lang_manager.get_text("common.success", "成功"),
                    self.lang_manager.get_text("admin.userDeleted", "使用者已刪除"),
                )
            except Exception as exc:
                messagebox.showerror(
                    self.lang_manager.get_text("common.error", "錯誤"),
                    self.lang_manager.get_text(
                        "admin.userDeleteFailed", "刪除使用者失敗：{error}"
                    ).format(error=exc),
                )

    def on_tree_select(self, event):
        """處理表格項目選擇事件"""
        selection = self.tree.selection()
        if selection:
            item_values = self.tree.item(selection[0])["values"]

            # 將選擇的項目數據填入輸入字段
            if len(item_values) >= 4:
                self.username_var.set(item_values[1])
                self.email_var.set(item_values[2])

                # 設置角色選擇
                if item_values[3] in ["admin", "user"]:
                    self.role_var.set(item_values[3])

                # 啟用更新、刪除和重設密碼按鈕
                self.update_button.config(state=tk.NORMAL)
                # Allow clicks for non-admin to show permission message
                self.delete_button.config(state=tk.NORMAL)
                self.reset_password_btn.config(state=tk.NORMAL)
        else:
            # 禁用按鈕
            self.update_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            self.reset_password_btn.config(state=tk.DISABLED)

    def reset_password(self):
        """重設選定使用者的密碼"""
        if not self._is_admin():
            messagebox.showwarning(
                self.lang_manager.get_text("common.warning", "Warning"),
                self.lang_manager.get_text(
                    "admin.permissionDenied", "Permission denied"
                ),
            )
            return

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                self.lang_manager.get_text("common.warning", "警告"),
                self.lang_manager.get_text(
                    "admin.selectUserToResetPassword", "請先選擇要重設密碼的使用者"
                ),
            )
            return

        # 獲取選定的使用者名稱
        item_values = self.tree.item(selection[0])["values"]
        username = item_values[1]

        # 確認對話框
        result = messagebox.askyesno(
            self.lang_manager.get_text("common.confirm", "確認"),
            self.lang_manager.get_text(
                "admin.confirmResetPassword",
                f"確定要重設使用者 '{username}' 的密碼嗎？",
            ),
            icon="warning",
        )

        if result:
            try:
                new_password = tk.simpledialog.askstring(
                    self.lang_manager.get_text("admin.resetPasswordTitle", "重設密碼"),
                    self.lang_manager.get_text(
                        "admin.resetPasswordPrompt",
                        f"請輸入使用者 '{username}' 的新密碼：",
                    ),
                    show="*",
                )
                if not new_password:
                    return
                with SessionLocal() as db:
                    user = db.query(User).filter(User.username == username).first()
                    if not user:
                        messagebox.showerror(
                            self.lang_manager.get_text("common.error", "錯誤"),
                            self.lang_manager.get_text(
                                "admin.userNotFound", "找不到使用者"
                            ),
                        )
                        return
                    user.password_hash = hash_password(new_password)
                    db.commit()
                messagebox.showinfo(
                    self.lang_manager.get_text("common.success", "成功"),
                    self.lang_manager.get_text(
                        "admin.passwordResetSuccess",
                        f"使用者 '{username}' 的密碼已重設",
                    ),
                )
            except Exception as e:
                messagebox.showerror(
                    self.lang_manager.get_text("common.error", "錯誤"),
                    f"{self.lang_manager.get_text('admin.passwordResetFailed', '重設密碼失敗')}: {str(e)}",
                )

    def reset_fields(self):
        """重置輸入字段"""
        self.username_var.set("")
        self.email_var.set("")
        self.password_var.set("")
        self.role_var.set("user")
        self.active_var.set(True)

        # 禁用更新、刪除和重設密碼按鈕
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.reset_password_btn.config(state=tk.DISABLED)

    def get_widget(self):
        """獲取組件主框架"""
        return self.main_frame


class MasterDataSection:
    """
    班別/區域管理介面
    """

    def __init__(self, parent, lang_manager, on_change=None, current_user=None):
        self.parent = parent
        self.lang_manager = lang_manager
        self.current_user = current_user or {}
        self.on_change = on_change
        self.selected_shift_id = None
        self.selected_area_id = None
        self.setup_ui()
        self._init_crud_managers()
        self.load_data()

    def _init_crud_managers(self):
        """Initialize CRUD managers for shift and area."""
        self.shift_crud = create_crud_manager(
            model_class=ShiftOption,
            lang_manager=self.lang_manager,
            name_key="common.shift",
            singular_name_key="admin.shift",
            load_data_callback=self.load_data,
            notify_callback=self._notify_change,
        )

        self.area_crud = create_crud_manager(
            model_class=AreaOption,
            lang_manager=self.lang_manager,
            name_key="common.area",
            singular_name_key="admin.area",
            load_data_callback=self.load_data,
            notify_callback=self._notify_change,
        )

    def setup_ui(self):
        self.main_frame = ttk.Frame(self.parent)

        container = ttk.Frame(self.main_frame)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        # 班別管理
        self.shift_frame = ttk.LabelFrame(container, text="班別管理", padding="10")
        self.shift_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.shift_frame.columnconfigure(1, weight=1)

        self.shift_name_label = ttk.Label(self.shift_frame, text="班別名稱:")
        self.shift_name_label.grid(row=0, column=0, sticky="w", pady=2)
        self.shift_name_var = tk.StringVar()
        ttk.Entry(self.shift_frame, textvariable=self.shift_name_var, width=20).grid(
            row=0, column=1, sticky="ew", pady=2
        )

        shift_btn_frame = ttk.Frame(self.shift_frame)
        shift_btn_frame.grid(row=1, column=0, columnspan=2, pady=(6, 4))

        self.shift_add_btn = ttk.Button(
            shift_btn_frame, text="新增", command=self.add_shift
        )
        self.shift_add_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.shift_update_btn = ttk.Button(
            shift_btn_frame, text="更新", command=self.update_shift, state=tk.DISABLED
        )
        self.shift_update_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.shift_delete_btn = ttk.Button(
            shift_btn_frame, text="刪除", command=self.delete_shift, state=tk.DISABLED
        )
        self.shift_delete_btn.pack(side=tk.LEFT)

        self.shift_tree = ttk.Treeview(
            self.shift_frame, columns=("ID", "Name"), show="headings", height=8
        )
        self.shift_tree.heading("ID", text="ID")
        self.shift_tree.heading("Name", text="班別")
        self.shift_tree.column("ID", width=60, anchor="center")
        self.shift_tree.column("Name", width=160, anchor="w")
        self.shift_tree.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(6, 0))
        self.shift_tree.bind("<<TreeviewSelect>>", self.on_shift_select)

        shift_scroll = ttk.Scrollbar(
            self.shift_frame, orient=tk.VERTICAL, command=self.shift_tree.yview
        )
        self.shift_tree.configure(yscrollcommand=shift_scroll.set)
        shift_scroll.grid(row=2, column=2, sticky="ns")

        # 區域管理
        self.area_frame = ttk.LabelFrame(container, text="區域管理", padding="10")
        self.area_frame.grid(row=0, column=1, sticky="nsew")
        self.area_frame.columnconfigure(1, weight=1)

        self.area_name_label = ttk.Label(self.area_frame, text="區域名稱:")
        self.area_name_label.grid(row=0, column=0, sticky="w", pady=2)
        self.area_name_var = tk.StringVar()
        ttk.Entry(self.area_frame, textvariable=self.area_name_var, width=20).grid(
            row=0, column=1, sticky="ew", pady=2
        )

        area_btn_frame = ttk.Frame(self.area_frame)
        area_btn_frame.grid(row=1, column=0, columnspan=2, pady=(6, 4))

        self.area_add_btn = ttk.Button(
            area_btn_frame, text="新增", command=self.add_area
        )
        self.area_add_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.area_update_btn = ttk.Button(
            area_btn_frame, text="更新", command=self.update_area, state=tk.DISABLED
        )
        self.area_update_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.area_delete_btn = ttk.Button(
            area_btn_frame, text="刪除", command=self.delete_area, state=tk.DISABLED
        )
        self.area_delete_btn.pack(side=tk.LEFT)

        self.area_tree = ttk.Treeview(
            self.area_frame, columns=("ID", "Name"), show="headings", height=8
        )
        self.area_tree.heading("ID", text="ID")
        self.area_tree.heading("Name", text="區域")
        self.area_tree.column("ID", width=60, anchor="center")
        self.area_tree.column("Name", width=180, anchor="w")
        self.area_tree.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(6, 0))
        self.area_tree.bind("<<TreeviewSelect>>", self.on_area_select)

        area_scroll = ttk.Scrollbar(
            self.area_frame, orient=tk.VERTICAL, command=self.area_tree.yview
        )
        self.area_tree.configure(yscrollcommand=area_scroll.set)
        area_scroll.grid(row=2, column=2, sticky="ns")

        self.update_ui_language()
        self._apply_access_control()

    def _apply_access_control(self):
        return

    def get_widget(self):
        return self.main_frame

    def load_data(self):
        for tree in (self.shift_tree, self.area_tree):
            for item in tree.get_children():
                tree.delete(item)
        try:
            with SessionLocal() as db:
                shifts = db.query(ShiftOption).order_by(ShiftOption.name).all()
                areas = db.query(AreaOption).order_by(AreaOption.name).all()
            for shift in shifts:
                self.shift_tree.insert("", "end", values=(shift.id, shift.name))
            for area in areas:
                self.area_tree.insert("", "end", values=(area.id, area.name))
        except Exception as exc:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                self.lang_manager.get_text(
                    "admin.loadOptionsFailed", "讀取班別/區域選項失敗：{error}"
                ).format(error=exc),
            )

    def update_ui_language(self):
        self.shift_frame.config(
            text=self.lang_manager.get_text("admin.shiftManagement", "班別管理")
        )
        self.area_frame.config(
            text=self.lang_manager.get_text("admin.areaManagement", "區域管理")
        )
        self.shift_name_label.config(
            text=f"{self.lang_manager.get_text('common.shiftName', '班別名稱')}:"
        )
        self.area_name_label.config(
            text=f"{self.lang_manager.get_text('common.areaName', '區域名稱')}:"
        )
        self.shift_add_btn.config(
            text=self.lang_manager.get_text("common.create", "新增")
        )
        self.shift_update_btn.config(
            text=self.lang_manager.get_text("common.update", "更新")
        )
        self.shift_delete_btn.config(
            text=self.lang_manager.get_text("common.delete", "刪除")
        )
        self.area_add_btn.config(
            text=self.lang_manager.get_text("common.create", "新增")
        )
        self.area_update_btn.config(
            text=self.lang_manager.get_text("common.update", "更新")
        )
        self.area_delete_btn.config(
            text=self.lang_manager.get_text("common.delete", "刪除")
        )
        self.shift_tree.heading(
            "ID", text=self.lang_manager.get_text("common.id", "ID")
        )
        self.shift_tree.heading(
            "Name", text=self.lang_manager.get_text("common.shift", "班別")
        )
        self.area_tree.heading("ID", text=self.lang_manager.get_text("common.id", "ID"))
        self.area_tree.heading(
            "Name", text=self.lang_manager.get_text("common.area", "區域")
        )

    def on_shift_select(self, _event):
        """Handle shift tree selection."""
        self.selected_shift_id = create_treeview_select_handler(
            self.shift_tree,
            self.shift_name_var,
            None,
            self.shift_update_btn,
            self.shift_delete_btn,
        )(_event)

    def on_area_select(self, _event):
        """Handle area tree selection."""
        self.selected_area_id = create_treeview_select_handler(
            self.area_tree,
            self.area_name_var,
            None,
            self.area_update_btn,
            self.area_delete_btn,
        )(_event)

    def add_shift(self):
        """Add a new shift."""
        self.shift_crud["add"](
            self.shift_name_var,
            self.shift_add_btn,
            self.shift_update_btn,
            self.shift_delete_btn,
        )

    def update_shift(self):
        """Update selected shift."""
        self.shift_crud["update"](
            self.selected_shift_id,
            self.shift_name_var,
            self.shift_update_btn,
            self.shift_delete_btn,
        )

    def delete_shift(self):
        """Delete selected shift."""
        self.shift_crud["delete"](
            self.selected_shift_id,
            self.shift_name_var,
            self.shift_update_btn,
            self.shift_delete_btn,
        )

    def add_area(self):
        """Add a new area."""
        self.area_crud["add"](
            self.area_name_var,
            self.area_add_btn,
            self.area_update_btn,
            self.area_delete_btn,
        )

    def update_area(self):
        """Update selected area."""
        self.area_crud["update"](
            self.selected_area_id,
            self.area_name_var,
            self.area_update_btn,
            self.area_delete_btn,
        )

    def delete_area(self):
        """Delete selected area."""
        self.area_crud["delete"](
            self.selected_area_id,
            self.area_name_var,
            self.area_update_btn,
            self.area_delete_btn,
        )

    def _notify_change(self):
        if callable(self.on_change):
            try:
                self.on_change()
            except Exception:
                pass


class TranslationManagementSection:
    """
    翻譯資源管理界面組件
    提供管理員管理翻譯資源的功能
    """

    def __init__(self, parent, lang_manager, current_user=None):
        """
        初始化翻譯管理組件

        Args:
            parent: 父組件
            lang_manager: 語言管理器實例
        """
        self.parent = parent
        self.lang_manager = lang_manager
        self.current_user = current_user or {}
        self._admin_controls = []

        # 創建界面
        self.setup_ui()

    def setup_ui(self):
        """設置界面元素"""
        # 主框架
        self.main_frame = ttk.LabelFrame(self.parent, text="翻譯資源管理", padding="10")

        # 工具欄
        toolbar = ttk.Frame(self.main_frame)
        toolbar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 語言選擇
        self.toolbar_lang_label = ttk.Label(toolbar, text="選擇語言:")
        self.toolbar_lang_label.pack(side=tk.LEFT, padx=(0, 5))
        self.selected_language_var = tk.StringVar()
        lang_combo = ttk.Combobox(
            toolbar,
            textvariable=self.selected_language_var,
            values=sorted(["ja", "zh", "en"]),
            state="readonly",
            width=10,
        )
        lang_combo.pack(side=tk.LEFT, padx=(0, 10))

        # 命名空間
        self.toolbar_namespace_label = ttk.Label(toolbar, text="命名空間:")
        self.toolbar_namespace_label.pack(side=tk.LEFT, padx=(0, 5))
        self.namespace_var = tk.StringVar(value="common")
        namespace_entry = ttk.Entry(toolbar, textvariable=self.namespace_var, width=15)
        namespace_entry.pack(side=tk.LEFT, padx=(0, 10))

        # 匯入按鈕
        self.import_btn = ttk.Button(
            toolbar, text="匯入翻譯", command=self.import_translations
        )
        self.import_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 匯出按鈕
        self.export_btn = ttk.Button(
            toolbar, text="匯出翻譯", command=self.export_translations
        )
        self.export_btn.pack(side=tk.RIGHT)

        # 輸入框架
        self.input_frame = ttk.LabelFrame(
            self.main_frame, text="新增/編輯翻譯", padding="5"
        )
        self.input_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # 語言代碼
        self.resource_lang_label = ttk.Label(self.input_frame, text="語言代碼:")
        self.resource_lang_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.resource_lang_var = tk.StringVar(value="ja")
        lang_combo2 = ttk.Combobox(
            self.input_frame,
            textvariable=self.resource_lang_var,
            values=sorted(["ja", "zh", "en"]),
            state="readonly",
            width=10,
        )
        lang_combo2.grid(row=0, column=1, sticky=tk.W, pady=2)

        # 資源鍵
        self.resource_key_label = ttk.Label(self.input_frame, text="資源鍵:")
        self.resource_key_label.grid(row=0, column=2, sticky=tk.W, padx=(10, 5), pady=2)
        self.resource_key_var = tk.StringVar()
        key_entry = ttk.Entry(
            self.input_frame, textvariable=self.resource_key_var, width=30
        )
        key_entry.grid(row=0, column=3, sticky=tk.W, pady=2)

        # 資源值
        self.resource_value_label = ttk.Label(self.input_frame, text="資源值:")
        self.resource_value_label.grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2
        )
        self.resource_value_var = tk.StringVar()
        value_entry = ttk.Entry(
            self.input_frame, textvariable=self.resource_value_var, width=80
        )
        value_entry.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=2)

        # 命名空間
        self.resource_namespace_label = ttk.Label(self.input_frame, text="命名空間:")
        self.resource_namespace_label.grid(
            row=2, column=0, sticky=tk.W, padx=(0, 5), pady=2
        )
        self.resource_namespace_var = tk.StringVar(value="common")
        namespace_entry2 = ttk.Entry(
            self.input_frame, textvariable=self.resource_namespace_var, width=30
        )
        namespace_entry2.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=2)

        # 按鈕框架
        button_frame = ttk.Frame(self.input_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=5)

        # 新增按鈕
        self.add_resource_btn = ttk.Button(
            button_frame, text="新增翻譯", command=self.add_translation_resource
        )
        self.add_resource_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 更新按鈕
        self.update_resource_btn = ttk.Button(
            button_frame,
            text="更新翻譯",
            command=self.update_translation_resource,
            state=tk.DISABLED,
        )
        self.update_resource_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 刪除按鈕
        self.delete_resource_btn = ttk.Button(
            button_frame,
            text="刪除翻譯",
            command=self.delete_translation_resource,
            state=tk.DISABLED,
        )
        self.delete_resource_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 重置按鈕
        self.reset_resource_btn = ttk.Button(
            button_frame, text="重置", command=self.reset_resource_fields
        )
        self.reset_resource_btn.pack(side=tk.LEFT)

        # 翻譯資源表格
        self.table_frame = ttk.LabelFrame(self.main_frame, text="翻譯資源", padding="5")
        self.table_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S)
        )

        # 創建表格
        columns = ("ID", "Language", "Key", "Value", "Namespace", "Updated At")
        self.resource_tree = ttk.Treeview(
            self.table_frame, columns=columns, show="headings", height=12
        )

        # 定義表頭
        headers = {
            "ID": "ID",
            "Language": "語言",
            "Key": "資源鍵",
            "Value": "資源值",
            "Namespace": "命名空間",
            "Updated At": "更新時間",
        }

        widths = {
            "Key": 150,
            "Value": 150,
            "__default__": 80,
        }
        configure_treeview_columns(self.resource_tree, columns, headers, widths)

        self.resource_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        attach_vertical_scrollbar(self.table_frame, self.resource_tree)

        # 綁定表格選擇事件
        self.resource_tree.bind("<<TreeviewSelect>>", self.on_resource_tree_select)

        # 更新界面語言
        self.update_ui_language()
        self._apply_access_control()

    def update_ui_language(self):
        """根據當前語言更新界面標示"""
        # 更新框架標題
        self.main_frame.config(
            text=self.lang_manager.get_text(
                "admin.translationManagement", "翻譯資源管理"
            )
        )
        self.input_frame.config(
            text=self.lang_manager.get_text("admin.addEditTranslation", "新增/編輯翻譯")
        )
        self.table_frame.config(
            text=self.lang_manager.get_text("admin.translationResources", "翻譯資源")
        )
        self.toolbar_lang_label.config(
            text=f"{self.lang_manager.get_text('common.language', '語言')}:"
        )
        self.toolbar_namespace_label.config(
            text=f"{self.lang_manager.get_text('common.namespace', '命名空間')}:"
        )

        # 更新標籤文本
        self.resource_lang_label.config(
            text=f"{self.lang_manager.get_text('common.languageCode', '語言代碼')}:"
        )
        self.resource_key_label.config(
            text=f"{self.lang_manager.get_text('common.resourceKey', '資源鍵')}:"
        )
        self.resource_value_label.config(
            text=f"{self.lang_manager.get_text('common.resourceValue', '資源值')}:"
        )
        self.resource_namespace_label.config(
            text=f"{self.lang_manager.get_text('common.namespace', '命名空間')}:"
        )

        # 更新按鈕文本
        self.add_resource_btn.config(
            text=self.lang_manager.get_text("common.add", "新增")
        )
        self.update_resource_btn.config(
            text=self.lang_manager.get_text("common.update", "更新")
        )
        self.delete_resource_btn.config(
            text=self.lang_manager.get_text("common.delete", "刪除")
        )
        self.reset_resource_btn.config(
            text=self.lang_manager.get_text("common.reset", "重置")
        )
        self.import_btn.config(text=self.lang_manager.get_text("common.import", "匯入"))
        self.export_btn.config(text=self.lang_manager.get_text("common.export", "匯出"))

        # 更新表格標頭
        headers = {
            "ID": self.lang_manager.get_text("common.id", "ID"),
            "Language": self.lang_manager.get_text("common.language", "語言"),
            "Key": self.lang_manager.get_text("common.resourceKey", "資源鍵"),
            "Value": self.lang_manager.get_text("common.resourceValue", "資源值"),
            "Namespace": self.lang_manager.get_text("common.namespace", "命名空間"),
            "Updated At": self.lang_manager.get_text("common.updatedAt", "更新時間"),
        }

        for col in self.resource_tree["columns"]:
            self.resource_tree.heading(col, text=headers.get(col, col))

    def add_translation_resource(self):
        """新增翻譯資源"""
        if (
            not self.resource_key_var.get().strip()
            or not self.resource_value_var.get().strip()
        ):
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                self.lang_manager.get_text(
                    "admin.requiredFields", "資源鍵和資源值是必填字段"
                ),
            )
            return

        # 在實際應用中，這會調用後端API保存翻譯資源
        # 目前僅添加到表格中
        item_id = len(self.resource_tree.get_children()) + 1
        self.resource_tree.insert(
            "",
            "end",
            values=(
                item_id,
                self.resource_lang_var.get(),
                self.resource_key_var.get().strip(),
                self.resource_value_var.get().strip(),
                self.resource_namespace_var.get().strip(),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ),
        )

        # 重置字段
        self.reset_resource_fields()

        messagebox.showinfo(
            self.lang_manager.get_text("common.success", "成功"),
            self.lang_manager.get_text("admin.resourceAdded", "翻譯資源已新增"),
        )

    def update_translation_resource(self):
        """更新選定的翻譯資源"""
        selection = self.resource_tree.selection()
        if not selection:
            messagebox.showwarning(
                self.lang_manager.get_text("common.warning", "警告"),
                self.lang_manager.get_text(
                    "admin.selectResourceToUpdate", "請先選擇要更新的翻譯資源"
                ),
            )
            return

        # 更新表格中選定項目
        try:
            item_id = self.resource_tree.item(selection[0])["values"][0]
            self.resource_tree.item(
                selection[0],
                values=(
                    item_id,
                    self.resource_lang_var.get(),
                    self.resource_key_var.get().strip(),
                    self.resource_value_var.get().strip(),
                    self.resource_namespace_var.get().strip(),
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                ),
            )

            messagebox.showinfo(
                self.lang_manager.get_text("common.success", "成功"),
                self.lang_manager.get_text("admin.resourceUpdated", "翻譯資源已更新"),
            )
        except Exception as e:
            messagebox.showerror(
                self.lang_manager.get_text("common.error", "錯誤"),
                f"{self.lang_manager.get_text('common.updateFailed', '更新失敗')}: {str(e)}",
            )

    def delete_translation_resource(self):
        """刪除選定的翻譯資源"""
        selection = self.resource_tree.selection()
        if not selection:
            messagebox.showwarning(
                self.lang_manager.get_text("common.warning", "警告"),
                self.lang_manager.get_text(
                    "admin.selectResourceToDelete", "請先選擇要刪除的翻譯資源"
                ),
            )
            return

        # 確認對話框
        result = messagebox.askyesno(
            self.lang_manager.get_text("common.confirm", "確認"),
            self.lang_manager.get_text(
                "admin.confirmDeleteResource", "確定要刪除此翻譯資源嗎？"
            ),
        )

        if result:
            # 刪除表格項目
            self.resource_tree.delete(selection)

            # 重置字段
            self.reset_resource_fields()

            messagebox.showinfo(
                self.lang_manager.get_text("common.success", "成功"),
                self.lang_manager.get_text("admin.resourceDeleted", "翻譯資源已刪除"),
            )

    def import_translations(self):
        """匯入翻譯資源"""
        file_path = filedialog.askopenfilename(
            title=self.lang_manager.get_text("admin.selectJsonFile", "選擇 JSON 文件"),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 在實際應用中，這會將數據發送到後端API
                # 目前僅模擬數據加載
                self.load_translation_data_from_json(data)

                messagebox.showinfo(
                    self.lang_manager.get_text("common.success", "成功"),
                    self.lang_manager.get_text(
                        "admin.resourcesImported", "翻譯資源已匯入"
                    ),
                )
            except Exception as e:
                messagebox.showerror(
                    self.lang_manager.get_text("common.error", "錯誤"),
                    f"{self.lang_manager.get_text('admin.importFailed', '匯入失敗')}: {str(e)}",
                )

    def export_translations(self):
        """匯出翻譯資源"""
        file_path = filedialog.asksaveasfilename(
            title=self.lang_manager.get_text("admin.saveJsonFile", "保存 JSON 文件"),
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if file_path:
            try:
                # 從表格獲取所有翻譯資源
                resources = []
                for item in self.resource_tree.get_children():
                    values = self.resource_tree.item(item)["values"]
                    resources.append(
                        {
                            "id": values[0],
                            "language_code": values[1],
                            "resource_key": values[2],
                            "resource_value": values[3],
                            "namespace": values[4],
                            "updated_at": values[5],
                        }
                    )

                # 寫入文件
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(resources, f, ensure_ascii=False, indent=2)

                messagebox.showinfo(
                    self.lang_manager.get_text("common.success", "成功"),
                    self.lang_manager.get_text(
                        "admin.resourcesExported", "翻譯資源已匯出"
                    ),
                )
            except Exception as e:
                messagebox.showerror(
                    self.lang_manager.get_text("common.error", "錯誤"),
                    f"{self.lang_manager.get_text('admin.exportFailed', '匯出失敗')}: {str(e)}",
                )

    def load_translation_data_from_json(self, data):
        """從JSON數據加載翻譯資源到表格"""
        # 清空現有資源
        for item in self.resource_tree.get_children():
            self.resource_tree.delete(item)

        # 添加新翻譯資源
        item_id = 1
        for resource in data:
            if isinstance(resource, dict) and all(
                k in resource
                for k in ["language_code", "resource_key", "resource_value"]
            ):
                self.resource_tree.insert(
                    "",
                    "end",
                    values=(
                        item_id,
                        resource["language_code"],
                        resource["resource_key"],
                        resource["resource_value"],
                        resource.get("namespace", "common"),
                        resource.get(
                            "updated_at", datetime.now().strftime("%Y-%m-%d %H:%M")
                        ),
                    ),
                )
                item_id += 1

    def on_resource_tree_select(self, event):
        """處理翻譯資源表格選擇事件"""
        selection = self.resource_tree.selection()
        if selection:
            item_values = self.resource_tree.item(selection[0])["values"]

            # 將選擇的項目數據填入輸入字段
            if len(item_values) >= 5:
                self.resource_lang_var.set(item_values[1])
                self.resource_key_var.set(item_values[2])
                self.resource_value_var.set(item_values[3])
                self.resource_namespace_var.set(item_values[4])

                # 啟用更新和刪除按鈕
                self.update_resource_btn.config(state=tk.NORMAL)
                self.delete_resource_btn.config(state=tk.NORMAL)
        else:
            # 禁用按鈕
            self.update_resource_btn.config(state=tk.DISABLED)
            self.delete_resource_btn.config(state=tk.DISABLED)

    def reset_resource_fields(self):
        """重置翻譯資源輸入字段"""
        self.resource_lang_var.set("ja")
        self.resource_key_var.set("")
        self.resource_value_var.set("")
        self.resource_namespace_var.set("common")

        # 禁用更新和刪除按鈕
        self.update_resource_btn.config(state=tk.DISABLED)
        self.delete_resource_btn.config(state=tk.DISABLED)

    def get_widget(self):
        """獲取組件主框架"""
        return self.main_frame
