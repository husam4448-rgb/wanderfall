#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/art/baked_actor_visual.gd"
s = p.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# D2D.12 — REAL explicit 8-pose body renderer + continuous 360-degree gun aim.
# Unlike D2D.11, these are eight separate authored coordinate sets.
# ---------------------------------------------------------------------------

draw_start = s.index("func _draw() -> void:")
draw_end = s.index("\nfunc _arm_pose", draw_start)

helpers = r'''func _pose8_data() -> Dictionary:
    var d := _body_direction_name()

    # Eight deliberately separate body poses. Coordinates are screen-local pixels.
    # North/NE/NW are back-facing; S/SE/SW are front-facing; E/W are profiles.
    match d:
        "N":
            return {
                "torso":PackedVector2Array([
                    Vector2(-7.9,-9.2),Vector2(-6.8,-10.2),Vector2(6.8,-10.2),Vector2(7.9,-9.2),
                    Vector2(6.0,5.0),Vector2(5.2,7.0),Vector2(-5.2,7.0),Vector2(-6.0,5.0)
                ]),
                "l_sh":Vector2(-6.9,-8.8),"r_sh":Vector2(6.9,-8.8),
                "l_hip":Vector2(-3.2,5.5),"r_hip":Vector2(3.2,5.5),
                "l_knee":Vector2(-3.2,12.7),"r_knee":Vector2(3.2,12.7),
                "l_ankle":Vector2(-4.0,20.6),"r_ankle":Vector2(4.0,20.6),
                "head":Vector2(0.0,-18.4),"near_left":true,"back":true,"front":false,"profile":false,"pack_x":0.0
            }
        "NE":
            return {
                "torso":PackedVector2Array([
                    Vector2(-6.7,-8.5),Vector2(-5.4,-9.8),Vector2(7.6,-10.0),Vector2(8.3,-8.3),
                    Vector2(5.5,5.5),Vector2(4.3,7.0),Vector2(-5.5,6.2),Vector2(-6.4,4.5)
                ]),
                "l_sh":Vector2(-5.4,-7.9),"r_sh":Vector2(7.1,-9.0),
                "l_hip":Vector2(-2.9,5.0),"r_hip":Vector2(3.8,5.8),
                "l_knee":Vector2(-3.8,12.0),"r_knee":Vector2(4.0,13.0),
                "l_ankle":Vector2(-4.8,19.8),"r_ankle":Vector2(4.8,21.1),
                "head":Vector2(0.9,-18.5),"near_left":false,"back":true,"front":false,"profile":false,"pack_x":-1.0
            }
        "E":
            return {
                "torso":PackedVector2Array([
                    Vector2(-3.8,-9.5),Vector2(-2.2,-10.4),Vector2(3.5,-9.7),Vector2(4.8,-7.8),
                    Vector2(3.7,5.4),Vector2(2.8,6.9),Vector2(-2.8,6.3),Vector2(-3.7,4.8)
                ]),
                "l_sh":Vector2(-2.2,-8.8),"r_sh":Vector2(4.1,-7.5),
                "l_hip":Vector2(-1.8,5.0),"r_hip":Vector2(2.4,5.8),
                "l_knee":Vector2(-1.8,11.8),"r_knee":Vector2(2.8,13.0),
                "l_ankle":Vector2(-2.2,19.5),"r_ankle":Vector2(3.4,21.2),
                "head":Vector2(1.2,-18.3),"near_left":false,"back":false,"front":false,"profile":true,"pack_x":-2.1
            }
        "SE":
            return {
                "torso":PackedVector2Array([
                    Vector2(-6.7,-9.5),Vector2(-5.6,-10.3),Vector2(7.5,-9.3),Vector2(8.3,-7.6),
                    Vector2(5.7,5.4),Vector2(4.7,7.0),Vector2(-5.6,6.4),Vector2(-6.4,4.8)
                ]),
                "l_sh":Vector2(-5.7,-8.9),"r_sh":Vector2(7.1,-7.9),
                "l_hip":Vector2(-3.0,5.2),"r_hip":Vector2(3.9,5.8),
                "l_knee":Vector2(-3.8,12.4),"r_knee":Vector2(4.4,13.2),
                "l_ankle":Vector2(-4.7,20.4),"r_ankle":Vector2(5.0,21.4),
                "head":Vector2(0.9,-18.3),"near_left":false,"back":false,"front":true,"profile":false,"pack_x":-1.0
            }
        "S":
            return {
                "torso":PackedVector2Array([
                    Vector2(-8.5,-9.0),Vector2(-7.4,-10.1),Vector2(7.4,-10.1),Vector2(8.5,-9.0),
                    Vector2(6.1,5.1),Vector2(5.7,7.0),Vector2(-5.7,7.0),Vector2(-6.1,5.1)
                ]),
                "l_sh":Vector2(-7.5,-8.6),"r_sh":Vector2(7.5,-8.6),
                "l_hip":Vector2(-3.4,5.5),"r_hip":Vector2(3.4,5.5),
                "l_knee":Vector2(-3.8,12.8),"r_knee":Vector2(3.8,12.8),
                "l_ankle":Vector2(-4.6,20.9),"r_ankle":Vector2(4.6,20.9),
                "head":Vector2(0.0,-18.5),"near_left":false,"back":false,"front":true,"profile":false,"pack_x":0.0
            }
        "SW":
            return {
                "torso":PackedVector2Array([
                    Vector2(-8.3,-7.6),Vector2(-7.5,-9.3),Vector2(5.6,-10.3),Vector2(6.7,-9.5),
                    Vector2(6.4,4.8),Vector2(5.6,6.4),Vector2(-4.7,7.0),Vector2(-5.7,5.4)
                ]),
                "l_sh":Vector2(-7.1,-7.9),"r_sh":Vector2(5.7,-8.9),
                "l_hip":Vector2(-3.9,5.8),"r_hip":Vector2(3.0,5.2),
                "l_knee":Vector2(-4.4,13.2),"r_knee":Vector2(3.8,12.4),
                "l_ankle":Vector2(-5.0,21.4),"r_ankle":Vector2(4.7,20.4),
                "head":Vector2(-0.9,-18.3),"near_left":true,"back":false,"front":true,"profile":false,"pack_x":1.0
            }
        "W":
            return {
                "torso":PackedVector2Array([
                    Vector2(-4.8,-7.8),Vector2(-3.5,-9.7),Vector2(2.2,-10.4),Vector2(3.8,-9.5),
                    Vector2(3.7,4.8),Vector2(2.8,6.3),Vector2(-2.8,6.9),Vector2(-3.7,5.4)
                ]),
                "l_sh":Vector2(-4.1,-7.5),"r_sh":Vector2(2.2,-8.8),
                "l_hip":Vector2(-2.4,5.8),"r_hip":Vector2(1.8,5.0),
                "l_knee":Vector2(-2.8,13.0),"r_knee":Vector2(1.8,11.8),
                "l_ankle":Vector2(-3.4,21.2),"r_ankle":Vector2(2.2,19.5),
                "head":Vector2(-1.2,-18.3),"near_left":true,"back":false,"front":false,"profile":true,"pack_x":2.1
            }
        "NW":
            return {
                "torso":PackedVector2Array([
                    Vector2(-8.3,-8.3),Vector2(-7.6,-10.0),Vector2(5.4,-9.8),Vector2(6.7,-8.5),
                    Vector2(6.4,4.5),Vector2(5.5,6.2),Vector2(-4.3,7.0),Vector2(-5.5,5.5)
                ]),
                "l_sh":Vector2(-7.1,-9.0),"r_sh":Vector2(5.4,-7.9),
                "l_hip":Vector2(-3.8,5.8),"r_hip":Vector2(2.9,5.0),
                "l_knee":Vector2(-4.0,13.0),"r_knee":Vector2(3.8,12.0),
                "l_ankle":Vector2(-4.8,21.1),"r_ankle":Vector2(4.8,19.8),
                "head":Vector2(-0.9,-18.5),"near_left":true,"back":true,"front":false,"profile":false,"pack_x":1.0
            }
    return {}

func _shift_pose_points(points: PackedVector2Array, offset: Vector2) -> PackedVector2Array:
    var out := PackedVector2Array()
    for pt in points:
        out.append(_q(pt + offset))
    return out

func _draw_pose_boot(ankle: Vector2, color: Color, body_dir: Vector2, outline: Color, near: bool) -> void:
    var d := body_dir.normalized() if body_dir.length_squared() > 0.0001 else Vector2.DOWN
    var toe := _q(ankle + Vector2(d.x * 3.4, d.y * 2.6 + 1.0))
    var c := color if near else color.darkened(0.12)
    draw_line(ankle,toe,outline,6.0,true)
    draw_line(ankle,toe,c,4.2,true)
    var side := Vector2(-d.y,d.x)
    draw_line(toe-side*2.0,toe+side*2.0,c.darkened(0.16),2.3,true)

'''

