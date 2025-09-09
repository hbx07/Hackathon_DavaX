# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.web_api.core.database import get_db, User

router = APIRouter(prefix="/auth", tags=["auth"])

# Swagger-barát Bearer séma (jobb felső "Authorize" gomb)
bearer_scheme = HTTPBearer(auto_error=True)


# ----------- Pydantic modellek -----------
class LoginIn(BaseModel):
    cnp: str = Field(..., description="CNP (13 számjegy)")
    last_name: str = Field(..., min_length=1, description="Nume (vezetéknév)")
    first_name: str = Field(..., min_length=1, description="Prenume (keresztnév)")

    @field_validator("cnp")
    @classmethod
    def cnp_13_digits(cls, v: str) -> str:
        if not (len(v) == 13 and v.isdigit()):
            raise ValueError("CNP must have exactly 13 digits")
        return v


class UserOut(BaseModel):
    id: UUID | str
    cnp: str
    last_name: str
    first_name: str


class LoginOut(BaseModel):
    token: str
    user: UserOut


# ----------- Helper: aktuális user a Bearer tokenből -----------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserOut:
    """
    Swagger 'Authorize' mezőjébe CSAK a tokent írd: DEMO::<cnp>
    (A 'Bearer ' előtagot a Swagger automatikusan hozzáteszi.)
    """
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")

    token = credentials.credentials  # pl. DEMO::1234567890123
    if not token.startswith("DEMO::"):
        raise HTTPException(status_code=401, detail="Invalid token")

    cnp = token.split("::", 1)[1]
    user = db.scalar(select(User).where(User.cnp == cnp))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return UserOut(id=user.id, cnp=user.cnp, last_name=user.last_name, first_name=user.first_name)


# ----------- VÉGPONTOK -----------
@router.post("/login", response_model=LoginOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    """
    LOGIN CSAK ELLENŐRZÉSHEZ:
    - NEM hoz létre felhasználót
    - Ellenőrzi, hogy van-e ilyen CNP a DB-ben, és a nevek (case-insensitive) stimmelnek-e
    - Ha igen: 200 + token (DEMO::<cnp>) + user
    - Ha nem: 401 hiba üzenettel
    """
    user = db.scalar(select(User).where(User.cnp == payload.cnp))
    if not user:
        raise HTTPException(status_code=401, detail="User not found in database")

    # név-ellenőrzés (kis/nagybetű független, trim)
    if user.last_name.strip().lower() != payload.last_name.strip().lower() or \
       user.first_name.strip().lower() != payload.first_name.strip().lower():
        raise HTTPException(status_code=401, detail="Name does not match this CNP")

    token = f"DEMO::{payload.cnp}"
    return LoginOut(
        token=token,
        user=UserOut(id=user.id, cnp=user.cnp, last_name=user.last_name, first_name=user.first_name),
    )


@router.get("/me", response_model=UserOut)
def me(user: UserOut = Depends(get_current_user)):
    """Bejelentkezett felhasználó lekérése Bearer token alapján."""
    return user
