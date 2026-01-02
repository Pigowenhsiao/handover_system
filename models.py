from __future__ import annotations

from datetime import datetime, date
from pathlib import Path
import json
import sys
import shutil
import sqlite3
import time
from typing import Dict, Generator, Optional

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Float, ForeignKey, create_engine, event
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

def _get_app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _get_data_dir() -> Path:
    data_dir = _get_app_root() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


_DATABASE_FALLBACK_NOTICE: Optional[Dict[str, str]] = None


def _set_database_fallback_notice(custom_path: Path, default_path: Path) -> None:
    global _DATABASE_FALLBACK_NOTICE
    if _DATABASE_FALLBACK_NOTICE is not None:
        return
    _DATABASE_FALLBACK_NOTICE = {
        "custom_path": str(custom_path),
        "default_path": str(default_path),
    }


def consume_database_fallback_notice() -> Optional[Dict[str, str]]:
    global _DATABASE_FALLBACK_NOTICE
    notice = _DATABASE_FALLBACK_NOTICE
    _DATABASE_FALLBACK_NOTICE = None
    return notice


def get_database_path() -> Path:
    db_path = _get_data_dir() / "handover_system.db"
    settings_path = _get_app_root() / "handover_settings.json"
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            custom_path = data.get("database_path")
            if custom_path:
                custom = Path(custom_path)
                if not custom.is_absolute():
                    custom = (_get_app_root() / custom).resolve()
                if custom.is_file():
                    db_path = custom
                else:
                    _set_database_fallback_notice(custom, db_path)
        except Exception:
            pass
    _maybe_migrate_database(db_path)
    return db_path


def _maybe_migrate_database(target_path: Path) -> None:
    if target_path.exists():
        return

    legacy_paths = [_get_app_root() / "handover_system.db"]
    legacy_base = getattr(sys, "_MEIPASS", None)
    if legacy_base:
        legacy_paths.append(Path(legacy_base) / "handover_system.db")

    for legacy_path in legacy_paths:
        if not legacy_path.exists():
            continue
        try:
            shutil.move(str(legacy_path), str(target_path))
        except Exception:
            try:
                shutil.copy2(str(legacy_path), str(target_path))
            except Exception:
                pass
        break


DATABASE_PATH = get_database_path()
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

SQLITE_BUSY_TIMEOUT_MS = 5000
SQLITE_BUSY_RETRY_COUNT = 3
SQLITE_BUSY_RETRY_BACKOFF_SEC = 0.25

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": SQLITE_BUSY_TIMEOUT_MS / 1000},
    future=True,
)


def _is_sqlite_busy_error(error: Exception) -> bool:
    message = str(error).lower()
    if "database is locked" in message or "database is busy" in message:
        return True
    if isinstance(error, OperationalError):
        orig = getattr(error, "orig", None)
        if orig:
            orig_message = str(orig).lower()
            return "database is locked" in orig_message or "database is busy" in orig_message
    return False


class RetryingSession(Session):
    def commit(self) -> None:
        for attempt in range(SQLITE_BUSY_RETRY_COUNT + 1):
            try:
                super().commit()
                return
            except OperationalError as exc:
                if _is_sqlite_busy_error(exc) and attempt < SQLITE_BUSY_RETRY_COUNT:
                    self.rollback()
                    time.sleep(SQLITE_BUSY_RETRY_BACKOFF_SEC * (attempt + 1))
                    continue
                raise
            except sqlite3.OperationalError as exc:
                if _is_sqlite_busy_error(exc) and attempt < SQLITE_BUSY_RETRY_COUNT:
                    self.rollback()
                    time.sleep(SQLITE_BUSY_RETRY_BACKOFF_SEC * (attempt + 1))
                    continue
                raise


@event.listens_for(engine, "connect")
def _configure_sqlite(connection, _):
    if not isinstance(connection, sqlite3.Connection):
        return
    cursor = connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
    finally:
        cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
    class_=RetryingSession,
)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(50), unique=True, nullable=False, index=True)
    password_hash: str = Column(String(128), nullable=False)
    role: str = Column(String(20), nullable=False, default="user")

    reports = relationship("DailyReport", back_populates="author")


