#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

def read(rel):
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"Missing D2B.2D target: {p}")
    return p, p.read_text(encoding="utf-8")

def replace_once(rel, old, new):
    p, s = read(rel)
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"D2B.2D anchor missing in {rel}: {old[:140]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

replace_once(
    "scripts/art/weapon_visual.gd",
    'var static_attachments: Dictionary = {"laser":"", "light":"", "optic":"", "muzzle":""}\n',
    'var static_attachments: Dictionary = {"laser":"", "light":"", "optic":"", "muzzle":""}\nvar facing_direction := Vector2.RIGHT\nvar melee_time := 0.0\nconst MELEE_VISUAL_DURATION := 0.28\n',
)

replace_once(
    "scripts/art/weapon_visual.gd",
    '''func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    rotation = value.angle()
''',
    '''func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    facing_direction = value.normalized()
    _apply_pose()

func play_melee() -> void:
    if ItemDatabase.get_category(weapon_id) != "melee":
        return
    melee_time = MELEE_VISUAL_DURATION
    _apply_pose()

func _process(delta: float) -> void:
    if melee_time <= 0.0:
        return
    melee_time = maxf(0.0, melee_time - delta)
    _apply_pose()
    queue_redraw()

func _apply_pose() -> void:
    var angle := facing_direction.angle()
    if melee_time > 0.0 and ItemDatabase.get_category(weapon_id) == "melee":
        var progress := 1.0 - melee_time / MELEE_VISUAL_DURATION
        angle += lerpf(-0.78, 0.92, progress)
    rotation = angle
    scale.y = -absf(scale.y) if facing_direction.x < -0.02 else absf(scale.y)
''',
)

replace_once(
    "scripts/player.gd",
    '''    _weapon_visual.z_index = 2
    _weapon_visual.scale = Vector2(0.84, 0.84)
    add_child(_weapon_visual)
''',
    '''    _weapon_visual.z_index = 3
    _weapon_visual.scale = Vector2(0.60, 0.60)
    add_child(_weapon_visual)
''',
)

print("Applied v0.19.0D2B.2D correct left/right weapon mirroring, melee pose hook, and restrained player weapon scale.")
