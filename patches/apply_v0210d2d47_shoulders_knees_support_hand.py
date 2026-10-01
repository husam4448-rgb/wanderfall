#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.47 requires D2D.46 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.46 GEAR:"', 'title.text = "D2D.47 GEAR:"', 1)

# Weapon-hand policy: current long gun uses two hands; future pistols/melee can set false.
anchor = 'var visual_zoom := 1.0\n'
if anchor not in s:
    raise SystemExit("D2D.47 weapon mode anchor missing")
s = s.replace(anchor, anchor + 'var weapon_two_handed := true\n', 1)

# Remove artificial shoulder joint circles from the unequipped torso.
old_base_torso = '''    if not gear_torso:
        # Same authored torso silhouette and dimensions as equipped state,
        # but flattened to plain shirt/body coloring.
        draw_circle(base + Vector2(-8.5,-8.0), 4.6, Color("4e594b"))
        draw_circle(base + Vector2(8.5,-8.0), 4.6, Color("4e594b"))
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
new_base_torso = '''    if not gear_torso:
        # Same authored torso silhouette/dimensions as equipped state,
        # but without artificial shoulder-joint balls.
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if old_base_torso not in s:
    raise SystemExit("D2D.47 base torso anchor missing")
s = s.replace(old_base_torso, new_base_torso, 1)

# Remove black shoulder balls from the equipped vest too.
old_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    # D2D.45: authored torso mirrors with the same L/R aim state as gun/hands.
    # Fill both shoulder-socket areas beneath the transparent sprite so the
    # authored circular joint reads as solid black instead of a hole.
    draw_circle(base + Vector2(-8.5,-8.0), 4.6, Color("080909"))
    draw_circle(base + Vector2(8.5,-8.0), 4.6, Color("080909"))
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
new_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    # D2D.47: clean authored torso; no artificial shoulder-joint circles.
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if old_vest not in s:
    raise SystemExit("D2D.47 equipped torso anchor missing")
s = s.replace(old_vest, new_vest, 1)

# Both knees must face the character's forward direction.
old_leg_orientation = '''    if gear_legs:
        _draw_equipment_texture(tex_gear_legs, mid, Vector2(16.5,26.5), side > 0.0, leg_angle)
    else:
        _draw_equipment_texture(tex_base_leg, mid, Vector2(16.5,26.5), side > 0.0, leg_angle)
'''
new_leg_orientation = '''    # D2D.47: both leg/knee sprites face forward with the character.
    # Do not mirror one leg inward toward the other.
    var leg_flip := dir_sign < 0.0
    if gear_legs:
        _draw_equipment_texture(tex_gear_legs, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
    else:
        _draw_equipment_texture(tex_base_leg, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
'''
if old_leg_orientation not in s:
    raise SystemExit("D2D.47 leg orientation anchor missing")
s = s.replace(old_leg_orientation, new_leg_orientation, 1)

# Create a dedicated support-hand renderer with no trigger-finger silhouette.
hand_func_anchor = '''func _draw_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:
'''
if hand_func_anchor not in s:
    raise SystemExit("D2D.47 hand function anchor missing")
support_func = '''func _draw_support_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:
    # Fore-end support grip: compact palm/fingers wrapped around the weapon.
    # Intentionally no extended trigger/index finger.
    var palm := [
        Vector2(-4.2,-2.3) * scale,
        Vector2(2.8,-2.6) * scale,
        Vector2(4.2,-1.0) * scale,
        Vector2(3.6,2.4) * scale,
        Vector2(-2.8,2.7) * scale,
        Vector2(-4.4,1.1) * scale
    ]
    var pts := PackedVector2Array()
    for p in palm:
        pts.append(center + _pose_point(p, angle, dir_sign))
    draw_colored_polygon(pts, color)
    # Short wrapped thumb only.
    var thumb := center + _pose_point(Vector2(1.5,2.3) * scale, angle, dir_sign)
    draw_circle(thumb, 1.1 * scale, color)

'''
s = s.replace(hand_func_anchor, support_func + hand_func_anchor, 1)

# Replace support-hand draws while preserving dominant/trigger hand.
old_support_block = '''    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
    if not face_right:
        _draw_hand(hand_front + _pose_point(Vector2(0,2.0), angle, dir_sign), angle, dir_sign, Color("ad704f"))

    draw_line(stock_a, muzzle, Color("34383a"), 6.0, true)
'''
new_support_block = '''    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
    # One-handed weapons intentionally skip this hand completely.
    if weapon_two_handed and not face_right:
        _draw_support_hand(hand_front + _pose_point(Vector2(0,2.0), angle, dir_sign), angle, dir_sign, Color("ad704f"), 1.08)

    draw_line(stock_a, muzzle, Color("34383a"), 6.0, true)
'''
if old_support_block not in s:
    raise SystemExit("D2D.47 pre-weapon support-hand anchor missing")
s = s.replace(old_support_block, new_support_block, 1)

old_final_hands = '''    _draw_hand(hand_rear, angle, dir_sign, Color("c98e68"))
    if face_right:
        _draw_hand(hand_front, angle, dir_sign, Color("b97755"))
    else:
        _draw_hand(hand_front + _pose_point(Vector2(0,2.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.62)
'''
new_final_hands = '''    # Dominant/trigger hand is always present.
    _draw_hand(hand_rear, angle, dir_sign, Color("c98e68"))

    # Support hand only exists for two-handed weapons.
    if weapon_two_handed:
        if face_right:
            _draw_support_hand(hand_front, angle, dir_sign, Color("b97755"), 1.08)
        else:
            _draw_support_hand(hand_front + _pose_point(Vector2(0,2.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.72)
'''
if old_final_hands not in s:
    raise SystemExit("D2D.47 final hand anchor missing")
s = s.replace(old_final_hands, new_final_hands, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=120',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.47"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.47 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.47"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.47: clean shoulders, forward knees, support-hand grip, one-hand weapon policy.")