new_draw = r'''func _draw() -> void:
    var female := body_type == "female"
    var pose := _pose8_data()
    if pose.is_empty():
        return

    var body_dir := _body_direction()
    var dir_name := _body_direction_name()
    var moving := move_velocity.length() > 2.0
    var move_dir := move_velocity.normalized() if moving else Vector2.ZERO
    var stride_wave := sin(gait_phase) if moving else 0.0
    var lift_wave := absf(cos(gait_phase)) if moving else 0.0
    var stride_amp := 4.6 if sprinting else (2.0 if crouching else 3.2)

    var breath := sin(idle_phase) * 0.28 if not moving else 0.0
    var body_bob := -absf(sin(gait_phase)) * (1.25 if sprinting else 0.65) if moving else breath
    var crouch_y := 2.8 if crouching else 0.0
    var body_offset := Vector2(0.0,body_bob+crouch_y)
    var lean := move_dir * (0.75 if sprinting else 0.35)
    if crouching:
        lean *= 0.35

    var torso_id := _gear("torso")
    var armor_id := _gear("armor")
    var hands_id := _gear("hands")
    var legs_id := _gear("legs")
    var feet_id := _gear("feet")
    var back_id := _gear("back")
    var head_id := _gear("head")
    var eyes_id := _gear("eyes")
    var lower_face_id := _gear("lower_face")
    var binoculars_id := _gear("binoculars")

    var torso_color := _color(torso_id,Color("59685c") if role!="bandit" else Color("6a4d42"))
    var pants_color := _color(legs_id,Color("455663"))
    var boot_color := _color(feet_id,Color("433d35"))
    var glove_color := _color(hands_id,skin_color)
    var outline := Color("202725")

    var torso_pts := _shift_pose_points(pose["torso"],body_offset+lean)
    var l_shoulder:Vector2 = _q(pose["l_sh"]+body_offset+lean)
    var r_shoulder:Vector2 = _q(pose["r_sh"]+body_offset+lean)
    var l_hip:Vector2 = _q(pose["l_hip"]+body_offset+lean*0.15)
    var r_hip:Vector2 = _q(pose["r_hip"]+body_offset+lean*0.15)
    var l_knee:Vector2 = _q(pose["l_knee"]+body_offset)
    var r_knee:Vector2 = _q(pose["r_knee"]+body_offset)
    var l_ankle:Vector2 = _q(pose["l_ankle"]+body_offset)
    var r_ankle:Vector2 = _q(pose["r_ankle"]+body_offset)

    # Locomotion moves around the explicit pose; idle/aiming never changes the leg pose.
    var l_stride := stride_wave*stride_amp
    var r_stride := -l_stride
    if moving:
        l_knee += move_dir*l_stride*0.42
        r_knee += move_dir*r_stride*0.42
        l_ankle += move_dir*l_stride
        r_ankle += move_dir*r_stride
        if stride_wave > 0.0:
            l_ankle.y -= lift_wave*(1.8 if sprinting else 1.0)
        else:
            r_ankle.y -= lift_wave*(1.8 if sprinting else 1.0)
    if crouching:
        l_knee.y += 1.8
        r_knee.y += 1.8
        l_ankle.y -= 0.8
        r_ankle.y -= 0.8

    var left_near:bool = pose["near_left"]

    var draw_leg := func(hip:Vector2,knee:Vector2,ankle:Vector2,near:bool) -> void:
        var c := pants_color if near else pants_color.darkened(0.14)
        _limb(hip,knee,c,5.25,outline)
        _joint(knee,c.lightened(0.03),2.3,outline)
        _limb(knee,ankle,c.darkened(0.03),4.8,outline)
        _joint(ankle,boot_color if near else boot_color.darkened(0.10),1.8,outline)
        _draw_pose_boot(ankle,boot_color,body_dir,outline,near)

    # Far leg first. E/W and diagonals therefore read as actual depth changes.
    if left_near:
        draw_leg.call(r_hip,r_knee,r_ankle,false)
        draw_leg.call(l_hip,l_knee,l_ankle,true)
    else:
        draw_leg.call(l_hip,l_knee,l_ankle,false)
        draw_leg.call(r_hip,r_knee,r_ankle,true)
    _draw_pants_detail(legs_id,l_knee,r_knee,pants_color)

    var arm_pose := _arm_pose(l_shoulder,r_shoulder,body_bob+crouch_y)
    _last_lw=arm_pose[1]
    _last_rw=arm_pose[3]

    var draw_arm := func(sh:Vector2,el:Vector2,wr:Vector2,near:bool) -> void:
        var c := torso_color if near else torso_color.darkened(0.15)
        var hc := glove_color if near else glove_color.darkened(0.08)
        _joint(sh,c,2.1,outline)
        _limb(sh,el,c,4.25,outline)
        _joint(el,c.lightened(0.03),2.0,outline)
        _limb(el,wr,c.darkened(0.02),3.75,outline)
        _joint(wr,hc,1.6,outline)
        _hand(wr,hc,outline)

    var back_view:bool = pose["back"]
    var front_view:bool = pose["front"]
    var profile_view:bool = pose["profile"]

    # Backpacks are behind front/profile poses but visibly sit on top of north-facing backs.
    var pack_offset:=Vector2(float(pose["pack_x"]),body_bob+crouch_y)
    if not back_view:
        _draw_backpack(back_id,pack_offset,outline)

    # Rear arm pass.
    if back_view:
        draw_arm.call(l_shoulder,arm_pose[0],arm_pose[1],false)
        draw_arm.call(r_shoulder,arm_pose[2],arm_pose[3],false)
    elif not front_view:
        if left_near:
            draw_arm.call(r_shoulder,arm_pose[2],arm_pose[3],false)
        else:
            draw_arm.call(l_shoulder,arm_pose[0],arm_pose[1],false)

    _polygon(torso_pts,torso_color,outline,1.6)

    # Front-oriented garment detail must not turn side profiles back into rectangles.
    if not profile_view and not back_view:
        _draw_torso_detail(torso_id,torso_color,-8.8+body_bob+crouch_y,5.5+body_bob+crouch_y,5.8,outline)

    # Direction-aware armor: side views use a narrow plate instead of the old front-facing vest.
    if not armor_id.is_empty():
        if profile_view:
            var ac:=_color(armor_id,Color("4d574d"))
            var sx:=1.0 if dir_name=="E" else -1.0
            var ap:=PackedVector2Array([
                _q(Vector2(-3.1+sx*0.5,-7.2)+body_offset),
                _q(Vector2(3.0+sx*0.5,-6.6)+body_offset),
                _q(Vector2(2.4+sx*0.5,3.8)+body_offset),
                _q(Vector2(-2.7+sx*0.5,3.6)+body_offset)
            ])
            _polygon(ap,ac,outline,1.2)
        elif not back_view:
            _draw_armor(armor_id,Vector2(0,body_bob+crouch_y),outline)

    if back_view:
        _draw_backpack(back_id,pack_offset,outline)

    # Neck and head use their own anchor from each of the eight poses.
    var neck_center:=_q((l_shoulder+r_shoulder)*0.5+Vector2(0,-3.0))
    draw_rect(Rect2(neck_center-Vector2(2.2,2.5),Vector2(4.4,5.5)),outline,true)
    draw_rect(Rect2(neck_center-Vector2(1.5,2.2),Vector2(3.0,4.8)),skin_color.darkened(0.06),true)

    var head_center:Vector2 = _q(pose["head"]+body_offset*Vector2(1.0,0.45)+lean*0.20)
    _draw_head(head_center,female,outline)
    _draw_hair(head_center,female,outline)
    _draw_face_direction(head_center,outline)
    if not back_view:
        _draw_lower_face(lower_face_id,head_center,outline)
        if not profile_view:
            _draw_eyes(eyes_id,head_center,outline)
    _draw_headwear(head_id,head_center,outline)

    # Foreground arm pass. South shows both arms; side/diagonal shows only near arm.
    # North keeps upper arms behind the back, but hands + firearm remain readable.
    if front_view:
        draw_arm.call(l_shoulder,arm_pose[0],arm_pose[1],true)
        draw_arm.call(r_shoulder,arm_pose[2],arm_pose[3],true)
    elif not back_view:
        if left_near:
            draw_arm.call(l_shoulder,arm_pose[0],arm_pose[1],true)
        else:
            draw_arm.call(r_shoulder,arm_pose[2],arm_pose[3],true)
    else:
        _hand(arm_pose[1],glove_color.darkened(0.05),outline)
        _hand(arm_pose[3],glove_color,outline)

    _draw_glove_detail(hands_id,arm_pose[1],arm_pose[3],glove_color)
    _draw_skeleton_weapon(arm_pose[1],arm_pose[3],outline)
    _draw_binoculars(binoculars_id,Vector2(0,body_bob+crouch_y),outline)
'''

