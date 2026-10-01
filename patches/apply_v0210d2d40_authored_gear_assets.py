#!/usr/bin/env python3
from pathlib import Path
import base64, re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parents[1]
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.40 requires D2D.39 runtime script")

gear_dir = repo_root / "art_source" / "gear" / "d2d40"
gear_files = {
    "PACK": gear_dir / "pack.webp",
    "VEST": gear_dir / "vest.webp",
    "LEGS": gear_dir / "legs.webp",
    "BOOT": gear_dir / "boot.webp",
    "GLOVE": gear_dir / "glove.webp",
    "HELMET": gear_dir / "helmet.webp",
}
for key, p in gear_files.items():
    if not p.is_file():
        raise SystemExit(f"D2D.40 missing authored gear asset: {p}")
gear_b64 = {k: base64.b64encode(p.read_bytes()).decode("ascii") for k,p in gear_files.items()}

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.39 GEAR:"', 'title.text = "D2D.40 GEAR:"')

# Add glove slot state.
old_vars = '''var gear_head := false
var gear_torso := false
var gear_back := false
var gear_legs := false
var gear_boots := false
var gear_buttons: Dictionary = {}'''
new_vars = '''var gear_head := false
var gear_torso := false
var gear_back := false
var gear_legs := false
var gear_boots := false
var gear_gloves := false
var gear_buttons: Dictionary = {}'''
if old_vars not in s:
    raise SystemExit("D2D.40 gear state anchor missing")
s = s.replace(old_vars, new_vars, 1)

# Inject authored gear textures after existing head texture vars.
anchor = 'var tex_head_left: Texture2D = null\n'
if anchor not in s:
    raise SystemExit("D2D.40 texture var anchor missing")
injected = f'''var tex_head_left: Texture2D = null
const GEAR_PACK_B64 := "{gear_b64["PACK"]}"
const GEAR_VEST_B64 := "{gear_b64["VEST"]}"
const GEAR_LEGS_B64 := "{gear_b64["LEGS"]}"
const GEAR_BOOT_B64 := "{gear_b64["BOOT"]}"
const GEAR_GLOVE_B64 := "{gear_b64["GLOVE"]}"
const GEAR_HELMET_B64 := "{gear_b64["HELMET"]}"
var tex_gear_pack: Texture2D = null
var tex_gear_vest: Texture2D = null
var tex_gear_legs: Texture2D = null
var tex_gear_boot: Texture2D = null
var tex_gear_glove: Texture2D = null
var tex_gear_helmet: Texture2D = null
'''
s = s.replace(anchor, injected, 1)

# Initialize authored gear textures at runtime, avoiding importer/export dependencies.
old_ready = '''    tex_head_right = _texture_from_embedded_png(HEAD_RIGHT_B64)
    tex_head_left = _texture_from_embedded_png(HEAD_LEFT_B64)
    _build_gear_ui()
    queue_redraw()'''
new_ready = '''    tex_head_right = _texture_from_embedded_png(HEAD_RIGHT_B64)
    tex_head_left = _texture_from_embedded_png(HEAD_LEFT_B64)
    tex_gear_pack = _texture_from_embedded_webp(GEAR_PACK_B64)
    tex_gear_vest = _texture_from_embedded_webp(GEAR_VEST_B64)
    tex_gear_legs = _texture_from_embedded_webp(GEAR_LEGS_B64)
    tex_gear_boot = _texture_from_embedded_webp(GEAR_BOOT_B64)
    tex_gear_glove = _texture_from_embedded_webp(GEAR_GLOVE_B64)
    tex_gear_helmet = _texture_from_embedded_webp(GEAR_HELMET_B64)
    _build_gear_ui()
    queue_redraw()'''
if old_ready not in s:
    raise SystemExit("D2D.40 ready anchor missing")
s = s.replace(old_ready, new_ready, 1)

# WebP decoder and generic texture renderer.
anchor = 'func _build_gear_ui() -> void:\n'
if anchor not in s:
    raise SystemExit("D2D.40 helper anchor missing")
helpers = '''func _texture_from_embedded_webp(encoded: String) -> Texture2D:
    var bytes := Marshalls.base64_to_raw(encoded)
    var img := Image.new()
    var err := img.load_webp_from_buffer(bytes)
    if err != OK:
        push_error("D2D.40 embedded gear WebP decode failed: %s" % err)
        return null
    return ImageTexture.create_from_image(img)

func _draw_equipment_texture(tex: Texture2D, center: Vector2, size: Vector2, flip_x: bool = false, rotation: float = 0.0) -> void:
    if tex == null:
        return
    var sx := -1.0 if flip_x else 1.0
    draw_set_transform(center, rotation, Vector2(sx, 1.0))
    draw_texture_rect(tex, Rect2(Vector2(-size.x * 0.5, -size.y * 0.5), size), false)
    draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

'''
s = s.replace(anchor, helpers + anchor, 1)

# Extend gear test UI.
s = s.replace('panel.custom_minimum_size = Vector2(620, 54)', 'panel.custom_minimum_size = Vector2(730, 54)', 1)
old_buttons = '''    _add_gear_button(row, "head", "HEAD")
    _add_gear_button(row, "torso", "VEST")
    _add_gear_button(row, "back", "PACK")
    _add_gear_button(row, "legs", "LEGS")
    _add_gear_button(row, "boots", "BOOTS")
    _refresh_gear_buttons()'''
new_buttons = '''    _add_gear_button(row, "head", "HEAD")
    _add_gear_button(row, "torso", "VEST")
    _add_gear_button(row, "back", "PACK")
    _add_gear_button(row, "legs", "LEGS")
    _add_gear_button(row, "boots", "BOOTS")
    _add_gear_button(row, "gloves", "GLOVES")
    _refresh_gear_buttons()'''
