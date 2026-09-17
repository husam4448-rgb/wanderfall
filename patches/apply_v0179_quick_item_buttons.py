#!/usr/bin/env python3
"""Compatibility entry point for the current Android Quick-Use test build.

Keeps safe spawn and BAG binding data, applies joystick polish, replaces the
old Quick renderer with the static scene, then applies responsive and v0.18.4
uniform-HUD / inventory-grid polish.
"""
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).resolve().parent
combined = patch_dir / "apply_v0179_quick_items_safe_spawn.py"
radial = patch_dir / "apply_v0180_radial_quick_menu.py"
polish = patch_dir / "apply_v0181_quick_radial_joystick.py"
static_scene = patch_dir / "apply_v0182_static_quick_scene.py"
ci_compat = patch_dir / "apply_v0182_ci_compat.py"
responsive_hud = patch_dir / "apply_v0183_responsive_hud.py"
uniform_inventory = patch_dir / "apply_v0184_uniform_hud_inventory_grid.py"

for step in (combined, radial, polish, static_scene, ci_compat, responsive_hud, uniform_inventory):
    if not step.is_file():
        raise SystemExit(f"Missing Quick-Use applicator: {step}")

result = subprocess.run([sys.executable, str(combined), str(root)])
if result.returncode != 0:
    raise SystemExit(result.returncode)

# v0.17.9 retired legacy hotbar assignment helpers/declarations. The BAG
# binding UI still reuses those names for Q1..Q6 assignment.
mobile_path = root / "scripts/mobile_hud.gd"
mobile = mobile_path.read_text(encoding="utf-8")

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

for step in (radial, polish, static_scene, ci_compat, responsive_hud, uniform_inventory):
    result = subprocess.run([sys.executable, str(step), str(root)])
    if result.returncode != 0:
        raise SystemExit(result.returncode)

print("Applied safe spawn + static Quick scene + v0.18.4 uniform HUD and inventory grid.")
