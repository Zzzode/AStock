#!/usr/bin/env python3
"""Compatibility wrapper for the AI-storage research workspace verifier."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> int:
    verifier = Path(__file__).with_name("verify_ai_storage.py")
    if not verifier.exists():
        print(f"Missing verifier: {verifier}", file=sys.stderr)
        return 2
    try:
        runpy.run_path(str(verifier), run_name="__main__")
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
