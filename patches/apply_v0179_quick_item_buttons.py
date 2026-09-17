#!/usr/bin/env python3
"""Compatibility entry point for the v0.17.9 Android build.

Applies the combined Quick-Use + safe-spawn patch, then moves Quick-Use
controls onto an independent Android CanvasLayer so they cannot disappear
through the legacy hotbar/layout system.
"""
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).resolve().parent
steps = [
    patch_dir / "apply_v0179_quick_items_safe_spawn.py",
    patch_dir / "apply_v0179_quick_overlay_fix.py",
]

for step in steps:
    if not step.is_file():
        raise SystemExit(f"Missing v0.17.9 applicator: {step}")
    result = subprocess.run([sys.executable, str(step), str(root)])
    if result.returncode != 0:
        raise SystemExit(result.returncode)

print("Applied v0.17.9 safe-spawn plus independent Quick-Use overlay fixes.")
