#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo_root=Path(__file__).resolve().parents[1]
old=(repo_root/"patches/apply_v0190d2b10_pure_sprite_skeleton.py").read_text(encoding="utf-8")
m=re.search(r"visual_path\.write_text\(r'''(.*?)''', encoding=\"utf-8\"\)",old,re.S)
if not m:
    raise SystemExit("D2D.6 could not extract D2B.10 renderer")
src=m.group(1)

src=src.replace("class_name ProductionSurvivorVisual","class_name BakedActorVisual",1)
src=src.replace("res://assets/art/characters/hybrid_male_head.png","res://assets/authored2d/parts/head.png")
src=src.replace("res://assets/art/characters/hybrid_male_torso.png","res://assets/authored2d/parts/torso.png")
src=src.replace("res://assets/art/characters/hybrid_male_upper_arm.png","res://assets/authored2d/parts/upper_arm.png")
src=src.replace("res://assets/art/characters/hybrid_male_forearm_hand.png","res://assets/authored2d/parts/forearm_hand.png")
src=src.replace("res://assets/art/characters/hybrid_male_thigh.png","res://assets/authored2d/parts/thigh.png")
src=src.replace("res://assets/art/characters/hybrid_male_shin_foot.png","res://assets/authored2d/parts/shin_foot.png")

# Add current gear textures and overlay nodes.
src=src.replace(
'const MELEE_DURATION := 0.30',
'''const MELEE_DURATION := 0.30
const GEAR_BACK := preload("res://assets/authored2d/gear/backpack.png")
const GEAR_VEST := preload("res://assets/authored2d/gear/vest.png")
const GEAR_HEAD := preload("res://assets/authored2d/gear/headgear.png")''',1)
src=src.replace(
'var _last_rw := Vector2.ZERO',
'''var _last_rw := Vector2.ZERO
var gear_back: Sprite2D
var gear_vest: Sprite2D
var gear_head: Sprite2D
var _static_role := "player"''',1)

# BakedActorVisual compatibility for NPC/static setup.
src=src.replace(
'func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:',
'''func setup(set_name_value: String) -> void:
    _static_role = "bandit" if "bandit" in set_name_value else "player"
    _ensure_nodes()
    _apply_pose()

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:''',1)

# Create gear sprites as additional skins; they never define skeleton joints.
needle='''    l_shin.flip_h = true
'''
insert='''    l_shin.flip_h = true

    gear_back = _sprite(GEAR_BACK, -8)
    gear_vest = _sprite(GEAR_VEST, 1)
    gear_head = _sprite(GEAR_HEAD, 6)
'''
src=src.replace(needle,insert,1)

# Gear slot helpers and real refresh.
src=src.replace(
'''func refresh_gear() -> void:
    _apply_pose()
''',
'''func _gear(slot: String) -> String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item"):
        return String(equipment.call("get_visual_item", slot))
    if _static_role == "bandit":
        match slot:
            "armor": return "tactical_vest"
            "back": return "small_backpack"
            "head": return "wool_beanie"
    return ""

func _refresh_gear_visuals() -> void:
    if gear_back == null:
        return
    gear_back.visible = not _gear("back").is_empty()
    gear_vest.visible = not _gear("armor").is_empty()
    gear_head.visible = not _gear("head").is_empty()

func refresh_gear() -> void:
    _refresh_gear_visuals()
    _apply_pose()
''',1)

# Follow torso/head sockets; no independent gear skeleton.
pose_tail='''    _apply_layering(side, backness)
'''
pose_new='''    _apply_layering(side, backness)

    _refresh_gear_visuals()
    gear_vest.position = torso.position
    gear_vest.rotation = torso.rotation
    gear_vest.scale = torso.scale * Vector2(1.10, 1.04)
    gear_back.position = torso.position + Vector2(0.0, 1.5)
    gear_back.rotation = torso.rotation
    gear_back.scale = torso.scale * Vector2(1.16, 1.16)
    gear_back.z_index = 5 if backness > 0.55 else -8
    gear_head.position = head.position + Vector2(0.0, -1.2)
    gear_head.rotation = head.rotation
    gear_head.scale = Vector2(absf(head.scale.x) * 1.08, head.scale.y * 1.05)
'''
src=src.replace(pose_tail,pose_new,1)

(root/"scripts/art/baked_actor_visual.gd").write_text(src,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
h=h.replace('marker.text = "D2D.5.1  |  SOUTH + GEAR"','marker.text = "D2D.6  |  OLD SKELETON + SPRITES"',1)
hud.write_text(h,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e=re.sub(r'(?m)^version/code=\d+$','version/code=77',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.6"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.6"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("Applied D2D.6 using the original D2B.10 sprite-skinned skeleton plus current gear skins.")
