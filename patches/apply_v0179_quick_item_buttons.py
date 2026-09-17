#!/usr/bin/env python3
"""Compatibility entry point for the Android Quick-Use test build.

Keeps the safe-spawn fix, retires the failed runtime-created Quick-Use widgets,
and applies the v0.18.0 permanent QUICK button + six-slot radial menu.
"""
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).resolve().parent
steps = [
    patch_dir / "apply_v0179_quick_items_safe_spawn.py",
    patch_dir / "apply_v0180_radial_quick_menu.py",
]

for step in steps:
    if not step.is_file():
        raise SystemExit(f"Missing Quick-Use applicator: {step}")
    result = subprocess.run([sys.executable, str(step), str(root)])
    if result.returncode != 0:
        raise SystemExit(result.returncode)

print("Applied safe spawn plus v0.18.0 permanent radial Quick menu.")
