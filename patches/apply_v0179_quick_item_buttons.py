#!/usr/bin/env python3
"""Compatibility entry point for the v0.17.9 Android build.

Applies the combined Quick-Use + safe-spawn patch, strips the legacy
Quick-Use layout registration, then moves Quick-Use controls onto an
independent Android CanvasLayer.
"""
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).resolve().parent
combined = patch_dir / "apply_v0179_quick_items_safe_spawn.py"
overlay = patch_dir / "apply_v0179_quick_overlay_fix.py"

for step in (combined, overlay):
    if not step.is_file():
        raise SystemExit(f"Missing v0.17.9 applicator: {step}")

result = subprocess.run([sys.executable, str(combined), str(root)])
if result.returncode != 0:
    raise SystemExit(result.returncode)

mobile_path = root / "scripts/mobile_hud.gd"
mobile = mobile_path.read_text(encoding="utf-8")
legacy_call = "UIManager.register_layout_control(button, _quick_item_layout_id(item_id))"
mobile = mobile.replace(legacy_call, "pass # Quick-Use overlay intentionally bypasses saved layout registration")
mobile_path.write_text(mobile, encoding="utf-8")

result = subprocess.run([sys.executable, str(overlay), str(root)])
if result.returncode != 0:
    raise SystemExit(result.returncode)

print("Applied v0.17.9 safe-spawn plus independent Quick-Use overlay fixes.")
