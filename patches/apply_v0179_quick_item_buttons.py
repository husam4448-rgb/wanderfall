#!/usr/bin/env python3
"""Compatibility entry point for the v0.17.9 Android build.

The active v0.17.9 implementation is the combined Quick-Use + safe-spawn
applicator. Keeping this filename lets the existing GitHub Actions workflow
build the corrected runtime without changing workflow permissions.
"""
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
combined = Path(__file__).resolve().with_name("apply_v0179_quick_items_safe_spawn.py")

if not combined.is_file():
    raise SystemExit(f"Missing combined v0.17.9 applicator: {combined}")

result = subprocess.run([sys.executable, str(combined), str(root)])
raise SystemExit(result.returncode)
