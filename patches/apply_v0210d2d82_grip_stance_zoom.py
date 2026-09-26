#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/baked_actor_visual.gd"
s=p.read_text(encoding="utf-8")

# D2D.8.2: make the player slightly larger at the renderer root.
for sig in [
    'func setup(set_name_value: String) -> void:\n',
    'func setup_equipment(equipment_value: Node, body_type_value: String = "male", role_value: String = "player") -> void:\n',
]:
    if sig in s:
        s=s.replace(sig, sig+'    scale = Vector2(1.10, 1.10)\n', 1)

# Freeze the lower body into a planted stance when stationary with a firearm.
anchor='''    if crouching:
        l_knee.y += 2.0; r_knee.y += 2.0
        l_ankle.y -= 1.0; r_ankle.y -= 1.0

    var draw_leg_chain := func'''
replacement='''    if crouching:
        l_knee.y += 2.0; r_knee.y += 2.0
        l_ankle.y -= 1.0; r_ankle.y -= 1.0

    # Aiming while stationary must not read as a walking frame.
    # Keep both feet planted and reduce side-view fore/aft leg separation.
    if _weapon_category() == "firearm" and not moving and not crouching:
        var stance_knee_half := lerpf(3.0, 1.15, profile)
        var stance_ankle_half := lerpf(3.6, 1.05, profile)
        l_knee = _q(Vector2(-stance_knee_half,12.0+body_bob))
        r_knee = _q(Vector2( stance_knee_half,12.0+body_bob))
        l_ankle = _q(Vector2(-stance_ankle_half,21.0+body_bob))
        r_ankle = _q(Vector2( stance_ankle_half,21.0+body_bob))
        l_stride = 0.0
        r_stride = 0.0

    var draw_leg_chain := func'''
if anchor not in s:
    raise SystemExit("D2D.8.2 planted-leg anchor missing")
s=s.replace(anchor,replacement,1)

# Replace the firearm arm pose: both pistol hands converge on one grip cluster.
a=s.index("func _arm_pose(")
b=s.index("\nfunc _draw_head",a)
old_arm=s[a:b]
new_arm=r'''func _arm_pose(l_shoulder: Vector2, r_shoulder: Vector2, body_bob: float) -> Array:
    var category := _weapon_category()
    var armed := category in ["firearm","melee"]
    var aim := facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var perp := Vector2(-aim.y,aim.x)
    var profile := absf(aim.x)

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

    if armed:
        var wid:=_weapon_id().to_lower()
        var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)

        if rifle:
            var grip_center:=_q(Vector2(0,-1.0+body_bob)+aim*9.6)
            var l_wrist:=_q(grip_center + perp*1.5 - aim*3.0)
            var r_wrist:=_q(grip_center - perp*1.35)
            var l_elbow:=_q((l_shoulder+l_wrist)*0.5+perp*2.9)
            var r_elbow:=_q((r_shoulder+r_wrist)*0.5-perp*2.9)
            return [l_elbow,l_wrist,r_elbow,r_wrist]

        # Pistol: dominant hand sits exactly on the grip; support hand cups it.
        # This prevents the left hand floating away from the pistol in side views.
        var dominant_is_right := aim.x >= -0.20
        var dominant_shoulder := r_shoulder if dominant_is_right else l_shoulder
        var support_shoulder := l_shoulder if dominant_is_right else r_shoulder
        var dominant_wrist := _q(Vector2(0,-1.0+body_bob)+aim*(9.4 if profile>0.70 else 8.2))
        var support_side := -1.0 if dominant_is_right else 1.0
        var support_wrist := _q(dominant_wrist-aim*0.75+perp*(0.85*support_side))
        var dominant_elbow := _q((dominant_shoulder+dominant_wrist)*0.52-perp*(2.0*support_side))
        var support_elbow := _q((support_shoulder+support_wrist)*0.50+perp*(2.6*support_side))
        if dominant_is_right:
            return [support_elbow,support_wrist,dominant_elbow,dominant_wrist]
        return [dominant_elbow,dominant_wrist,support_elbow,support_wrist]

    var swing:=sin(gait_phase)*(3.2 if sprinting else 2.6) if move_velocity.length()>2.0 else sin(idle_phase)*0.28
    var l_elbow:=_q(Vector2(-7.5,0.5+body_bob+swing*0.35))
    var l_wrist:=_q(Vector2(-6.0,7.0+body_bob+swing))
    var r_elbow:=_q(Vector2(7.5,0.5+body_bob-swing*0.35))
    var r_wrist:=_q(Vector2(6.0,7.0+body_bob-swing))
    return [l_elbow,l_wrist,r_elbow,r_wrist]
'''
s=s[:a]+new_arm+s[b:]

