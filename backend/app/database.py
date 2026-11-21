"""Scan storage. Uses a local JSON file by default; MongoDB if MONGO_URI is set.
Both stores expose: save_scan(scan), latest_scan(), list_scans(limit)."""
from __future__ import annotations

import json
import os
import threading
from functools import lru_cache
from typing import List, Optional

from app.config import settings

MAX_HISTORY = 20


class JsonStore:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def _read(self) -> List[dict]:
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def save_scan(self, scan: dict) -> None:
        with self._lock:
            scans = self._read()
            scans.append(scan)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(scans[-MAX_HISTORY:], f, indent=2)

    def latest_scan(self) -> Optional[dict]:
        scans = self._read()
        return scans[-1] if scans else None

    def list_scans(self, limit: int = 10) -> List[dict]:
        return [
            {"scan_id": s["scan_id"], "scanned_at": s["scanned_at"], "summary": s["summary"]}
            for s in reversed(self._read()[-limit:])
        ]


class MongoStore:
    def __init__(self, uri: str, db_name: str):
        from pymongo import MongoClient

        self.col = MongoClient(uri)[db_name]["scan_results"]

    def save_scan(self, scan: dict) -> None:
        self.col.insert_one(dict(scan))  # copy: insert_one adds _id

    def latest_scan(self) -> Optional[dict]:
        return self.col.find_one({}, {"_id": 0}, sort=[("scanned_at", -1)])

    def list_scans(self, limit: int = 10) -> List[dict]:
        cur = self.col.find({}, {"_id": 0, "scan_id": 1, "scanned_at": 1, "summary": 1}) \
                      .sort("scanned_at", -1).limit(limit)
        return list(cur)


@lru_cache(maxsize=1)
def get_store():
    if settings.mongo_uri:
        return MongoStore(settings.mongo_uri, settings.mongo_db)
    return JsonStore(settings.data_file)
