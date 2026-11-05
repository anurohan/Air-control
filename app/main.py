"""Safe application entry point.

The core can run in diagnostics mode without optional GUI or camera packages.
"""
from __future__ import annotations

import argparse

from services.diagnostics_service import environment_report


def main() -> int:
    parser = argparse.ArgumentParser(description="AirOS AI local touchless control")
    parser.add_argument("--diagnostics", action="store_true", help="print environment diagnostics")
    args = parser.parse_args()
    if args.diagnostics:
        print(environment_report())
        return 0
    try:
        from ui.main_window import run_desktop
    except ImportError as exc:
        print(f"Desktop UI unavailable: {exc}")
        print("Install optional dependencies with: pip install -e .[desktop,tracking]")
        return 2
    return run_desktop()


if __name__ == "__main__":
    raise SystemExit(main())

