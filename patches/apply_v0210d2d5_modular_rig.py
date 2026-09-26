#!/usr/bin/env python3
"""D2D.5: modular articulated 2D paper-doll rig using authored RGBA body parts."""
from pathlib import Path
import base64,re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo_root=Path(__file__).resolve().parents[1]
src_dir=repo_root/"art_source/characters"
out_dir=root/"assets/authored2d/parts"
out_dir.mkdir(parents=True,exist_ok=True)

parts={
 "head":"hybrid_male_head.b64",
 "torso":"hybrid_male_torso.b64",
 "upper_arm":"hybrid_male_upper_arm.b64",
 "forearm_hand":"hybrid_male_forearm_hand.b64",
 "thigh":"hybrid_male_thigh.b64",
 "shin_foot":"hybrid_male_shin_foot.b64",
}
for name,fn in parts.items():
    src=src_dir/fn
    if not src.is_file():
        raise SystemExit(f"D2D.5 missing modular source {src}")
    data=base64.b64decode(src.read_text(encoding="utf-8").strip())
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"D2D.5 invalid PNG source {src}")
    (out_dir/f"{name}.png").write_bytes(data)

baked=root/"scripts/art/baked_actor_visual.gd"
baked.write_text(r'''class_name BakedActorVisual
extends Node2D

# D2D.5 is a real articulated 2D paper-doll rig. No full-body baked frames.

var set_name := "player_male"
var facing := Vector2.DOWN
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var equipment: Node = null
var role := "player"
var gait_phase := 0.0
var breathe_phase := 0.0
var gear_poll := 0.0

const SCALE := 0.58
const TEX_HEAD := preload("res://assets/authored2d/parts/head.png")
const TEX_TORSO := preload("res://assets/authored2d/parts/torso.png")
const TEX_UPPER_ARM := preload("res://assets/authored2d/parts/upper_arm.png")
const TEX_FOREARM := preload("res://assets/authored2d/parts/forearm_hand.png")
const TEX_THIGH := preload("res://assets/authored2d/parts/thigh.png")
const TEX_SHIN := preload("res://assets/authored2d/parts/shin_foot.png")

var torso: Sprite2D
var head: Sprite2D
var l_upper: Sprite2D
var r_upper: Sprite2D
var l_fore: Sprite2D
var r_fore: Sprite2D
var l_thigh: Sprite2D
var r_thigh: Sprite2D
var l_shin: Sprite2D
var r_shin: Sprite2D

var l_shoulder := Node2D.new()
var r_shoulder := Node2D.new()
var l_elbow := Node2D.new()
var r_elbow := Node2D.new()
var l_hip := Node2D.new()
var r_hip := Node2D.new()
var l_knee := Node2D.new()
var r_knee := Node2D.new()

var backpack := Polygon2D.new()
var armor := Polygon2D.new()
var headgear := Polygon2D.new()
var weapon_body := Polygon2D.new()
var weapon_barrel := Line2D.new()
var weapon_grip := Line2D.new()

var _weapon_visible := false
var _weapon_kind := "pistol"
var _last_gear_key := ""

func _ready() -> void:
    set_process(true)

func _sprite(tex: Texture2D, z: int) -> Sprite2D:
    var s := Sprite2D.new()
    s.texture = tex
    s.centered = true
    s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    s.scale = Vector2(SCALE,SCALE)
    s.z_index = z
    return s

func _build_rig() -> void:
    if torso != null:
        return

    backpack.z_index = -10
    add_child(backpack)

    l_hip.position = Vector2(-3.0,5.0)
    r_hip.position = Vector2(3.0,5.0)
    add_child(l_hip); add_child(r_hip)

    l_thigh = _sprite(TEX_THIGH,0)
    r_thigh = _sprite(TEX_THIGH,1)
    l_thigh.position = Vector2(0,8.3)
    r_thigh.position = Vector2(0,8.3)
    l_hip.add_child(l_thigh); r_hip.add_child(r_thigh)

    l_knee.position = Vector2(0,16.4)
    r_knee.position = Vector2(0,16.4)
    l_hip.add_child(l_knee); r_hip.add_child(r_knee)

    l_shin = _sprite(TEX_SHIN,0)
    r_shin = _sprite(TEX_SHIN,1)
    l_shin.position = Vector2(0,9.7)
    r_shin.position = Vector2(0,9.7)
    l_knee.add_child(l_shin); r_knee.add_child(r_shin)

    torso = _sprite(TEX_TORSO,5)
    torso.position = Vector2(0,-6.0)
    add_child(torso)

    armor.z_index = 6
    add_child(armor)

    l_shoulder.position = Vector2(-7.0,-11.0)
    r_shoulder.position = Vector2(7.0,-11.0)
    add_child(l_shoulder); add_child(r_shoulder)

    l_upper = _sprite(TEX_UPPER_ARM,7)
    r_upper = _sprite(TEX_UPPER_ARM,8)
    l_upper.position = Vector2(0,7.8)
    r_upper.position = Vector2(0,7.8)
    l_upper.scale.x *= -1.0
    l_shoulder.add_child(l_upper); r_shoulder.add_child(r_upper)

    l_elbow.position = Vector2(0,15.2)
    r_elbow.position = Vector2(0,15.2)
    l_shoulder.add_child(l_elbow); r_shoulder.add_child(r_elbow)

    l_fore = _sprite(TEX_FOREARM,9)
    r_fore = _sprite(TEX_FOREARM,10)
    l_fore.position = Vector2(0,8.5)
    r_fore.position = Vector2(0,8.5)
    l_fore.scale.x *= -1.0
    l_elbow.add_child(l_fore); r_elbow.add_child(r_fore)

    head = _sprite(TEX_HEAD,12)
    head.position = Vector2(0,-25.0)
    add_child(head)

    headgear.z_index = 13
    add_child(headgear)

    weapon_body.z_index = 20
    weapon_barrel.z_index = 21
    weapon_barrel.width = 1.8
    weapon_barrel.default_color = Color("22272b")
    weapon_grip.z_index = 21
    weapon_grip.width = 2.2
    weapon_grip.default_color = Color("29231f")
    add_child(weapon_body)
    add_child(weapon_barrel)
    add_child(weapon_grip)

    _refresh_gear(true)
    _apply_pose()

func setup(set_name_value: String) -> void:
    set_name = set_name_value
    role = "bandit" if "bandit" in set_name_value else "player"
    _build_rig()
    _refresh_gear(true)

func setup_equipment(equipment_value: Node, _body_type_value: String = "male") -> void:
    equipment = equipment_value
    role = "player"
    set_name = "player_male"
    _build_rig()
    _refresh_gear(true)

func set_body_type(_value: String) -> void:
    pass

func set_facing(value: Vector2) -> void:
    if value.length_squared() > 0.0001:
        facing = value.normalized()
    _apply_pose()

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value

func play_melee(_direction: Vector2 = Vector2.ZERO) -> void:
    pass

func _visual_item(slot: String) -> String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item"):
        return String(equipment.call("get_visual_item",slot))
    if role == "bandit":
        match slot:
            "armor": return "tactical_vest"
            "back": return "small_backpack"
            "head": return "wool_beanie"
            "torso": return "field_jacket"
            "legs": return "cargo_pants"
            "feet": return "combat_boots"
    return ""

func _weapon_category() -> String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_weapon_category"):
        return String(equipment.call("get_weapon_category"))
    return "firearm" if role == "bandit" else ""

func _weapon_id() -> String:
    if equipment == null or not is_instance_valid(equipment):
        return "pistol_9mm" if role == "bandit" else ""
    for method_name in ["get_equipped_weapon_id","get_weapon_id","get_active_weapon_id"]:
        if equipment.has_method(method_name):
            var v = equipment.call(method_name)
            if v != null:
                return String(v)
    for prop_name in ["equipped_weapon_id","weapon_id","active_weapon_id"]:
        var v = equipment.get(prop_name)
        if v != null and String(v) != "":
            return String(v)
    return ""

func _gear_key() -> String:
    return "|".join([
        _visual_item("torso"),_visual_item("armor"),_visual_item("back"),
        _visual_item("head"),_visual_item("hands"),_visual_item("legs"),
        _visual_item("feet"),_weapon_category(),_weapon_id()
    ])

func refresh_gear() -> void:
    _refresh_gear(false)

func _refresh_gear(force: bool) -> void:
    if torso == null:
        return
    var key := _gear_key()
    if not force and key == _last_gear_key:
        return
    _last_gear_key = key

    var torso_item := _visual_item("torso")
    var legs_item := _visual_item("legs")
    var feet_item := _visual_item("feet")
    var hands_item := _visual_item("hands")

    torso.modulate = Color("677469") if torso_item != "" else Color("d3a07b")
    l_upper.modulate = torso.modulate
    r_upper.modulate = torso.modulate
    l_thigh.modulate = Color("485966") if legs_item != "" else Color("bd896b")
    r_thigh.modulate = l_thigh.modulate
    l_shin.modulate = Color("403b35") if feet_item != "" else Color("b98466")
    r_shin.modulate = l_shin.modulate
    l_fore.modulate = Color("5b5148") if hands_item != "" else Color("c89471")
    r_fore.modulate = l_fore.modulate

    var back_on := _visual_item("back") != ""
    backpack.visible = back_on
    backpack.polygon = PackedVector2Array([
        Vector2(-7,-14),Vector2(7,-14),Vector2(8,5),Vector2(5,11),
        Vector2(-5,11),Vector2(-8,5)
    ])
    backpack.color = Color("4b594d") if role == "player" else Color("624c3f")

    var armor_on := _visual_item("armor") != ""
    armor.visible = armor_on
    armor.polygon = PackedVector2Array([
        Vector2(-8,-15),Vector2(8,-15),Vector2(7,3),Vector2(4,8),
        Vector2(-4,8),Vector2(-7,3)
    ])
    armor.color = Color("38453f")

    var head_on := _visual_item("head") != ""
    headgear.visible = head_on
    headgear.polygon = PackedVector2Array([
        Vector2(-9,-31),Vector2(-6,-36),Vector2(6,-36),
        Vector2(9,-31),Vector2(7,-27),Vector2(-7,-27)
    ])
    headgear.color = Color("3e4a43")

    _weapon_visible = _weapon_category() != ""
    var wid := _weapon_id().to_lower()
    _weapon_kind = "rifle" if ("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid) else "pistol"
    _update_weapon_shape()

func _update_weapon_shape() -> void:
    weapon_body.visible = _weapon_visible
    weapon_barrel.visible = _weapon_visible
    weapon_grip.visible = _weapon_visible
    if not _weapon_visible:
        return
    if _weapon_kind == "rifle":
        weapon_body.polygon = PackedVector2Array([
            Vector2(-2,-2.5),Vector2(10,-2.5),Vector2(13,-1),
            Vector2(10,2.5),Vector2(-2,2.5)
        ])
        weapon_body.color = Color("30373a")
        weapon_barrel.points = PackedVector2Array([Vector2(10,0),Vector2(20,0)])
        weapon_grip.points = PackedVector2Array([Vector2(1,1),Vector2(-1,7)])
    else:
        weapon_body.polygon = PackedVector2Array([
            Vector2(-1.5,-2.2),Vector2(7,-2.2),Vector2(8.5,-0.4),
            Vector2(7,2.0),Vector2(-1.5,2.0)
        ])
        weapon_body.color = Color("30363a")
        weapon_barrel.points = PackedVector2Array([Vector2(7,0),Vector2(11,0)])
        weapon_grip.points = PackedVector2Array([Vector2(0.5,1),Vector2(-1.5,6)])

func _angle_from_down(v: Vector2) -> float:
    if v.length_squared() <= 0.0001:
        return 0.0
    return v.angle() - Vector2.DOWN.angle()

func _apply_direction_shape() -> void:
    var d := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var side := absf(d.x)
    var sx := -1.0 if d.x < -0.20 else 1.0
    var width_scale := lerpf(1.0,0.62,side)
    torso.scale = Vector2(SCALE*width_scale*sx,SCALE)
    head.scale = Vector2(SCALE*lerpf(1.0,0.76,side)*sx,SCALE)
    var back_view := d.y < -0.55
    var shade := Color(0.82,0.84,0.86,1.0) if back_view else Color.WHITE
    head.self_modulate = shade
    torso.self_modulate = shade
    backpack.z_index = 14 if back_view else -10
    if back_view:
        weapon_body.z_index = 4
        weapon_barrel.z_index = 4
        weapon_grip.z_index = 4
    else:
        weapon_body.z_index = 20
        weapon_barrel.z_index = 21
        weapon_grip.z_index = 21

func _apply_pose() -> void:
    if torso == null:
        return
    _apply_direction_shape()

    var moving := move_velocity.length() > 4.0
    var wave := sin(gait_phase)
    var run_mult := 1.35 if sprinting else 1.0
    var leg_swing := wave * 0.32 * run_mult if moving else 0.0
    var knee_bend := maxf(0.0,sin(gait_phase+PI*0.5)) * 0.28 * run_mult if moving else 0.0

    l_hip.rotation = leg_swing
    r_hip.rotation = -leg_swing
    l_knee.rotation = -leg_swing*0.35 + knee_bend
    r_knee.rotation = leg_swing*0.35 + maxf(0.0,sin(gait_phase-PI*0.5))*0.28*run_mult

    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    if _weapon_visible:
        var a := _angle_from_down(aim)
        l_shoulder.rotation = a - 0.18
        r_shoulder.rotation = a + 0.18
        l_elbow.rotation = 0.30
        r_elbow.rotation = -0.18
    else:
        var arm_swing := -leg_swing*0.75
        l_shoulder.rotation = arm_swing
        r_shoulder.rotation = -arm_swing
        l_elbow.rotation = -arm_swing*0.20
        r_elbow.rotation = arm_swing*0.20

    var breath := sin(breathe_phase*2.1) * 0.35
    torso.position.y = -6.0 + breath
    head.position.y = -25.0 + breath*0.55

    # Weapon is a genuinely separate layer, positioned from the current aim.
    var hand_mid := Vector2(0,-3.0) + aim*12.5
    weapon_body.position = hand_mid
    weapon_barrel.position = hand_mid
    weapon_grip.position = hand_mid
    var wa := aim.angle()
    weapon_body.rotation = wa
    weapon_barrel.rotation = wa
    weapon_grip.rotation = wa

func _process(delta: float) -> void:
    breathe_phase += delta
    if move_velocity.length() > 4.0:
        gait_phase = fmod(gait_phase + delta*(11.0 if sprinting else 7.2),TAU)
    else:
        gait_phase = lerpf(gait_phase,0.0,minf(1.0,delta*6.0))

    gear_poll += delta
    if gear_poll >= 0.10:
        gear_poll = 0.0
        _refresh_gear(false)

    _apply_pose()
''',encoding="utf-8")

# Visible marker/version.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D2D.4.6  |  OPAQUE + DIR FIX"' not in h:
    raise SystemExit("D2D.5 HUD anchor missing")
h=h.replace('marker.text = "D2D.4.6  |  OPAQUE + DIR FIX"',
            'marker.text = "D2D.5  |  MODULAR 2D RIG"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
e=preset.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=75',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.5"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.5 version anchors missing")
preset.write_text(e,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    q=save.read_text(encoding="utf-8")
    q,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.5"',q,count=1)
    save.write_text(q,encoding="utf-8")

print("Applied D2D.5 modular articulated 2D rig with authored RGBA body parts and separate gear/weapon layers.")