class ShiftOption(Base):
    __tablename__ = "shift_options"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(50), unique=True, nullable=False)


class AreaOption(Base):
    __tablename__ = "area_options"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(50), unique=True, nullable=False)


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id: int = Column(Integer, primary_key=True, index=True)
    date: date = Column(Date, nullable=False)
    shift: str = Column(String(20), nullable=False)
    area: str = Column(String(50), nullable=False)
    author_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified_by: Optional[str] = Column(String(100), nullable=True)
    last_modified_at: Optional[datetime] = Column(DateTime, nullable=True)
    is_hidden: int = Column(Integer, default=0, nullable=False)
    summary_key_output: str = Column(Text, default="", nullable=False)
    summary_issues: str = Column(Text, default="", nullable=False)
    summary_countermeasures: str = Column(Text, default="", nullable=False)

    author = relationship("User", back_populates="reports")
    attendance_entries = relationship("AttendanceEntry", back_populates="report", cascade="all, delete-orphan")
    overtime_entry = relationship(
        "OvertimeEntry",
        back_populates="report",
        cascade="all, delete-orphan",
        uselist=False,
    )
    equipment_logs = relationship("EquipmentLog", back_populates="report", cascade="all, delete-orphan")
    lot_logs = relationship("LotLog", back_populates="report", cascade="all, delete-orphan")


class AttendanceEntry(Base):
    __tablename__ = "attendance_entries"

    id: int = Column(Integer, primary_key=True, index=True)
    report_id: int = Column(Integer, ForeignKey("daily_reports.id"), nullable=False)
    category: str = Column(String(20), nullable=False)  # Regular / Contract
    scheduled_count: int = Column(Integer, default=0, nullable=False)
    present_count: int = Column(Integer, default=0, nullable=False)
    absent_count: int = Column(Integer, default=0, nullable=False)
    reason: str = Column(Text, default="", nullable=False)

    report = relationship("DailyReport", back_populates="attendance_entries")


class OvertimeEntry(Base):
    __tablename__ = "overtime_entries"

    id: int = Column(Integer, primary_key=True, index=True)
    report_id: int = Column(Integer, ForeignKey("daily_reports.id"), nullable=False)
    category: str = Column(String(20), default="", nullable=False)
    count: int = Column(Integer, default=0, nullable=False)
    notes: str = Column(Text, default="", nullable=False)

    report = relationship("DailyReport", back_populates="overtime_entry")


class EquipmentLog(Base):
    __tablename__ = "equipment_logs"

    id: int = Column(Integer, primary_key=True, index=True)
    report_id: int = Column(Integer, ForeignKey("daily_reports.id"), nullable=False)
    equip_id: str = Column(String(50), nullable=False)
    description: str = Column(Text, default="", nullable=False)
    start_time: str = Column(String(50), default="", nullable=False)
    impact_qty: int = Column(Integer, default=0, nullable=False)
    impact_hours: float = Column(Float, default=0.0, nullable=False)
    action_taken: str = Column(Text, default="", nullable=False)
    image_path: Optional[str] = Column(String(255), nullable=True)

    report = relationship("DailyReport", back_populates="equipment_logs")


class LotLog(Base):
    __tablename__ = "lot_logs"

    id: int = Column(Integer, primary_key=True, index=True)
    report_id: int = Column(Integer, ForeignKey("daily_reports.id"), nullable=False)
    lot_id: str = Column(String(50), default="", nullable=False)
    description: str = Column(Text, default="", nullable=False)
    status: str = Column(Text, default="", nullable=False)
    notes: str = Column(Text, default="", nullable=False)

    report = relationship("DailyReport", back_populates="lot_logs")


