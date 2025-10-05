from __future__ import annotations

import os
import platform
import subprocess
from typing import Optional


def open_in_file_manager(path: str) -> bool:
    try:
        if platform.system() == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
            return True
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
            return True
        else:
            subprocess.Popen(["xdg-open", path])
            return True
    except Exception:
        return False


def reveal_in_file_manager(path: str) -> bool:
    if os.path.isdir(path):
        return open_in_file_manager(path)
    directory = os.path.dirname(path)
    return open_in_file_manager(directory)
