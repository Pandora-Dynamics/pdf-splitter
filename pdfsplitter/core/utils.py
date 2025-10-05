from __future__ import annotations

import os
import re
from typing import Iterable, List, Tuple


class RangeParseError(ValueError):
    pass


def parse_page_ranges(ranges_text: str, num_pages: int) -> List[Tuple[int, int]]:
    """
    Parse a human-friendly page range string into a list of 1-based inclusive ranges.

    Supported formats:
      - "1-3, 5, 7-" (to end), "-4" (from start)
      - Spaces are ignored; duplicates are removed and merged
    Raises RangeParseError with a helpful message when invalid.
    """
    if not ranges_text or not ranges_text.strip():
        raise RangeParseError("Page ranges cannot be empty.")

    normalized = ranges_text.replace(" ", "")
    parts = [p for p in normalized.split(",") if p]
    if not parts:
        raise RangeParseError("No valid ranges found.")

    ranges: List[Tuple[int, int]] = []
    for part in parts:
        if part == "-":
            raise RangeParseError("'-' is not a valid range by itself.")
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = 1 if start_str == "" else _parse_positive_int(start_str, "range start")
            end = num_pages if end_str == "" else _parse_positive_int(end_str, "range end")
            if start < 1 or end < 1:
                raise RangeParseError("Page numbers must be >= 1.")
            if start > end:
                raise RangeParseError(f"Range start {start} is greater than end {end}.")
            if start > num_pages:
                continue  # silently skip beyond end
            end = min(end, num_pages)
            ranges.append((start, end))
        else:
            page = _parse_positive_int(part, "page number")
            if page < 1:
                raise RangeParseError("Page numbers must be >= 1.")
            if page > num_pages:
                continue
            ranges.append((page, page))

    # merge overlaps and sort
    ranges.sort(key=lambda r: (r[0], r[1]))
    merged: List[Tuple[int, int]] = []
    for start, end in ranges:
        if not merged:
            merged.append((start, end))
        else:
            last_start, last_end = merged[-1]
            if start <= last_end + 1:
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))
    return merged


def _parse_positive_int(text: str, label: str) -> int:
    if not re.fullmatch(r"\d+", text):
        raise RangeParseError(f"Invalid {label}: '{text}'.")
    try:
        return int(text)
    except Exception as exc:
        raise RangeParseError(f"Invalid {label}: '{text}'.") from exc


def ensure_directory(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def safe_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._-") or "file"


def humanize_ms(ms: int) -> str:
    seconds = ms / 1000.0
    if seconds < 1:
        return f"{ms} ms"
    if seconds < 60:
        return f"{seconds:.1f} s"
    minutes = int(seconds // 60)
    rem = seconds - minutes * 60
    return f"{minutes} min {int(rem)} s"
