import os
from datetime import datetime, timezone
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PPV Hausaufgabe 1 Backend")

frontend_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend",
)


@app.get("/api/ping")
def ping():
    return {"status": "ok", "time": datetime.now(timezone.utc)}


@app.post("/api/pong")
def pong():
    logger.info("Pong")
    return {"message": "logged"}


app.mount(
    "/",
    StaticFiles(directory=frontend_path, html=True),
    name="frontend",
)
