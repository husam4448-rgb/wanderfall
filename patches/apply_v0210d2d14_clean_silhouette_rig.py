#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/art/baked_actor_visual.gd"
s = p.read_text(encoding="utf-8")

# D2D.14 — clean silhouette rig.
# Preserve D2D.13 proportions + eight body poses, but reduce joint clutter and
# pose-lock upper arms to the 8-way body while forearms/hands/gun handle fine aim.

# 1) Cleaner line/joint language across the articulated character.
s = s.replace(
'''func _limb(a: Vector2, b: Vector2, fill: Color, width: float, outline: Color) -> void:
    draw_line(a, b, outline, width + 2.0, true)
    draw_line(a, b, fill, width, true)

func _joint(pos: Vector2, fill: Color, radius: float, outline: Color) -> void:
    draw_circle(pos, radius + 1.0, outline)
    draw_circle(pos, radius, fill)

func _hand(pos: Vector2, fill: Color, outline: Color) -> void:
    draw_circle(pos, 2.5, outline)
    draw_circle(pos, 1.7, fill)
''',
'''func _limb(a: Vector2, b: Vector2, fill: Color, width: float, outline: Color) -> void:
    draw_line(a, b, outline, width + 1.25, true)
    draw_line(a, b, fill, width, true)

func _joint(pos: Vector2, fill: Color, radius: float, outline: Color) -> void:
    draw_circle(pos, radius + 0.55, outline)
    draw_circle(pos, radius, fill)

func _hand(pos: Vector2, fill: Color, outline: Color) -> void:
    draw_circle(pos, 1.85, outline)
    draw_circle(pos, 1.25, fill)
''', 1)

# 2) Reduce knee/ankle/shoulder/elbow/wrist blob stacking in the D2D.12/13 renderer.
old_leg = '''    var draw_leg := func(hip:Vector2,knee:Vector2,ankle:Vector2,near:bool) -> void:
        var c := pants_color if near else pants_color.darkened(0.14)
        _limb(hip,knee,c,4.85,outline)
        _joint(knee,c.lightened(0.03),2.3,outline)
        _limb(knee,ankle,c.darkened(0.03),4.45,outline)
        _joint(ankle,boot_color if near else boot_color.darkened(0.10),1.8,outline)
        _draw_pose_boot(ankle,boot_color,body_dir,outline,near)
'''
new_leg = '''    var draw_leg := func(hip:Vector2,knee:Vector2,ankle:Vector2,near:bool) -> void:
        var c := pants_color if near else pants_color.darkened(0.12)
        _limb(hip,knee,c,4.45,outline)
        _joint(knee,c.lightened(0.02),1.45,outline)
        _limb(knee,ankle,c.darkened(0.02),4.05,outline)
        _draw_pose_boot(ankle,boot_color,body_dir,outline,near)
'''
if old_leg not in s:
    raise SystemExit("D2D.14 clean-leg anchor missing")
s = s.replace(old_leg,new_leg,1)

old_arm = '''    var draw_arm := func(sh:Vector2,el:Vector2,wr:Vector2,near:bool) -> void:
        var c := torso_color if near else torso_color.darkened(0.15)
        var hc := glove_color if near else glove_color.darkened(0.08)
        _joint(sh,c,2.1,outline)
        _limb(sh,el,c,4.0,outline)
        _joint(el,c.lightened(0.03),2.0,outline)
        _limb(el,wr,c.darkened(0.02),3.45,outline)
        _joint(wr,hc,1.6,outline)
        _hand(wr,hc,outline)
'''
new_arm = '''    var draw_arm := func(sh:Vector2,el:Vector2,wr:Vector2,near:bool) -> void:
        var c := torso_color if near else torso_color.darkened(0.12)
        var hc := glove_color if near else glove_color.darkened(0.06)
        # No shoulder/wrist balls: continuous segments read as one arm instead of stacked pieces.
        _limb(sh,el,c,3.65,outline)
        _joint(el,c.lightened(0.02),1.20,outline)
        _limb(el,wr,c.darkened(0.01),3.05,outline)
        _hand(wr,hc,outline)
'''
if old_arm not in s:
    raise SystemExit("D2D.14 clean-arm anchor missing")
