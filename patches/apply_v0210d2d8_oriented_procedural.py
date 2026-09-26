#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/baked_actor_visual.gd"
s=p.read_text(encoding="utf-8")

# Idle breathing clock.
s=s.replace(
'var gait_phase := 0.0\nvar melee_time := 0.0',
'var gait_phase := 0.0\nvar idle_phase := 0.0\nvar melee_time := 0.0',1)

# Keep the procedural character alive while idle.
old_proc='''func _process(delta: float) -> void:
    var speed := move_velocity.length()
    if speed > 2.0:
        var cadence := 11.0 if sprinting else (5.5 if crouching else 7.5)
        gait_phase = fmod(gait_phase + delta * cadence, TAU)
    else:
        gait_phase = lerpf(gait_phase, 0.0, minf(1.0, delta * 7.0))
    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)
    if speed > 2.0 or melee_time > 0.0:
        queue_redraw()
'''
new_proc='''func _process(delta: float) -> void:
    idle_phase = fmod(idle_phase + delta * 1.9, TAU)
    var speed := move_velocity.length()
    if speed > 2.0:
        var cadence := 11.5 if sprinting else (5.8 if crouching else 7.7)
        gait_phase = fmod(gait_phase + delta * cadence, TAU)
    else:
        gait_phase = lerpf(gait_phase, 0.0, minf(1.0, delta * 7.0))
    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)
    queue_redraw()
'''
if old_proc not in s:
    raise SystemExit("D2D.8 process anchor missing")
s=s.replace(old_proc,new_proc,1)

start=s.index("func _draw() -> void:")
end=s.index("\nfunc _arm_pose",start)

