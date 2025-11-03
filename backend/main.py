from fastapi import FastAPI
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PPV Hausaufgabe 1 Backend")


@app.get("/api/ping")
def ping():
    return {"status": "ok", "time": datetime.now(timezone.utc)}


@app.post("/api/pong")
def pong():
    logger.info("Pong")
    return {"message": "logged"}
