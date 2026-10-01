#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.41 requires D2D.40 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.40 GEAR:"', 'title.text = "D2D.41 GEAR:"', 1)

# Exact mirrored face: always use the approved right-facing source and mirror it horizontally.
old_head = '''    var head_center := base + Vector2(0,-25)
    var head_tex: Texture2D = tex_head_right if face_right else tex_head_left

    # D2D.39: enlarge the approved side-profile head to match the torso proportions,
    # while keeping identical sizing for left/right and lowering it slightly into the neck.
    var head_dst := Rect2(head_center + Vector2(-13.5,-14.5), Vector2(27.0,29.0))
    if head_tex != null:
        draw_texture_rect(head_tex, head_dst, false)
'''
new_head = '''    var head_center := base + Vector2(0,-25)

    # D2D.41: one canonical approved face, mirrored exactly for the opposite side.
    # This guarantees identical facial geometry, hair and proportions when flipping.
    if tex_head_right != null:
        draw_set_transform(head_center, 0.0, Vector2(dir_sign, 1.0))
        draw_texture_rect(tex_head_right, Rect2(Vector2(-13.5,-14.5), Vector2(27.0,29.0)), false)
        draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
'''
if old_head not in s:
    raise SystemExit("D2D.41 head anchor missing")
s = s.replace(old_head, new_head, 1)

# Smaller helmet fit.
old_helmet = '''func _draw_headgear(base: Vector2, dir_sign: float) -> void:
    # Authored helmet follows the two-side head orientation.
    _draw_equipment_texture(tex_gear_helmet, base + Vector2(0,-32), Vector2(29,25), dir_sign < 0.0)
'''
new_helmet = '''func _draw_headgear(base: Vector2, dir_sign: float) -> void:
    # D2D.41: reduced helmet envelope so it fits the approved head instead of overpowering it.
    _draw_equipment_texture(tex_gear_helmet, base + Vector2(0,-31.2), Vector2(23.0,19.5), dir_sign < 0.0)
'''
if old_helmet not in s:
    raise SystemExit("D2D.41 helmet anchor missing")
s = s.replace(old_helmet, new_helmet, 1)

# Zoom state.
anchor = 'var gear_buttons: Dictionary = {}\n'
if anchor not in s:
    raise SystemExit("D2D.41 zoom state anchor missing")
s = s.replace(anchor, anchor + 'var visual_zoom := 1.0\nvar zoom_label: Label = null\n', 1)

# Add zoom controls to fixed CanvasLayer UI.
old_ui_end = '''    _add_gear_button(row, "boots", "BOOTS")
    _add_gear_button(row, "gloves", "GLOVES")
    _refresh_gear_buttons()
'''
new_ui_end = '''    _add_gear_button(row, "boots", "BOOTS")
    _add_gear_button(row, "gloves", "GLOVES")

    var zoom_minus := Button.new()
    zoom_minus.text = "ZOOM -"
    zoom_minus.custom_minimum_size = Vector2(82,44)
    zoom_minus.add_theme_font_size_override("font_size", 14)
    zoom_minus.pressed.connect(func(): _change_zoom(-0.5))
    row.add_child(zoom_minus)

    zoom_label = Label.new()
    zoom_label.custom_minimum_size = Vector2(62,44)
    zoom_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    zoom_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    zoom_label.add_theme_font_size_override("font_size", 14)
    row.add_child(zoom_label)

    var zoom_plus := Button.new()
    zoom_plus.text = "ZOOM +"
    zoom_plus.custom_minimum_size = Vector2(82,44)
    zoom_plus.add_theme_font_size_override("font_size", 14)
    zoom_plus.pressed.connect(func(): _change_zoom(0.5))
    row.add_child(zoom_plus)

    _refresh_gear_buttons()
    _refresh_zoom_label()
'''
if old_ui_end not in s:
    raise SystemExit("D2D.41 zoom UI anchor missing")
s = s.replace(old_ui_end, new_ui_end, 1)
s = s.replace('panel.custom_minimum_size = Vector2(730, 54)', 'panel.custom_minimum_size = Vector2(980, 54)', 1)

