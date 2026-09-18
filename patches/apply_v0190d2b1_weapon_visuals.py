#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

def read(rel):
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"Missing D2B1 target: {p}")
    return p, p.read_text(encoding="utf-8")

def replace_once(rel, old, new):
    p, s = read(rel)
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"D2B1 anchor missing in {rel}: {old[:140]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

weapon_visual = root / "scripts/art/weapon_visual.gd"
weapon_visual.parent.mkdir(parents=True, exist_ok=True)
weapon_visual.write_text(r'''class_name WeaponVisual
extends Node2D

var equipment: Node = null
var weapon_id := ""
var static_attachments: Dictionary = {"laser":"", "light":"", "optic":"", "muzzle":""}

func setup_equipment(equipment_value: Node) -> void:
    equipment = equipment_value
    refresh_weapon()

func setup_static(weapon_id_value: String, attachments_value: Dictionary = {}) -> void:
    equipment = null
    weapon_id = weapon_id_value
    static_attachments = {"laser":"", "light":"", "optic":"", "muzzle":""}
    for slot in static_attachments.keys():
        static_attachments[slot] = String(attachments_value.get(slot, ""))
    refresh_weapon()

func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    rotation = value.angle()

func refresh_weapon() -> void:
    if equipment != null and is_instance_valid(equipment):
        weapon_id = String(equipment.equipped_weapon_id)
    queue_redraw()

func _attachment(slot: String) -> String:
    if equipment != null and is_instance_valid(equipment):
        if equipment.has_attachment(slot):
            return String(equipment.attachments.get(slot, ""))
        return ""
    return String(static_attachments.get(slot, ""))

func get_muzzle_distance() -> float:
    var base := _base_muzzle_distance(weapon_id)
    var muzzle_id := _attachment("muzzle")
    if muzzle_id == "suppressor_9mm":
        base += 10.0
    elif muzzle_id == "rifle_suppressor":
        base += 14.0
    return base

func _base_muzzle_distance(id: String) -> float:
    match id:
        "pistol_9mm": return 26.0
        "revolver_357": return 29.0
        "smg_9mm": return 34.0
        "rifle_556": return 42.0
        "shotgun_12g": return 45.0
        "hunting_rifle": return 48.0
        "knife": return 24.0
        "hatchet": return 29.0
        "crowbar": return 33.0
        "machete": return 34.0
        "baseball_bat": return 36.0
        "sledgehammer": return 36.0
        "spear": return 46.0
        _: return 28.0

func _draw() -> void:
    if weapon_id.is_empty():
        return
    var c := ItemDatabase.get_world_color(weapon_id, Color("454c4e"))
    match weapon_id:
        "pistol_9mm": _draw_pistol(c)
        "revolver_357": _draw_revolver(c)
        "smg_9mm": _draw_smg(c)
        "rifle_556": _draw_carbine(c)
        "shotgun_12g": _draw_shotgun(c)
        "hunting_rifle": _draw_hunting_rifle(c)
        "knife": _draw_knife(c)
        "hatchet": _draw_hatchet(c)
        "crowbar": _draw_crowbar(c)
        "machete": _draw_machete(c)
        "baseball_bat": _draw_bat(c)
        "sledgehammer": _draw_sledge(c)
        "spear": _draw_spear(c)
        _: draw_line(Vector2(4,0), Vector2(_base_muzzle_distance(weapon_id),0), c, 4.0)
    if ItemDatabase.get_category(weapon_id) == "firearm":
        _draw_attachments()

func _draw_pistol(c: Color) -> void:
    draw_rect(Rect2(7,-3,17,6), c, true)
    draw_rect(Rect2(10,-5,13,2), c.lightened(0.12), true)
    draw_colored_polygon(PackedVector2Array([Vector2(11,3),Vector2(18,3),Vector2(15,14),Vector2(10,14)]), c.darkened(0.18))

func _draw_revolver(c: Color) -> void:
    draw_rect(Rect2(7,-3,20,5), c, true)
    draw_circle(Vector2(15,2), 5.0, c.lightened(0.08))
    draw_circle(Vector2(15,2), 2.2, c.darkened(0.22))
    draw_colored_polygon(PackedVector2Array([Vector2(10,5),Vector2(16,5),Vector2(14,15),Vector2(9,15)]), c.darkened(0.18))

func _draw_smg(c: Color) -> void:
    draw_rect(Rect2(5,-4,26,8), c, true)
    draw_rect(Rect2(1,-2,8,5), c.darkened(0.18), true)
    draw_colored_polygon(PackedVector2Array([Vector2(12,4),Vector2(18,4),Vector2(20,16),Vector2(13,16)]), c.darkened(0.10))
    draw_rect(Rect2(29,-2,5,4), c.darkened(0.12), true)

func _draw_carbine(c: Color) -> void:
    draw_colored_polygon(PackedVector2Array([Vector2(1,-3),Vector2(10,-5),Vector2(15,-3),Vector2(15,3),Vector2(6,5),Vector2(1,3)]), c.darkened(0.18))
    draw_rect(Rect2(12,-4,18,8), c, true)
    draw_colored_polygon(PackedVector2Array([Vector2(18,4),Vector2(24,4),Vector2(27,15),Vector2(20,15)]), c.darkened(0.10))
    draw_rect(Rect2(29,-2,13,4), c.darkened(0.05), true)

func _draw_shotgun(c: Color) -> void:
    var wood := Color("7b5a3d")
    draw_colored_polygon(PackedVector2Array([Vector2(0,-3),Vector2(12,-5),Vector2(18,-3),Vector2(17,3),Vector2(7,6),Vector2(0,4)]), wood)
    draw_rect(Rect2(15,-3,28,5), c, true)
    draw_rect(Rect2(23,3,14,4), wood.darkened(0.06), true)
    draw_line(Vector2(19,4), Vector2(43,4), c.darkened(0.18), 2.0)

func _draw_hunting_rifle(c: Color) -> void:
    var wood := Color("76563b")
    draw_colored_polygon(PackedVector2Array([Vector2(0,-3),Vector2(12,-6),Vector2(20,-3),Vector2(18,3),Vector2(7,7),Vector2(0,5)]), wood)
    draw_rect(Rect2(16,-3,13,6), c, true)
    draw_rect(Rect2(28,-1.8,20,3.6), c.darkened(0.05), true)
    draw_line(Vector2(20,3), Vector2(24,10), wood.darkened(0.15), 4.0)

func _draw_knife(c: Color) -> void:
    draw_rect(Rect2(4,-3,8,6), Color("4b3d31"), true)
    draw_colored_polygon(PackedVector2Array([Vector2(12,-2.2),Vector2(24,0),Vector2(12,2.2)]), c.lightened(0.16))

func _draw_hatchet(c: Color) -> void:
    draw_line(Vector2(4,0), Vector2(27,0), Color("76563b"), 5.0)
    draw_colored_polygon(PackedVector2Array([Vector2(22,-8),Vector2(30,-6),Vector2(30,6),Vector2(22,8),Vector2(20,0)]), c.lightened(0.08))

func _draw_crowbar(c: Color) -> void:
    draw_line(Vector2(4,3), Vector2(31,-2), c, 4.0)
    draw_arc(Vector2(31,-5), 4.0, 0.0, PI * 0.65, 8, c, 3.0)

func _draw_machete(c: Color) -> void:
    draw_rect(Rect2(3,-3,9,6), Color("4d3d30"), true)
    draw_colored_polygon(PackedVector2Array([Vector2(12,-3),Vector2(33,-2),Vector2(35,1),Vector2(28,5),Vector2(12,3)]), c.lightened(0.10))

func _draw_bat(c: Color) -> void:
    draw_line(Vector2(5,0), Vector2(34,0), c, 6.0)
    draw_line(Vector2(5,0), Vector2(12,0), c.darkened(0.18), 3.0)

func _draw_sledge(c: Color) -> void:
    draw_line(Vector2(4,0), Vector2(31,0), Color("785a3b"), 5.0)
    draw_rect(Rect2(27,-8,10,16), c, true)

func _draw_spear(c: Color) -> void:
    draw_line(Vector2(3,0), Vector2(40,0), Color("806343"), 3.5)
    draw_colored_polygon(PackedVector2Array([Vector2(40,-4),Vector2(47,0),Vector2(40,4)]), c.lightened(0.12))

func _draw_attachments() -> void:
    var optic := _attachment("optic")
    var light := _attachment("light")
    var laser := _attachment("laser")
    var muzzle := _attachment("muzzle")
    var base_muzzle := _base_muzzle_distance(weapon_id)

    if optic == "red_dot":
        draw_rect(Rect2(18,-8,9,4), Color("4e4540"), true)
        draw_circle(Vector2(23,-8), 1.4, Color("b54c45"))
    elif optic == "scope_4x":
        draw_rect(Rect2(16,-10,16,5), Color("424a49"), true)
        draw_circle(Vector2(16,-7.5), 3.4, Color("596564"))
        draw_circle(Vector2(32,-7.5), 3.8, Color("596564"))

    if light == "weapon_light":
        draw_rect(Rect2(17,5,10,4), Color("676b62"), true)
        draw_circle(Vector2(27,7), 2.0, Color("e0ce77"))

    if laser == "laser_module":
        draw_rect(Rect2(14,5,8,3), Color("593c3d"), true)
        draw_circle(Vector2(22,6.5), 1.3, Color("d14949"))

    if muzzle == "suppressor_9mm":
        draw_rect(Rect2(base_muzzle,-3.2,10,6.4), Color("34383a"), true)
        draw_line(Vector2(base_muzzle+2,-3.2), Vector2(base_muzzle+2,3.2), Color("555b5d"), 1.0)
    elif muzzle == "rifle_suppressor":
        draw_rect(Rect2(base_muzzle,-3.7,14,7.4), Color("3b4140"), true)
        draw_line(Vector2(base_muzzle+3,-3.7), Vector2(base_muzzle+3,3.7), Color("59615f"), 1.0)
''', encoding="utf-8")

