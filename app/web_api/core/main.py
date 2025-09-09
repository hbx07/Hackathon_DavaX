# app/web_api/core/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from pathlib import Path
import os

from ..api.auth import router as auth_router
from .database import seed_default_user

app = FastAPI(title="payments-api", docs_url="/api/docs", redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _seed_on_startup() -> None:
    seed_default_user()

def resolve_ui_dir() -> Path:
    # 1) CWD/UI (onnan indítod az uvicornt)
    # 2) <repo gyökér>/UI (main.py -> core -> web_api -> app -> repo gyökér)
    # 3) egyéb fallbackek
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
    raise RuntimeError("UI directory not found. Tried: " + " | ".join(map(str, candidates)))

UI_DIR = Path(r"C:\Endava\EndevLocal\TechFest\Hackathon_DavaX\UI")

# html=True: ha könyvtárat kérsz be (pl. /ui/), index.html-t keres.
app.mount("/ui", StaticFiles(directory=str(UI_DIR), html=True), name="ui")

def login_path_under_ui() -> str:
    """Döntsük el, hol van a login.html, és arra irányítsunk."""
    if (UI_DIR / "login.html").exists():
        print("[UI] Found login at UI/login.html")
        return "/ui/login.html"
    if (UI_DIR / "Login" / "login.html").exists():
        print("[UI] Found login at UI/Login/login.html")
        return "/ui/Login/login.html"
    # ha egyik sincs, akkor legalább logoljunk hasznosat
    print("[UI] login.html not found at UI/login.html or UI/Login/login.html")
    return "/ui/login.html"  # default próbálkozás

@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url=login_path_under_ui(), status_code=307)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router)
