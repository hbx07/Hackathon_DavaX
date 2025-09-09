# app/web_api/core/database.py
import os
import uuid
from typing import Generator

from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, Session

# --- DB URL: alapból SQLite fájl a repo gyökerében (app.db) ---
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
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)    # Nume
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)   # Prenume


# Táblák létrehozása
Base.metadata.create_all(bind=engine)


# ---------------- Seed: 1 db teszt user ----------------
def seed_default_user() -> None:
    """
    Fejlesztői seed: ha nincs meg, beszúrunk egy felhasználót.
    CNP: 1234567890123 | Nume: Popescu | Prenume: Ion
    """
    db = SessionLocal()
    try:
        cnp = "1234567890123"
        exists = db.scalar(select(User).where(User.cnp == cnp))
        if not exists:
            user = User(
                id=str(uuid.uuid4()),
                cnp=cnp,
                last_name="Popescu",
                first_name="Ion",
            )
            db.add(user)
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
