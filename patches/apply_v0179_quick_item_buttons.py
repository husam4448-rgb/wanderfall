#!/usr/bin/env python3
"""Compatibility entry point for the current Android Quick-Use test build."""
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
dual_stick = patch_dir / "apply_v0185_dual_stick_combat.py"
qol_world = patch_dir / "apply_v0186_qol_world_spacing.py"
vehicle_controls = patch_dir / "apply_v0187a_character_vehicle_controls.py"
vehicle_qol = patch_dir / "apply_v0187a2_vehicle_qol_fix.py"
vehicle_a3 = patch_dir / "apply_v0187a3_vehicle_sensitivity_quick_melee.py"
control_editor_a4 = patch_dir / "apply_v0187a4_control_editor_stability.py"
storage_b = patch_dir / "apply_v0187b_storage_windows.py"
storage_b2 = patch_dir / "apply_v0187b2_storage_grid_interaction.py"
universal_c = patch_dir / "apply_v0187c_universal_windows.py"
universal_c2 = patch_dir / "apply_v0187c2_window_touch_scroll.py"
universal_c3 = patch_dir / "apply_v0187c3_inventory_gestures_hud_bounds.py"
art_foundation = patch_dir / "apply_v0190a_survival_paradise_art_foundation.py"
terrain_props = patch_dir / "apply_v0190b_terrain_props.py"
grass_density = patch_dir / "apply_v0190b1_grass_density.py"
structures_interiors = patch_dir / "apply_v0190c_structures_interiors.py"
structures_parser_fix = patch_dir / "apply_v0190c_parser_fix.py"
world_coherence_c1 = patch_dir / "apply_v0190c1_world_coherence.py"
hud_natural_water_c2 = patch_dir / "apply_v0190c2_hud_natural_water.py"
world_density_c3 = patch_dir / "apply_v0190c3_world_density.py"

steps = (combined, radial, polish, static_scene, ci_compat, responsive_hud, uniform_inventory, dual_stick, qol_world, vehicle_controls, vehicle_qol, vehicle_a3, control_editor_a4, storage_b, storage_b2, universal_c, universal_c2, universal_c3, art_foundation, terrain_props, grass_density, structures_interiors, structures_parser_fix, world_coherence_c1, hud_natural_water_c2, world_density_c3)
for step in steps:
    if not step.is_file():
        raise SystemExit(f"Missing Quick-Use applicator: {step}")

result = subprocess.run([sys.executable, str(combined), str(root)])
if result.returncode != 0:
    raise SystemExit(result.returncode)

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

for step in steps[1:]:
    result = subprocess.run([sys.executable, str(step), str(root)])
    if result.returncode != 0:
        raise SystemExit(result.returncode)

print("Applied through v0.19.0C3 Survival Paradise world density, lake visibility, wilderness resources, and structure/door coherence.")
