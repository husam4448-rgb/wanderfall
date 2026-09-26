#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/baked_actor_visual.gd"
s=p.read_text(encoding="utf-8")

# 1) Fix arm draw-order policy.
old=r'''    # Arms behind torso first. When facing up, both belong behind the chest.
    var pure_side := profile > 0.86 and absf(aim.y) < 0.34
    var left_arm_near := side < -0.05
    if backness > 0.68:
        draw_arm_chain.call(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),false)
        draw_arm_chain.call(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,false)
    elif pure_side:
        if left_arm_near:
            draw_arm_chain.call(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,false)
        else:
            draw_arm_chain.call(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),false)
    else:
        # Diagonals/front: far arm behind torso.
        if left_arm_near:
            draw_arm_chain.call(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,false)
        else:
            draw_arm_chain.call(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),false)
'''
new=r'''    # Correct 2D arm depth policy:
    # South/front = both arms in front.
    # Side/diagonals = only the far arm behind.
    # North/back = both arms behind the torso.
    var pure_side := profile > 0.86 and absf(aim.y) < 0.34
    var front_facing := aim.y > 0.62
    var back_facing := aim.y < -0.62
    var left_arm_near := side < -0.05
    if back_facing:
        draw_arm_chain.call(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.08),false)
        draw_arm_chain.call(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color.darkened(0.08),false)
    elif not front_facing:
        if left_arm_near:
            draw_arm_chain.call(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color.darkened(0.10),false)
        else:
            draw_arm_chain.call(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.10),false)
'''
if old not in s:
    raise SystemExit("D2D.8.1 rear-arm block anchor missing")
s=s.replace(old,new,1)

old2=r'''    # Near arm in front. Pure side deliberately shows only the near arm.
    if backness <= 0.68:
        if pure_side:
            if left_arm_near:
                draw_arm_chain.call(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),true)
            else:
                draw_arm_chain.call(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,true)
        elif left_arm_near:
            draw_arm_chain.call(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),true)
        else:
            draw_arm_chain.call(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,true)
'''
new2=r'''    # Front-facing keeps BOTH arms in front. Side/diagonal keeps only near arm in front.
    if not back_facing:
        if front_facing:
            draw_arm_chain.call(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.03),true)
            draw_arm_chain.call(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,true)
        elif left_arm_near:
            draw_arm_chain.call(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.03),true)
        else:
            draw_arm_chain.call(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,true)
'''
if old2 not in s:
    raise SystemExit("D2D.8.1 front-arm block anchor missing")
s=s.replace(old2,new2,1)

# 2) Replace armed pose with a dedicated side-extension solution.
a=s.index("func _arm_pose(")
b=s.index("\nfunc _draw_head",a)
arm=r'''func _arm_pose(l_shoulder: Vector2, r_shoulder: Vector2, body_bob: float) -> Array:
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

        # Side aiming needs visibly extended arms.
        if profile > 0.78 and absf(aim.y) < 0.50:
            var dominant_wrist:=_q(Vector2(0,-1.2+body_bob)+aim*(11.5 if rifle else 9.3))
            var support_wrist:=_q(dominant_wrist-aim*(4.0 if rifle else 1.6)+perp*(1.2 if aim.x>0.0 else -1.2))
            var dominant_shoulder:=r_shoulder if aim.x>0.0 else l_shoulder
            var support_shoulder:=l_shoulder if aim.x>0.0 else r_shoulder
            var dominant_elbow:=_q((dominant_shoulder+dominant_wrist)*0.5 - perp*(1.7 if aim.x>0.0 else -1.7))
            var support_elbow:=_q((support_shoulder+support_wrist)*0.5 + perp*(2.6 if aim.x>0.0 else -2.6))
            if aim.x>0.0:
                return [support_elbow,support_wrist,dominant_elbow,dominant_wrist]
            return [dominant_elbow,dominant_wrist,support_elbow,support_wrist]

        # Front/back/diagonal two-hand aim.
        var grip_center:=_q(Vector2(0,-1.0+body_bob)+aim*(9.0 if rifle else 7.4))
        var l_wrist:=_q(grip_center + perp*1.45 - aim*(2.8 if rifle else 0.8))
        var r_wrist:=_q(grip_center - perp*1.45)
        var l_elbow:=_q((l_shoulder+l_wrist)*0.5+perp*3.2)
        var r_elbow:=_q((r_shoulder+r_wrist)*0.5-perp*3.2)
        return [l_elbow,l_wrist,r_elbow,r_wrist]

    var swing:=sin(gait_phase)*(3.2 if sprinting else 2.6) if move_velocity.length()>2.0 else sin(idle_phase)*0.28
    var l_elbow:=_q(Vector2(-7.5,0.5+body_bob+swing*0.35))
    var l_wrist:=_q(Vector2(-6.0,7.0+body_bob+swing))
    var r_elbow:=_q(Vector2(7.5,0.5+body_bob-swing*0.35))
    var r_wrist:=_q(Vector2(6.0,7.0+body_bob-swing))
    return [l_elbow,l_wrist,r_elbow,r_wrist]
'''
s=s[:a]+arm+s[b:]

