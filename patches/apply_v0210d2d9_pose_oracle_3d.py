#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# ---------------------------------------------------------------------------
# D2D.9: 3D pose oracle -> 2D skeleton
# A mathematical 3D mannequin is used only to generate/provide joint anchors.
# No 3D model or SubViewport is used in gameplay.
# ---------------------------------------------------------------------------
oracle_path=root/"scripts/art/pose_oracle_3d.gd"
oracle_path.parent.mkdir(parents=True,exist_ok=True)
oracle_path.write_text(r'''class_name PoseOracle3D
extends RefCounted

# Lightweight 3D kinematic reference.
# Coordinates are body-local meters: +Y up, +Z forward, +X body-right.
# The pose is yaw-rotated to the 8 gameplay directions and orthographically
# projected to screen space. This is a pose oracle only; it renders no 3D model.

const PX := 10.2
const DEPTH_Y := 0.72

static func _yaw_for_screen_dir(dir: Vector2) -> float:
    var d := dir.normalized() if dir.length_squared() > 0.0001 else Vector2.DOWN
    # Body +Z maps to screen DOWN.
    return atan2(d.x, d.y)

static func _rot_y(p: Vector3, yaw: float) -> Vector3:
    var c:=cos(yaw)
    var s:=sin(yaw)
    return Vector3(p.x*c + p.z*s, p.y, -p.x*s + p.z*c)

static func _project(p: Vector3, origin: Vector2) -> Vector2:
    # Orthographic top-down/isometric-ish projection:
    # world X -> screen X, world Z -> screen Y, world Y -> screen up.
    return origin + Vector2(p.x*PX, p.z*PX - p.y*PX*DEPTH_Y)

static func pistol_pose(dir: Vector2, origin: Vector2) -> Dictionary:
    var yaw:=_yaw_for_screen_dir(dir)

    # Canonical two-handed pistol stance in 3D.
    # Arms are deliberately extended well clear of the chest.
    var sh_l:=Vector3(-0.47,1.34,0.00)
    var sh_r:=Vector3( 0.47,1.34,0.00)

    var el_l:=Vector3(-0.34,1.13,0.62)
    var el_r:=Vector3( 0.24,1.11,0.70)

    var wr_l:=Vector3(-0.12,1.04,1.13)
    var wr_r:=Vector3( 0.10,1.04,1.20)

    var grip:=Vector3(0.10,1.04,1.20)
    var support:=Vector3(-0.08,1.04,1.11)
    var muzzle:=Vector3(0.10,1.04,1.92)

    var d2:=dir.normalized() if dir.length_squared()>0.0001 else Vector2.DOWN
    var perp:=Vector2(-d2.y,d2.x)

    var p_sh_l:=_project(_rot_y(sh_l,yaw),origin)
    var p_sh_r:=_project(_rot_y(sh_r,yaw),origin)
    var p_el_l:=_project(_rot_y(el_l,yaw),origin)
    var p_el_r:=_project(_rot_y(el_r,yaw),origin)
    var p_wr_l:=_project(_rot_y(wr_l,yaw),origin)
    var p_wr_r:=_project(_rot_y(wr_r,yaw),origin)
    var p_grip:=_project(_rot_y(grip,yaw),origin)
    var p_support:=_project(_rot_y(support,yaw),origin)
    var p_muzzle:=_project(_rot_y(muzzle,yaw),origin)

    # Keep the silhouette readable after projection. This is equivalent to a
    # small shoulder-width change in the 3D mannequin, not independent 2D IK.
    var side:=absf(d2.x)
    var spread:=lerpf(2.8,4.8,side)
    p_el_l -= perp*spread
    p_el_r += perp*spread
    p_wr_l -= perp*1.10
    p_wr_r += perp*1.10

    return {
        "shoulder_l":p_sh_l,
        "shoulder_r":p_sh_r,
        "elbow_l":p_el_l,
        "elbow_r":p_el_r,
        "wrist_l":p_wr_l,
        "wrist_r":p_wr_r,
        "grip":p_grip,
        "support":p_support,
        "muzzle":p_muzzle,
    }

static func rifle_pose(dir: Vector2, origin: Vector2) -> Dictionary:
    var yaw:=_yaw_for_screen_dir(dir)
    var sh_l:=Vector3(-0.47,1.34,0.00)
    var sh_r:=Vector3( 0.47,1.34,0.00)
    var el_l:=Vector3(-0.40,1.12,0.60)
    var el_r:=Vector3( 0.18,1.13,0.72)
    var wr_l:=Vector3(-0.18,1.06,1.17)
    var wr_r:=Vector3( 0.13,1.04,1.29)
    var grip:=Vector3(0.13,1.04,1.29)
    var support:=Vector3(-0.18,1.06,1.17)
    var muzzle:=Vector3(0.13,1.04,2.20)
    return {
        "shoulder_l":_project(_rot_y(sh_l,yaw),origin),
        "shoulder_r":_project(_rot_y(sh_r,yaw),origin),
        "elbow_l":_project(_rot_y(el_l,yaw),origin),
        "elbow_r":_project(_rot_y(el_r,yaw),origin),
        "wrist_l":_project(_rot_y(wr_l,yaw),origin),
        "wrist_r":_project(_rot_y(wr_r,yaw),origin),
        "grip":_project(_rot_y(grip,yaw),origin),
        "support":_project(_rot_y(support,yaw),origin),
        "muzzle":_project(_rot_y(muzzle,yaw),origin),
    }
''',encoding="utf-8")

p=root/"scripts/art/baked_actor_visual.gd"
s=p.read_text(encoding="utf-8")