# Zoom functions. The Node2D world is scaled around the player while CanvasLayer UI remains fixed.
anchor = 'func _add_gear_button(parent: HBoxContainer, key: String, label_text: String) -> void:\n'
if anchor not in s:
    raise SystemExit("D2D.41 zoom helper anchor missing")
helpers = '''func _change_zoom(delta: float) -> void:
    visual_zoom = clampf(visual_zoom + delta, 1.0, 4.0)
    _apply_visual_zoom()
    _refresh_zoom_label()
    queue_redraw()

func _refresh_zoom_label() -> void:
    if zoom_label != null:
        zoom_label.text = "%.1fx" % visual_zoom

func _apply_visual_zoom() -> void:
    scale = Vector2(visual_zoom, visual_zoom)
    position = actor_pos * (1.0 - visual_zoom)

func _screen_to_world(p: Vector2) -> Vector2:
    return (p - position) / visual_zoom

'''
s = s.replace(anchor, helpers + anchor, 1)

# Keep zoom centered on the moving character.
old_clamp = '''    actor_pos.x = clampf(actor_pos.x, 90.0, vp.x - 90.0)
    actor_pos.y = clampf(actor_pos.y, 110.0, vp.y - 90.0)

    if mag > 0.05:
'''
new_clamp = '''    actor_pos.x = clampf(actor_pos.x, 90.0, vp.x - 90.0)
    actor_pos.y = clampf(actor_pos.y, 110.0, vp.y - 90.0)
    _apply_visual_zoom()

    if mag > 0.05:
'''
if old_clamp not in s:
    raise SystemExit("D2D.41 process zoom anchor missing")
s = s.replace(old_clamp, new_clamp, 1)

# Convert gameplay touch/mouse positions from fixed screen coordinates into zoomed world coordinates.
s = s.replace('''        if e.pressed:
            if e.position.x < vp.x * 0.48 and left_touch == -1:
                left_touch = e.index
                left_origin = e.position
                left_now = e.position
            elif right_touch == -1:
                right_touch = e.index
                aim_pos = e.position
''', '''        var wp := _screen_to_world(e.position)
        if e.pressed:
            if e.position.x < vp.x * 0.48 and left_touch == -1:
                left_touch = e.index
                left_origin = wp
                left_now = wp
            elif right_touch == -1:
                right_touch = e.index
                aim_pos = wp
''', 1)
s = s.replace('''        if d.index == left_touch:
            left_now = d.position
            var dv := left_now - left_origin
            move_vec = dv.limit_length(JOY_RADIUS) / JOY_RADIUS
        elif d.index == right_touch:
            aim_pos = d.position
''', '''        var wp := _screen_to_world(d.position)
        if d.index == left_touch:
            left_now = wp
            var dv := left_now - left_origin
            move_vec = dv.limit_length(JOY_RADIUS / visual_zoom) / (JOY_RADIUS / visual_zoom)
        elif d.index == right_touch:
            aim_pos = wp
''', 1)
s = s.replace('''            if mb.pressed:
                if mb.position.x < vp.x * 0.48:
                    left_origin = mb.position
                    left_now = mb.position
                else:
                    aim_pos = mb.position
''', '''            if mb.pressed:
                var wp := _screen_to_world(mb.position)
                if mb.position.x < vp.x * 0.48:
                    left_origin = wp
                    left_now = wp
                else:
                    aim_pos = wp
''', 1)
s = s.replace('''            if mm.position.x < vp.x * 0.48:
                left_now = mm.position
                var dv2 := left_now - left_origin
                move_vec = dv2.limit_length(JOY_RADIUS) / JOY_RADIUS
            else:
                aim_pos = mm.position
''', '''            var wp := _screen_to_world(mm.position)
            if mm.position.x < vp.x * 0.48:
                left_now = wp
                var dv2 := left_now - left_origin
                move_vec = dv2.limit_length(JOY_RADIUS / visual_zoom) / (JOY_RADIUS / visual_zoom)
            else:
                aim_pos = wp
''', 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=114',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.41"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.41 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.41"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.41: exact mirrored face, smaller helmet and 1x-4x UI zoom.")