class DelayEntry(Base):
    __tablename__ = "delay_entries"

    id: int = Column(Integer, primary_key=True, index=True)
    delay_date: date = Column(Date, nullable=False)
    time_range: str = Column(String(50), default="", nullable=False)
    reactor: str = Column(String(50), default="", nullable=False)
    process: str = Column(String(100), default="", nullable=False)
    lot: str = Column(String(50), default="", nullable=False)
    wafer: str = Column(String(50), default="", nullable=False)
    progress: str = Column(String(100), default="", nullable=False)
    prev_steps: str = Column(String(100), default="", nullable=False)
    prev_time: str = Column(String(50), default="", nullable=False)
    severity: str = Column(String(50), default="", nullable=False)
    action: str = Column(Text, default="", nullable=False)
    note: str = Column(Text, default="", nullable=False)
    imported_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


class SummaryActualEntry(Base):
    __tablename__ = "summary_actual_entries"

    id: int = Column(Integer, primary_key=True, index=True)
    summary_date: date = Column(Date, nullable=False)
    label: str = Column(String(200), default="", nullable=False)
    plan: int = Column(Integer, default=0, nullable=False)
    completed: int = Column(Integer, default=0, nullable=False)
    in_process: int = Column(Integer, default=0, nullable=False)
    on_track: int = Column(Integer, default=0, nullable=False)
    at_risk: int = Column(Integer, default=0, nullable=False)
    delayed: int = Column(Integer, default=0, nullable=False)
    no_data: int = Column(Integer, default=0, nullable=False)
    scrapped: int = Column(Integer, default=0, nullable=False)
    imported_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

class AttendanceSummaryDeleteLog(Base):
    __tablename__ = "attendance_summary_delete_logs"

    id: int = Column(Integer, primary_key=True, index=True)
    report_id: int = Column(Integer, nullable=False)
    deleted_by: str = Column(String(100), default="", nullable=False)
    deleted_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    snapshot_json: str = Column(Text, default="", nullable=False)



def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(default_admin_username: str = "admin", default_admin_password: str = "admin123") -> None:
    """Initialize database tables and ensure default admin exists."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        print(f"資料庫初始化失敗: {exc}")
        return
    _ensure_daily_report_columns()
    _ensure_equipment_log_columns()

    from auth import hash_password  # local import to avoid circular dependency

    try:
        with SessionLocal() as session:
            admin = session.query(User).filter_by(username=default_admin_username).first()
            if admin is None:
                admin = User(
                    username=default_admin_username,
                    password_hash=hash_password(default_admin_password),
                    role="admin",
                )
                session.add(admin)
            if session.query(ShiftOption).count() == 0:
                session.add_all([ShiftOption(name="Day"), ShiftOption(name="Night")])
            if session.query(AreaOption).count() == 0:
                session.add_all(
                    [
                        AreaOption(name="etching_D"),
                        AreaOption(name="etching_E"),
                        AreaOption(name="litho"),
                        AreaOption(name="thin_film"),
                    ]
                )
            session.commit()
    except Exception as exc:
        print(f"建立預設管理員失敗: {exc}")


def _ensure_daily_report_columns() -> None:
    try:
        with engine.begin() as conn:
            rows = conn.exec_driver_sql("PRAGMA table_info(daily_reports)").fetchall()
            existing = {row[1] for row in rows}
            if "last_modified_by" not in existing:
                conn.exec_driver_sql(
                    "ALTER TABLE daily_reports ADD COLUMN last_modified_by VARCHAR(100)"
                )
            if "last_modified_at" not in existing:
                conn.exec_driver_sql(
                    "ALTER TABLE daily_reports ADD COLUMN last_modified_at DATETIME"
                )
            if "is_hidden" not in existing:
                conn.exec_driver_sql(
                    "ALTER TABLE daily_reports ADD COLUMN is_hidden INTEGER NOT NULL DEFAULT 0"
                )
    except Exception as exc:
        print(f"資料庫欄位檢查失敗: {exc}")
def _ensure_equipment_log_columns() -> None:
    try:
        with engine.begin() as conn:
            rows = conn.exec_driver_sql("PRAGMA table_info(equipment_logs)").fetchall()
            existing = {row[1] for row in rows}
            if "impact_hours" not in existing:
                conn.exec_driver_sql(
                    "ALTER TABLE equipment_logs ADD COLUMN impact_hours REAL NOT NULL DEFAULT 0"
                )
    except Exception as exc:
        print(f"Equipment log migration failed: {exc}")


