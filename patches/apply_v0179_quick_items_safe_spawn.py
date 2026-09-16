#!/usr/bin/env python3
from pathlib import Path
import base64
import hashlib
import lzma
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
payload_path = Path(__file__).resolve().parent / "v0179_changes.diff.xz.b64"
expected_sha256 = "47e4962aad2c741e5d25d7472f1639e60cc1e00b7deeac4861841ad4945a27a2"

if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")
if not payload_path.is_file():
    raise SystemExit(f"Missing v0.17.9 patch payload: {payload_path}")

encoded = payload_path.read_text(encoding="utf-8").strip()
compressed = base64.b64decode(encoded, validate=True)
actual_sha256 = hashlib.sha256(compressed).hexdigest()
if actual_sha256 != expected_sha256:
    raise SystemExit(f"v0.17.9 payload checksum mismatch: {actual_sha256}")

diff_bytes = lzma.decompress(compressed)
diff_path = Path("/tmp/wanderfall-v0179.diff")
diff_path.write_bytes(diff_bytes)

# The diff was generated between exact reconstructed v0.17.8 and the verified
# v0.17.9 working copy. -p1 strips wfinspect/ or wfwork/ and targets root.
result = subprocess.run(
    ["patch", "-p1", "--batch", "--forward", "-d", str(root), "-i", str(diff_path)],
    text=True,
    capture_output=True,
)
if result.returncode != 0:
    sys.stderr.write(result.stdout)
    sys.stderr.write(result.stderr)
    raise SystemExit(f"v0.17.9 patch failed with exit code {result.returncode}")

# Strong assertions for the user-facing changes.
mobile = (root / "scripts/mobile_hud.gd").read_text(encoding="utf-8")
settings = (root / "scripts/settings/game_settings.gd").read_text(encoding="utf-8")
main = (root / "scripts/main.gd").read_text(encoding="utf-8")
menu = (root / "scripts/ui/main_menu.gd").read_text(encoding="utf-8")
export = (root / "export_presets.cfg").read_text(encoding="utf-8")

required_mobile = [
    'inventory_promote_button = _make_small_button("ADD QUICK BUTTON")',
    "func _rebuild_quick_item_buttons() -> void:",
    "func _activate_quick_item(item_id: String) -> void:",
    'UIManager.register_layout_control(button, "quick_item_" + item_id, true)',
    "ItemDatabase.get_icon_path(item_id)",
]
for needle in required_mobile:
    if needle not in mobile:
        raise SystemExit(f"v0.17.9 mobile assertion missing: {needle}")
if "_build_quickbar()" in mobile.split("func _build_ui() -> void:", 1)[1].split("func _build_status_panel()", 1)[0]:
    raise SystemExit("v0.17.9 still constructs the retired fixed hotbar")

if 'var quick_item_ids: Array[String] = []' not in settings or 'const MAX_QUICK_ITEMS := 12' not in settings:
    raise SystemExit("v0.17.9 quick item persistence assertions failed")
if "func start_new_game_safe_camp() -> void:" not in main or "START_SAFE_RADIUS" not in main:
    raise SystemExit("v0.17.9 safe spawn assertions failed")
if "start_new_game_safe_camp" not in menu:
    raise SystemExit("v0.17.9 main menu safe-spawn call missing")
if 'version/code=26' not in export or 'version/name="0.17.9"' not in export:
    raise SystemExit("v0.17.9 Android version assertions failed")

print("Applied Wanderfall v0.17.9: free-form quick item buttons, safe-camp new-game spawn, and compact control editor startup.")
