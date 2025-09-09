import uvicorn
from fastapi import FastAPI


from app.payment_api import payments_api

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/pay", response_model=payments_api.PayResponse)
def process_payment(request: payments_api.PayRequest):
    return payments_api.pay(request)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
