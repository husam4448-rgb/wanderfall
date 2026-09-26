#!/usr/bin/env python3
"""D2D.5.1: South-first anatomical reassembly + sprite-based equipment layers."""
from pathlib import Path
import re,sys,shutil
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo_root=Path(__file__).resolve().parents[1]

gear_src=repo_root/"assets/authored2d/gear"
gear_dst=root/"assets/authored2d/gear"
gear_dst.mkdir(parents=True,exist_ok=True)
for fn in ["backpack.png","vest.png","headgear.png","pistol.png","rifle.png"]:
    src=gear_src/fn
    if not src.is_file():
        raise SystemExit("D2D.5.1 missing gear sprite "+str(src))
    shutil.copy2(src,gear_dst/fn)

visual=root/"scripts/art/baked_actor_visual.gd"
visual.write_text(r'''class_name BakedActorVisual
extends Node2D

# D2D.5.1: South/front anatomy calibration. Body and equipment are independent
# Sprite2D layers; 3D is not rendered.

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
var _last_gear_key := ""

const TEX_HEAD := preload("res://assets/authored2d/parts/head.png")
const TEX_TORSO := preload("res://assets/authored2d/parts/torso.png")
const TEX_UPPER := preload("res://assets/authored2d/parts/upper_arm.png")
const TEX_FORE := preload("res://assets/authored2d/parts/forearm_hand.png")
const TEX_THIGH := preload("res://assets/authored2d/parts/thigh.png")
const TEX_SHIN := preload("res://assets/authored2d/parts/shin_foot.png")

const TEX_BACKPACK := preload("res://assets/authored2d/gear/backpack.png")
const TEX_VEST := preload("res://assets/authored2d/gear/vest.png")
const TEX_HEADGEAR := preload("res://assets/authored2d/gear/headgear.png")
const TEX_PISTOL := preload("res://assets/authored2d/gear/pistol.png")
const TEX_RIFLE := preload("res://assets/authored2d/gear/rifle.png")

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

var shirt: Sprite2D
var vest: Sprite2D
var backpack: Sprite2D
var headgear: Sprite2D
var l_pants: Sprite2D
var r_pants: Sprite2D
var l_boots: Sprite2D
var r_boots: Sprite2D
var l_gloves: Sprite2D
var r_gloves: Sprite2D
var weapon: Sprite2D

var l_shoulder := Node2D.new()
var r_shoulder := Node2D.new()
var l_elbow := Node2D.new()
var r_elbow := Node2D.new()
var l_hip := Node2D.new()
var r_hip := Node2D.new()
var l_knee := Node2D.new()
var r_knee := Node2D.new()

var _weapon_on := false
var _weapon_kind := "pistol"

func _ready() -> void:
    set_process(true)

func _mk(tex: Texture2D, scale_value: Vector2, z: int) -> Sprite2D:
    var s := Sprite2D.new()
    s.texture = tex
    s.centered = true
    s.scale = scale_value
    s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    s.z_index = z
    return s

func _build() -> void:
    if torso != null:
        return

    # Back layer.
    backpack = _mk(TEX_BACKPACK,Vector2(0.62,0.62),-20)
    backpack.position = Vector2(0,-8)
    add_child(backpack)

    # Legs: proportions derived from approved South/front survivor reference.
    l_hip.position = Vector2(-5.2,2.0)
    r_hip.position = Vector2(5.2,2.0)
    add_child(l_hip); add_child(r_hip)

    l_thigh = _mk(TEX_THIGH,Vector2(0.72,0.60),0)
    r_thigh = _mk(TEX_THIGH,Vector2(0.72,0.60),1)
    l_thigh.position = Vector2(0,9.0)
    r_thigh.position = Vector2(0,9.0)
    l_hip.add_child(l_thigh); r_hip.add_child(r_thigh)

    l_pants = _mk(TEX_THIGH,Vector2(0.75,0.62),2)
    r_pants = _mk(TEX_THIGH,Vector2(0.75,0.62),3)
    l_pants.position = Vector2(0,9.0)
    r_pants.position = Vector2(0,9.0)
    l_pants.modulate = Color("53636c")
    r_pants.modulate = Color("53636c")
    l_hip.add_child(l_pants); r_hip.add_child(r_pants)

    l_knee.position = Vector2(0,18.0)
    r_knee.position = Vector2(0,18.0)
    l_hip.add_child(l_knee); r_hip.add_child(r_knee)

    l_shin = _mk(TEX_SHIN,Vector2(0.74,0.54),0)
    r_shin = _mk(TEX_SHIN,Vector2(0.74,0.54),1)
    l_shin.position = Vector2(0,9.0)
    r_shin.position = Vector2(0,9.0)
    l_knee.add_child(l_shin); r_knee.add_child(r_shin)

    l_boots = _mk(TEX_SHIN,Vector2(0.78,0.56),4)
    r_boots = _mk(TEX_SHIN,Vector2(0.78,0.56),5)
    l_boots.position = Vector2(0,9.0)
    r_boots.position = Vector2(0,9.0)
    l_boots.modulate = Color("4b4037")
    r_boots.modulate = Color("4b4037")
    l_knee.add_child(l_boots); r_knee.add_child(r_boots)

    # Torso is deliberately wider/shorter than D2D.5.
    torso = _mk(TEX_TORSO,Vector2(0.88,0.54),8)
    torso.position = Vector2(0,-8.0)
    add_child(torso)

    shirt = _mk(TEX_TORSO,Vector2(0.92,0.56),9)
    shirt.position = Vector2(0,-8.0)
    shirt.modulate = Color("64725f")
    add_child(shirt)

    vest = _mk(TEX_VEST,Vector2(0.68,0.68),10)
    vest.position = Vector2(0,-8.0)
    add_child(vest)

    # Shoulder anchors now sit on the visible torso edges.
    l_shoulder.position = Vector2(-10.0,-15.0)
    r_shoulder.position = Vector2(10.0,-15.0)
    add_child(l_shoulder); add_child(r_shoulder)

    l_upper = _mk(TEX_UPPER,Vector2(-0.62,0.56),7)
    r_upper = _mk(TEX_UPPER,Vector2(0.62,0.56),7)
    l_upper.position = Vector2(0,7.5)
    r_upper.position = Vector2(0,7.5)
    l_shoulder.add_child(l_upper); r_shoulder.add_child(r_upper)

    l_elbow.position = Vector2(0,15.0)
    r_elbow.position = Vector2(0,15.0)
    l_shoulder.add_child(l_elbow); r_shoulder.add_child(r_elbow)

    l_fore = _mk(TEX_FORE,Vector2(-0.55,0.52),11)
    r_fore = _mk(TEX_FORE,Vector2(0.55,0.52),11)
    l_fore.position = Vector2(0,7.8)
    r_fore.position = Vector2(0,7.8)
    l_elbow.add_child(l_fore); r_elbow.add_child(r_fore)

    l_gloves = _mk(TEX_FORE,Vector2(-0.57,0.53),12)
    r_gloves = _mk(TEX_FORE,Vector2(0.57,0.53),12)
    l_gloves.position = Vector2(0,7.8)
    r_gloves.position = Vector2(0,7.8)
    l_gloves.modulate = Color("4a443c")
    r_gloves.modulate = Color("4a443c")
    l_elbow.add_child(l_gloves); r_elbow.add_child(r_gloves)

    # Head is substantially reduced from D2D.5.
    head = _mk(TEX_HEAD,Vector2(0.39,0.39),15)
    head.position = Vector2(0,-27.0)
    add_child(head)

    headgear = _mk(TEX_HEADGEAR,Vector2(0.58,0.58),16)
    headgear.position = Vector2(0,-32.0)
    add_child(headgear)

    weapon = _mk(TEX_PISTOL,Vector2(0.62,0.62),20)
    weapon.position = Vector2(7,-7)
    add_child(weapon)

    _refresh_gear(true)
    _apply_pose()

func setup(set_name_value: String) -> void:
    set_name=set_name_value
    role="bandit" if "bandit" in set_name_value else "player"
    _build()
    _refresh_gear(true)

func setup_equipment(equipment_value: Node, _body_type_value: String="male") -> void:
    equipment=equipment_value
    set_name="player_male"
    role="player"
    _build()
    _refresh_gear(true)

func set_body_type(_value: String) -> void:
    pass

func set_facing(value: Vector2) -> void:
    if value.length_squared()>0.0001:
        facing=value.normalized()
    _apply_pose()

func set_motion_state(velocity_value: Vector2, sprinting_value: bool=false, crouching_value: bool=false) -> void:
    move_velocity=velocity_value
    sprinting=sprinting_value
    crouching=crouching_value

func play_melee(_direction: Vector2=Vector2.ZERO) -> void:
    pass

func _visual(slot: String) -> String:
    if equipment!=null and is_instance_valid(equipment) and equipment.has_method("get_visual_item"):
        return String(equipment.call("get_visual_item",slot))
    if role=="bandit":
        match slot:
            "torso": return "field_jacket"
            "armor": return "tactical_vest"
            "hands": return "work_gloves"
            "legs": return "cargo_pants"
            "feet": return "combat_boots"
            "head": return "wool_beanie"
            "back": return "small_backpack"
    return ""

func _has_weapon() -> bool:
    if role=="bandit":
        return true
    if equipment==null or not is_instance_valid(equipment):
        return false
    if equipment.has_method("get_weapon_category"):
        if not String(equipment.call("get_weapon_category")).is_empty():
            return true
    if equipment.has_method("get_visual_item"):
        for slot in ["weapon","primary","secondary"]:
            if not String(equipment.call("get_visual_item",slot)).is_empty():
                return true
    return false

func _weapon_id() -> String:
    if role=="bandit":
        return "pistol_9mm"
    if equipment==null or not is_instance_valid(equipment):
        return ""
    if equipment.has_method("get_visual_item"):
        for slot in ["weapon","primary","secondary"]:
            var w:=String(equipment.call("get_visual_item",slot))
            if not w.is_empty():
                return w
    if equipment.has_method("get_weapon_category"):
        return String(equipment.call("get_weapon_category"))
    return ""

func _gear_key() -> String:
    return "|".join([
        _visual("torso"),_visual("armor"),_visual("hands"),_visual("legs"),
        _visual("feet"),_visual("head"),_visual("back"),
        "1" if _has_weapon() else "0",_weapon_id()
    ])

func refresh_gear() -> void:
    _refresh_gear(false)

func _refresh_gear(force: bool) -> void:
    if torso==null:
        return
    var key:=_gear_key()
    if not force and key==_last_gear_key:
        return
    _last_gear_key=key

    shirt.visible = not _visual("torso").is_empty()
    vest.visible = not _visual("armor").is_empty()
    backpack.visible = not _visual("back").is_empty()
    headgear.visible = not _visual("head").is_empty()
    l_pants.visible = not _visual("legs").is_empty()
    r_pants.visible = l_pants.visible
    l_boots.visible = not _visual("feet").is_empty()
    r_boots.visible = l_boots.visible
    l_gloves.visible = not _visual("hands").is_empty()
    r_gloves.visible = l_gloves.visible

    _weapon_on=_has_weapon()
    var wid:=_weapon_id().to_lower()
    _weapon_kind="rifle" if ("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid) else "pistol"
    weapon.texture=TEX_RIFLE if _weapon_kind=="rifle" else TEX_PISTOL
    weapon.scale=Vector2(0.55,0.55) if _weapon_kind=="rifle" else Vector2(0.62,0.62)
    weapon.visible=_weapon_on

func _apply_pose() -> void:
    if torso==null:
        return

    var moving:=move_velocity.length()>4.0
    var wave:=sin(gait_phase)
    var stride:=(0.22 if sprinting else 0.16)*wave if moving else 0.0

    # Conservative, human-readable gait. Knees bend forward, not backward.
    l_hip.rotation=stride
    r_hip.rotation=-stride
    l_knee.rotation=maxf(0.0,-wave)*0.18 if moving else 0.0
    r_knee.rotation=maxf(0.0,wave)*0.18 if moving else 0.0

    var d:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var side:=clampf(d.x,-1.0,1.0)

    if _weapon_on:
        # South/front first: elbows stay connected and form a stable two-hand hold.
        var lateral:=side*0.36
        l_shoulder.rotation=-0.62+lateral
        r_shoulder.rotation=0.62+lateral
        l_elbow.rotation=0.72
        r_elbow.rotation=-0.72
        if absf(d.y)>0.70:
            weapon.rotation=0.18*side
            weapon.position=Vector2(4.0*side,-5.5)
        else:
            weapon.rotation=d.angle()
            weapon.position=Vector2(d.x*12.0,-8.0+d.y*4.0)
    else:
        var arm:=(-stride*0.72) if moving else 0.05
        l_shoulder.rotation=arm
        r_shoulder.rotation=-arm
        l_elbow.rotation=-0.06
        r_elbow.rotation=0.06

    var breath:=sin(breathe_phase*2.0)*0.22
    torso.position.y=-8.0+breath
    shirt.position.y=-8.0+breath
    vest.position.y=-8.0+breath
    head.position.y=-27.0+breath*0.45
    headgear.position.y=-32.0+breath*0.45

    # South/front is the calibrated checkpoint; other directions compress width
    # rather than mirroring/detaching limbs.
    var lateral_view:=absf(d.x)
    var body_w:=lerpf(1.0,0.78,lateral_view)
    torso.scale.x=0.88*body_w
    shirt.scale.x=0.92*body_w
    vest.scale.x=0.68*body_w
    head.scale.x=0.39*lerpf(1.0,0.88,lateral_view)

    var back_view:=d.y < -0.60
    backpack.z_index=18 if back_view else -20
    weapon.z_index=6 if back_view else 20

func _process(delta: float) -> void:
    breathe_phase+=delta
    if move_velocity.length()>4.0:
        gait_phase=fmod(gait_phase+delta*(9.2 if sprinting else 6.5),TAU)
    else:
        gait_phase=lerpf(gait_phase,0.0,minf(1.0,delta*6.0))

    gear_poll+=delta
    if gear_poll>=0.10:
        gear_poll=0.0
        _refresh_gear(false)

    _apply_pose()
''',encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D2D.5  |  MODULAR 2D RIG"' not in h:
    raise SystemExit("D2D.5.1 HUD anchor missing")
h=h.replace('marker.text = "D2D.5  |  MODULAR 2D RIG"',
            'marker.text = "D2D.5.1  |  SOUTH + GEAR"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
e=preset.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=76',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.5.1"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.5.1 version anchors missing")
preset.write_text(e,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    q=save.read_text(encoding="utf-8")
    q,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.5.1"',q,count=1)
    save.write_text(q,encoding="utf-8")

print("Applied D2D.5.1 South-first anatomical calibration with sprite-based gear and weapons.")
