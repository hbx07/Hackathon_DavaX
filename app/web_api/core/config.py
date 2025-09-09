# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # beolvassa a .env fájlt

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "payments-api")
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    DEMO_SECRET: str = os.getenv("DEMO_SECRET", "dev-secret")  # később hasznos

settings = Settings()
