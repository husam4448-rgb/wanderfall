#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.48 requires D2D.47 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.47 GEAR:"', 'title.text = "D2D.48 GEAR:"', 1)

# Move head pivot slightly forward in facing direction.
old_head_pivot = '''    var neck_anchor := base + Vector2(0,-16.0)
'''
new_head_pivot = '''    var neck_anchor := base + Vector2(1.6 * dir_sign,-16.0)
'''
if old_head_pivot not in s:
    raise SystemExit("D2D.48 head pivot anchor missing")
s = s.replace(old_head_pivot, new_head_pivot, 1)

# Helmet must use the same forward-shifted neck pivot.
old_helmet_pivot = '''    var neck_anchor := base + Vector2(0,-16.0)
    draw_set_transform(neck_anchor, head_rot, Vector2(dir_sign,1.0))
'''
new_helmet_pivot = '''    var neck_anchor := base + Vector2(1.6 * dir_sign,-16.0)
    draw_set_transform(neck_anchor, head_rot, Vector2(dir_sign,1.0))
'''
if old_helmet_pivot not in s:
    raise SystemExit("D2D.48 helmet pivot anchor missing")
s = s.replace(old_helmet_pivot, new_helmet_pivot, 1)

# Remove the broad unequipped hip bridge completely so the leg cleft reaches the torso.
old_hip_bridge = '''    if not gear_legs:
        # Small plain hip bridge only; actual leg silhouettes below use the same
        # authored envelopes as equipped pants.
        draw_rect(Rect2(base + Vector2(-6.0,8.0), Vector2(12.0,8.0)), Color("394247"), true)
'''
new_hip_bridge = '''    # D2D.48: no broad pelvis bridge. Both legs remain visibly separated
    # up to the lower torso, matching the geared silhouette.
'''
if old_hip_bridge not in s:
    raise SystemExit("D2D.48 hip bridge anchor missing")
s = s.replace(old_hip_bridge, new_hip_bridge, 1)

# Narrow the stance/hips for both geared and ungeared states.
old_hips = '''    var hip := base + Vector2(side * 5.0, 11)
    var knee := base + Vector2(side * 6.0 + stride * 0.22, 18)
    var ankle := base + Vector2(side * 6.5 + stride * 0.62, 25 - min(abs(stride) * 0.10, 1.8))
'''
new_hips = '''    # D2D.48: narrower adult pelvis/stance while preserving leg thickness.
    var hip := base + Vector2(side * 3.8, 11)
    var knee := base + Vector2(side * 4.9 + stride * 0.22, 18)
    var ankle := base + Vector2(side * 5.4 + stride * 0.62, 25 - min(abs(stride) * 0.10, 1.8))
'''
if old_hips not in s:
    raise SystemExit("D2D.48 hip coordinates anchor missing")
s = s.replace(old_hips, new_hips, 1)

# Lower both geared and plain boots so they sit below the shins instead of overlapping upward.
old_boots = '''    if gear_boots:
        _draw_equipment_texture(tex_gear_boot, ankle + Vector2(3.5 * dir_sign,1.5), Vector2(17.0,12.8), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_base_boot, ankle + Vector2(3.5 * dir_sign,1.5), Vector2(17.0,12.8), dir_sign < 0.0)
'''
new_boots = '''    if gear_boots:
        _draw_equipment_texture(tex_gear_boot, ankle + Vector2(3.5 * dir_sign,4.0), Vector2(17.0,12.8), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_base_boot, ankle + Vector2(3.5 * dir_sign,4.0), Vector2(17.0,12.8), dir_sign < 0.0)
'''
if old_boots not in s:
    raise SystemExit("D2D.48 boot placement anchor missing")
s = s.replace(old_boots, new_boots, 1)

# Replace the blocky support hand with a smaller articulated support grip.
old_support_func = '''func _draw_support_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:
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
new_support_func = '''func _draw_support_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:
    # D2D.48 compact fore-end support grip: smaller palm plus visible curled fingers.
    # No trigger/index finger extends along the firearm.
    var hand_color := Color("4a4037") if gear_gloves else color
    var palm := [
        Vector2(-3.3,-1.8) * scale,
        Vector2(2.2,-1.9) * scale,
        Vector2(3.2,-0.7) * scale,
        Vector2(2.8,1.9) * scale,
        Vector2(-2.2,2.1) * scale,
        Vector2(-3.4,0.8) * scale
    ]
    var pts := PackedVector2Array()
    for p in palm:
        pts.append(center + _pose_point(p, angle, dir_sign))
    draw_colored_polygon(pts, hand_color)

    # Three short curled fingers gripping the fore-end.
    for fy in [-1.15, 0.0, 1.15]:
        var a := center + _pose_point(Vector2(1.0,fy) * scale, angle, dir_sign)
        var b := center + _pose_point(Vector2(3.0,fy + 0.35) * scale, angle, dir_sign)
        draw_line(a,b,hand_color,1.15 * scale,true)

    # Compact thumb wrapping underneath.
    var ta := center + _pose_point(Vector2(-0.5,1.6) * scale, angle, dir_sign)
    var tb := center + _pose_point(Vector2(1.6,2.5) * scale, angle, dir_sign)
    draw_line(ta,tb,hand_color,1.35 * scale,true)

'''
if old_support_func not in s:
    raise SystemExit("D2D.48 support-hand function anchor missing")
s = s.replace(old_support_func, new_support_func, 1)

# Reduce support hand scale in both draw paths.
s = s.replace(
    '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.0), angle, dir_sign), angle, dir_sign, Color("ad704f"), 1.08)',
    '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.0), angle, dir_sign), angle, dir_sign, Color("ad704f"), 0.88)',
    1
)
s = s.replace(
    '_draw_support_hand(hand_front, angle, dir_sign, Color("b97755"), 1.08)',
    '_draw_support_hand(hand_front, angle, dir_sign, Color("b97755"), 0.88)',
    1
)
s = s.replace(
    '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.72)',
    '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.64)',
    1
)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=121',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.48"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.48 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.48"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.48: smaller articulated support hand, narrower hips, full leg cleft, lower boots, forward head.")