s = s[:draw_start] + helpers + new_draw + s[draw_end:]

# Replace the D2D.10/11 arm solver. Body pose is discrete; hands/forearms remain raw analog aim.
arm_start = s.index("func _arm_pose(")
arm_end = s.index("\nfunc _draw_head",arm_start)
new_arm = r'''func _arm_pose(l_shoulder: Vector2, r_shoulder: Vector2, body_bob: float) -> Array:
    var category:=_weapon_category()
    var aim:=_aim_direction()
    var perp:=Vector2(-aim.y,aim.x)
    var moving:=move_velocity.length()>2.0

    if melee_time > 0.0:
        var progress:=1.0-melee_time/MELEE_DURATION
        var swing:=lerpf(-0.95,0.95,sin(progress*PI*0.5))
        var attack_dir:=melee_direction.rotated(swing)
        var attack_perp:=Vector2(-attack_dir.y,attack_dir.x)
        var wrist:=_q(Vector2(0,-1+body_bob)+attack_dir*11.0)
        var elbow:=_q((r_shoulder+wrist)*0.5+attack_perp*4.0)
        var support_wrist:=_q(Vector2(0,1+body_bob)+attack_dir*5.5-attack_perp*3.0)
        var support_elbow:=_q((l_shoulder+support_wrist)*0.5-attack_perp*2.5)
        return [support_elbow,support_wrist,elbow,wrist]

    if category=="firearm":
        var wid:=_weapon_id().to_lower()
        var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)
        var reach:=14.2 if rifle else 11.8
        if moving:
            reach-=0.8

        # Right hand is always the dominant pistol grip. Left hand cups/supports it.
        # Only these upper-limb targets rotate continuously through 360 degrees.
        var chest:=Vector2(0.0,-1.0+body_bob)
        var r_wrist:=_q(chest+aim*reach)
        var l_wrist:=_q(r_wrist-aim*(3.1 if rifle else 0.85)-perp*(1.0 if rifle else 0.65))

        var bend_sign:=1.0 if aim.y>=0.0 else -1.0
        var l_elbow:=_q(l_shoulder.lerp(l_wrist,0.54)+perp*(2.8*bend_sign))
        var r_elbow:=_q(r_shoulder.lerp(r_wrist,0.54)-perp*(2.8*bend_sign))

        # Prevent straight locked elbows near cardinal side aim.
        if absf(aim.x)>0.82:
            l_elbow.y+=2.0
            r_elbow.y-=2.0

        return [l_elbow,l_wrist,r_elbow,r_wrist]

    var sway:=sin(gait_phase)*(2.7 if moving else 0.0)
    var l_elbow:=_q(l_shoulder+Vector2(-1.0,7.5+sway*0.25))
    var l_wrist:=_q(l_elbow+Vector2(1.0,7.0+sway*0.55))
    var r_elbow:=_q(r_shoulder+Vector2(1.0,7.5-sway*0.25))
    var r_wrist:=_q(r_elbow+Vector2(-1.0,7.0-sway*0.55))
    return [l_elbow,l_wrist,r_elbow,r_wrist]
'''
s = s[:arm_start] + new_arm + s[arm_end:]