s = s.replace(old_arm,new_arm,1)

# 3) Slimmer, less blocky boots.
boot_start=s.index("func _draw_pose_boot(")
boot_end=s.index("\n\nfunc _draw()",boot_start)
clean_boot=r'''func _draw_pose_boot(ankle: Vector2, color: Color, body_dir: Vector2, outline: Color, near: bool) -> void:
    var d := body_dir.normalized() if body_dir.length_squared() > 0.0001 else Vector2.DOWN
    var toe := _q(ankle + Vector2(d.x*3.0,d.y*2.15+0.8))
    var c := color if near else color.darkened(0.10)
    draw_line(ankle,toe,outline,4.7,true)
    draw_line(ankle,toe,c,3.35,true)
    var side:=Vector2(-d.y,d.x)
    draw_line(toe-side*1.55,toe+side*1.55,c.darkened(0.14),1.55,true)
'''
s=s[:boot_start]+clean_boot+s[boot_end:]

# 4) Replace firearm arm solver: upper arms follow quantized body direction;
#    wrists retain continuous analog aim. This removes the rotating "spaghetti shoulder" look.
a=s.index("func _arm_pose(")
b=s.index("\nfunc _draw_head",a)
new_pose=r'''func _arm_pose(l_shoulder: Vector2, r_shoulder: Vector2, body_bob: float) -> Array:
    var category:=_weapon_category()
    var aim:=_aim_direction()
    var body_aim:=_body_direction()
    var body_perp:=Vector2(-body_aim.y,body_aim.x)
    var moving:=move_velocity.length()>2.0

    if melee_time > 0.0:
        var progress:=1.0-melee_time/MELEE_DURATION
        var swing:=lerpf(-0.95,0.95,sin(progress*PI*0.5))
        var attack_dir:=melee_direction.rotated(swing)
        var attack_perp:=Vector2(-attack_dir.y,attack_dir.x)
        var wrist:=_q(Vector2(0,-1+body_bob)+attack_dir*13.0)
        var elbow:=_q(r_shoulder+body_aim*5.5-body_perp*0.7)
        var support_wrist:=_q(Vector2(0,0.5+body_bob)+attack_dir*7.0-attack_perp*2.4)
        var support_elbow:=_q(l_shoulder+body_aim*5.0+body_perp*0.7)
        return [support_elbow,support_wrist,elbow,wrist]

    if category=="firearm":
        var wid:=_weapon_id().to_lower()
        var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)
        var reach:=18.0 if rifle else 16.3
        if moving:
            reach-=0.7

        var chest:=Vector2(0.0,-1.4+body_bob)
        var r_wrist:=_q(chest+aim*reach)
        var support_back:=4.0 if rifle else 1.10
        var support_side:=1.15 if rifle else 0.72
        var aim_perp:=Vector2(-aim.y,aim.x)
        var l_wrist:=_q(r_wrist-aim*support_back-aim_perp*support_side)

        # Upper arms are anchored to the discrete 8-way body pose.
        # Only the forearms bridge from these stable elbows to the continuously moving wrists.
        var l_elbow:=_q(l_shoulder+body_aim*5.55+body_perp*0.80)
        var r_elbow:=_q(r_shoulder+body_aim*5.75-body_perp*0.80)

        # Side profiles need a small vertical separation so the two forearms remain readable.
        if absf(body_aim.x)>0.90:
            if body_aim.x>0.0:
                l_elbow.y+=1.0
                r_elbow.y-=0.7
            else:
                l_elbow.y-=0.7
                r_elbow.y+=1.0

        return [l_elbow,l_wrist,r_elbow,r_wrist]

    # Relaxed unarmed pose keeps the same long-limb proportions but avoids oversized joints.
    var sway:=sin(gait_phase)*(2.6 if moving else 0.0)
    var l_elbow:=_q(l_shoulder+Vector2(-0.8,8.5+sway*0.20))
    var l_wrist:=_q(l_elbow+Vector2(0.7,8.0+sway*0.45))
    var r_elbow:=_q(r_shoulder+Vector2(0.8,8.5-sway*0.20))
    var r_wrist:=_q(r_elbow+Vector2(-0.7,8.0-sway*0.45))
    return [l_elbow,l_wrist,r_elbow,r_wrist]
'''
s=s[:a]+new_pose+s[b:]

