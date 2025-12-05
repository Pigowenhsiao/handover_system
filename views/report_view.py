from __future__ import annotations

from datetime import date
from typing import Optional

import pandas as pd
import streamlit as st
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models import DailyReport


def render_report_view(db: Session) -> None:
    st.header("歷史報表")

    today = date.today()
    start_date, end_date = st.date_input(
        "選擇日期範圍",
        value=(today.replace(day=1), today),
    )
    area = st.selectbox("區域", ["全部", "etching_D", "etching_E", "litho", "thin_film"], index=0)

    if st.button("查詢"):
        query = db.query(DailyReport)
        try:
            if start_date and end_date:
                query = query.filter(and_(DailyReport.date >= start_date, DailyReport.date <= end_date))
            if area != "全部":
                query = query.filter(DailyReport.area == area)

            reports = query.order_by(DailyReport.date.desc()).all()
        except Exception as exc:
            st.error(f"查詢失敗：{exc}")
            return

        if not reports:
            st.info("查無資料")
            return

        data = [
            {
                "日期": r.date,
                "班別": r.shift,
                "區域": r.area,
                "填寫者ID": r.author_id,
                "摘要": (r.summary_issues or "")[:50],
                "建立時間": r.created_at,
            }
            for r in reports
        ]
        df = pd.DataFrame(data)
        st.dataframe(df)

        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("匯出 CSV", data=csv_data, file_name="reports.csv", mime="text/csv")