new_draw=r'''func _draw() -> void:
    var female := body_type == "female"
    var moving := move_velocity.length() > 2.0
    var move_dir := move_velocity.normalized() if moving else Vector2.ZERO
    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var side := clampf(aim.x,-1.0,1.0)
    var profile := absf(side)
    var backness := clampf(-aim.y,0.0,1.0)

    var stride_wave := sin(gait_phase) if moving else 0.0
    var lift_wave := absf(cos(gait_phase)) if moving else 0.0
    var stride_amp := 5.2 if sprinting else (2.3 if crouching else 3.6)
    var breath := sin(idle_phase) * 0.42 if not moving else 0.0
    var chest_breath := sin(idle_phase) * 0.32 if not moving else 0.0
    var body_bob := -absf(sin(gait_phase)) * (1.45 if sprinting else 0.75) if moving else breath
    if crouching:
        body_bob += 2.7

    # Pure 2D directional silhouette: side-on narrows the body, never pitches it in 3D.
    var shoulder_w_base := 7.8 if female else 8.8
    var shoulder_w := lerpf(shoulder_w_base,3.2,profile) + chest_breath
    var waist_w_base := 5.4 if female else 6.2
    var waist_w := lerpf(waist_w_base,3.7,profile)
    var hip_w_base := 6.6 if female else 6.0
    var hip_w := lerpf(hip_w_base,3.5,profile)
    var torso_top := -8.0 + body_bob - chest_breath*0.35
    var torso_bottom := 5.0 + body_bob
    var lean := move_dir * (1.2 if sprinting else 0.55)
    if crouching:
        lean *= 0.45

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

    var torso_color := _color(torso_id, Color("59685c") if role != "bandit" else Color("6a4d42"))
    var pants_color := _color(legs_id, Color("455663"))
    var boot_color := _color(feet_id, Color("433d35"))
    var glove_color := _color(hands_id, skin_color)
    var outline := Color("202725")

    # Lower-body rotation is still flat 2D: narrow separation + depth ordering only.
    var leg_depth := side * profile * 1.65
    var knee_half := lerpf(3.2,1.4,profile)
    var ankle_half := lerpf(3.8,1.25,profile)
    var l_hip := _q(Vector2(-hip_w*0.55,torso_bottom-0.5 + leg_depth*0.25)+lean*0.2)
    var r_hip := _q(Vector2( hip_w*0.55,torso_bottom-0.5 - leg_depth*0.25)+lean*0.2)
    var l_stride := stride_wave*stride_amp
    var r_stride := -l_stride
    var lateral := Vector2(-move_dir.y,move_dir.x)
    var l_knee := _q(Vector2(-knee_half,12.0+body_bob+leg_depth*0.65)+move_dir*l_stride*0.58+lateral*l_stride*0.10)
    var r_knee := _q(Vector2( knee_half,12.0+body_bob-leg_depth*0.65)+move_dir*r_stride*0.58+lateral*r_stride*0.10)
    var l_ankle := _q(Vector2(-ankle_half,21.0+body_bob+leg_depth*0.40)+move_dir*l_stride)
    var r_ankle := _q(Vector2( ankle_half,21.0+body_bob-leg_depth*0.40)+move_dir*r_stride)
    if moving:
        if stride_wave > 0.0:
            l_ankle.y -= lift_wave*(2.0 if sprinting else 1.25)
        else:
            r_ankle.y -= lift_wave*(2.0 if sprinting else 1.25)
    if crouching:
        l_knee.y += 2.0; r_knee.y += 2.0
        l_ankle.y -= 1.0; r_ankle.y -= 1.0

    func draw_leg_chain(hip: Vector2,knee: Vector2,ankle: Vector2,c: Color,stride: float,front: bool) -> void:
        var shade:=c if front else c.darkened(0.13)
        _limb(hip,knee,shade,4.9,outline)
        _joint(knee,shade.lightened(0.03),2.25,outline)
        _limb(knee,ankle,shade.darkened(0.02),4.45,outline)
        _joint(ankle,boot_color if front else boot_color.darkened(0.10),1.85,outline)
        _draw_boot(boots_id_or(feet_id),ankle,boot_color if front else boot_color.darkened(0.10),move_dir,stride,outline)

    # Far leg first, near leg last.
    var left_near := side < -0.15
    if profile > 0.38:
        if left_near:
            draw_leg_chain(r_hip,r_knee,r_ankle,pants_color,r_stride,false)
            draw_leg_chain(l_hip,l_knee,l_ankle,pants_color,l_stride,true)
        else:
            draw_leg_chain(l_hip,l_knee,l_ankle,pants_color,l_stride,false)
            draw_leg_chain(r_hip,r_knee,r_ankle,pants_color,r_stride,true)
    elif stride_wave >= 0.0:
        draw_leg_chain(r_hip,r_knee,r_ankle,pants_color,r_stride,false)
        draw_leg_chain(l_hip,l_knee,l_ankle,pants_color,l_stride,true)
    else:
        draw_leg_chain(l_hip,l_knee,l_ankle,pants_color,l_stride,false)
        draw_leg_chain(r_hip,r_knee,r_ankle,pants_color,r_stride,true)
    _draw_pants_detail(legs_id,l_knee,r_knee,pants_color)

    var torso := PackedVector2Array([
        _q(Vector2(-shoulder_w,torso_top)+lean),
        _q(Vector2(-shoulder_w+1.2,torso_top-2.0)+lean),
        _q(Vector2( shoulder_w-1.2,torso_top-2.0)+lean),
        _q(Vector2( shoulder_w,torso_top)+lean),
        _q(Vector2( waist_w,torso_bottom)+lean*0.35),
        _q(Vector2( hip_w,torso_bottom+2.0)),
        _q(Vector2(-hip_w,torso_bottom+2.0)),
        _q(Vector2(-waist_w,torso_bottom)+lean*0.35)
    ])

    var l_shoulder := _q(Vector2(-shoulder_w+0.8,torso_top-0.6 + side*profile*1.2)+lean)
    var r_shoulder := _q(Vector2( shoulder_w-0.8,torso_top-0.6 - side*profile*1.2)+lean)
    var arm_pose := _arm_pose(l_shoulder,r_shoulder,body_bob)
    _last_lw=arm_pose[1]; _last_rw=arm_pose[3]

    func draw_arm_chain(sh: Vector2,el: Vector2,wr: Vector2,c: Color,hand_c: Color,front: bool) -> void:
        var shade:=c if front else c.darkened(0.15)
        _joint(sh,shade,2.15,outline)
        _limb(sh,el,shade,4.25,outline)
        _joint(el,shade.lightened(0.03),2.0,outline)
        _limb(el,wr,shade.darkened(0.01),3.75,outline)
        _joint(wr,hand_c,1.6,outline)
        _hand(wr,hand_c,outline)

    # Arms behind torso first. When facing up, both belong behind the chest.
    var pure_side := profile > 0.86 and absf(aim.y) < 0.34
    var left_arm_near := side < -0.05
    if backness > 0.68:
        draw_arm_chain(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),false)
        draw_arm_chain(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,false)
    elif pure_side:
        if left_arm_near:
            draw_arm_chain(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,false)
        else:
            draw_arm_chain(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),false)
    else:
        # Diagonals/front: far arm behind torso.
        if left_arm_near:
            draw_arm_chain(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,false)
        else:
            draw_arm_chain(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),false)

    # Equipment follows depth: backpack behind when facing front, visible over back when facing up.
    if backness < 0.62:
        _draw_backpack(back_id,Vector2(0,body_bob),outline)

    _polygon(torso,torso_color,outline,1.6)
    _draw_torso_detail(torso_id,torso_color,torso_top,torso_bottom,waist_w,outline)

    var neck_center := _q(Vector2(lean.x*0.35,torso_top-3.0))
    draw_rect(Rect2(neck_center-Vector2(2.2,2.5),Vector2(4.4,5.5)),outline,true)
    draw_rect(Rect2(neck_center-Vector2(1.5,2.2),Vector2(3.0,4.8)),skin_color.darkened(0.06),true)

    _draw_armor(armor_id,Vector2(0,body_bob),outline)
    if backness >= 0.62:
        _draw_backpack(back_id,Vector2(0,body_bob),outline)

    # Near arm in front. Pure side deliberately shows only the near arm.
    if backness <= 0.68:
        if pure_side:
            if left_arm_near:
                draw_arm_chain(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),true)
            else:
                draw_arm_chain(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,true)
        elif left_arm_near:
            draw_arm_chain(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),true)
        else:
            draw_arm_chain(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,true)

    _draw_glove_detail(hands_id,arm_pose[1],arm_pose[3],glove_color)
    _draw_skeleton_weapon(arm_pose[1],arm_pose[3],outline)

    var head_center := _q(Vector2(lean.x*0.25 + side*0.75,-18.0+body_bob*0.45-chest_breath*0.20))
    _draw_head(head_center,female,outline)
    _draw_hair(head_center,female,outline)
    _draw_face_direction(head_center,outline)
    _draw_lower_face(lower_face_id,head_center,outline)
    _draw_eyes(eyes_id,head_center,outline)
    _draw_headwear(head_id,head_center,outline)
    _draw_binoculars(binoculars_id,Vector2(0,body_bob),outline)
'''

