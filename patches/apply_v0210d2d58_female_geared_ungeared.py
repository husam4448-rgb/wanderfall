#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.58 requires D2D.57 runtime script")

s = script.read_text(encoding="utf-8")
if 'title.text = "D2D.57 GEAR:"' not in s:
    raise SystemExit("D2D.58 title anchor missing")
s = s.replace('title.text = "D2D.57 GEAR:"', 'title.text = "D2D.58 FEMALE:"', 1)

# Female is the default test character for this build; the male remains available by toggle.
state_anchor = 'var gear_buttons: Dictionary = {}\n'
if state_anchor not in s:
    raise SystemExit("D2D.58 state anchor missing")
s = s.replace(state_anchor, state_anchor + 'var female_mode := true\nvar female_button: Button = null\n', 1)

# Female head is sourced from the approved SP_Player_Female_8Directions reference.
head_anchor = 'var tex_head_left: Texture2D = null\n'
if head_anchor not in s:
    raise SystemExit("D2D.58 head texture anchor missing")
s = s.replace(head_anchor, head_anchor + 'const FEMALE_HEAD_B64 := "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"\nvar tex_head_female: Texture2D = null\n', 1)

ready_anchor = '    tex_head_left = _texture_from_embedded_png(HEAD_LEFT_B64)\n'
if ready_anchor not in s:
    raise SystemExit("D2D.58 head ready anchor missing")
s = s.replace(ready_anchor, ready_anchor + '    tex_head_female = _texture_from_embedded_png(FEMALE_HEAD_B64)\n', 1)

# Add a dedicated gender test button without changing the existing gear-slot controls.
s = s.replace('panel.custom_minimum_size = Vector2(980, 54)', 'panel.custom_minimum_size = Vector2(1090, 54)', 1)
buttons_anchor = '''    var zoom_plus := Button.new()
    zoom_plus.text = "ZOOM +"
    zoom_plus.custom_minimum_size = Vector2(82,44)
    zoom_plus.add_theme_font_size_override("font_size", 14)
    zoom_plus.pressed.connect(func(): _change_zoom(0.5))
    row.add_child(zoom_plus)

    _refresh_gear_buttons()
    _refresh_zoom_label()
'''
if buttons_anchor not in s:
    raise SystemExit("D2D.58 gear UI anchor missing")
buttons_new = '''    var zoom_plus := Button.new()
    zoom_plus.text = "ZOOM +"
    zoom_plus.custom_minimum_size = Vector2(82,44)
    zoom_plus.add_theme_font_size_override("font_size", 14)
    zoom_plus.pressed.connect(func(): _change_zoom(0.5))
    row.add_child(zoom_plus)

    female_button = Button.new()
    female_button.custom_minimum_size = Vector2(102,44)
    female_button.add_theme_font_size_override("font_size",14)
    female_button.pressed.connect(_toggle_female)
    row.add_child(female_button)

    _refresh_gear_buttons()
    _refresh_zoom_label()
    _refresh_gender_button()
'''
s = s.replace(buttons_anchor, buttons_new, 1)

func_anchor = 'func _add_gear_button(parent: HBoxContainer, key: String, label_text: String) -> void:\n'
if func_anchor not in s:
    raise SystemExit("D2D.58 UI function anchor missing")
gender_funcs = '''func _toggle_female() -> void:
    female_mode = not female_mode
    _refresh_gender_button()
    queue_redraw()

func _refresh_gender_button() -> void:
    if female_button != null:
        female_button.text = "FEMALE" if female_mode else "MALE"

'''
s = s.replace(func_anchor, gender_funcs + func_anchor, 1)

refresh_anchor = '    _set_gear_button("gloves", gear_gloves)\n'
if refresh_anchor not in s:
    raise SystemExit("D2D.58 refresh anchor missing")
s = s.replace(refresh_anchor, refresh_anchor + '    _refresh_gender_button()\n', 1)

# Approved female face/hair texture, preserving the same neck pivot and aim pitch.
head_draw = '''        # D2D.53: slightly smaller head for more realistic body proportion.
        draw_texture_rect(tex_head_right, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
'''
if head_draw not in s:
    raise SystemExit("D2D.58 head draw anchor missing")
head_draw_new = '''        if female_mode and tex_head_female != null:
            # Female profile uses the same neck pivot/aim rotation as the male rig.
            draw_texture_rect(tex_head_female, Rect2(Vector2(-8.1,-17.7), Vector2(16.2,18.9)), false)
        else:
            draw_texture_rect(tex_head_right, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
'''
s = s.replace(head_draw, head_draw_new, 1)

