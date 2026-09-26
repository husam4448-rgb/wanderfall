#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo_root=Path(__file__).resolve().parents[1]

core=(repo_root/"patches/apply_v0190d2b2a_articulated_actor_core.py").read_text(encoding="utf-8")
gear=(repo_root/"patches/apply_v0190d2b2b_articulated_gear.py").read_text(encoding="utf-8")

m=re.search(r"p\.write_text\(r'''(.*?)''', encoding=\"utf-8\"\)",core,re.S)
if not m:
    raise SystemExit("D2D.7 could not extract D2B.2A renderer")
src=m.group(1).replace("class_name LayeredActorVisual","class_name BakedActorVisual",1)

gm=re.search(r"helpers = r'''(.*?)'''\n",gear,re.S)
if not gm:
    raise SystemExit("D2D.7 could not extract D2B.2B gear helpers")
helpers=gm.group(1)
src=src.replace("# __D2B2_GEAR_HELPERS__",helpers,1)

# Current BakedActorVisual compatibility.
src=src.replace(
'var melee_direction := Vector2.RIGHT',
'''var melee_direction := Vector2.RIGHT
var _last_lw := Vector2.ZERO
var _last_rw := Vector2.ZERO
var _weapon_id_cache := ""''',1)

src=src.replace(
'func setup_equipment(equipment_value: Node, body_type_value: String = "male", role_value: String = "player") -> void:',
'''func setup(set_name_value: String) -> void:
    var r := "bandit" if "bandit" in set_name_value else "player"
    var g := {}
    if r == "bandit":
        g = {
            "torso":"field_jacket",
            "armor":"tactical_vest",
            "hands":"work_gloves",
            "legs":"cargo_pants",
            "feet":"combat_boots",
            "head":"wool_beanie",
            "back":"small_backpack"
        }
    setup_static("male", r, g)

func setup_equipment(equipment_value: Node, body_type_value: String = "male", role_value: String = "player") -> void:''',1)

# Persist hand anchors and draw weapon directly on skeleton.
old='''    var arm_pose := _arm_pose(l_shoulder, r_shoulder, body_bob)
'''
new='''    var arm_pose := _arm_pose(l_shoulder, r_shoulder, body_bob)
    _last_lw = arm_pose[1]
    _last_rw = arm_pose[3]
'''
src=src.replace(old,new,1)

call='''    _draw_glove_detail(hands_id, arm_pose[1], arm_pose[3], glove_color)

    # Armor overlays torso and straps while retaining the underlying anatomy.
'''
repl='''    _draw_glove_detail(hands_id, arm_pose[1], arm_pose[3], glove_color)
    _draw_skeleton_weapon(arm_pose[1], arm_pose[3], outline)

    # Armor overlays torso and straps while retaining the underlying anatomy.
'''
src=src.replace(call,repl,1)

# Extra current weapon helpers.
src += r'''

func _weapon_id() -> String:
    if equipment == null or not is_instance_valid(equipment):
        return "pistol_9mm" if role == "bandit" else ""
    if equipment.has_method("get_visual_item"):
        for slot in ["weapon","primary","secondary"]:
            var w := String(equipment.call("get_visual_item",slot))
            if not w.is_empty():
                return w
    for prop in ["equipped_weapon_id","weapon_id","active_weapon_id"]:
        var v = equipment.get(prop)
        if v != null and String(v) != "":
            return String(v)
    return ""

func _draw_skeleton_weapon(lw: Vector2, rw: Vector2, outline: Color) -> void:
    if _weapon_category() != "firearm":
        return
    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var wid := _weapon_id().to_lower()
    var rifle := ("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)
    var grip := rw
    var muzzle := grip + aim * (15.5 if rifle else 8.5)
    draw_line(grip,muzzle,outline,4.2 if rifle else 3.4,true)
    draw_line(grip,muzzle,Color("35393a"),2.6 if rifle else 2.1,true)
    var perp := Vector2(-aim.y,aim.x)
    draw_line(grip-perp*0.4,grip-aim*1.2+perp*2.8,Color("4b4036"),2.2,true)
    if rifle:
        draw_line(grip-aim*2.0,grip-aim*6.0,Color("4a4037"),3.5,true)
        draw_line(lw,grip+aim*3.0,Color("2d3030"),1.4,true)

func get_weapon_anchor() -> Dictionary:
    return {"grip":_last_rw,"support":_last_lw,"back_view":facing.y < -0.50}
'''

(root/"scripts/art/baked_actor_visual.gd").write_text(src,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
h=h.replace('marker.text = "D2D.6  |  OLD SKELETON + SPRITES"','marker.text = "D2D.7  |  DRAWN SKELETON"',1)
hud.write_text(h,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e=re.sub(r'(?m)^version/code=\d+$','version/code=78',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.7"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.7"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("Applied D2D.7 procedural drawn skeleton: no body-part sprite rendering.")
