#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/art/baked_actor_visual.gd"
s = p.read_text(encoding="utf-8")

# D2D.13 — anatomy/proportion correction + extended aim + directional gun occlusion.
# Keeps the D2D.12 eight explicit body poses.

# 1) Lengthen legs from the existing explicit pose anchors without changing direction identity.
leg_anchor = '''    var l_ankle:Vector2 = _q(pose["l_ankle"]+body_offset)
    var r_ankle:Vector2 = _q(pose["r_ankle"]+body_offset)

    # Locomotion moves around the explicit pose; idle/aiming never changes the leg pose.
'''
leg_repl = '''    var l_ankle:Vector2 = _q(pose["l_ankle"]+body_offset)
    var r_ankle:Vector2 = _q(pose["r_ankle"]+body_offset)

    # D2D.13 proportions: keep each 8-way pose, but restore adult-length thighs/shins.
    l_knee = _q(l_hip + (l_knee-l_hip)*1.18)
    r_knee = _q(r_hip + (r_knee-r_hip)*1.18)
    l_ankle = _q(l_knee + (l_ankle-l_knee)*1.18)
    r_ankle = _q(r_knee + (r_ankle-r_knee)*1.18)

    # Locomotion moves around the explicit pose; idle/aiming never changes the leg pose.
'''
if leg_anchor not in s:
    raise SystemExit("D2D.13 leg proportion anchor missing")
s = s.replace(leg_anchor, leg_repl, 1)

# Slightly reduce limb thickness so longer anatomy does not read as a compact block.
s = s.replace('_limb(hip,knee,c,5.25,outline)', '_limb(hip,knee,c,4.85,outline)', 1)
s = s.replace('_limb(knee,ankle,c.darkened(0.03),4.8,outline)', '_limb(knee,ankle,c.darkened(0.03),4.45,outline)', 1)
s = s.replace('_limb(sh,el,c,4.25,outline)', '_limb(sh,el,c,4.0,outline)', 1)
s = s.replace('_limb(el,wr,c.darkened(0.02),3.75,outline)', '_limb(el,wr,c.darkened(0.02),3.45,outline)', 1)

# 2) Replace firearm arm solver with longer, genuinely extended aim pose.
a = s.index("func _arm_pose(")
b = s.index("\nfunc _draw_head", a)
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
        var wrist:=_q(Vector2(0,-1+body_bob)+attack_dir*13.0)
        var elbow:=_q(r_shoulder.lerp(wrist,0.58)+attack_perp*2.6)
        var support_wrist:=_q(Vector2(0,0.5+body_bob)+attack_dir*7.0-attack_perp*2.4)
        var support_elbow:=_q(l_shoulder.lerp(support_wrist,0.56)-attack_perp*2.0)
        return [support_elbow,support_wrist,elbow,wrist]

    if category=="firearm":
        var wid:=_weapon_id().to_lower()
        var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)

        # Longer adult arm envelope. The dominant wrist is pushed well clear of the chest.
        var reach:=18.2 if rifle else 16.6
        if moving:
            reach-=0.8
        var chest:=Vector2(0.0,-1.4+body_bob)
        var r_wrist:=_q(chest+aim*reach)

        # Support hand cups the pistol grip (or fore-end for a long gun) without
        # collapsing both forearms into the torso.
        var support_back:=4.2 if rifle else 1.15
        var support_side:=1.25 if rifle else 0.85
        var l_wrist:=_q(r_wrist-aim*support_back-perp*support_side)

        # Elbows sit farther along the shoulder-to-hand segment. Small lateral bend
        # keeps a human elbow angle while allowing the arms to look extended.
        var bend:=2.0 if rifle else 1.65
        var l_elbow:=_q(l_shoulder.lerp(l_wrist,0.62)+perp*bend)
        var r_elbow:=_q(r_shoulder.lerp(r_wrist,0.64)-perp*bend)

        # For pure side aim, drop the lower elbow slightly instead of folding both arms.
        if absf(aim.x)>0.86:
            if aim.x>0.0:
                l_elbow.y+=1.4
                r_elbow.y-=0.6
            else:
                l_elbow.y-=0.6
                r_elbow.y+=1.4
        return [l_elbow,l_wrist,r_elbow,r_wrist]

    # Unarmed limbs are also lengthened so the character does not revert to short arms.
    var sway:=sin(gait_phase)*(3.0 if moving else 0.0)
    var l_elbow:=_q(l_shoulder+Vector2(-1.1,8.8+sway*0.25))
    var l_wrist:=_q(l_elbow+Vector2(0.9,8.2+sway*0.55))
    var r_elbow:=_q(r_shoulder+Vector2(1.1,8.8-sway*0.25))
    var r_wrist:=_q(r_elbow+Vector2(-0.9,8.2-sway*0.55))
    return [l_elbow,l_wrist,r_elbow,r_wrist]
'''
s = s[:a] + new_arm + s[b:]

# 3) Directional draw order: the gun belongs with the dominant/right arm depth.
depth_anchor = '''    var back_view:bool = pose["back"]
    var front_view:bool = pose["front"]
    var profile_view:bool = pose["profile"]

    # Backpacks are behind front/profile poses but visibly sit on top of north-facing backs.
