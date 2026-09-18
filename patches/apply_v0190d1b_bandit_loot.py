#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

def read(rel):
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"Missing D1b target: {p}")
    return p, p.read_text(encoding="utf-8")

def replace_once(rel, old, new):
    p, s = read(rel)
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"D1b anchor missing in {rel}: {old[:120]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

replace_once(
    "scripts/combat/hostile_actor.gd",
    "class_name HostileActor\nextends CharacterBody2D\n",
    'class_name HostileActor\nextends CharacterBody2D\n\nconst LootContainerScript = preload("res://scripts/items/loot_container.gd")\n',
)

replace_once(
    "scripts/combat/hostile_actor.gd",
    '''func _on_died(_source: Node) -> void:
    MissionManager.report_kill(faction_id, _source)
    remove_from_group("hostile_actor")
    set_physics_process(false)
    velocity = Vector2.ZERO
    queue_free()
''',
    '''func _on_died(_source: Node) -> void:
    MissionManager.report_kill(faction_id, _source)
    remove_from_group("hostile_actor")
    set_physics_process(false)
    velocity = Vector2.ZERO
    if faction_id == "bandit":
        _spawn_bandit_loot()
    queue_free()

func _spawn_bandit_loot() -> void:
    var parent := get_parent()
    if parent == null:
        return
    var drop := LootContainerScript.new()
    var px := int(round(global_position.x))
    var py := int(round(global_position.y))
    var seed_value := int(abs(float(px) * 92821.0 + float(py) * 68917.0)) & 0x7fffffff
    var drop_id := "bandit_drop_%d_%d_%d" % [px, py, get_instance_id()]
    drop.setup(drop_id, seed_value, "bandit", "Bandit Loot")
    parent.add_child(drop)
    drop.global_position = global_position
''',
)

replace_once(
    "scripts/items/world_state.gd",
    '''        "bunker_entrance": ["painkillers","trauma_dressing","ammo_9mm","ammo_556","pistol_9mm","rifle_556","laser_module","weapon_light","red_dot","combat_helmet","tactical_vest","night_vision_goggles","water_bottle","multitool"],
        "default":''',
    '''        "bunker_entrance": ["painkillers","trauma_dressing","ammo_9mm","ammo_556","pistol_9mm","rifle_556","laser_module","weapon_light","red_dot","combat_helmet","tactical_vest","night_vision_goggles","water_bottle","multitool"],
        "bandit": ["ammo_9mm","pistol_9mm","knife","bandage","painkillers","water_bottle","jerky","cloth","duct_tape","small_backpack","scrap_metal"],
        "default":''',
)

replace_once(
    "scripts/items/loot_container.gd",
    '''func _draw() -> void:
    var empty := is_empty()
    _draw_ellipse(Vector2(0, 10), Vector2(20, 8), Color(0.03, 0.04, 0.04, 0.28))
''',
    '''func _draw() -> void:
    var empty := is_empty()
    if loot_profile == "bandit":
        _draw_ellipse(Vector2(0, 9), Vector2(18, 7), Color(0.03, 0.04, 0.04, 0.28))
        draw_rect(Rect2(-14, -8, 28, 20), Color("4c4336") if empty else Color("6f5b43"), true)
        draw_rect(Rect2(-9, -13, 18, 7), Color("3d362e"), true)
        draw_line(Vector2(-10, -6), Vector2(10, 8), Color("9d835d"), 3.0)
        return
    _draw_ellipse(Vector2(0, 10), Vector2(20, 8), Color(0.03, 0.04, 0.04, 0.28))
''',
)

print("Applied v0.19.0D1b bandit death loot containers.")
