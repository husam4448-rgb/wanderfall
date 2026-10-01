#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.46 requires D2D.45 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.45 GEAR:"', 'title.text = "D2D.46 GEAR:"', 1)

# Plain/body-color versions of the authored alpha silhouettes.
anchor = '''var tex_gear_helmet: Texture2D = null
'''
insert = '''var tex_gear_helmet: Texture2D = null
var tex_base_torso: Texture2D = null
var tex_base_leg: Texture2D = null
var tex_base_boot: Texture2D = null
var tex_base_hand: Texture2D = null
'''
if anchor not in s:
    raise SystemExit("D2D.46 texture-vars anchor missing")
s = s.replace(anchor, insert, 1)

# Create plain silhouettes from the exact same authored shapes.
ready_anchor = '''    tex_gear_helmet = _texture_from_embedded_webp(GEAR_HELMET_B64)
    _build_gear_ui()
'''
ready_new = '''    tex_gear_helmet = _texture_from_embedded_webp(GEAR_HELMET_B64)
    tex_base_torso = _solid_texture_from_embedded_webp(GEAR_VEST_B64, Color("4e594b"))
    tex_base_leg = _solid_texture_from_embedded_webp(GEAR_LEGS_B64, Color("394247"))
    tex_base_boot = _solid_texture_from_embedded_webp(GEAR_BOOT_B64, Color("2d3030"))
    tex_base_hand = _solid_texture_from_embedded_webp(GEAR_GLOVE_B64, Color("c98e68"))
    _build_gear_ui()
'''
if ready_anchor not in s:
    raise SystemExit("D2D.46 ready anchor missing")
s = s.replace(ready_anchor, ready_new, 1)

helper_anchor = '''func _draw_equipment_texture(tex: Texture2D, center: Vector2, size: Vector2, flip_x: bool = false, rotation: float = 0.0) -> void:
'''
helper = '''func _solid_texture_from_embedded_webp(encoded: String, fill: Color) -> Texture2D:
    var bytes := Marshalls.base64_to_raw(encoded)
    var img := Image.new()
    var err := img.load_webp_from_buffer(bytes)
    if err != OK:
        push_error("D2D.46 base silhouette WebP decode failed: %s" % err)
        return null
    img.convert(Image.FORMAT_RGBA8)
    for y in range(img.get_height()):
        for x in range(img.get_width()):
            var p := img.get_pixel(x,y)
            if p.a > 0.01:
                img.set_pixel(x,y,Color(fill.r,fill.g,fill.b,p.a))
    return ImageTexture.create_from_image(img)

'''
if helper_anchor not in s:
    raise SystemExit("D2D.46 helper anchor missing")
s = s.replace(helper_anchor, helper + helper_anchor, 1)

# Head now rotates around the neck socket, not its center.
old_head = '''    var head_center := base + Vector2(0,-25)
    var head_aim_vec := aim_pos - head_center
    var head_tilt := clampf(atan2(head_aim_vec.y, maxf(abs(head_aim_vec.x), 0.001)), -0.38, 0.38)
    var head_rot := head_tilt * dir_sign

    # D2D.45: the canonical side-profile face mirrors L/R and also pitches
    # toward the current aim, matching the gun/hands without allowing a full spin.
    if tex_head_right != null:
        draw_set_transform(head_center, head_rot, Vector2(dir_sign, 1.0))
        draw_texture_rect(tex_head_right, Rect2(Vector2(-10.0,-10.9), Vector2(20.0,21.8)), false)
        draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
'''
new_head = '''    # D2D.46: neck is the anatomical rotation pivot. The head hangs above it
    # instead of orbiting around its own center, preventing neck dislocation.
    var neck_anchor := base + Vector2(0,-16.0)
    var head_aim_vec := aim_pos - neck_anchor
    var head_tilt := clampf(atan2(head_aim_vec.y, maxf(abs(head_aim_vec.x), 0.001)), -0.34, 0.34)
    var head_rot := head_tilt * dir_sign

    if tex_head_right != null:
        draw_set_transform(neck_anchor, head_rot, Vector2(dir_sign, 1.0))
        # Center remains about 9 px above neck; lower edge overlaps the neck naturally.
        draw_texture_rect(tex_head_right, Rect2(Vector2(-10.0,-19.9), Vector2(20.0,21.8)), false)
        draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
'''
if old_head not in s:
    raise SystemExit("D2D.46 head anchor missing")
s = s.replace(old_head, new_head, 1)

# Lower helmet and make it share the exact neck-pivot transform.
old_headgear = '''func _draw_headgear(base: Vector2, dir_sign: float, head_rot: float) -> void:
    # Helmet follows the same mirrored/pitched head transform.
    _draw_equipment_texture(tex_gear_helmet, base + Vector2(0,-31.2), Vector2(23.0,19.5), dir_sign < 0.0, head_rot)
'''
new_headgear = '''func _draw_headgear(base: Vector2, dir_sign: float, head_rot: float) -> void:
    # D2D.46: same neck pivot as the head, with helmet lowered for more crown/side coverage.
    if tex_gear_helmet == null:
        return
    var neck_anchor := base + Vector2(0,-16.0)
    draw_set_transform(neck_anchor, head_rot, Vector2(dir_sign,1.0))
    draw_texture_rect(tex_gear_helmet, Rect2(Vector2(-11.5,-23.35), Vector2(23.0,19.5)), false)
    draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
'''
if old_headgear not in s:
    raise SystemExit("D2D.46 helmet anchor missing")
