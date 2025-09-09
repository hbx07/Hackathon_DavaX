# app/web_api/core/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from pathlib import Path
import os

from ..api.auth import router as auth_router
from ..api.bills import router as bills_router
from .database import seed_default_user, seed_bills_for_user

app = FastAPI(title="payments-api", docs_url="/api/docs", redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _seed_on_startup() -> None:
    user = seed_default_user()
    seed_bills_for_user(user.id)

# --- UI mount (amit korábban beállítottunk) ---
def resolve_ui_dir() -> Path:
    candidates = [
        Path(os.getcwd()) / "UI",
        Path(__file__).resolve().parents[3] / "UI",
        Path(__file__).resolve().parents[2] / "UI",
        Path(__file__).resolve().parents[1] / "UI",
    ]
    for p in candidates:
        if p.exists() and p.is_dir():
            print(f"[UI] Serving static files from: {p}")
            return p
    raise RuntimeError("UI directory not found.")
UI_DIR = resolve_ui_dir()
app.mount("/ui", StaticFiles(directory=str(UI_DIR), html=True), name="ui")

@app.get("/", include_in_schema=False)
def root_redirect():
    # nálatok UI/Login/login.html a login
    return RedirectResponse(url="/ui/Login/login.html", status_code=307)

@app.get("/health")
def health():
    return {"status": "ok"}

# API-k
app.include_router(auth_router)
app.include_router(bills_router)
