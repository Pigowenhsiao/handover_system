from __future__ import annotations

from datetime import datetime, date
from typing import Generator, Optional

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

DATABASE_URL = "sqlite:///handover_system.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
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
    summary_key_output: str = Column(Text, default="", nullable=False)
    summary_issues: str = Column(Text, default="", nullable=False)
    summary_countermeasures: str = Column(Text, default="", nullable=False)

    author = relationship("User", back_populates="reports")
    attendance_entries = relationship("AttendanceEntry", back_populates="report", cascade="all, delete-orphan")
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


class EquipmentLog(Base):
    __tablename__ = "equipment_logs"

    id: int = Column(Integer, primary_key=True, index=True)
    report_id: int = Column(Integer, ForeignKey("daily_reports.id"), nullable=False)
    equip_id: str = Column(String(50), nullable=False)
    description: str = Column(Text, default="", nullable=False)
    start_time: str = Column(String(50), default="", nullable=False)
    impact_qty: int = Column(Integer, default=0, nullable=False)
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
