from __future__ import annotations

from typing import Dict, Optional

import streamlit as st
from sqlalchemy.orm import Session

from auth import hash_password
from models import User


def render_user_management(db: Session, user: Optional[Dict[str, str]]) -> None:
    if not user or user.get("role") != "admin":
        st.error("只有管理員可以管理使用者。")
        return

    st.header("使用者管理")

    st.subheader("現有使用者")
    try:
        users = db.query(User).all()
        for u in users:
            cols = st.columns([2, 1, 1, 1])
            cols[0].write(f"{u.username}（{u.role}）")
            new_role = cols[1].selectbox("角色", ["admin", "user"], index=0 if u.role == "admin" else 1, key=f"role-{u.id}")
            new_password = cols[2].text_input("新密碼（留空則不變）", type="password", key=f"pwd-{u.id}")
            update_clicked = cols[3].button("更新", key=f"update-{u.id}")
            delete_clicked = cols[3].button("刪除", key=f"delete-{u.id}")

            if update_clicked:
                try:
                    u.role = new_role
                    if new_password:
                        u.password_hash = hash_password(new_password)
                    db.commit()
                    st.success(f"已更新使用者 {u.username}")
                except Exception as exc:
                    db.rollback()
                    st.error(f"更新失敗：{exc}")
            if delete_clicked:
                try:
                    db.delete(u)
                    db.commit()
                    st.success(f"已刪除使用者 {u.username}")
                except Exception as exc:
                    db.rollback()
                    st.error(f"刪除失敗：{exc}")
    except Exception as exc:
        st.error(f"讀取使用者失敗：{exc}")

    st.divider()
    st.subheader("新增使用者")
    with st.form("add-user-form"):
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")
        role = st.selectbox("角色", ["user", "admin"])
        submitted = st.form_submit_button("新增")

    if not submitted:
        return

    if not username or not password:
        st.error("帳號與密碼不可為空。")
        return

    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            st.error("帳號已存在。")
            return
        new_user = User(username=username, password_hash=hash_password(password), role=role)
        db.add(new_user)
        db.commit()
        st.success(f"已新增使用者 {username}")
    except Exception as exc:
        db.rollback()
        st.error(f"新增失敗：{exc}")
