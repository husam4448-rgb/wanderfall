#!/usr/bin/env python3
from pathlib import Path
import base64, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
assets=root/"assets/art/characters"; assets.mkdir(parents=True,exist_ok=True)
data={
 "player_male_core.png":"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",
 "player_male_leg_left.png":"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",
 "player_male_leg_right.png":"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",
 "player_female_core.png":"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",
 "player_female_leg_left.png":"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",
 "player_female_leg_right.png":"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",
}
for name,b64 in data.items():
    (assets/name).write_bytes(base64.b64decode(b64))

visual=root/"scripts/art/production_survivor_visual.gd"
visual.write_text(r'''class_name ProductionSurvivorVisual
extends Node2D

const MELEE_DURATION := 0.30
var equipment: Node = null
var body_type := "male"
var facing := Vector2.DOWN
var pose_key := "down"
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var gait_phase := 0.0
var melee_time := 0.0
var melee_direction := Vector2.DOWN
var core: Sprite2D
var leg_left: Sprite2D
var leg_right: Sprite2D
var left_outline: Line2D
var left_fill: Line2D
var right_outline: Line2D
var right_fill: Line2D
var hand_left: Polygon2D
var hand_right: Polygon2D
var knee_left: Polygon2D
var knee_right: Polygon2D

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:
    equipment = equipment_value
    body_type = "female" if body_type_value == "female" else "male"
    _ensure_nodes()
    _load_body_textures()
    _apply_pose()

func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"
    _ensure_nodes()
    _load_body_textures()
    _apply_pose()

func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001: return
    facing = value.normalized()
    pose_key = _resolve_pose_key(facing)
    _apply_pose()

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value
    _apply_pose()

func play_melee(direction: Vector2 = Vector2.ZERO) -> void:
    melee_direction = facing if direction.length_squared() <= 0.0001 else direction.normalized()
    melee_time = MELEE_DURATION
    _apply_pose()

func refresh_gear() -> void: _apply_pose()

func is_supported_visual() -> bool:
    if equipment == null or not is_instance_valid(equipment): return false
    return (
        _gear("torso") == "hoodie"
        and _gear("legs") == "jeans"
        and _gear("feet") == "hiking_boots"
        and _gear("back") == "small_backpack"
        and _gear("hands") == "work_gloves"
        and _gear("head").is_empty()
        and _gear("eyes").is_empty()
        and _gear("lower_face").is_empty()
        and _gear("armor").is_empty()
        and _gear("binoculars").is_empty()
    )

func _gear(slot:String)->String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item"):
        return String(equipment.get_visual_item(slot))
    return ""

func _process(delta:float)->void:
    var moving:=move_velocity.length()>2.0
    if moving:
        gait_phase=fmod(gait_phase+delta*(12.0 if sprinting else (5.5 if crouching else 8.0)),TAU)
    else:
        gait_phase=lerpf(gait_phase,0.0,minf(1.0,delta*7.0))
    if melee_time>0.0: melee_time=maxf(0.0,melee_time-delta)
    if moving or melee_time>0.0: _apply_pose()

func _ensure_nodes()->void:
    if core!=null:return
    core=_make_sprite(0); leg_left=_make_sprite(-1); leg_right=_make_sprite(1)
    left_outline=_make_line(Color("202523"),5.2); left_fill=_make_line(Color("665a48"),3.2)
    right_outline=_make_line(Color("202523"),5.2); right_fill=_make_line(Color("70624d"),3.2)
    hand_left=_make_hand(); hand_right=_make_hand()
    knee_left=_make_joint(); knee_right=_make_joint()

func _make_sprite(z:int)->Sprite2D:
    var s:=Sprite2D.new(); s.hframes=8; s.centered=true
    s.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST; s.z_index=z; add_child(s); return s

func _make_line(color:Color,width:float)->Line2D:
    var l:=Line2D.new(); l.width=width; l.default_color=color; l.antialiased=false; l.z_index=2; add_child(l); return l

func _make_hand()->Polygon2D:
    var p:=Polygon2D.new(); p.polygon=PackedVector2Array([Vector2(-1.6,-1.6),Vector2(1.6,-1.6),Vector2(1.6,1.6),Vector2(-1.6,1.6)])
    p.color=Color("b98261"); p.z_index=4; add_child(p); return p

func _make_joint()->Polygon2D:
    var p:=Polygon2D.new(); p.polygon=PackedVector2Array([Vector2(-2,-1),Vector2(0,-2),Vector2(2,-1),Vector2(2,1),Vector2(0,2),Vector2(-2,1)])
    p.color=Color("3b4141"); p.z_index=3; add_child(p); return p

func _load_body_textures()->void:
    var prefix:="player_female" if body_type=="female" else "player_male"
    core.texture=load("res://assets/art/characters/%s_core.png" % prefix)
    leg_left.texture=load("res://assets/art/characters/%s_leg_left.png" % prefix)
    leg_right.texture=load("res://assets/art/characters/%s_leg_right.png" % prefix)

func _apply_pose()->void:
    if core==null:return
    var frame:=_frame_for_pose(pose_key)
    core.frame=frame; leg_left.frame=frame; leg_right.frame=frame
    var moving:=move_velocity.length()>2.0
    var move_dir:=move_velocity.normalized() if moving else Vector2.ZERO
    var wave:=sin(gait_phase) if moving else 0.0
    var stride:=wave*(4.0 if sprinting else (1.6 if crouching else 2.6))
    var bob:=absf(sin(gait_phase))*(1.2 if sprinting else 0.7) if moving else 0.0
    var crouch_y:=2.4 if crouching else 0.0
    core.position=Vector2(0,-bob+crouch_y)
    leg_left.position=move_dir*stride+Vector2(0,crouch_y)
    leg_right.position=-move_dir*stride+Vector2(0,crouch_y)
    leg_left.rotation=-wave*(0.055 if sprinting else 0.035)
    leg_right.rotation=wave*(0.055 if sprinting else 0.035)
    var side:=_side_amount(pose_key)
    if side>0.2: leg_left.z_index=-2; leg_right.z_index=1
    elif side< -0.2: leg_right.z_index=-2; leg_left.z_index=1
    else: leg_left.z_index=-1; leg_right.z_index=1
    knee_left.position=Vector2(-4.2,14.5+crouch_y)+move_dir*stride*0.45
    knee_right.position=Vector2(4.2,14.5+crouch_y)-move_dir*stride*0.45
    knee_left.visible=moving or crouching; knee_right.visible=moving or crouching
    _apply_arms(core.position.y)

func _apply_arms(body_y:float)->void:
    var side:=_side_amount(pose_key)
    var back:=pose_key in ["up","up_left","up_right"]
    var shoulder_y:=-10.0+body_y
    var shift:=side*1.6
    var ls:=Vector2(-7.6+shift,shoulder_y+maxf(0.0,side)*1.1)
    var rs:=Vector2(7.6+shift,shoulder_y+maxf(0.0,-side)*1.1)
    var pts:=_arm_points(ls,rs,body_y)
    var le:Vector2=pts[0]; var lw:Vector2=pts[1]; var re:Vector2=pts[2]; var rw:Vector2=pts[3]
    left_outline.points=PackedVector2Array([ls,le,lw]); left_fill.points=PackedVector2Array([ls,le,lw])
    right_outline.points=PackedVector2Array([rs,re,rw]); right_fill.points=PackedVector2Array([rs,re,rw])
    var sleeve:=ItemDatabase.get_world_color(_gear("torso"),Color("665a48"))
    left_fill.default_color=sleeve.darkened(0.10); right_fill.default_color=sleeve
    var glove:=ItemDatabase.get_world_color(_gear("hands"),Color("5d5449"))
    hand_left.color=glove.darkened(0.08); hand_right.color=glove
    hand_left.position=lw; hand_right.position=rw
    if back: _set_arm_z(-2,-2)
    elif side>0.2: _set_left_arm_z(-2); _set_right_arm_z(2)
    elif side< -0.2: _set_right_arm_z(-2); _set_left_arm_z(2)
    else: _set_arm_z(2,2)

func _arm_points(ls:Vector2,rs:Vector2,body_y:float)->Array:
    var category:=String(equipment.get_weapon_category()) if equipment!=null and equipment.has_method("get_weapon_category") else ""
    var aim:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var perp:=Vector2(-aim.y,aim.x)
    if melee_time>0.0:
        var progress:=1.0-melee_time/MELEE_DURATION
        var attack:=melee_direction.rotated(lerpf(-0.95,0.95,sin(progress*PI*0.5)))
        var ap:=Vector2(-attack.y,attack.x)
        var rw:=Vector2(0,-4+body_y)+attack*15.5
        var re:=(rs+rw)*0.5-ap*5.8
        var lw:=Vector2(0,-3+body_y)+attack*8.0+ap*3.4
        var le:=(ls+lw)*0.5+ap*4.2
        return [le,lw,re,rw]
    if category=="firearm":
        var rw:=Vector2(0,-4+body_y)+aim*8.5-perp*1.0
        var lw:=Vector2(0,-4+body_y)+aim*13.5+perp*1.6
        var re:=(rs+rw)*0.5-perp*4.4-aim*0.8
        var le:=(ls+lw)*0.5+perp*4.8-aim*1.0
        return [le,lw,re,rw]
    if category=="melee":
        var center:=Vector2(0,-4+body_y)+aim*10.5
        var lw:=center+perp*2.8; var rw:=center-perp*2.8
        return [(ls+lw)*0.5+perp*4.5,lw,(rs+rw)*0.5-perp*4.5,rw]
    var aw:=sin(gait_phase)*(3.2 if move_velocity.length()>2.0 else 0.0)
    return [Vector2(-8.3,body_y+aw*0.3),Vector2(-7.0,7.5+body_y+aw),Vector2(8.3,body_y-aw*0.3),Vector2(7.0,7.5+body_y-aw)]

func get_weapon_anchor()->Dictionary:
    if core==null:return {"grip":Vector2.ZERO,"support":Vector2.ZERO,"back_view":false}
    var body_y:=core.position.y
    var side:=_side_amount(pose_key)
    var ls:=Vector2(-7.6+side*1.6,-10.0+body_y+maxf(0.0,side)*1.1)
    var rs:=Vector2(7.6+side*1.6,-10.0+body_y+maxf(0.0,-side)*1.1)
    var pts:=_arm_points(ls,rs,body_y)
    return {"grip":Vector2(pts[3]),"support":Vector2(pts[1]),"back_view":pose_key in ["up","up_left","up_right"]}

func _set_arm_z(l:int,r:int)->void:_set_left_arm_z(l);_set_right_arm_z(r)
func _set_left_arm_z(z:int)->void:left_outline.z_index=z;left_fill.z_index=z+1;hand_left.z_index=z+2
func _set_right_arm_z(z:int)->void:right_outline.z_index=z;right_fill.z_index=z+1;hand_right.z_index=z+2

func _resolve_pose_key(d:Vector2)->String:
    if d.length_squared()<=0.0001:return "down"
    var n:=d.normalized()
    if n.y< -0.72:
        if n.x< -0.34:return "up_left"
        if n.x>0.34:return "up_right"
        return "up"
    if n.y>0.72:
        if n.x< -0.34:return "down_left"
        if n.x>0.34:return "down_right"
        return "down"
    if n.x< -0.45:return "left"
    if n.x>0.45:return "right"
    return "down"

func _frame_for_pose(key:String)->int:
    match key:
        "down_right":return 1
        "right":return 2
        "up_right":return 3
        "up":return 4
        "up_left":return 5
        "left":return 6
        "down_left":return 7
        _:return 0

func _side_amount(key:String)->float:
    match key:
        "right":return 1.0
        "up_right","down_right":return 0.72
        "left":return -1.0
        "up_left","down_left":return -0.72
        _:return 0.0
''',encoding="utf-8")

