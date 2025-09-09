# app/main.py
from fastapi import FastAPI
from app.web_api.api.auth import router as auth_router
from app.web_api.core.database import seed_default_user

app = FastAPI(title="payments-api")

@app.on_event("startup")
def _seed_on_startup():
    # Induláskor egyszer lefut: berak egy teszt usert, ha még nincs
    seed_default_user()

@app.get("/")
def root():
    return {"message": "Payments API – see /docs for interactive docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

# router(ek)
app.include_router(auth_router)
