#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")

changed = []


def replace_exact(rel: str, old: str, new: str, expected: int = 1) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{rel}: expected {expected} occurrence(s), found {count}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    changed.append(rel)


# Godot 4.7 introduced CanvasItem.draw_ellipse(). Wanderfall's older helper used the
# same name with a Vector2-radii signature, so rename only our custom calls/definitions.
for path in sorted((root / "scripts").rglob("*.gd")):
    text = path.read_text(encoding="utf-8")
    fixed, count = re.subn(r"(?<!_)draw_ellipse\(", "_draw_ellipse(", text)
    if count:
        path.write_text(fixed, encoding="utf-8")
        changed.append(str(path.relative_to(root)))

# Node.get_name() is native in Godot 4.7; avoid overriding it with a different signature.
replace_exact(
    "scripts/vehicles/vehicle_database.gd",
    "func get_name(vehicle_id: String) -> String:",
    "func get_vehicle_name(vehicle_id: String) -> String:",
)

# Godot 4.7 now exposes a native VirtualJoystick class. Keep Wanderfall's scripted
# joystick globally named, but make its class name project-specific.
replace_exact(
    "scripts/virtual_joystick.gd",
    "class_name VirtualJoystick",
    "class_name WanderfallVirtualJoystick",
)

# Godot 4.7 is stricter when := tries to infer a type from a dynamic/Variant expression.
replacements = {
    "scripts/player.gd": [
        ("        var offset := node.global_position - global_position", "        var offset: Vector2 = node.global_position - global_position"),
        ("        var distance := offset.length()", "        var distance: float = offset.length()"),
        ("        var dot := _facing.dot(offset / distance)", "        var dot: float = _facing.dot(offset / distance)"),
        ("        var score := distance * (2.0 - dot)", "        var score: float = distance * (2.0 - dot)"),
        ("        var optic_pos := lerp(weapon_start, weapon_end, 0.58) + _facing.orthogonal() * -3.0", "        var optic_pos: Vector2 = lerp(weapon_start, weapon_end, 0.58) + _facing.orthogonal() * -3.0"),
    ],
    "scripts/mobile_hud.gd": [
        ("    var s := player.survival_stats.get_snapshot()", "    var s: Dictionary = player.survival_stats.get_snapshot()"),
        ("    var selected := \"Unknown\" if settlement == null else settlement.get_build_type_name()", "    var selected: String = \"Unknown\" if settlement == null else String(settlement.get_build_type_name())"),
    ],
    "scripts/settlement/settlement_world_manager.gd": [
        ("    var type_id := build_types[build_index]", "    var type_id: String = String(build_types[build_index])", 2),
    ],
    "scripts/ecology/dog_companion.gd": [
        ("                var target_position := _player.global_position - _player.get_facing_direction() * 42.0 + Vector2(28, 18)", "                var target_position: Vector2 = _player.global_position - _player.get_facing_direction() * 42.0 + Vector2(28, 18)"),
        ("                var offset := target_position - global_position", "                var offset: Vector2 = target_position - global_position"),
    ],
    "scripts/settings/settings_hud.gd": [
        ("    var player := _player()", "    var player = _player()", 3),
        ("        var short := {\"health\":\"HP\",\"stamina\":\"STA\",\"hunger\":\"HUN\",\"thirst\":\"THR\",\"fatigue\":\"FAT\",\"encumbrance\":\"ENC\"}.get(key, key)", "        var short: String = String({\"health\":\"HP\",\"stamina\":\"STA\",\"hunger\":\"HUN\",\"thirst\":\"THR\",\"fatigue\":\"FAT\",\"encumbrance\":\"ENC\"}.get(key, key))"),
        ("    var enc := player.inventory.get_encumbrance_percent()", "    var enc: float = float(player.inventory.get_encumbrance_percent())"),
        ("    var remaining := player.inventory.add_item(item_id, quantity)", "    var remaining: int = int(player.inventory.add_item(item_id, quantity))"),
        ("    var added := quantity - remaining", "    var added: int = quantity - remaining"),
    ],
    "scripts/content/gear_hud.gd": [
        ("var _slots := [\"head\", \"eyes\", \"torso\", \"legs\", \"feet\", \"back\"]", "var _slots: Array[String] = [\"head\", \"eyes\", \"torso\", \"legs\", \"feet\", \"back\"]"),
    ],
}

for rel, items in replacements.items():
    for item in items:
        if len(item) == 2:
            old, new = item
            expected = 1
        else:
            old, new, expected = item
        replace_exact(rel, old, new, expected)

print(f"Applied Godot 4.7 compatibility fixes to {len(set(changed))} file(s).")
