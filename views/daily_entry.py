from __future__ import annotations

import os
from datetime import date, datetime
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from models import AttendanceEntry, DailyReport, EquipmentLog, LotLog


ATTENDANCE_DEFAULT = pd.DataFrame(
    [
        {"category": "正社員", "scheduled_count": 0, "present_count": 0, "absent_count": 0, "reason": ""},
        {"category": "契約/派遣", "scheduled_count": 0, "present_count": 0, "absent_count": 0, "reason": ""},
    ]
)

EQUIPMENT_DEFAULT = pd.DataFrame(
    [
        {"equip_id": "", "description": "", "start_time": "", "impact_qty": 0, "action_taken": ""},
    ]
)

LOT_DEFAULT = pd.DataFrame(
    [
        {"lot_id": "", "description": "", "status": "", "notes": ""},
    ]
)

SHIFT_OPTIONS = ["Day", "Night"]
AREA_OPTIONS = ["etching_D", "etching_E", "litho", "thin_film"]


def save_uploaded_files(files: List, upload_dir: str = "uploads") -> List[str]:
    os.makedirs(upload_dir, exist_ok=True)
    saved_paths: List[str] = []
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    for index, file in enumerate(files):
        filename = f"{timestamp}_{index}_{file.name}"
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        saved_paths.append(file_path)

    return saved_paths


def render_daily_entry(db: Session, user: Optional[Dict[str, str]]) -> None:
    if not user:
        st.error("請先登入以填寫日報。")
        return

    st.header("日報填寫")
    with st.form("daily-entry-form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            report_date = st.date_input("日期", value=date.today())
        with col2:
            shift = st.selectbox("班別", SHIFT_OPTIONS, index=0)
        with col3:
            area = st.selectbox("區域", AREA_OPTIONS, index=0)

        st.subheader("出勤狀況")
        attendance_df = st.data_editor(
            ATTENDANCE_DEFAULT,
            num_rows="dynamic",
            use_container_width=True,
            key="attendance_editor",
            column_config={
                "category": "分類",
                "scheduled_count": "定員",
                "present_count": "出勤",
                "absent_count": "欠勤",
                "reason": "理由",
            },
        )

        st.subheader("設備異常")
        equipment_df = st.data_editor(
            EQUIPMENT_DEFAULT,
            num_rows="dynamic",
            use_container_width=True,
            key="equipment_editor",
            column_config={
                "equip_id": "設備番号",
                "description": "異常內容",
                "start_time": "發生時刻",
                "impact_qty": "影響數量",
                "action_taken": "對應內容",
            },
        )

        st.subheader("本日異常批次")
        lot_df = st.data_editor(
            LOT_DEFAULT,
            num_rows="dynamic",
            use_container_width=True,
            key="lot_editor",
            column_config={
                "lot_id": "批號",
                "description": "異常內容",
                "status": "處置狀況",
                "notes": "特記事項",
            },
        )

        st.subheader("總結")
        summary_key_output = st.text_area("Key Machine Output")
        summary_issues = st.text_area("Key Issues")
        summary_countermeasures = st.text_area("Countermeasures")

        uploaded_files = st.file_uploader("上傳照片 (可多選)", accept_multiple_files=True)

        submitted = st.form_submit_button("提交")

    if not submitted:
        return

    try:
        image_paths = save_uploaded_files(uploaded_files) if uploaded_files else []
    except Exception as exc:
        st.error(f"保存圖片失敗：{exc}")
        return

    try:
        report = DailyReport(
            date=report_date,
            shift=shift,
            area=area,
            author_id=user["id"],
            summary_key_output=summary_key_output,
            summary_issues=summary_issues,
            summary_countermeasures=summary_countermeasures,
        )
        db.add(report)
        db.flush()

        for _, row in attendance_df.fillna("").iterrows():
            db.add(
                AttendanceEntry(
                    report_id=report.id,
                    category=str(row.get("category", "")),
                    scheduled_count=int(row.get("scheduled_count", 0) or 0),
                    present_count=int(row.get("present_count", 0) or 0),
                    absent_count=int(row.get("absent_count", 0) or 0),
                    reason=str(row.get("reason", "")),
                )
            )

        for idx, row in equipment_df.fillna("").iterrows():
            image_path = image_paths[idx] if idx < len(image_paths) else None
            db.add(
                EquipmentLog(
                    report_id=report.id,
                    equip_id=str(row.get("equip_id", "")),
                    description=str(row.get("description", "")),
                    start_time=str(row.get("start_time", "")),
                    impact_qty=int(row.get("impact_qty", 0) or 0),
                    action_taken=str(row.get("action_taken", "")),
                    image_path=image_path,
                )
            )

        for _, row in lot_df.fillna("").iterrows():
            db.add(
                LotLog(
                    report_id=report.id,
                    lot_id=str(row.get("lot_id", "")),
                    description=str(row.get("description", "")),
                    status=str(row.get("status", "")),
                    notes=str(row.get("notes", "")),
                )
            )

        db.commit()
        st.success("提交成功！")
    except Exception as exc:
        db.rollback()
        st.error(f"提交失敗：{exc}")
