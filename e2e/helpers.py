"""Shared helpers for SPA Comments E2E tests."""

from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path

import pymysql
import requests
from PIL import Image

BASE_URL = os.environ.get("E2E_BASE_URL", "http://127.0.0.1:5173")
API_URL = os.environ.get("E2E_API_URL", "http://127.0.0.1:8000")

DB = {
    "host": os.environ.get("E2E_DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("E2E_DB_PORT", "3306")),
    "user": os.environ.get("E2E_DB_USER", "spa_user"),
    "password": os.environ.get("E2E_DB_PASSWORD", "spa_password"),
    "database": os.environ.get("E2E_DB_NAME", "spa_dzen"),
}

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def captcha_answer(hashkey: str) -> str:
    conn = pymysql.connect(
        host=DB["host"],
        port=DB["port"],
        user=DB["user"],
        password=DB["password"],
        database=DB["database"],
        charset="utf8mb4",
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT response FROM captcha_captchastore WHERE hashkey=%s",
                (hashkey,),
            )
            row = cur.fetchone()
            if not row:
                raise AssertionError(f"Captcha key not found in DB: {hashkey}")
            return row[0]
    finally:
        conn.close()


def fetch_new_captcha() -> tuple[str, str]:
    res = requests.get(f"{API_URL}/api/captcha/", timeout=10)
    res.raise_for_status()
    data = res.json()
    key = data["captcha_key"]
    return key, captcha_answer(key)


def make_test_image(path: Path, size: tuple[int, int] = (400, 300)) -> Path:
    """Create an oversized PNG so server resize logic is exercised."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color=(40, 120, 200))
    img.save(path, format="PNG")
    return path


def make_test_txt(path: Path, text: str = "e2e attachment txt\nline2\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def png_bytes(size: tuple[int, int] = (400, 300)) -> bytes:
    buf = BytesIO()
    Image.new("RGB", size, color=(40, 120, 200)).save(buf, format="PNG")
    return buf.getvalue()
