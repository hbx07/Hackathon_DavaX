# app/web_api/core/database.py
import os
import uuid
from enum import Enum
from typing import Generator, Optional

from sqlalchemy import create_engine, String, select, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


# ---------------- ORM modellek ----------------
class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cnp: Mapped[str] = mapped_column(String(13), unique=True, index=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)


class BillStatus(str, Enum):
    DUE = "DUE"
    PAID = "PAID"


class Bill(Base):
    __tablename__ = "bills"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    company: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[BillStatus] = mapped_column(String(8), default=BillStatus.DUE.value)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    due_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


# Táblák létrehozása (minden modell után)
Base.metadata.create_all(bind=engine)


# ---------------- Seed helpers ----------------
def seed_default_user() -> User:
    """
    Fejlesztői seed: ha nincs meg, beszúrunk egy felhasználót.
    CNP: 1234567890123 | Nume: Popescu | Prenume: Ion
    """
    db = SessionLocal()
    try:
        cnp = "1234567890123"
        user = db.scalar(select(User).where(User.cnp == cnp))
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                cnp=cnp,
                last_name="Popescu",
                first_name="Ion",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


def seed_bills_for_user(user_id: str) -> None:
    """Ha nincs még számla, pár minta számla seedelése."""
    db = SessionLocal()
    try:
        exists = db.scalar(select(Bill).where(Bill.user_id == user_id))
        if exists:
            return
        sample = [
            Bill(user_id=user_id, company="Electrica", amount=150.0, status=BillStatus.DUE.value,
                 description="Factura energie", due_date="2025-09-22"),
            Bill(user_id=user_id, company="Digi", amount=65.0, status=BillStatus.DUE.value,
                 description="Abonament internet", due_date="2025-10-20"),
            Bill(user_id=user_id, company="E.ON", amount=120.0, status=BillStatus.DUE.value,
                 description="Gaz", due_date="2025-09-25"),
        ]
        db.add_all(sample)
        db.commit()
    finally:
        db.close()


# ---------------- FastAPI dependency ----------------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
