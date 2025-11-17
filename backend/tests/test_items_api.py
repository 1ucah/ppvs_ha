# ChatGPT generation was used in this file
from collections.abc import Generator
from pathlib import Path
import sqlite3
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend import main  # noqa: E402
from backend.main import app, get_db  # noqa: E402


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    test_db = tmp_path / "notes.db"
    main.db_path = str(test_db)
    main.init_db()

    def override_connection() -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(main.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = override_connection
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_note(client: TestClient) -> None:
    response = client.post("/api/items", json={"title": "Test", "content": "Something"})
    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Test"
    assert payload["content"] == "Something"
    assert "id" in payload


def test_list_notes(client: TestClient) -> None:
    client.post("/api/items", json={"title": "A", "content": "a"})
    client.post("/api/items", json={"title": "B", "content": "b"})

    response = client.get("/api/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_delete_note(client: TestClient) -> None:
    created = client.post("/api/items", json={"title": "Temp", "content": "delete"})
    note_id = created.json()["id"]

    delete_response = client.delete(f"/api/items/{note_id}")
    assert delete_response.status_code == 204

    missing = client.get(f"/api/items/{note_id}")
    assert missing.status_code == 404
