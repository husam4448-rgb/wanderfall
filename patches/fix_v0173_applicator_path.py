#!/usr/bin/env python3
from pathlib import Path

patch_dir = Path(__file__).resolve().parent

# Historical v0.17.3 cwd-safe patch fix.
path = patch_dir / "apply_v0173_touch_layout_fixes.py"
text = path.read_text(encoding="utf-8")
old = 'subprocess.run(["patch", "-p1", "-i", str(patch_path)], cwd=root, check=True)'
new = 'subprocess.run(["patch", "-p1", "-i", str(patch_path.resolve())], cwd=root, check=True)'
count = text.count(old)
if count == 1:
    path.write_text(text.replace(old, new), encoding="utf-8")
elif new in text:
    pass
else:
    raise SystemExit("Unexpected v0.17.3 applicator shape; refusing an unsafe rewrite")

# v0.17.9 compatibility: the reconstructed HUD uses the final function names
# _clear_quickslot_assign() and _toggle_inventory(). Normalize the applicator
# before it executes, then append the seven-slot BAG selector correction.
v179 = patch_dir / "apply_v0179_android_hotbar_replacement.py"
if v179.is_file():
    s = v179.read_text(encoding="utf-8")
    s = s.replace("_clear_selected_quickbar_slot", "_clear_quickslot_assign")
    s = s.replace("_cycle_quickslot_assign", "_toggle_inventory")
    slot7_marker = "# v0.17.9 slot-7 BAG selector correction"
    if slot7_marker not in s:
        s += '''\n\n# v0.17.9 slot-7 BAG selector correction\nreplace_once(\n    "scripts/mobile_hud.gd",\n    "    _quickslot_assign_index = (_quickslot_assign_index + 1) % 6",\n    "    _quickslot_assign_index = (_quickslot_assign_index + 1) % 7",\n)\n'''
    v179.write_text(s, encoding="utf-8")

print("Prepared v0.17.3 applicator and normalized v0.17.9 hotbar anchors.")