s = s.replace(old_headgear, new_headgear, 1)

# Replace the procedural no-gear torso/pelvis with the exact authored torso envelope,
# recolored as plain clothing. This preserves size/shape while remaining visually unarmored.
old_body = '''    if not gear_torso:
        # D2D.44: visibly slimmer base body, with rounded-ish taper rather than
        # a broad geometric wedge. Height remains aligned to authored gear.
        var torso_pts := PackedVector2Array([
            base + Vector2(-8.8,-15.0),
            base + Vector2(-5.6,-16.2),
            base + Vector2(5.6,-16.2),
            base + Vector2(8.8,-15.0),
            base + Vector2(8.3,-9.0),
            base + Vector2(7.1,-2.0),
            base + Vector2(5.8,6.0),
            base + Vector2(4.9,12.0),
            base + Vector2(-4.9,12.0),
            base + Vector2(-5.8,6.0),
            base + Vector2(-7.1,-2.0),
            base + Vector2(-8.3,-9.0)
        ])
        draw_colored_polygon(torso_pts, Color("4e594b"))

    if not gear_legs:
        var pelvis_pts := PackedVector2Array([
            base + Vector2(-6.2,8.5),
            base + Vector2(6.2,8.5),
            base + Vector2(5.8,16.7),
            base + Vector2(4.2,18.0),
            base + Vector2(-4.2,18.0),
            base + Vector2(-5.8,16.7)
        ])
        draw_colored_polygon(pelvis_pts, Color("394247"))
'''
new_body = '''    if not gear_torso:
        # Same authored torso silhouette and dimensions as equipped state,
        # but flattened to plain shirt/body coloring.
        draw_circle(base + Vector2(-8.5,-8.0), 4.6, Color("4e594b"))
        draw_circle(base + Vector2(8.5,-8.0), 4.6, Color("4e594b"))
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)

    if not gear_legs:
        # Small plain hip bridge only; actual leg silhouettes below use the same
        # authored envelopes as equipped pants.
        draw_rect(Rect2(base + Vector2(-6.0,8.0), Vector2(12.0,8.0)), Color("394247"), true)
'''
if old_body not in s:
    raise SystemExit("D2D.46 base body anchor missing")
s = s.replace(old_body, new_body, 1)

# Base legs/feet now use the exact same authored dimensions as geared legs/boots.
old_leg = '''    if gear_legs:
        # Authored pants are the visible leg geometry.
        var mid := (hip + ankle) * 0.5
        var leg_angle := (ankle - hip).angle() - PI * 0.5
        _draw_equipment_texture(tex_gear_legs, mid, Vector2(16.5,26.5), side > 0.0, leg_angle)
    else:
        draw_line(hip, knee, leg_color, 6.9, true)
        draw_circle(knee, 3.6, leg_color)
        draw_line(knee, ankle, leg_color, 6.1, true)

    if gear_boots:
        # Authored boot replaces the old procedural foot completely.
        _draw_equipment_texture(tex_gear_boot, ankle + Vector2(3.5 * dir_sign,1.5), Vector2(17.0,12.8), dir_sign < 0.0)
    else:
        _draw_foot_shape(ankle, dir_sign, boot_color)
'''
new_leg = '''    var mid := (hip + ankle) * 0.5
    var leg_angle := (ankle - hip).angle() - PI * 0.5
    if gear_legs:
        _draw_equipment_texture(tex_gear_legs, mid, Vector2(16.5,26.5), side > 0.0, leg_angle)
    else:
        _draw_equipment_texture(tex_base_leg, mid, Vector2(16.5,26.5), side > 0.0, leg_angle)

    if gear_boots:
        _draw_equipment_texture(tex_gear_boot, ankle + Vector2(3.5 * dir_sign,1.5), Vector2(17.0,12.8), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_base_boot, ankle + Vector2(3.5 * dir_sign,1.5), Vector2(17.0,12.8), dir_sign < 0.0)
'''
if old_leg not in s:
    raise SystemExit("D2D.46 leg anchor missing")
s = s.replace(old_leg, new_leg, 1)

# No-glove hands use the same silhouette/size as equipped gloves, recolored to skin.
old_hand = '''    if gear_gloves and tex_gear_glove != null:
        _draw_equipment_texture(tex_gear_glove, center, Vector2(13.2,10.5) * scale, dir_sign < 0.0, angle)
        return
    var hand_scale := scale * 1.06
'''
new_hand = '''    if gear_gloves and tex_gear_glove != null:
        _draw_equipment_texture(tex_gear_glove, center, Vector2(13.2,10.5) * scale, dir_sign < 0.0, angle)
        return
    if tex_base_hand != null:
        _draw_equipment_texture(tex_base_hand, center, Vector2(13.2,10.5) * scale, dir_sign < 0.0, angle)
        return
    var hand_scale := scale * 1.06
'''
if old_hand not in s:
    raise SystemExit("D2D.46 hand anchor missing")
s = s.replace(old_hand, new_hand, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=119',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.46"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.46 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.46"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.46: neck-pivot head/helmet and gear-matched plain body silhouettes.")
