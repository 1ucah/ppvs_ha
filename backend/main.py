import logging
import os
import sqlite3
from datetime import datetime, timezone
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PPV Hausaufgabe 2 Backend")

frontend_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend",
)

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.db")


def init_db() -> None:
    with sqlite3.connect(db_path, check_same_thread=False) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/ping")
def ping():
    return {"status": "ok", "time": datetime.now(timezone.utc)}


@app.post("/api/items", status_code=201)
async def create_item(request: Request, conn: sqlite3.Connection = Depends(get_db)):
    payload = await request.json()
    title = (payload.get("title") or "").strip()
    content = (payload.get("content") or "").strip()
    if not title or not content:
        raise HTTPException(status_code=400, detail="title and content required")

    created_at = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        "INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)",
        (title, content, created_at),
    )
    conn.commit()
    return {
        "id": cursor.lastrowid,
        "title": title,
        "content": content,
        "created_at": created_at,
    }


@app.get("/api/items")
def list_items(conn: sqlite3.Connection = Depends(get_db)):
    rows = conn.execute(
        "SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC"
    ).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/items/{item_id}")
def get_item(item_id: int, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute(
        "SELECT id, title, content, created_at FROM notes WHERE id = ?", (item_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict(row)


@app.delete("/api/items/{item_id}", status_code=204)
def delete_item(item_id: int, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.execute("DELETE FROM notes WHERE id = ?", (item_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return None


@app.post("/api/pong")
def pong():
    logger.info("Pong")
    return {"message": "logged"}


app.mount(
    "/",
    StaticFiles(directory=frontend_path, html=True),
    name="frontend",
)
