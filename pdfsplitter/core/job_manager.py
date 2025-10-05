from __future__ import annotations

import threading
from typing import Callable, Optional

from .history import HistoryStore
from .models import HistoryRecord, JobStatus, SplitJobParams, SplitJobResult, SplitStrategy, now_utc
from .splitter import SplitCancelled, split_pdf


class JobHandle:
    def __init__(self) -> None:
        self._cancel_flag = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self.job_id: Optional[int] = None

    def cancel(self) -> None:
        self._cancel_flag.set()

    def is_cancelled(self) -> bool:
        return self._cancel_flag.is_set()


class JobManager:
    def __init__(self, history: Optional[HistoryStore] = None) -> None:
        self.history = history or HistoryStore()

    def start_job(
        self,
        params: SplitJobParams,
        on_progress: Optional[Callable[[float, str], None]] = None,
        on_complete: Optional[Callable[[Optional[SplitJobResult], Optional[Exception], int], None]] = None,
    ) -> JobHandle:
        handle = JobHandle()

        # Create history record as pending
        rec = HistoryRecord(
            id=None,
            created_at=now_utc(),
            input_path=params.input_path,
            output_dir=params.output_dir,
            strategy=params.strategy,
            params_json=params.to_json_dict(),
            status=JobStatus.PENDING,
            duration_ms=None,
            output_count=None,
            error_message=None,
            output_sample=None,
        )
        job_id = self.history.add_job(rec)
        handle.job_id = job_id

        def run() -> None:
            # mark running
            self.history.update_job(job_id, status=JobStatus.RUNNING.value)
            try:
                result = split_pdf(
                    params,
                    progress_callback=lambda p, m: on_progress(p, m) if on_progress else None,
                    should_cancel=handle.is_cancelled,
                )
                self.history.update_job(
                    job_id,
                    status=JobStatus.SUCCESS.value,
                    duration_ms=result.duration_ms,
                    output_count=len(result.output_files),
                    output_sample=result.output_files[:5],
                )
                if on_complete:
                    on_complete(result, None, job_id)
            except SplitCancelled as exc:
                self.history.update_job(job_id, status=JobStatus.CANCELLED.value, error_message=str(exc))
                if on_complete:
                    on_complete(None, exc, job_id)
            except Exception as exc:
                self.history.update_job(job_id, status=JobStatus.FAILED.value, error_message=str(exc))
                if on_complete:
                    on_complete(None, exc, job_id)

        t = threading.Thread(target=run, daemon=True)
        handle.thread = t
        t.start()
        return handle
