from fastapi import APIRouter
from pydantic import BaseModel
from uuid import uuid4
import time

router = APIRouter()

class PayRequest(BaseModel):
    sum: float
    currency: str
    receiver: str
    nr_card: str
    exp_date: str
    cvv: str
    first_name: str
    last_name: str

class PayResponse(BaseModel):
    status: str
    transaction_id: str
    message: str

def pay(request: PayRequest):
    time.sleep(3)
    if len(request.nr_card) != 16 or not request.nr_card.isdigit():
        return PayResponse(
            status="failure",
            transaction_id="",
            message="Invalid card number."
        )

    return PayResponse(
        status="success",
        transaction_id=str(uuid4()),
        message=f"Payment of {request.sum} {request.currency} to {request.receiver} processed."
    )