replace_once(
    "scripts/player.gd",
    'const LayeredActorVisualScript = preload("res://scripts/art/layered_actor_visual.gd")\n',
    'const LayeredActorVisualScript = preload("res://scripts/art/layered_actor_visual.gd")\nconst WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")\n',
)
replace_once(
    "scripts/player.gd",
    'var _actor_visual: LayeredActorVisual = null\n',
    'var _actor_visual: LayeredActorVisual = null\nvar _weapon_visual: Node2D = null\n',
)
replace_once(
    "scripts/player.gd",
    '''    _actor_visual.setup_equipment(equipment, body_type, "player")
    equipment.apparel_changed.connect(_refresh_actor_visual)
    equipment.transmog_changed.connect(_refresh_actor_visual)
    queue_redraw()
''',
    '''    _actor_visual.setup_equipment(equipment, body_type, "player")
    equipment.apparel_changed.connect(_refresh_actor_visual)
    equipment.transmog_changed.connect(_refresh_actor_visual)
    _weapon_visual = WeaponVisualScript.new()
    _weapon_visual.z_index = 2
    _weapon_visual.scale = Vector2(0.84, 0.84)
    add_child(_weapon_visual)
    _weapon_visual.setup_equipment(equipment)
    equipment.weapon_changed.connect(func(_id: String): _refresh_weapon_visual())
    equipment.attachments_changed.connect(_refresh_weapon_visual)
    queue_redraw()
''',
)
replace_once(
    "scripts/player.gd",
    '''func _update_actor_visual() -> void:
    if _actor_visual == null:
        return
    _actor_visual.visible = current_vehicle == null or not is_instance_valid(current_vehicle)
    _actor_visual.set_facing(_facing)
''',
    '''func _refresh_weapon_visual() -> void:
    if _weapon_visual != null:
        _weapon_visual.refresh_weapon()
    queue_redraw()

func _update_actor_visual() -> void:
    var show_actor := current_vehicle == null or not is_instance_valid(current_vehicle)
    if _actor_visual != null:
        _actor_visual.visible = show_actor
        _actor_visual.set_facing(_facing)
    if _weapon_visual != null:
        _weapon_visual.visible = show_actor
        _weapon_visual.set_facing(_facing)
''',
)

