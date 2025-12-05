from __future__ import annotations

from typing import Dict, Optional

import streamlit as st
from sqlalchemy.orm import Session

from auth import verify_password
from models import SessionLocal, User, init_db
from views.daily_entry import render_daily_entry
from views.report_view import render_report_view
from views.user_management import render_user_management
from views.account import render_password_change
from views.report_view import render_report_view


def get_db_session() -> Session:
    return SessionLocal()


def ensure_session_state() -> None:
    st.session_state.setdefault("authentication_status", False)
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("current_page", "填寫日報")


def do_logout() -> None:
    st.session_state["authentication_status"] = False
    st.session_state["user"] = None
    st.session_state["current_page"] = "填寫日報"


def handle_login(db: Session) -> None:
    st.subheader("登入")
    with st.form("login-form"):
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")
        submitted = st.form_submit_button("登入")

    if not submitted:
        return

    try:
        user: Optional[User] = db.query(User).filter(User.username == username).first()
    except Exception as exc:
        st.error(f"登入失敗：{exc}")
        return

    if user is None or not verify_password(password, user.password_hash):
        st.error("帳號或密碼錯誤")
        return

    st.session_state["authentication_status"] = True
    st.session_state["user"] = {"id": user.id, "username": user.username, "role": user.role}
    st.success("登入成功")


def render_sidebar(user: Optional[Dict[str, str]]) -> None:
    st.sidebar.title("導航")
    if user:
        st.sidebar.write(f"使用者：{user.get('username')}（{user.get('role')}）")
        options = ["填寫日報", "歷史查詢", "修改密碼"]
        if user.get("role") == "admin":
            options.append("使用者管理")
        current = st.session_state.get("current_page", options[0])
        idx = options.index(current) if current in options else 0
        page = st.sidebar.radio("功能", options, index=idx)
        st.session_state["current_page"] = page
        st.sidebar.button("登出", on_click=do_logout)
    else:
        st.sidebar.info("請先登入")


def main() -> None:
    st.set_page_config(page_title="電子交接本系統", layout="wide")
    ensure_session_state()
    init_db()

    user = st.session_state.get("user")
    render_sidebar(user)

    if not st.session_state["authentication_status"]:
        with get_db_session() as db:
            handle_login(db)
        return

    page = st.session_state.get("current_page", "填寫日報")
    with get_db_session() as db:
        if page == "填寫日報":
            render_daily_entry(db, user)
        elif page == "歷史查詢":
            render_report_view(db)
        elif page == "使用者管理":
            if user and user.get("role") == "admin":
                render_user_management(db, user)
            else:
                st.error("只有管理員可以存取使用者管理。")
        elif page == "修改密碼":
            render_password_change(db, user)
        else:
            st.error("未知頁面")


if __name__ == "__main__":
    main()