'''
depth_repl = '''    var back_view:bool = pose["back"]
    var front_view:bool = pose["front"]
    var profile_view:bool = pose["profile"]

    # D2D.13 weapon depth:
    # - N/NE/NW: right/dominant arm and weapon are behind the torso.
    # - W profile: right arm is the far arm, so the weapon is also behind.
    # - S/SE/SW/E: weapon remains foreground.
    var weapon_behind:=back_view or (profile_view and left_near)

    # Backpacks are behind front/profile poses but visibly sit on top of north-facing backs.
'''
if depth_anchor not in s:
    raise SystemExit("D2D.13 weapon depth anchor missing")
s = s.replace(depth_anchor, depth_repl, 1)

rear_anchor = '''    elif not front_view:
        if left_near:
            draw_arm.call(r_shoulder,arm_pose[2],arm_pose[3],false)
        else:
            draw_arm.call(l_shoulder,arm_pose[0],arm_pose[1],false)

    _polygon(torso_pts,torso_color,outline,1.6)
'''
rear_repl = '''    elif not front_view:
        if left_near:
            draw_arm.call(r_shoulder,arm_pose[2],arm_pose[3],false)
        else:
            draw_arm.call(l_shoulder,arm_pose[0],arm_pose[1],false)

    # Draw far-side weapon before the torso so the body correctly occludes it.
    if weapon_behind:
        _draw_skeleton_weapon(arm_pose[1],arm_pose[3],outline)

    _polygon(torso_pts,torso_color,outline,1.6)
'''
if rear_anchor not in s:
    raise SystemExit("D2D.13 rear weapon insertion anchor missing")
s = s.replace(rear_anchor, rear_repl, 1)

front_arm_old = '''    elif not back_view:
        if left_near:
            draw_arm.call(l_shoulder,arm_pose[0],arm_pose[1],true)
        else:
            draw_arm.call(r_shoulder,arm_pose[2],arm_pose[3],true)
    else:
        _hand(arm_pose[1],glove_color.darkened(0.05),outline)
        _hand(arm_pose[3],glove_color,outline)

    _draw_glove_detail(hands_id,arm_pose[1],arm_pose[3],glove_color)
    _draw_skeleton_weapon(arm_pose[1],arm_pose[3],outline)
'''
front_arm_new = '''    elif not back_view:
        if left_near:
            draw_arm.call(l_shoulder,arm_pose[0],arm_pose[1],true)
        else:
            draw_arm.call(r_shoulder,arm_pose[2],arm_pose[3],true)
    # back_view arms/hands were already rendered in the rear pass.

    if not back_view:
        _draw_glove_detail(hands_id,arm_pose[1],arm_pose[3],glove_color)
    if not weapon_behind:
        _draw_skeleton_weapon(arm_pose[1],arm_pose[3],outline)
'''
if front_arm_old not in s:
    raise SystemExit("D2D.13 foreground weapon anchor missing")
s = s.replace(front_arm_old, front_arm_new, 1)

# 4) Slimmer firearm geometry. Pistol is the main on-screen offender.
w0 = s.index("func _draw_skeleton_weapon(")
w1 = s.index("\nfunc get_weapon_anchor", w0)
new_weapon = r'''func _draw_skeleton_weapon(lw: Vector2, rw: Vector2, outline: Color) -> void:
    if _weapon_category()!="firearm":
        return
    var aim:=_aim_direction()
    var perp:=Vector2(-aim.y,aim.x)
    var wid:=_weapon_id().to_lower()
    var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)
    var grip:=rw

    if rifle:
        var body_start:=grip-aim*0.6
        var body_end:=grip+aim*7.5
        var muzzle:=body_end+aim*7.2
        draw_line(body_start,body_end,outline,4.2,true)
        draw_line(body_start,body_end,Color("35393a"),2.45,true)
        draw_line(body_end,muzzle,outline,2.6,true)
        draw_line(body_end,muzzle,Color("252a2c"),1.45,true)
        draw_line(body_start,body_start-aim*4.8,outline,3.7,true)
        draw_line(body_start,body_start-aim*4.8,Color("4a4037"),2.2,true)
        return

    # Slim pistol: readable at gameplay scale without looking like a block.
    var slide_start:=grip-aim*0.45
    var slide_end:=grip+aim*5.8
    draw_line(slide_start,slide_end,outline,3.25,true)
    draw_line(slide_start,slide_end,Color("34383a"),1.75,true)

    # Narrow angled grip, anchored exactly at the dominant hand.
    var handle_end:=grip-aim*0.9+perp*2.8
    draw_line(grip,handle_end,outline,2.7,true)
    draw_line(grip,handle_end,Color("4b4036"),1.45,true)

    # Small support-hand bridge; no thick bar across the forearms.
    draw_line(lw,grip-aim*0.15,Color("6a5542"),1.15,true)
'''
s = s[:w0] + new_weapon + s[w1:]

# Version / marker.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
h=re.sub(r'marker\.text = "D2D\.[^"]+"','marker.text = "D2D.13  |  LONG LIMBS + DEPTH AIM"',h,count=1)
hud.write_text(h,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e=re.sub(r'(?m)^version/code=\d+$','version/code=86',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.13"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.13"',q,count=1)
    sm.write_text(q,encoding="utf-8")

p.write_text(s,encoding="utf-8")
print("Applied D2D.13: longer arms/legs, slimmer firearm geometry, extended aim, and directional weapon occlusion.")
