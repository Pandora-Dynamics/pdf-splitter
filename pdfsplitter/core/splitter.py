from __future__ import annotations

import os
import time
from typing import Callable, List, Optional, Tuple

from pypdf import PdfReader, PdfWriter

from .models import SplitJobParams, SplitJobResult, SplitStrategy
from .utils import ensure_directory, parse_page_ranges, safe_filename


class SplitCancelled(Exception):
    pass


def split_pdf(
    params: SplitJobParams,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    should_cancel: Optional[Callable[[], bool]] = None,
) -> SplitJobResult:
    """
    Run the PDF split operation based on the provided parameters.

    progress_callback: (0..1, message)
    should_cancel: returns True to request cancellation
    """
    start_ns = time.perf_counter_ns()

    if progress_callback:
        progress_callback(0.0, "Starting...")

    if should_cancel and should_cancel():
        raise SplitCancelled()

    if not os.path.exists(params.input_path) or not params.input_path.lower().endswith(".pdf"):
        raise ValueError("Input file must exist and be a .pdf")

    ensure_directory(params.output_dir)

    reader = PdfReader(params.input_path)

    # Try to access number of pages to validate quickly; raises if encrypted without password.
    try:
        num_pages = len(reader.pages)
    except Exception as exc:
        raise ValueError(f"Unable to read PDF: {exc}")

    if num_pages == 0:
        raise ValueError("PDF has no pages")

    # Determine list of (start,end) 1-based inclusive ranges for output
    ranges: List[Tuple[int, int]]
    single_files_labels: Optional[List[str]] = None

    strategy = params.strategy
    if strategy == SplitStrategy.RANGES:
        if not params.ranges_text:
            raise ValueError("Ranges strategy requires 'ranges_text'.")
        ranges = parse_page_ranges(params.ranges_text, num_pages)
        single_files_labels = [f"{s}-{e}" if s != e else f"p{s}" for s, e in ranges]
    elif strategy == SplitStrategy.EACH_PAGE:
        ranges = [(i, i) for i in range(1, num_pages + 1)]
        single_files_labels = [f"p{i}" for i in range(1, num_pages + 1)]
    elif strategy == SplitStrategy.EVERY_N_PAGES:
        if not params.pages_per_file or params.pages_per_file < 1:
            raise ValueError("Every N pages strategy requires 'pages_per_file' >= 1.")
        ranges = []
        for start in range(1, num_pages + 1, params.pages_per_file):
            end = min(num_pages, start + params.pages_per_file - 1)
            ranges.append((start, end))
        single_files_labels = [f"{s}-{e}" if s != e else f"p{s}" for s, e in ranges]
    elif strategy == SplitStrategy.ODD_TOGETHER:
        ranges = []
        # Special case: odd pages together into one output
        # We'll treat as a single range list marker using (-1, -1) to indicate special grouping
        # but simpler: build pages list directly later
    elif strategy == SplitStrategy.EVEN_TOGETHER:
        ranges = []
    else:
        raise ValueError(f"Unknown split strategy: {strategy}")

    if progress_callback:
        progress_callback(0.05, f"Preparing to split {num_pages} pages...")

    if should_cancel and should_cancel():
        raise SplitCancelled()

    # Generate output files
    output_files: List[str] = []

    def copy_metadata(writer: PdfWriter) -> None:
        try:
            if params.preserve_metadata and reader.metadata is not None:
                writer.add_metadata(reader.metadata)
        except Exception:
            # Non-fatal if metadata copy fails
            pass

    def unique_path(base_dir: str, base_name: str) -> str:
        candidate = os.path.join(base_dir, base_name)
        if not os.path.exists(candidate):
            return candidate
        root, ext = os.path.splitext(candidate)
        suffix = 1
        while True:
            cand = f"{root}-{suffix}{ext}"
            if not os.path.exists(cand):
                return cand
            suffix += 1

    total_outputs = 0

    if strategy in (SplitStrategy.RANGES, SplitStrategy.EACH_PAGE, SplitStrategy.EVERY_N_PAGES):
        digits = max(params.zero_pad_digits, len(str(len(ranges))))
        for index, (start, end) in enumerate(ranges, start=1):
            if should_cancel and should_cancel():
                raise SplitCancelled()
            writer = PdfWriter()
            for i in range(start - 1, end):
                writer.add_page(reader.pages[i])
            copy_metadata(writer)
            label = single_files_labels[index - 1] if single_files_labels else f"{start}-{end}"
            filename = f"{params.output_prefix}_{str(index).zfill(digits)}_{label}.pdf"
            filename = safe_filename(filename)
            out_path = unique_path(params.output_dir, filename)
            with open(out_path, "wb") as f:
                writer.write(f)
            output_files.append(out_path)
            total_outputs += 1
            if progress_callback:
                progress_callback(0.05 + 0.9 * (index / max(1, len(ranges))), f"Wrote {index}/{len(ranges)} files")
    elif strategy == SplitStrategy.ODD_TOGETHER:
        writer = PdfWriter()
        for i in range(0, num_pages):
            if (i + 1) % 2 == 1:
                writer.add_page(reader.pages[i])
        if len(writer.pages) > 0:
            copy_metadata(writer)
            filename = safe_filename(f"{params.output_prefix}_odd_pages.pdf")
            out_path = unique_path(params.output_dir, filename)
            with open(out_path, "wb") as f:
                writer.write(f)
            output_files.append(out_path)
            total_outputs += 1
            if progress_callback:
                progress_callback(0.95, "Wrote odd pages file")
    elif strategy == SplitStrategy.EVEN_TOGETHER:
        writer = PdfWriter()
        for i in range(0, num_pages):
            if (i + 1) % 2 == 0:
                writer.add_page(reader.pages[i])
        if len(writer.pages) > 0:
            copy_metadata(writer)
            filename = safe_filename(f"{params.output_prefix}_even_pages.pdf")
            out_path = unique_path(params.output_dir, filename)
            with open(out_path, "wb") as f:
                writer.write(f)
            output_files.append(out_path)
            total_outputs += 1
            if progress_callback:
                progress_callback(0.95, "Wrote even pages file")

    duration_ms = int((time.perf_counter_ns() - start_ns) / 1_000_000)

    if should_cancel and should_cancel():
        raise SplitCancelled()

    if progress_callback:
        progress_callback(1.0, f"Done in {duration_ms} ms")

    return SplitJobResult(output_files=output_files, total_pages=num_pages, duration_ms=duration_ms)
