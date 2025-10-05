from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SplitStrategy(str, Enum):
    RANGES = "ranges"  # Split by custom page ranges
    EACH_PAGE = "each_page"  # Split each page into a separate PDF
    EVERY_N_PAGES = "every_n_pages"  # Split into chunks of N pages
    ODD_TOGETHER = "odd_together"  # Collect all odd pages into one PDF
    EVEN_TOGETHER = "even_together"  # Collect all even pages into one PDF


@dataclass
class SplitJobParams:
    input_path: str
    output_dir: str
    strategy: SplitStrategy
    ranges_text: Optional[str] = None  # e.g., "1-3, 5, 10-"
    pages_per_file: Optional[int] = None  # for EVERY_N_PAGES
    output_prefix: str = "split"
    zero_pad_digits: int = 3
    preserve_metadata: bool = True

    def to_json_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["strategy"] = self.strategy.value
        return data


@dataclass
class SplitJobResult:
    output_files: List[str]
    total_pages: int
    duration_ms: int


@dataclass
class HistoryRecord:
    id: Optional[int]
    created_at: datetime
    input_path: str
    output_dir: str
    strategy: SplitStrategy
    params_json: Dict[str, Any]
    status: JobStatus
    duration_ms: Optional[int]
    output_count: Optional[int]
    error_message: Optional[str]
    output_sample: Optional[List[str]]


def now_utc() -> datetime:
    return datetime.utcnow()