# Preload the oracle once.
if 'PoseOracle3D' not in s.split('\n',20)[0:20]:
    s=s.replace('extends Node2D\n','extends Node2D\n\nconst PoseOracle3DRef = preload("res://scripts/art/pose_oracle_3d.gd")\n',1)

# Replace arm pose with oracle-driven 3D projection.
a=s.index("func _arm_pose(")
b=s.index("\nfunc _draw_head",a)
new_arm=r'''func _arm_pose(l_shoulder: Vector2, r_shoulder: Vector2, body_bob: float) -> Array:
    var category:=_weapon_category()
    var aim:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN

    if melee_time > 0.0:
        var progress:=1.0-melee_time/MELEE_DURATION
        var swing:=lerpf(-0.95,0.95,sin(progress*PI*0.5))
        var attack_dir:=melee_direction.rotated(swing)
        var attack_perp:=Vector2(-attack_dir.y,attack_dir.x)
        var wrist:=_q(Vector2(0,-1+body_bob)+attack_dir*10.5)
        var elbow:=_q((r_shoulder+wrist)*0.5+attack_perp*4.0)
        var support_wrist:=_q(Vector2(0,1+body_bob)+attack_dir*5.0-attack_perp*3.0)
        var support_elbow:=_q((l_shoulder+support_wrist)*0.5-attack_perp*2.5)
        return [support_elbow,support_wrist,elbow,wrist]

    if category == "firearm":
        var wid:=_weapon_id().to_lower()
        var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)
        var origin:=Vector2(0.0, 8.6 + body_bob)
        var pose:=PoseOracle3DRef.rifle_pose(aim,origin) if rifle else PoseOracle3DRef.pistol_pose(aim,origin)

        # Keep real torso sockets, but use 3D-derived elbows/wrists.
        var le:Vector2=pose["elbow_l"]
        var lw:Vector2=pose["wrist_l"]
        var re:Vector2=pose["elbow_r"]
        var rw:Vector2=pose["wrist_r"]

        # Pull first segment naturally out of actual shoulder sockets.
        le=le.lerp(l_shoulder + (le-l_shoulder).normalized()*10.5,0.18)
        re=re.lerp(r_shoulder + (re-r_shoulder).normalized()*10.5,0.18)
        return [_q(le),_q(lw),_q(re),_q(rw)]

    var swing:=sin(gait_phase)*(3.2 if sprinting else 2.6) if move_velocity.length()>2.0 else sin(idle_phase)*0.28
    var l_elbow:=_q(Vector2(-7.5,0.5+body_bob+swing*0.35))
    var l_wrist:=_q(Vector2(-6.0,7.0+body_bob+swing))
    var r_elbow:=_q(Vector2(7.5,0.5+body_bob-swing*0.35))
    var r_wrist:=_q(Vector2(6.0,7.0+body_bob-swing))
    return [l_elbow,l_wrist,r_elbow,r_wrist]
'''
s=s[:a]+new_arm+s[b:]

# Replace weapon geometry using the same oracle so hands and gun share one source.
w=s.index("func _draw_skeleton_weapon(")
x=s.index("\nfunc get_weapon_anchor",w)
new_weapon=r'''func _draw_skeleton_weapon(lw: Vector2, rw: Vector2, outline: Color) -> void:
    if _weapon_category() != "firearm":
        return

    var aim:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var wid:=_weapon_id().to_lower()
    var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)
    var origin:=Vector2(0.0,8.6)
    var pose:=PoseOracle3DRef.rifle_pose(aim,origin) if rifle else PoseOracle3DRef.pistol_pose(aim,origin)

    var grip:Vector2=pose["grip"]
    var support:Vector2=pose["support"]
    var muzzle:Vector2=pose["muzzle"]
    var gun_dir:=(muzzle-grip).normalized()
    if gun_dir.length_squared()<0.01:
        gun_dir=aim
    var perp:=Vector2(-gun_dir.y,gun_dir.x)

    if rifle:
        var body_end:=grip+gun_dir*8.0
        draw_line(grip,body_end,outline,5.0,true)
        draw_line(grip,body_end,Color("35393a"),3.1,true)
        draw_line(body_end,muzzle,outline,3.2,true)
        draw_line(body_end,muzzle,Color("252a2c"),1.9,true)
        var stock_end:=grip-gun_dir*5.2
        draw_line(grip,stock_end,outline,4.4,true)
        draw_line(grip,stock_end,Color("4a4037"),2.8,true)
        draw_line(support,grip+gun_dir*3.2,Color("2d3030"),1.25,true)
        return

    # Prominent pistol: long enough to read at gameplay scale.
    var slide_start:=grip-gun_dir*0.9
    var slide_end:=grip+gun_dir*7.3
    draw_line(slide_start,slide_end,outline,4.6,true)
    draw_line(slide_start,slide_end,Color("34383a"),2.9,true)

    var handle_sign:=1.0
    var handle_end:=grip-gun_dir*1.2+perp*3.8*handle_sign
    draw_line(grip,handle_end,outline,3.8,true)
    draw_line(grip,handle_end,Color("4b4036"),2.3,true)

    # Visible support-hand bridge to prevent the two forearms reading as one blob.
    draw_line(support,grip-gun_dir*0.2,Color("6a5542"),2.0,true)
'''
s=s[:w]+new_weapon+s[x:]

# Marker/version.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
h=re.sub(r'marker\.text = "D2D\.[^"]+"','marker.text = "D2D.9  |  3D POSE ORACLE"',h,count=1)
hud.write_text(h,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e=re.sub(r'(?m)^version/code=\d+$','version/code=82',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.9"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.9"',q,count=1)
    sm.write_text(q,encoding="utf-8")

p.write_text(s,encoding="utf-8")
print("Applied D2D.9: 3D mathematical pose oracle projected into the 2D skeleton; no 3D gameplay model.")
