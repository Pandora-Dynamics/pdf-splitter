from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional, Tuple
from datetime import datetime

from platformdirs import user_data_dir

from .models import HistoryRecord, JobStatus, SplitStrategy, now_utc


_APP_NAME = "KivyPDFSplitter"
_APP_AUTHOR = "ModernTools"
_DB_NAME = "history.sqlite3"


def _db_path() -> str:
    base = user_data_dir(_APP_NAME, _APP_AUTHOR, ensure_exists=True)
    return os.path.join(base, _DB_NAME)


class HistoryStore:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or _db_path()
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        con = sqlite3.connect(self.path)
        try:
            cur = con.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    input_path TEXT NOT NULL,
                    output_dir TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    params_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration_ms INTEGER,
                    output_count INTEGER,
                    error_message TEXT,
                    output_sample TEXT
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);")
            con.commit()
        finally:
            con.close()

    def add_job(self, rec: HistoryRecord) -> int:
        con = sqlite3.connect(self.path)
        try:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO jobs (created_at, input_path, output_dir, strategy, params_json, status, duration_ms, output_count, error_message, output_sample)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec.created_at.isoformat(),
                    rec.input_path,
                    rec.output_dir,
                    rec.strategy.value,
                    json.dumps(rec.params_json),
                    rec.status.value,
                    rec.duration_ms,
                    rec.output_count,
                    rec.error_message,
                    json.dumps(rec.output_sample) if rec.output_sample is not None else None,
                ),
            )
            con.commit()
            return int(cur.lastrowid)
        finally:
            con.close()

    def update_job(self, job_id: int, **fields: Any) -> None:
        if not fields:
            return
        allowed = {"status", "duration_ms", "output_count", "error_message", "output_sample"}
        sets = []
        values: List[Any] = []
        for key, value in fields.items():
            if key not in allowed:
                continue
            sets.append(f"{key} = ?")
            if key == "output_sample" and value is not None:
                values.append(json.dumps(value))
            else:
                values.append(value)
        if not sets:
            return
        con = sqlite3.connect(self.path)
        try:
            cur = con.cursor()
            cur.execute(f"UPDATE jobs SET {', '.join(sets)} WHERE id = ?", (*values, job_id))
            con.commit()
        finally:
            con.close()

    def list_jobs(
        self,
        limit: int = 200,
        offset: int = 0,
        status: Optional[JobStatus] = None,
        search: Optional[str] = None,
    ) -> List[HistoryRecord]:
        where = []
        params: List[Any] = []
        if status:
            where.append("status = ?")
            params.append(status.value)
        if search:
            where.append("(input_path LIKE ? OR output_dir LIKE ?)" )
            like = f"%{search}%"
            params.extend([like, like])
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        sql = f"SELECT id, created_at, input_path, output_dir, strategy, params_json, status, duration_ms, output_count, error_message, output_sample FROM jobs {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        con = sqlite3.connect(self.path)
        try:
            cur = con.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
        finally:
            con.close()
        result: List[HistoryRecord] = []
        for row in rows:
            (rid, created_at, input_path, output_dir, strategy, params_json, status, duration_ms, output_count, error_message, output_sample) = row
            result.append(
                HistoryRecord(
                    id=int(rid),
                    created_at=datetime.fromisoformat(created_at),
                    input_path=input_path,
                    output_dir=output_dir,
                    strategy=SplitStrategy(strategy),
                    params_json=json.loads(params_json),
                    status=JobStatus(status),
                    duration_ms=duration_ms,
                    output_count=output_count,
                    error_message=error_message,
                    output_sample=json.loads(output_sample) if output_sample else None,
                )
            )
        return result

    def get_job(self, job_id: int) -> Optional[HistoryRecord]:
        con = sqlite3.connect(self.path)
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT id, created_at, input_path, output_dir, strategy, params_json, status, duration_ms, output_count, error_message, output_sample FROM jobs WHERE id = ?",
                (job_id,),
            )
            row = cur.fetchone()
        finally:
            con.close()
        if not row:
            return None
        (rid, created_at, input_path, output_dir, strategy, params_json, status, duration_ms, output_count, error_message, output_sample) = row
        return HistoryRecord(
            id=int(rid),
            created_at=datetime.fromisoformat(created_at),
            input_path=input_path,
            output_dir=output_dir,
            strategy=SplitStrategy(strategy),
            params_json=json.loads(params_json),
            status=JobStatus(status),
            duration_ms=duration_ms,
            output_count=output_count,
            error_message=error_message,
            output_sample=json.loads(output_sample) if output_sample else None,
        )

    def clear(self) -> None:
        con = sqlite3.connect(self.path)
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM jobs;")
            con.commit()
        finally:
            con.close()