# 3) Weapon transform is derived from BOTH hand anchors; gun must sit in the hands.
w=s.index("func _draw_skeleton_weapon(")
x=s.index("\nfunc get_weapon_anchor",w)
weapon=r'''func _draw_skeleton_weapon(lw: Vector2, rw: Vector2, outline: Color) -> void:
    if _weapon_category() != "firearm":
        return

    var aim:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var wid:=_weapon_id().to_lower()
    var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)

    # Dominant grip is the forward hand; support hand stays on the weapon body.
    var grip:=rw
    if aim.x < -0.72:
        grip=lw
    var support:=lw if grip==rw else rw

    var hand_axis:=(grip-support).normalized()
    if hand_axis.length_squared()<0.01:
        hand_axis=aim
    # Never let hand noise reverse the barrel: facing remains the authoritative 2D aim.
    var gun_dir:=aim
    var perp:=Vector2(-gun_dir.y,gun_dir.x)

    var body_start:=support.lerp(grip,0.55)
    var body_end:=body_start+gun_dir*(7.5 if rifle else 3.8)
    var muzzle:=body_end+gun_dir*(8.0 if rifle else 4.3)

    draw_line(body_start,body_end,outline,5.0 if rifle else 4.0,true)
    draw_line(body_start,body_end,Color("35393a"),3.0 if rifle else 2.4,true)
    draw_line(body_end,muzzle,outline,3.0 if rifle else 2.5,true)
    draw_line(body_end,muzzle,Color("252a2c"),1.8 if rifle else 1.5,true)

    # Grip originates exactly at dominant hand.
    var handle_end:=grip-gun_dir*0.7+perp*(3.0 if aim.x>=0.0 else -3.0)
    draw_line(grip,handle_end,outline,3.2,true)
    draw_line(grip,handle_end,Color("4b4036"),1.9,true)

    if rifle:
        var stock_end:=body_start-gun_dir*5.2
        draw_line(body_start,stock_end,outline,4.3,true)
        draw_line(body_start,stock_end,Color("4a4037"),2.7,true)
'''
s=s[:w]+weapon+s[x:]

# Version/marker.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
h=h.replace('marker.text = "D2D.8  |  ORIENTED 2D BODY"','marker.text = "D2D.8.1  |  AIM + ARMS FIX"',1)
hud.write_text(h,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e=re.sub(r'(?m)^version/code=\d+$','version/code=80',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.8.1"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.8.1"',q,count=1)
    sm.write_text(q,encoding="utf-8")

p.write_text(s,encoding="utf-8")
print("Applied D2D.8.1 front-arm visibility, side aim extension, and hand-bound weapon fix.")
