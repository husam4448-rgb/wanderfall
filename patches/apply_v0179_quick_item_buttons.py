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
combined = patch_dir / "apply_v0179_quick_items_safe_spawn.py"
radial = patch_dir / "apply_v0180_radial_quick_menu.py"

for step in (combined, radial):
    if not step.is_file():
        raise SystemExit(f"Missing Quick-Use applicator: {step}")

result = subprocess.run([sys.executable, str(combined), str(root)])
if result.returncode != 0:
    raise SystemExit(result.returncode)

# v0.17.9 retired legacy hotbar assignment helpers/declarations. The radial
# system deliberately reuses those names for BAG -> Q1..Q6 binding.
mobile_path = root / "scripts/mobile_hud.gd"
mobile = mobile_path.read_text(encoding="utf-8")

# Restore the three declarations removed by v0.17.9.
decl_anchor = "var inventory_use_button: Button\n"
if decl_anchor not in mobile:
    raise SystemExit("Inventory declaration anchor missing")
decls = ""
if "var inventory_quickslot_button: Button" not in mobile:
    decls += "var inventory_quickslot_button: Button\n"
if "var inventory_quickslot_clear_button: Button" not in mobile:
    decls += "var inventory_quickslot_clear_button: Button\n"
if "var _quickslot_assign_index :=" not in mobile:
    decls += "var _quickslot_assign_index := 0\n"
if decls:
    mobile = mobile.replace(decl_anchor, decl_anchor + decls, 1)

# Restore function anchors if v0.17.9 removed them.
func_anchor = "func _toggle_inventory() -> void:\n"
if func_anchor not in mobile:
    raise SystemExit("Inventory toggle anchor missing")
missing = []
if "func _next_quickslot_assign() -> void:" not in mobile:
    missing.append("func _next_quickslot_assign() -> void:\n    pass\n\n")
if "func _assign_selected_to_quickbar() -> void:" not in mobile:
    missing.append("func _assign_selected_to_quickbar() -> void:\n    pass\n\n")
if "func _clear_quickslot_assign() -> void:" not in mobile:
    missing.append("func _clear_quickslot_assign() -> void:\n    pass\n\n")
if missing:
    mobile = mobile.replace(func_anchor, "".join(missing) + func_anchor, 1)

mobile_path.write_text(mobile, encoding="utf-8")

result = subprocess.run([sys.executable, str(radial), str(root)])
if result.returncode != 0:
    raise SystemExit(result.returncode)

print("Applied safe spawn plus v0.18.0 permanent radial Quick menu.")
