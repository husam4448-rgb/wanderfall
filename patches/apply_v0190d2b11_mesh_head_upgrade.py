#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/production_survivor_visual.gd"
if not p.is_file():
    raise SystemExit(f"Missing D2B.11 target: {p}")
s=p.read_text(encoding="utf-8")

s=s.replace(
'const HEAD_TEX = preload("res://assets/art/characters/hybrid_male_head.png")\n',
'const HEAD_TEX = preload("res://assets/art/characters/hybrid_male_head.png")\nconst DIRECTIONAL_CORE_TEX = preload("res://assets/art/characters/player_male_core.png")\n',
1)

s=s.replace(
'var _last_lw := Vector2.ZERO\nvar _last_rw := Vector2.ZERO\n',
'var _last_lw := Vector2.ZERO\nvar _last_rw := Vector2.ZERO\nvar head_frames: Array = []\n',
1)

s=s.replace(
'''    head = _sprite(HEAD_TEX, 5)
    l_upper = _sprite(UPPER_ARM_TEX, 1)''',
'''    head = _sprite(HEAD_TEX, 5)
    _build_head_frames()
    l_upper = _sprite(UPPER_ARM_TEX, 1)''',
1)

s=s.replace(
'''    var perspective_x := lerpf(1.0, 0.76, absf(side))
    var torso_w := 15.5 * perspective_x
    var shoulder_half := 7.3 * perspective_x
    var hip_half := 3.5 * perspective_x''',
'''    var perspective_x := lerpf(1.0, 0.78, absf(side))
    var torso_w := 18.0 * perspective_x
    var shoulder_half := 8.0 * perspective_x
    var hip_half := 4.0 * perspective_x''',
1)

s=s.replace(
'''    _place_segment(l_thigh, l_hip, l_knee, 1.22)
    _place_segment(r_thigh, r_hip, r_knee, 1.22)
    _place_segment(l_shin, l_knee, l_ankle, 1.28)
    _place_segment(r_shin, r_knee, r_ankle, 1.28)''',
'''    _place_segment(l_thigh, l_hip, l_knee, 1.36)
    _place_segment(r_thigh, r_hip, r_knee, 1.36)
    _place_segment(l_shin, l_knee, l_ankle, 1.42)
    _place_segment(r_shin, r_knee, r_ankle, 1.42)''',
1)

s=s.replace(
'''    var torso_sy := 19.0 / maxf(1.0, float(TORSO_TEX.get_height()))
    var torso_sx := torso_sy * (torso_w / 15.5)
    torso.scale = Vector2(torso_sx, torso_sy)

    var head_center := Vector2(side * 0.8, -19.8 + body_bob * 0.55) + lean * 0.18
    head.position = head_center
    var head_sy := 13.4 / maxf(1.0, float(HEAD_TEX.get_height()))
    var head_sx := head_sy * lerpf(1.0, 0.78, absf(side))
    head.scale = Vector2(head_sx, head_sy)
    head.flip_h = side < -0.12''',
'''    var torso_sy := 19.0 / maxf(1.0, float(TORSO_TEX.get_height()))
    var torso_sx := torso_sy * (torso_w / 18.0)
    torso.scale = Vector2(torso_sx, torso_sy)

    var head_center := Vector2(side * 0.72, -19.6 + body_bob * 0.55) + lean * 0.18
    head.position = head_center
    if not head_frames.is_empty():
        head.texture = head_frames[_direction_frame()]
    var head_sy := 13.0 / maxf(1.0, float(head.texture.get_height()))
    head.scale = Vector2(head_sy, head_sy)
    head.flip_h = false
    head.rotation = 0.0''',
1)

s=s.replace(
'''    _place_segment(l_upper, ls, le, 1.20)
    _place_segment(r_upper, rs, re, 1.20)
    _place_segment(l_fore, le, lw, 1.12)
    _place_segment(r_fore, re, rw, 1.12)''',
'''    _place_segment(l_upper, ls, le, 1.34)
    _place_segment(r_upper, rs, re, 1.34)
    _place_segment(l_fore, le, lw, 1.26)
    _place_segment(r_fore, re, rw, 1.26)''',
1)

s=s.replace(
'var target_width := maxf(2.5, length * 0.36 * width_mul)',
'var target_width := maxf(3.2, length * 0.46 * width_mul)',
1)

insert_before='func _weapon_category() -> String:\n'
helper=r'''func _build_head_frames() -> void:
    head_frames.clear()
    var frame_w := float(DIRECTIONAL_CORE_TEX.get_width()) / 8.0
    var frame_h := float(DIRECTIONAL_CORE_TEX.get_height())
    var crop_w := minf(30.0, frame_w * 0.68)
    var crop_h := minf(28.0, frame_h * 0.42)
    var crop_y := 0.0
    for i in range(8):
        var t := AtlasTexture.new()
        t.atlas = DIRECTIONAL_CORE_TEX
        t.region = Rect2(i * frame_w + (frame_w - crop_w) * 0.5, crop_y, crop_w, crop_h)
        head_frames.append(t)

func _direction_frame() -> int:
    var d := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    if d.y > 0.72:
        if d.x < -0.34:
            return 7
        if d.x > 0.34:
            return 1
        return 0
    if d.y < -0.72:
        if d.x < -0.34:
            return 5
        if d.x > 0.34:
            return 3
        return 4
    return 2 if d.x >= 0.0 else 6

'''
if insert_before not in s:
    raise SystemExit("D2B.11 helper insertion anchor missing")
s=s.replace(insert_before,helper+insert_before,1)

p.write_text(s,encoding="utf-8")

sp=root/"scripts/save/save_manager.gd"
if sp.is_file():
    x=sp.read_text(encoding="utf-8")
    x=x.replace('const GAME_VERSION := "0.19.0D2B.10"','const GAME_VERSION := "0.19.0D2B.11"')
    sp.write_text(x,encoding="utf-8")

print("Applied v0.19.0D2B.11 mesh-width and directional-head upgrade: wider torso/arms/legs with unchanged overall scale and true 8-direction head frames.")
