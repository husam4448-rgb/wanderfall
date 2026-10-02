#!/usr/bin/env python3
from pathlib import Path
import base64, re, sys
from PIL import Image
import numpy as np

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parents[1]
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
gear_dir = repo_root / "art_source" / "gear" / "d2d40"
vest_path = gear_dir / "vest.webp"
legs_path = gear_dir / "legs.webp"
front_path = gear_dir / "legs_front_d2d57.webp"
if not script.exists() or not vest_path.exists() or not legs_path.exists() or not front_path.exists():
    raise SystemExit("D2D.59 required runtime/source assets missing")

# D2D.59 female geometry is authored as distinct source images, not male textures resized at runtime.
def warp_width(src, keys):
    src = src.convert("RGBA")
    a = np.array(src)
    h,w = a.shape[:2]
    out = np.zeros_like(a)
    for y in range(h):
        t = y / max(h-1,1)
        # piecewise-linear width profile
        for i in range(len(keys)-1):
            t0,s0 = keys[i]; t1,s1 = keys[i+1]
            if t <= t1:
                u = 0.0 if t1 == t0 else (t-t0)/(t1-t0)
                scale = s0 + (s1-s0)*u
                break
        else:
            scale = keys[-1][1]
        nw = max(1,int(round(w*scale)))
        row = Image.fromarray(a[y:y+1], "RGBA").resize((nw,1), Image.Resampling.LANCZOS)
        x0 = (w-nw)//2
        out[y:y+1,x0:x0+nw] = np.array(row)
    return Image.fromarray(out,"RGBA")

# Approved female template: same overall height as male, narrower shoulders/torso,
# slimmer limbs, but a relatively wider pelvis/hip transition.
female_vest = warp_width(Image.open(vest_path), [(0.0,0.88),(0.28,0.84),(0.60,0.80),(1.0,0.94)])
female_legs = warp_width(Image.open(legs_path), [(0.0,0.94),(0.25,0.91),(0.62,0.89),(1.0,0.88)])
female_front = warp_width(Image.open(front_path), [(0.0,0.94),(0.25,0.91),(0.62,0.89),(1.0,0.88)])

female_vest_path = gear_dir / "female_vest_d2d59.webp"
female_legs_path = gear_dir / "female_legs_d2d59.webp"
female_front_path = gear_dir / "female_legs_front_d2d59.webp"
female_vest.save(female_vest_path,"WEBP",lossless=True,quality=100,method=6)
female_legs.save(female_legs_path,"WEBP",lossless=True,quality=100,method=6)
female_front.save(female_front_path,"WEBP",lossless=True,quality=100,method=6)

fv_b64 = base64.b64encode(female_vest_path.read_bytes()).decode("ascii")
fl_b64 = base64.b64encode(female_legs_path.read_bytes()).decode("ascii")
ff_b64 = base64.b64encode(female_front_path.read_bytes()).decode("ascii")
head_b64 = "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"

s = script.read_text(encoding="utf-8")
if 'title.text = "D2D.58 FEMALE:"' not in s:
    raise SystemExit("D2D.59 title anchor missing")
s = s.replace('title.text = "D2D.58 FEMALE:"','title.text = "D2D.59 FEMALE BODY:"',1)

# Replace the incorrect female head source with the full approved side-profile crop.
s, n = re.subn(r'const FEMALE_HEAD_B64 := "[^"]+"',
               'const FEMALE_HEAD_B64 := "' + head_b64 + '"', s, count=1)
if n != 1:
    raise SystemExit("D2D.59 female head constant missing")

# Add distinct female torso/leg source textures.
anchor = 'const GEAR_VEST_B64 := '
idx = s.find(anchor)
if idx < 0:
    raise SystemExit("D2D.59 gear constants missing")
line_end = s.find("\n", idx)
insert = ('const FEMALE_VEST_B64 := "'+fv_b64+'"\n'
          'const FEMALE_LEGS_B64 := "'+fl_b64+'"\n'
          'const FEMALE_LEGS_FRONT_B64 := "'+ff_b64+'"\n')
s = s[:line_end+1] + insert + s[line_end+1:]

var_anchor = 'var tex_gear_vest: Texture2D = null\n'
s = s.replace(var_anchor, var_anchor +
'''var tex_female_vest: Texture2D = null
var tex_female_base_torso: Texture2D = null
var tex_female_legs: Texture2D = null
var tex_female_legs_front: Texture2D = null
var tex_female_base_leg: Texture2D = null
var tex_female_base_leg_front: Texture2D = null
''',1)

ready = '    tex_gear_vest = _texture_from_embedded_webp(GEAR_VEST_B64)\n'
s = s.replace(ready, ready +
'''    tex_female_vest = _texture_from_embedded_webp(FEMALE_VEST_B64)
    tex_female_base_torso = _solid_texture_from_embedded_webp(FEMALE_VEST_B64, Color("4e594b"))
    tex_female_legs = _texture_from_embedded_webp(FEMALE_LEGS_B64)
    tex_female_legs_front = _texture_from_embedded_webp(FEMALE_LEGS_FRONT_B64)
    tex_female_base_leg = _solid_texture_from_embedded_webp(FEMALE_LEGS_B64, Color("394247"))
    tex_female_base_leg_front = _solid_texture_from_embedded_webp(FEMALE_LEGS_FRONT_B64, Color("394247"))
''',1)