s=s[:start]+new_draw+s[end:]

# Better armed pose: wrists converge on a real grip/support line, while elbows stay bent.
arm_start=s.index("func _arm_pose(")
arm_end=s.index("\nfunc _draw_head",arm_start)
arm_func=r'''func _arm_pose(l_shoulder: Vector2, r_shoulder: Vector2, body_bob: float) -> Array:
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
        var rifle:=false
        var wid:=_weapon_id().to_lower()
        rifle=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)
        var grip_center:=_q(Vector2(0,-1.0+body_bob)+aim*(9.0 if rifle else 7.3))
        var support_sep:=1.8 if rifle else 1.35
        var l_wrist:=_q(grip_center + perp*support_sep - aim*(2.4 if rifle else 0.7))
        var r_wrist:=_q(grip_center - perp*support_sep)
        var bend:=3.4-profile*0.7
        var l_elbow:=_q((l_shoulder+l_wrist)*0.5+perp*bend)
        var r_elbow:=_q((r_shoulder+r_wrist)*0.5-perp*bend)
        return [l_elbow,l_wrist,r_elbow,r_wrist]

    var swing:=sin(gait_phase)*(3.2 if sprinting else 2.6) if move_velocity.length()>2.0 else sin(idle_phase)*0.28
    var l_elbow:=_q(Vector2(-7.5,0.5+body_bob+swing*0.35))
    var l_wrist:=_q(Vector2(-6.0,7.0+body_bob+swing))
    var r_elbow:=_q(Vector2(7.5,0.5+body_bob-swing*0.35))
    var r_wrist:=_q(Vector2(6.0,7.0+body_bob-swing))
    return [l_elbow,l_wrist,r_elbow,r_wrist]
'''
s=s[:arm_start]+arm_func+s[arm_end:]

# Replace weapon drawing with direction-correct flat 2D geometry.
w_start=s.index("func _draw_skeleton_weapon(")
w_end=s.index("\nfunc get_weapon_anchor",w_start)
weapon_func=r'''func _draw_skeleton_weapon(lw: Vector2, rw: Vector2, outline: Color) -> void:
    if _weapon_category() != "firearm":
        return
    var aim:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var wid:=_weapon_id().to_lower()
    var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)
    var grip:=rw
    var barrel_start:=grip + aim*(1.6 if rifle else 1.1)
    var muzzle:=barrel_start + aim*(13.8 if rifle else 7.0)
    var perp:=Vector2(-aim.y,aim.x)
    draw_line(barrel_start,muzzle,outline,4.3 if rifle else 3.4,true)
    draw_line(barrel_start,muzzle,Color("35393a"),2.7 if rifle else 2.1,true)
    # Handle always rotates with the gun rather than remaining screen-vertical.
    var handle_a:=grip-aim*0.5
    var handle_b:=grip-aim*1.0+perp*3.0
    draw_line(handle_a,handle_b,outline,3.1,true)
    draw_line(handle_a,handle_b,Color("4b4036"),1.9,true)
    if rifle:
        draw_line(grip-aim*1.6,grip-aim*5.4,outline,4.2,true)
        draw_line(grip-aim*1.6,grip-aim*5.4,Color("4a4037"),2.8,true)
        draw_line(lw,barrel_start+aim*4.0,Color("2d3030"),1.1,true)
'''
s=s[:w_start]+weapon_func+s[w_end:]

# Version/marker.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
h=h.replace('marker.text = "D2D.7  |  DRAWN SKELETON"','marker.text = "D2D.8  |  ORIENTED 2D BODY"',1)
hud.write_text(h,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e=re.sub(r'(?m)^version/code=\d+$','version/code=79',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.8"',e,count=1)
ep.write_text(e,encoding="utf-8")
sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.8"',q,count=1)
    sm.write_text(q,encoding="utf-8")

p.write_text(s,encoding="utf-8")
print("Applied D2D.8: directional 2D occlusion, breathing, richer joints/feet, corrected weapon rotation and equipment layering.")