# Weapon is attached to the dominant hand and follows the raw 360-degree aim vector.
w0 = s.index("func _draw_skeleton_weapon(")
w1 = s.index("\nfunc get_weapon_anchor",w0)
new_weapon = r'''func _draw_skeleton_weapon(lw: Vector2, rw: Vector2, outline: Color) -> void:
    if _weapon_category()!="firearm":
        return
    var aim:=_aim_direction()
    var perp:=Vector2(-aim.y,aim.x)
    var wid:=_weapon_id().to_lower()
    var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)
    var grip:=rw

    if rifle:
        var body_start:=grip-aim*0.7
        var body_end:=grip+aim*8.0
        var muzzle:=body_end+aim*7.8
        draw_line(body_start,body_end,outline,5.0,true)
        draw_line(body_start,body_end,Color("35393a"),3.0,true)
        draw_line(body_end,muzzle,outline,3.0,true)
        draw_line(body_end,muzzle,Color("252a2c"),1.8,true)
        draw_line(body_start,body_start-aim*5.0,outline,4.2,true)
        draw_line(body_start,body_start-aim*5.0,Color("4a4037"),2.7,true)
        draw_line(lw,body_start+aim*3.2,Color("2d3030"),1.2,true)
        return

    # Pistol slide begins at the dominant palm and rotates continuously.
    var slide_start:=grip-aim*0.7
    var slide_end:=grip+aim*6.7
    draw_line(slide_start,slide_end,outline,4.5,true)
    draw_line(slide_start,slide_end,Color("34383a"),2.8,true)

    # Grip rotates as part of the weapon instead of remaining screen-vertical.
    var handle_end:=grip-aim*1.1+perp*3.4
    draw_line(grip,handle_end,outline,3.7,true)
    draw_line(grip,handle_end,Color("4b4036"),2.2,true)

    # Support hand visibly connects to the dominant grip.
    draw_line(lw,grip-aim*0.20,Color("6a5542"),1.7,true)
'''
s = s[:w0] + new_weapon + s[w1:]

# Version / visible marker.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
h=re.sub(r'marker\.text = "D2D\.[^"]+"','marker.text = "D2D.12  |  TRUE 8 POSES + 360 AIM"',h,count=1)
hud.write_text(h,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e=re.sub(r'(?m)^version/code=\d+$','version/code=85',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.12"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.12"',q,count=1)
    sm.write_text(q,encoding="utf-8")

p.write_text(s,encoding="utf-8")
print("Applied D2D.12: eight explicit body coordinate poses, planted idle legs, direction-aware boots, and continuous 360-degree firearm arms.")