# Female head must be exactly the same displayed size and neck pivot as the approved male head.
old_head = '''        if female_mode and tex_head_female != null:
            # Female profile uses the same neck pivot/aim rotation as the male rig.
            draw_texture_rect(tex_head_female, Rect2(Vector2(-8.1,-17.7), Vector2(16.2,18.9)), false)
        else:
            draw_texture_rect(tex_head_right, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
'''
new_head = '''        if female_mode and tex_head_female != null:
            draw_texture_rect(tex_head_female, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
        else:
            draw_texture_rect(tex_head_right, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
'''
if old_head not in s:
    raise SystemExit("D2D.59 female head draw anchor missing")
s=s.replace(old_head,new_head,1)

# Unequipped torso uses the true female source silhouette, not a narrowed male draw.
old_base = '''    if not gear_torso:
        var torso_size := Vector2(22.8,29.0) if female_mode else Vector2(25.0,29.0)
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), torso_size, dir_sign < 0.0)
'''
new_base = '''    if not gear_torso:
        if female_mode:
            _draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)
        else:
            _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)
'''
if old_base not in s:
    raise SystemExit("D2D.59 base torso anchor missing")
s=s.replace(old_base,new_base,1)

old_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    var torso_size := Vector2(23.0,29.0) if female_mode else Vector2(25.0,29.0)
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), torso_size, dir_sign < 0.0)
'''
new_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    if female_mode:
        _draw_equipment_texture(tex_female_vest, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)
'''
if old_vest not in s:
    raise SystemExit("D2D.59 vest anchor missing")
s=s.replace(old_vest,new_vest,1)

# Female hip geometry: slightly wider pelvis but slimmer legs, same overall height.
old_hips = '''    # D2D.48: narrower adult pelvis/stance while preserving leg thickness.
    var hip := base + Vector2(side * 3.8, 11)
    var knee := base + Vector2(side * 4.9 + stride * 0.22, 18)
    var ankle := base + Vector2(side * 5.4 + stride * 0.62, 25 - min(abs(stride) * 0.10, 1.8))
'''
new_hips = '''    var hip_span := 4.35 if female_mode else 3.8
    var knee_span := 5.15 if female_mode else 4.9
    var ankle_span := 5.45 if female_mode else 5.4
    var hip := base + Vector2(side * hip_span, 11)
    var knee := base + Vector2(side * knee_span + stride * 0.22, 18)
    var ankle := base + Vector2(side * ankle_span + stride * 0.62, 25 - min(abs(stride) * 0.10, 1.8))
'''
if old_hips not in s:
    raise SystemExit("D2D.59 hip anchor missing")
s=s.replace(old_hips,new_hips,1)

old_leg = '''    var is_front_leg := side * dir_sign > 0.0
    var leg_size := Vector2(15.1,26.2) if female_mode else Vector2(16.5,26.5)
    if gear_legs:
        var leg_tex := tex_gear_legs_front if is_front_leg else tex_gear_legs
        _draw_equipment_texture(leg_tex, mid, leg_size, leg_flip, leg_angle)
    else:
        var leg_tex := tex_base_leg_front if is_front_leg else tex_base_leg
        _draw_equipment_texture(leg_tex, mid, leg_size, leg_flip, leg_angle)
'''
new_leg = '''    var is_front_leg := side * dir_sign > 0.0
    if female_mode:
        if gear_legs:
            var leg_tex := tex_female_legs_front if is_front_leg else tex_female_legs
            _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
        else:
            var leg_tex := tex_female_base_leg_front if is_front_leg else tex_female_base_leg
            _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
    else:
        if gear_legs:
            var leg_tex := tex_gear_legs_front if is_front_leg else tex_gear_legs
            _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
        else:
            var leg_tex := tex_base_leg_front if is_front_leg else tex_base_leg
            _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
'''
if old_leg not in s:
    raise SystemExit("D2D.59 leg anchor missing")
s=s.replace(old_leg,new_leg,1)

# A subtle pelvis bridge makes the female torso/legs read as one coherent body without changing height.
body_anchor = '''    # D2D.48: no broad pelvis bridge. Both legs remain visibly separated
    # up to the lower torso, matching the geared silhouette.
'''
body_new = '''    # D2D.59: female pelvis is relatively wider than the waist, but stays compact.
    if female_mode:
        var pelvis_col := Color("5c574a") if gear_legs else Color("394247")
        var pelvis_pts := PackedVector2Array([
            base + Vector2(-5.3,7.5), base + Vector2(5.3,7.5),
            base + Vector2(6.2,13.2), base + Vector2(4.3,15.0),
            base + Vector2(-4.3,15.0), base + Vector2(-6.2,13.2)
        ])
        draw_colored_polygon(pelvis_pts,pelvis_col)
    # Male remains unchanged.
'''
if body_anchor not in s:
    raise SystemExit("D2D.59 pelvis anchor missing")
s=s.replace(body_anchor,body_new,1)

script.write_text(s,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=132',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.59"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.59 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.59"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.59: corrected full female head at male scale, true female torso/leg source meshes, wider female pelvis and matched ungeared silhouette.")
