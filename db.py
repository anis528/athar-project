"""SQLite-backed order storage for the Athar admin portal.

Stores every confirmed order, including the high-resolution AI image URL and
the full PDF blob, so admins can fulfill orders without leaking high-res assets
to end users."""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any

DB_PATH = os.path.join(os.path.dirname(__file__), 'athar.db')


@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                child_name    TEXT NOT NULL,
                theme         TEXT NOT NULL,
                phone         TEXT NOT NULL,
                wilaya        TEXT NOT NULL,
                address       TEXT NOT NULL,
                shipping_type TEXT NOT NULL,
                shipping_cost INTEGER NOT NULL,
                items_json    TEXT NOT NULL,
                total_dzd     INTEGER NOT NULL,
                ai_image_url  TEXT,
                pdf_blob      BLOB,
                created_at    TEXT NOT NULL
            )
        """)


def create_order(*, child_name: str, theme: str, phone: str, wilaya: str,
                 address: str, shipping_type: str, shipping_cost: int,
                 items_json: str, total_dzd: int, ai_image_url: str | None,
                 pdf_blob: bytes | None) -> int:
    with _conn() as c:
        cur = c.execute("""
            INSERT INTO orders (child_name, theme, phone, wilaya, address,
                                shipping_type, shipping_cost, items_json, total_dzd,
                                ai_image_url, pdf_blob, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (child_name, theme, phone, wilaya, address,
              shipping_type, shipping_cost, items_json, total_dzd,
              ai_image_url, pdf_blob,
              datetime.utcnow().isoformat(timespec='seconds')))
        return int(cur.lastrowid)


def list_orders() -> list[dict[str, Any]]:
    with _conn() as c:
        rows = c.execute("""
            SELECT id, child_name, theme, phone, wilaya, address,
                   shipping_type, shipping_cost, items_json, total_dzd,
                   ai_image_url, created_at,
                   (CASE WHEN pdf_blob IS NULL THEN 0 ELSE LENGTH(pdf_blob) END) AS pdf_size
            FROM orders
            ORDER BY id DESC
        """).fetchall()
        return [dict(r) for r in rows]


def get_order(order_id: int) -> dict[str, Any] | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        return dict(row) if row else None


def format_order_id(order_id: int) -> str:
    return f"#{order_id:04d}"