if old_buttons not in s:
    raise SystemExit("D2D.40 gear buttons anchor missing")
s = s.replace(old_buttons, new_buttons, 1)

old_toggle = '''        "legs": gear_legs = not gear_legs
        "boots": gear_boots = not gear_boots
    _refresh_gear_buttons()'''
new_toggle = '''        "legs": gear_legs = not gear_legs
        "boots": gear_boots = not gear_boots
        "gloves": gear_gloves = not gear_gloves
    _refresh_gear_buttons()'''
if old_toggle not in s:
    raise SystemExit("D2D.40 toggle anchor missing")
s = s.replace(old_toggle, new_toggle, 1)

old_refresh = '''    _set_gear_button("legs", gear_legs)
    _set_gear_button("boots", gear_boots)'''
new_refresh = '''    _set_gear_button("legs", gear_legs)
    _set_gear_button("boots", gear_boots)
    _set_gear_button("gloves", gear_gloves)'''
if old_refresh not in s:
    raise SystemExit("D2D.40 refresh anchor missing")
s = s.replace(old_refresh, new_refresh, 1)

# Replace procedural pack with authored storage asset.
start = s.find('func _draw_backpack(base: Vector2, dir_sign: float) -> void:\n')
end = s.find('func _draw_vest(base: Vector2) -> void:\n', start)
if start == -1 or end == -1:
    raise SystemExit("D2D.40 pack function anchor missing")
s = s[:start] + '''func _draw_backpack(base: Vector2, dir_sign: float) -> void:
    var center := base + Vector2(-14.0 * dir_sign, -1.0)
    _draw_equipment_texture(tex_gear_pack, center, Vector2(25,31), dir_sign < 0.0)

''' + s[end:]

# Replace procedural vest with authored storage asset.
start = s.find('func _draw_vest(base: Vector2) -> void:\n')
end = s.find('func _draw_headgear(base: Vector2, dir_sign: float) -> void:\n', start)
if start == -1 or end == -1:
    raise SystemExit("D2D.40 vest function anchor missing")
s = s[:start] + '''func _draw_vest(base: Vector2) -> void:
    # Authored vest remains above the pants region.
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), false)

''' + s[end:]

# Replace procedural headgear with authored helmet.
start = s.find('func _draw_headgear(base: Vector2, dir_sign: float) -> void:\n')
end = s.find('func _draw_separate_leg(base: Vector2, side: float, stride: float, dir_sign: float) -> void:\n', start)
if start == -1 or end == -1:
    raise SystemExit("D2D.40 headgear function anchor missing")
s = s[:start] + '''func _draw_headgear(base: Vector2, dir_sign: float) -> void:
    # Authored helmet follows the two-side head orientation.
    _draw_equipment_texture(tex_gear_helmet, base + Vector2(0,-32), Vector2(29,25), dir_sign < 0.0)

''' + s[end:]

# Replace equipped pants/boot drawing with authored overlays while preserving D2D.32 gait geometry.
old_leg = '''    draw_line(hip, knee, leg_color, 6.5, true)
    draw_circle(knee, 3.5, leg_color)
    draw_line(knee, ankle, leg_color, 5.5, true)

    if gear_legs:
        var patch := knee + Vector2(side * 1.4, -1)
        draw_rect(Rect2(patch + Vector2(-2,-2), Vector2(4,4)), Color("626864"), true)

    _draw_foot_shape(ankle, dir_sign, boot_color)'''
new_leg = '''    draw_line(hip, knee, leg_color, 6.5, true)
    draw_circle(knee, 3.5, leg_color)
    draw_line(knee, ankle, leg_color, 5.5, true)

    if gear_legs:
        var mid := (hip + ankle) * 0.5
        var leg_angle := (ankle - hip).angle() - PI * 0.5
        _draw_equipment_texture(tex_gear_legs, mid, Vector2(11,24), side > 0.0, leg_angle)

    _draw_foot_shape(ankle, dir_sign, boot_color)
    if gear_boots:
        _draw_equipment_texture(tex_gear_boot, ankle + Vector2(3.5 * dir_sign,1.5), Vector2(14,11), dir_sign < 0.0)'''
if old_leg not in s:
    raise SystemExit("D2D.40 leg overlay anchor missing")
s = s.replace(old_leg, new_leg, 1)

# Use authored gloves for all existing hand draw calls without changing gun/hand layering.
old_hand = '''func _draw_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:
    var local := [
        Vector2(-3.8,-2.8) * scale,
        Vector2(3.5,-2.4) * scale,
        Vector2(4.8,0.8) * scale,
        Vector2(2.2,3.3) * scale,
        Vector2(-3.4,2.7) * scale
    ]'''
new_hand = '''func _draw_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:
    if gear_gloves and tex_gear_glove != null:
        _draw_equipment_texture(tex_gear_glove, center, Vector2(8.5,7.0) * scale, dir_sign < 0.0, angle)
        return
    var local := [
        Vector2(-3.8,-2.8) * scale,
        Vector2(3.5,-2.4) * scale,
        Vector2(4.8,0.8) * scale,
        Vector2(2.2,3.3) * scale,
        Vector2(-3.4,2.7) * scale
    ]'''
if old_hand not in s:
    raise SystemExit("D2D.40 hand function anchor missing")
s = s.replace(old_hand, new_hand, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=113',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.40"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.40 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.40"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.40: authored stored helmet, vest, pack, pants, boots and gloves on D2D.39 core.")
