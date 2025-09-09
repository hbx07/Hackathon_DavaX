# app/web_api/api/bills.py
from __future__ import annotations
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.database import get_db, Bill, BillStatus
from .auth import get_current_user, UserOut  # token ellenőrzéshez

router = APIRouter(prefix="/bills", tags=["bills"])


# ---------- Pydantic ----------
class BillOut(BaseModel):
    id: str
    user_id: str
    company: str
    amount: float
    status: BillStatus
    description: Optional[str] = None
    due_date: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Endpoints ----------
@router.get("", response_model=List[BillOut])
def list_bills(
    status: Optional[BillStatus] = Query(default=None, description="DUE vagy PAID"),
    user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Bill).where(Bill.user_id == str(user.id))
    if status:
        stmt = stmt.where(Bill.status == status)
    rows = db.scalars(stmt).all()
    return rows


@router.get("/{bill_id}", response_model=BillOut)
def get_bill(
    bill_id: str,
    user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bill = db.get(Bill, bill_id)
    if not bill or bill.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.post("/{bill_id}/pay", response_model=BillOut)
def pay_bill(
    bill_id: str,
    user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bill = db.get(Bill, bill_id)
    if not bill or bill.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Bill not found")
    if bill.status == BillStatus.PAID:
        return bill

    bill.status = BillStatus.PAID
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill
