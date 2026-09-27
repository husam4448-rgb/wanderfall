#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/art/baked_actor_visual.gd"
s = p.read_text(encoding="utf-8")

# D2D.11 — explicit 8-direction body pose + continuous 360-degree firearm aim.
# Body/head/leg silhouette is quantized to 45-degree sectors.
# Hands/forearms/weapon continue to use the raw analog aim vector.

draw_anchor = "func _draw() -> void:\n"
if draw_anchor not in s:
    raise SystemExit("D2D.11 draw anchor missing")

helpers = r'''func _aim_direction() -> Vector2:
    return facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN

func _body_direction() -> Vector2:
    var a := _aim_direction()
    var step := PI / 4.0
    var ang := snappedf(atan2(a.y, a.x), step)
    return Vector2(cos(ang), sin(ang)).normalized()

func _body_direction_name() -> String:
    var d := _body_direction()
    if d.y < -0.92:
        return "N"
    if d.y > 0.92:
        return "S"
    if d.x > 0.92:
        return "E"
    if d.x < -0.92:
        return "W"
    if d.x > 0.0 and d.y < 0.0:
        return "NE"
    if d.x < 0.0 and d.y < 0.0:
        return "NW"
    if d.x > 0.0 and d.y > 0.0:
        return "SE"
    return "SW"

'''
if "func _body_direction() -> Vector2:" not in s:
    s = s.replace(draw_anchor, helpers + draw_anchor, 1)

old = "    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN\n"
new = "    var aim := _body_direction()\n    var aim_continuous := _aim_direction()\n"
if old not in s:
    raise SystemExit("D2D.11 body aim anchor missing")
s = s.replace(old, new, 1)

# D2D.10 head/hair/face are body presentation: snap them to the same 8-way pose.
head_expr = "    var d:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN\n"
count = s.count(head_expr)
if count < 3:
    raise SystemExit(f"D2D.11 expected 3 head direction anchors, found {count}")
s = s.replace(head_expr, "    var d:=_body_direction()\n", 3)

# Firearm arm solver + weapon geometry remain truly continuous.
arm_start = s.index("func _arm_pose(")
arm_end = s.index("\nfunc _draw_head", arm_start)
arm_block = s[arm_start:arm_end]
arm_old = "    var aim:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN\n"
if arm_old not in arm_block:
    raise SystemExit("D2D.11 arm aim anchor missing")
arm_block = arm_block.replace(arm_old, "    var aim:=_aim_direction()\n", 1)
s = s[:arm_start] + arm_block + s[arm_end:]

weapon_start = s.index("func _draw_skeleton_weapon(")
weapon_end = s.index("\nfunc get_weapon_anchor", weapon_start)
weapon_block = s[weapon_start:weapon_end]
if arm_old not in weapon_block:
    raise SystemExit("D2D.11 weapon aim anchor missing")
weapon_block = weapon_block.replace(arm_old, "    var aim:=_aim_direction()\n", 1)
s = s[:weapon_start] + weapon_block + s[weapon_end:]

# While armed, do not bury the rotating hands behind the torso.
behind_anchor = '''    # Arms behind torso first. When facing up, both belong behind the chest.
    var pure_side := profile > 0.86 and absf(aim.y) < 0.34
    var left_arm_near := side < -0.05
    if backness > 0.68:
'''
behind_repl = '''    # Body uses the snapped 8-way pose, while firearm hands rotate continuously.
    # For firearms, both arm chains are rendered in the foreground pass so 360-degree
    # aim never makes the hands vanish behind the torso.
    var firearm_aiming := _weapon_category() == "firearm"
    var pure_side := profile > 0.86 and absf(aim.y) < 0.34
    var left_arm_near := side < -0.05
    if firearm_aiming:
        pass
    elif backness > 0.68:
'''
if behind_anchor not in s:
    raise SystemExit("D2D.11 arm occlusion anchor missing")
s = s.replace(behind_anchor, behind_repl, 1)

front_anchor = '''    # Near arm in front. Pure side deliberately shows only the near arm.
    if backness <= 0.68:
        if pure_side:
'''
front_repl = '''    # Foreground arm pass.
    if firearm_aiming:
        # Keep both hands readable while they orbit continuously around the body.
        draw_arm_chain.call(l_shoulder,arm_pose[0],arm_pose[1],torso_color,glove_color.darkened(0.05),true)
        draw_arm_chain.call(r_shoulder,arm_pose[2],arm_pose[3],torso_color,glove_color,true)
    elif backness <= 0.68:
        if pure_side:
'''
if front_anchor not in s:
    raise SystemExit("D2D.11 foreground arm anchor missing")
s = s.replace(front_anchor, front_repl, 1)

# Pose-lab diagnostic: body direction is discrete; aim angle remains continuous.
pose_lab_anchor = "    _draw_binoculars(binoculars_id,Vector2(0,body_bob),outline)\n"
pose_lab_repl = '''    _draw_binoculars(binoculars_id,Vector2(0,body_bob),outline)

    # D2D.11 Pose Lab visual guides: short body ray + longer continuous aim ray.
    var body_ray := _body_direction()
    var raw_ray := _aim_direction()
    draw_line(Vector2.ZERO, body_ray * 13.0, Color(0.35,0.65,1.0,0.45), 1.0, true)
    draw_line(Vector2.ZERO, raw_ray * 19.0, Color(1.0,0.72,0.25,0.55), 1.0, true)
'''
if pose_lab_anchor not in s:
    raise SystemExit("D2D.11 pose-lab anchor missing")
s = s.replace(pose_lab_anchor, pose_lab_repl, 1)

hud = root / "scripts/mobile_hud.gd"
h = hud.read_text(encoding="utf-8")
h = re.sub(r'marker\.text = "D2D\.[^"]+"', 'marker.text = "D2D.11  |  8-DIR BODY + 360 AIM"', h, count=1)
hud.write_text(h, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$', 'version/code=84', e, count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.11"', e, count=1)
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    q = sm.read_text(encoding="utf-8")
    q = re.sub(r'const GAME_VERSION := "[^"]+"', 'const GAME_VERSION := "0.21.0D2D.11"', q, count=1)
    sm.write_text(q, encoding="utf-8")

p.write_text(s, encoding="utf-8")
print("Applied D2D.11: explicit 8-direction body poses, continuous 360-degree hands/weapon aim, and Pose Lab guides.")