# Base and geared torso use exactly the same rig coordinates, only a slightly narrower
# authored envelope for the female silhouette. This keeps gear/no-gear transitions stable.
base_torso = '''    if not gear_torso:
        # D2D.57: source torso asset already contains the sleeve mesh.
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if base_torso not in s:
    raise SystemExit("D2D.58 base torso anchor missing")
base_torso_new = '''    if not gear_torso:
        var torso_size := Vector2(22.8,29.0) if female_mode else Vector2(25.0,29.0)
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), torso_size, dir_sign < 0.0)
'''
s = s.replace(base_torso, base_torso_new, 1)

vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    # D2D.57: no runtime shoulder overlay; source art is corrected.
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if vest not in s:
    raise SystemExit("D2D.58 vest anchor missing")
vest_new = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    var torso_size := Vector2(23.0,29.0) if female_mode else Vector2(25.0,29.0)
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), torso_size, dir_sign < 0.0)
'''
s = s.replace(vest, vest_new, 1)

# Pack sits closer to the narrower female back while preserving the male placement.
pack_old = '''func _draw_backpack(base: Vector2, dir_sign: float) -> void:
    # D2D.49: pack hugs the spine instead of floating behind it, and rides higher.
    var center := base + Vector2(-10.5 * dir_sign, -4.0)
    _draw_equipment_texture(tex_gear_pack, center, Vector2(25,31), dir_sign < 0.0)
'''
if pack_old in s:
    pack_new = '''func _draw_backpack(base: Vector2, dir_sign: float) -> void:
    var back_x := -9.5 if female_mode else -10.5
    var center := base + Vector2(back_x * dir_sign, -4.0)
    var pack_size := Vector2(23.5,30.0) if female_mode else Vector2(25.0,31.0)
    _draw_equipment_texture(tex_gear_pack, center, pack_size, dir_sign < 0.0)
'''
    s = s.replace(pack_old, pack_new, 1)

# Female legs are slightly narrower but retain the exact male gait, knee direction,
# front-leg selection and successful pocketless-forward-leg asset logic.
leg_block = '''    var is_front_leg := side * dir_sign > 0.0
    if gear_legs:
        var leg_tex := tex_gear_legs_front if is_front_leg else tex_gear_legs
        _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
    else:
        var leg_tex := tex_base_leg_front if is_front_leg else tex_base_leg
        _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
'''
if leg_block not in s:
    raise SystemExit("D2D.58 leg block anchor missing")
leg_new = '''    var is_front_leg := side * dir_sign > 0.0
    var leg_size := Vector2(15.1,26.2) if female_mode else Vector2(16.5,26.5)
    if gear_legs:
        var leg_tex := tex_gear_legs_front if is_front_leg else tex_gear_legs
        _draw_equipment_texture(leg_tex, mid, leg_size, leg_flip, leg_angle)
    else:
        var leg_tex := tex_base_leg_front if is_front_leg else tex_base_leg
        _draw_equipment_texture(leg_tex, mid, leg_size, leg_flip, leg_angle)
'''
s = s.replace(leg_block, leg_new, 1)

# Boots fit the female leg width but preserve the successful ankle placement.
s = s.replace(
    '_draw_equipment_texture(tex_gear_boot, boot_center, Vector2(17.0,12.8), dir_sign < 0.0)',
    '_draw_equipment_texture(tex_gear_boot, boot_center, (Vector2(15.6,12.4) if female_mode else Vector2(17.0,12.8)), dir_sign < 0.0)',
    1
)
s = s.replace(
    '_draw_equipment_texture(tex_base_boot, boot_center, Vector2(17.0,12.8), dir_sign < 0.0)',
    '_draw_equipment_texture(tex_base_boot, boot_center, (Vector2(15.6,12.4) if female_mode else Vector2(17.0,12.8)), dir_sign < 0.0)',
    1
)

# Main hand/glove uses the same grip points with a modest female size reduction.
s = s.replace(
    '_draw_equipment_texture(tex_gear_glove, hand_center, Vector2(10.9,10.5) * scale, dir_sign < 0.0, angle)',
    '_draw_equipment_texture(tex_gear_glove, hand_center, (Vector2(10.0,9.8) if female_mode else Vector2(10.9,10.5)) * scale, dir_sign < 0.0, angle)',
    1
)
s = s.replace(
    '_draw_equipment_texture(tex_base_hand, hand_center, Vector2(10.9,10.5) * scale, dir_sign < 0.0, angle)',
    '_draw_equipment_texture(tex_base_hand, hand_center, (Vector2(10.0,9.8) if female_mode else Vector2(10.9,10.5)) * scale, dir_sign < 0.0, angle)',
    1
)

# Support hand keeps identical firearm contact points; only its visual size changes.
support_sig = 'func _draw_support_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:\n'
if support_sig not in s:
    raise SystemExit("D2D.58 support hand anchor missing")
s = s.replace(support_sig, support_sig + '    if female_mode:\n        scale *= 0.92\n', 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=131',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.58"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.58 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.58"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.58: female geared/ungeared variant on the proven male 2D rig, with female head/hair and proportion-matched gear.")
