"""Shared CRUD helpers for admin sections."""

import tkinter as tk
from tkinter import messagebox

from models import SessionLocal


def create_treeview_select_handler(tree, name_var, active_var, update_btn, delete_btn):
    """Return a handler that syncs form values from a selected Treeview row."""

    def _handler(_event):
        selections = tree.selection()
        if not selections:
            return None
        item_id = selections[0]
        values = tree.item(item_id, "values") or []
        if values:
            if name_var is not None:
                name_var.set(values[-1])
            if active_var is not None:
                active_var.set(True)
            if update_btn is not None:
                update_btn.config(state=tk.NORMAL)
            if delete_btn is not None:
                delete_btn.config(state=tk.NORMAL)
        try:
            return int(values[0])
        except (ValueError, TypeError, IndexError):
            return None

    return _handler


def create_crud_manager(
    model_class,
    lang_manager,
    name_key,
    singular_name_key,
    load_data_callback,
    notify_callback=None,
):
    """Build CRUD handlers for simple name-based lookup tables."""

    def _notify():
        if callable(notify_callback):
            try:
                notify_callback()
            except Exception:
                pass

    def _add(name_var, add_btn, update_btn, delete_btn):
        name = (name_var.get() if name_var else "").strip()
        if not name:
            messagebox.showwarning(
                lang_manager.get_text("common.warning", "提醒"),
                lang_manager.get_text("common.enterName", "請輸入名稱"),
            )
            return
        try:
            with SessionLocal() as db:
                existing = db.query(model_class).filter_by(name=name).first()
                if existing:
                    messagebox.showwarning(
                        lang_manager.get_text("common.warning", "提醒"),
                        lang_manager.get_text(
                            "admin.optionExists", "已存在相同名稱"
                        ),
                    )
                    return
                db.add(model_class(name=name))
                db.commit()
            if name_var is not None:
                name_var.set("")
            if update_btn is not None:
                update_btn.config(state=tk.DISABLED)
            if delete_btn is not None:
                delete_btn.config(state=tk.DISABLED)
            load_data_callback()
            _notify()
        except Exception as exc:
            messagebox.showerror(
                lang_manager.get_text("common.error", "錯誤"),
                lang_manager.get_text(
                    "admin.optionCreateFailed", "新增失敗：{error}"
                ).format(error=exc),
            )

    def _update(selected_id, name_var, update_btn, delete_btn):
        if not selected_id:
            messagebox.showwarning(
                lang_manager.get_text("common.warning", "提醒"),
                lang_manager.get_text("common.selectRow", "請先選擇一列"),
            )
            return
        name = (name_var.get() if name_var else "").strip()
        if not name:
            messagebox.showwarning(
                lang_manager.get_text("common.warning", "提醒"),
                lang_manager.get_text("common.enterName", "請輸入名稱"),
            )
            return
        try:
            with SessionLocal() as db:
                row = db.query(model_class).filter_by(id=selected_id).first()
                if not row:
                    return
                row.name = name
                db.commit()
            load_data_callback()
            _notify()
        except Exception as exc:
            messagebox.showerror(
                lang_manager.get_text("common.error", "錯誤"),
                lang_manager.get_text(
                    "admin.optionUpdateFailed", "更新失敗：{error}"
                ).format(error=exc),
            )
        if update_btn is not None:
            update_btn.config(state=tk.DISABLED)
        if delete_btn is not None:
            delete_btn.config(state=tk.DISABLED)

    def _delete(selected_id, name_var, update_btn, delete_btn):
        if not selected_id:
            messagebox.showwarning(
                lang_manager.get_text("common.warning", "提醒"),
                lang_manager.get_text("common.selectRow", "請先選擇一列"),
            )
            return
        try:
            with SessionLocal() as db:
                row = db.query(model_class).filter_by(id=selected_id).first()
                if not row:
                    return
                db.delete(row)
                db.commit()
            if name_var is not None:
                name_var.set("")
            load_data_callback()
            _notify()
        except Exception as exc:
            messagebox.showerror(
                lang_manager.get_text("common.error", "錯誤"),
                lang_manager.get_text(
                    "admin.optionDeleteFailed", "刪除失敗：{error}"
                ).format(error=exc),
            )
        if update_btn is not None:
            update_btn.config(state=tk.DISABLED)
        if delete_btn is not None:
            delete_btn.config(state=tk.DISABLED)

    return {"add": _add, "update": _update, "delete": _delete}
