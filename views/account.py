from __future__ import annotations

from typing import Dict, Optional

import streamlit as st
from sqlalchemy.orm import Session

from auth import hash_password, verify_password
from models import User


def render_password_change(db: Session, user: Optional[Dict[str, str]]) -> None:
    if not user:
        st.error("請先登入。")
        return

    st.header("修改密碼")
    with st.form("change-password-form"):
        old_password = st.text_input("目前密碼", type="password")
        new_password = st.text_input("新密碼", type="password")
        confirm_password = st.text_input("確認新密碼", type="password")
        submitted = st.form_submit_button("更新密碼")

    if not submitted:
        return

    if not new_password or new_password != confirm_password:
        st.error("新密碼與確認密碼不一致。")
        return

    try:
        current_user: Optional[User] = db.query(User).filter(User.id == user["id"]).first()
        if current_user is None:
            st.error("找不到使用者資料。")
            return
        if not verify_password(old_password, current_user.password_hash):
            st.error("目前密碼不正確。")
            return

        current_user.password_hash = hash_password(new_password)
        db.commit()
        st.success("密碼已更新，請重新登入。")
    except Exception as exc:
        db.rollback()
        st.error(f"更新密碼失敗：{exc}")
