from __future__ import annotations

import importlib.util
import platform
import sys


def environment_report() -> str:
    modules = {name: bool(importlib.util.find_spec(name)) for name in ("numpy", "cv2", "mediapipe", "PySide6")}
    return "\n".join([
        "AirOS AI diagnostics",
        f"OS: {platform.platform()}",
        f"Python: {sys.version.split()[0]}",
        "Optional modules: " + ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in modules.items()),
        "Camera: not probed by diagnostics mode",
    ])