# 5) Replace backpack with slimmer shapes so rear views no longer read as a large rectangle.
bp0=s.index("func _draw_backpack(")
bp1=s.index("\nfunc _draw_boot(",bp0)
backpack=r'''func _draw_backpack(item_id: String, offset: Vector2, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c:=_color(item_id,Color("536052"))
    var center:=Vector2(0,-0.2)+offset
    var half_w:=4.4
    var top:=-5.4
    var bottom:=8.0
    if item_id in ["daypack","hiking_pack","tactical_pack"]:
        half_w=5.0
        top=-6.2
        bottom=9.5
    var p:=PackedVector2Array([
        center+Vector2(-half_w+0.7,top),
        center+Vector2(half_w-0.7,top),
        center+Vector2(half_w,bottom-2.0),
        center+Vector2(half_w-1.0,bottom),
        center+Vector2(-half_w+1.0,bottom),
        center+Vector2(-half_w,bottom-2.0)
    ])
    _polygon(p,c.darkened(0.03),outline,1.0)
    draw_line(center+Vector2(-half_w+1.2,1.5),center+Vector2(half_w-1.2,1.5),c.darkened(0.13),0.9)
    if item_id in ["hiking_pack","tactical_pack"]:
        draw_rect(Rect2(center+Vector2(-2.9,4.0),Vector2(5.8,3.0)),c.darkened(0.12),true)
'''
s=s[:bp0]+backpack+s[bp1:]

# 6) Slim armor/vest silhouette, especially front/rear rectangles.
ar0=s.index("func _draw_armor(")
ar1=s.index("\nfunc _draw_lower_face(",ar0)
armor=r'''func _draw_armor(item_id: String, offset: Vector2, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c:=_color(item_id,Color("4d574d"))
    var y:=offset.y
    var p:=PackedVector2Array([
        Vector2(-6.1,-6.8+y),Vector2(6.1,-6.8+y),
        Vector2(5.2,3.9+y),Vector2(3.9,5.0+y),
        Vector2(-3.9,5.0+y),Vector2(-5.2,3.9+y)
    ])
    _polygon(p,c,outline,1.0)
    if item_id=="plate_carrier":
        draw_rect(Rect2(-4.4,-4.7+y,8.8,4.8),c.lightened(0.05),true)
        draw_rect(Rect2(-3.8,1.0+y,3.0,2.4),c.darkened(0.15),true)
        draw_rect(Rect2(0.8,1.0+y,3.0,2.4),c.darkened(0.15),true)
    elif item_id=="tactical_vest":
        draw_line(Vector2(0,-5.6+y),Vector2(0,3.7+y),c.darkened(0.18),0.9)
        draw_rect(Rect2(-3.8,0.6+y,3.0,2.3),c.darkened(0.12),true)
        draw_rect(Rect2(0.8,0.6+y,3.0,2.3),c.darkened(0.12),true)
'''
s=s[:ar0]+armor+s[ar1:]

# 7) Tighten side-profile armor generated directly by D2D.12.
s=s.replace('Vector2(-3.1+sx*0.5,-7.2)', 'Vector2(-2.55+sx*0.4,-6.7)', 1)
s=s.replace('Vector2(3.0+sx*0.5,-6.6)', 'Vector2(2.55+sx*0.4,-6.2)', 1)
s=s.replace('Vector2(2.4+sx*0.5,3.8)', 'Vector2(2.15+sx*0.4,3.5)', 1)
s=s.replace('Vector2(-2.7+sx*0.5,3.6)', 'Vector2(-2.20+sx*0.4,3.4)', 1)

# Version / marker.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
h=re.sub(r'marker\.text = "D2D\.[^"]+"','marker.text = "D2D.14  |  CLEAN SILHOUETTE RIG"',h,count=1)
hud.write_text(h,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e=re.sub(r'(?m)^version/code=\d+$','version/code=87',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.14"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.14"',q,count=1)
    sm.write_text(q,encoding="utf-8")

p.write_text(s,encoding="utf-8")
print("Applied D2D.14: pose-locked upper arms, clean joints/hands/boots, slimmer pack/armor, preserved 360 forearm aim.")