old_draw = '''    # D2A keeps the existing weapon placeholder in the foreground. D2B replaces this
    # with exact per-weapon sprites and attachment overlays without touching body layers.
    var firearm := equipment != null and equipment.get_weapon_category() == "firearm"
    var weapon_length := 30.0 if firearm else 23.0
    var weapon_start := _facing * 5.0
    var weapon_end := _facing * weapon_length
    var weapon_color := ItemDatabase.get_world_color(equipment.equipped_weapon_id, Color("2b2f34")) if equipment != null else Color("2b2f34")
    draw_line(weapon_start, weapon_end, weapon_color.darkened(0.15), 5.0)
    draw_circle(weapon_end, 2.2, Color("d8b04c"))
    if firearm and equipment.has_attachment("optic"):
        var optic_pos: Vector2 = lerp(weapon_start, weapon_end, 0.58) + _facing.orthogonal() * -3.0
        draw_rect(Rect2(optic_pos - Vector2(3,2), Vector2(6,4)), Color("4d5552"), true)
    if firearm and equipment.has_attachment("muzzle"):
        draw_line(weapon_end, weapon_end + _facing * 9.0, Color("353b3b"), 5.0)
        weapon_end += _facing * 9.0
    if PerformanceManager.get_effects_density() >= 0.45 and firearm and equipment.has_attachment("laser"):
        draw_line(weapon_end, weapon_end + _facing * 92.0, Color(0.92, 0.16, 0.17, 0.62), 1.5)
    if not GameSettings.reduced_flashes and PerformanceManager.get_effects_density() >= 0.45 and _muzzle_flash_timer > 0.0:
        draw_circle(weapon_end + _facing * 4.0, 5.5, Color(1.0, 0.75, 0.24, 0.92))
'''
new_draw = '''    var firearm := equipment != null and equipment.get_weapon_category() == "firearm"
    var muzzle_distance := 30.0
    if _weapon_visual != null and _weapon_visual.has_method("get_muzzle_distance"):
        muzzle_distance = float(_weapon_visual.get_muzzle_distance()) * absf(_weapon_visual.scale.x)
    var weapon_end := _facing * muzzle_distance
    if PerformanceManager.get_effects_density() >= 0.45 and firearm and equipment.has_attachment("laser"):
        draw_line(weapon_end, weapon_end + _facing * 92.0, Color(0.92, 0.16, 0.17, 0.62), 1.5)
    if not GameSettings.reduced_flashes and PerformanceManager.get_effects_density() >= 0.45 and _muzzle_flash_timer > 0.0:
        draw_circle(weapon_end + _facing * 4.0, 5.5, Color(1.0, 0.75, 0.24, 0.92))
'''
replace_once("scripts/player.gd", old_draw, new_draw)

print("Applied v0.19.0D2B1 exact player weapon and attachment visual renderer.")