# Replace pistol drawing so the slide begins at the dominant hand and the
# support hand visibly cups the grip instead of defining the weapon origin.
w=s.index("func _draw_skeleton_weapon(")
x=s.index("\nfunc get_weapon_anchor",w)
new_weapon=r'''func _draw_skeleton_weapon(lw: Vector2, rw: Vector2, outline: Color) -> void:
    if _weapon_category() != "firearm":
        return

    var aim:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var perp:=Vector2(-aim.y,aim.x)
    var wid:=_weapon_id().to_lower()
    var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)

    if rifle:
        var grip:=rw
        if aim.x < -0.20:
            grip=lw
        var support:=lw if grip==rw else rw
        var body_start:=grip-aim*0.6
        var body_end:=body_start+aim*8.0
        var muzzle:=body_end+aim*7.8
        draw_line(body_start,body_end,outline,5.0,true)
        draw_line(body_start,body_end,Color("35393a"),3.0,true)
        draw_line(body_end,muzzle,outline,3.0,true)
        draw_line(body_end,muzzle,Color("252a2c"),1.8,true)
        var stock_end:=body_start-aim*5.0
        draw_line(body_start,stock_end,outline,4.2,true)
        draw_line(body_start,stock_end,Color("4a4037"),2.7,true)
        draw_line(support,body_start+aim*3.5,Color("2d3030"),1.1,true)
        return

    var dominant_right:=aim.x >= -0.20
    var grip:=rw if dominant_right else lw
    var support:=lw if dominant_right else rw

    # Pistol slide sits directly above/forward of the dominant grip.
    var slide_start:=grip-aim*0.8
    var slide_end:=grip+aim*5.3
    draw_line(slide_start,slide_end,outline,4.2,true)
    draw_line(slide_start,slide_end,Color("34383a"),2.55,true)

    # Handle begins at the dominant hand. Offset to the screen-side of the gun,
    # never detached from the hand socket.
    var handle_sign:=1.0 if dominant_right else -1.0
    var handle_end:=grip-aim*1.2+perp*(3.15*handle_sign)
    draw_line(grip,handle_end,outline,3.4,true)
    draw_line(grip,handle_end,Color("4b4036"),2.05,true)

    # Small bridge shows the support hand cupping the dominant hand/grip.
    draw_line(support,grip-aim*0.35,Color("2b302d"),1.3,true)
'''
s=s[:w]+new_weapon+s[x:]

# More close zoom: previous 4.04 was still insufficient on-device.
player=root/"scripts/player.gd"
pt=player.read_text(encoding="utf-8")
pt,n=re.subn(r'@export var max_camera_zoom := [0-9.]+','@export var max_camera_zoom := 5.48',pt,count=1)
if not n:
    raise SystemExit("D2D.8.2 max_camera_zoom anchor missing")
player.write_text(pt,encoding="utf-8")

# Version/marker.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
h=h.replace('marker.text = "D2D.8.1  |  AIM + ARMS FIX"','marker.text = "D2D.8.2  |  GRIP + STANCE + ZOOM"',1)
hud.write_text(h,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e=re.sub(r'(?m)^version/code=\d+$','version/code=81',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.8.2"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.8.2"',q,count=1)
    sm.write_text(q,encoding="utf-8")

p.write_text(s,encoding="utf-8")
print("Applied D2D.8.2: larger actor, planted firearm stance, converged two-hand pistol grip, hand-bound pistol, and max zoom 5.48.")