wp=root/"scripts/art/weapon_visual.gd"
ws=wp.read_text(encoding="utf-8")
if "func get_grip_offset_world()" not in ws:
    marker="func refresh_weapon() -> void:\n"
    helper='''func get_grip_offset_local() -> Vector2:
    match weapon_id:
        "pistol_9mm": return Vector2(9.0,3.0)
        "revolver_357": return Vector2(8.5,3.0)
        "smg_9mm": return Vector2(12.0,4.0)
        "rifle_556": return Vector2(14.0,4.0)
        "shotgun_12g": return Vector2(18.0,4.0)
        "hunting_rifle": return Vector2(18.0,3.5)
        _: return Vector2(7.0,0.0)

func get_grip_offset_world() -> Vector2:
    var p:=get_grip_offset_local()
    return Vector2(p.x*scale.x,p.y*scale.y).rotated(rotation)

'''
    if marker not in ws: raise SystemExit("weapon anchor missing")
    ws=ws.replace(marker,helper+marker,1)
wp.write_text(ws,encoding="utf-8")

pp=root/"scripts/player.gd"
ps=pp.read_text(encoding="utf-8")
ps=ps.replace("@export var max_camera_zoom := 2.25","@export var max_camera_zoom := 2.60")
if "func _update_weapon_mount() -> void:" not in ps:
    anchor="func _update_actor_visual() -> void:\n"
    helper='''func _update_weapon_mount() -> void:
    if _production_visual == null or _weapon_visual == null:
        return
    if not _production_visual.visible or not _production_visual.has_method("get_weapon_anchor") or not _weapon_visual.has_method("get_grip_offset_world"):
        _weapon_visual.position = Vector2.ZERO
        _weapon_visual.z_index = 3
        return
    var mount: Dictionary = _production_visual.call("get_weapon_anchor")
    var grip := Vector2(mount.get("grip", Vector2.ZERO))
    _weapon_visual.position = grip - _weapon_visual.get_grip_offset_world()
    _weapon_visual.z_index = -2 if bool(mount.get("back_view", false)) else 3

'''
    if anchor not in ps: raise SystemExit("player visual anchor missing")
    ps=ps.replace(anchor,helper+anchor,1)
needle='''    if _weapon_visual != null:
        _weapon_visual.visible = show_actor
        _weapon_visual.set_facing(_facing)
'''
if needle in ps and "_update_weapon_mount()" not in ps[ps.find(needle):ps.find(needle)+len(needle)+80]:
    ps=ps.replace(needle,needle+"        _update_weapon_mount()\n",1)
pp.write_text(ps,encoding="utf-8")

sp=root/"scripts/save/save_manager.gd"
if sp.is_file():
    ss=sp.read_text(encoding="utf-8")
    ss=ss.replace('const GAME_VERSION := "0.19.0D2B.4"','const GAME_VERSION := "0.19.0D2B.5"')
    sp.write_text(ss,encoding="utf-8")
print("Applied v0.19.0D2B.5 male/female source-derived player visuals, articulated gait, weapon mount and extra zoom.")
