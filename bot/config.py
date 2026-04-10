import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN","").strip()
if not TG_BOT_TOKEN or TG_BOT_TOKEN.startswith("PUT_YOUR"):
    raise RuntimeError("TG_BOT_TOKEN не задан. Заполни .env")

# Список админов бота (через запятую): TG_ADMIN_IDS=123,456
TG_ADMIN_IDS = {s.strip() for s in os.getenv("TG_ADMIN_IDS", "").split(",") if s.strip()}


def is_admin(user_id: int) -> bool:
    return str(user_id) in TG_ADMIN_IDS
