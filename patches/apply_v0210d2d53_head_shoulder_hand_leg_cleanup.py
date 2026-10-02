#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.53 requires D2D.52 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.52 GEAR:"', 'title.text = "D2D.53 GEAR:"', 1)

# Slightly smaller head while preserving the current neck position.
old_head = '''        # D2D.51: slightly lower on the neck for better torso alignment.
        draw_texture_rect(tex_head_right, Rect2(Vector2(-9.0,-17.7), Vector2(18.0,19.6)), false)
'''
new_head = '''        # D2D.53: slightly smaller head for more realistic body proportion.
        draw_texture_rect(tex_head_right, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
'''
if old_head not in s:
    raise SystemExit("D2D.53 head anchor missing")
s = s.replace(old_head, new_head, 1)

# Helmet scales down and remains fitted to the reduced head.
old_helmet = '''    # D2D.52: helmet sits slightly lower over the head.
    draw_texture_rect(tex_gear_helmet, Rect2(Vector2(-10.4,-19.95), Vector2(20.8,17.6)), false)
'''
new_helmet = '''    # D2D.53: helmet scaled to the smaller head and kept low over the crown.
    draw_texture_rect(tex_gear_helmet, Rect2(Vector2(-9.75,-19.25), Vector2(19.5,16.5)), false)
'''
if old_helmet not in s:
    raise SystemExit("D2D.53 helmet anchor missing")
s = s.replace(old_helmet, new_helmet, 1)

# Trigger/main hand: shorten the glove/base-hand horizontal envelope so the forearm cuff
# no longer projects from the wrist. Keep overall hand height and finger detail.
old_hand_tex = '''    if gear_gloves and tex_gear_glove != null:
        _draw_equipment_texture(tex_gear_glove, center, Vector2(13.2,10.5) * scale, dir_sign < 0.0, angle)
        return
    if tex_base_hand != null:
        _draw_equipment_texture(tex_base_hand, center, Vector2(13.2,10.5) * scale, dir_sign < 0.0, angle)
        return
'''
new_hand_tex = '''    if gear_gloves and tex_gear_glove != null:
        var hand_center := center + _pose_point(Vector2(0.9,0.0) * scale, angle, dir_sign)
        _draw_equipment_texture(tex_gear_glove, hand_center, Vector2(10.9,10.5) * scale, dir_sign < 0.0, angle)
        return
    if tex_base_hand != null:
        var hand_center := center + _pose_point(Vector2(0.9,0.0) * scale, angle, dir_sign)
        _draw_equipment_texture(tex_base_hand, hand_center, Vector2(10.9,10.5) * scale, dir_sign < 0.0, angle)
        return
'''
if old_hand_tex not in s:
    raise SystemExit("D2D.53 main hand texture anchor missing")
s = s.replace(old_hand_tex, new_hand_tex, 1)

# Shoulder cavity cover. Draw a matching shoulder cap over the transparent authored socket
# after the torso itself, for both geared and ungeared states.
old_body = '''    if not gear_torso:
        # Same authored torso silhouette/dimensions as equipped state,
        # but without artificial shoulder-joint balls.
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)

    # D2D.48: no broad pelvis bridge. Both legs remain visibly separated
'''
new_body = '''    if not gear_torso:
        # Same authored torso silhouette/dimensions as equipped state.
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
        # Cover the authored shoulder socket with matching cloth.
        var shoulder_cap := base + Vector2(-8.0 * dir_sign,-8.1)
        draw_circle(shoulder_cap,4.15,Color("4e594b"))
        draw_circle(shoulder_cap + Vector2(0.35 * dir_sign,-0.15),2.7,Color("566253"))

    # D2D.48: no broad pelvis bridge. Both legs remain visibly separated
'''
if old_body not in s:
    raise SystemExit("D2D.53 base shoulder anchor missing")
s = s.replace(old_body, new_body, 1)

old_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    # D2D.47: clean authored torso; no artificial shoulder-joint circles.
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
new_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
    # D2D.53: armor/fabric shoulder patch closes the black transparent socket.
    var shoulder_cap := base + Vector2(-8.0 * dir_sign,-8.1)
    draw_circle(shoulder_cap,4.2,Color("655f50"))
    draw_circle(shoulder_cap + Vector2(0.35 * dir_sign,-0.2),2.75,Color("77705e"))
'''
if old_vest not in s:
    raise SystemExit("D2D.53 geared shoulder anchor missing")
s = s.replace(old_vest, new_vest, 1)

# Forward thigh pocket cleanup: cover the inner thigh pocket area with matching material.
# Insert immediately before the current D2D.50 boot-center line; avoids depending on
# the exact surrounding leg-render block from older patches.
boot_anchor = '''    # D2D.50: slightly forward and lower relative to ankle.
    var boot_center := ankle + Vector2(0.4 * dir_sign, 6.8)
'''
boot_new = '''    # D2D.53: remove the visually misplaced inner-thigh pocket from the forward leg.
    # Patch follows leg rotation so it stays attached during gait.
    if stride > 0.0:
        var patch_center := mid + _pose_point(Vector2(-2.2 * dir_sign,-4.0), leg_angle, 1.0)
        var patch_color := Color("716856") if gear_legs else Color("394247")
        draw_set_transform(patch_center,leg_angle,Vector2.ONE)
        draw_rect(Rect2(Vector2(-2.2,-2.8),Vector2(4.4,5.6)),patch_color,true)
        draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

    # D2D.50: slightly forward and lower relative to ankle.
    var boot_center := ankle + Vector2(0.4 * dir_sign, 6.8)
'''
if boot_anchor not in s:
    raise SystemExit("D2D.53 forward-leg boot anchor missing")
s = s.replace(boot_anchor, boot_new, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=126',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.53"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.53 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.53"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.53: smaller head/helmet, trimmed main hand cuff, shoulder covers, forward-thigh pocket cleanup.")
