#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d18_skinned_mesh_lab.gd"
if not script.exists():
    raise SystemExit("D2D.19 requires the D2D.18 skinned-mesh lab")

s = script.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit(f"D2D.19 missing anchor: {label}")
    s = s.replace(old, new, 1)

replace_once('const COLS := 19\nconst ROWS := 39', 'const COLS := 29\nconst ROWS := 61', 'mesh density')
replace_once('    "pelvis","torso","chest","neck","head",', '    "pelvis","torso","chest","breath","neck","head",', 'bone order')
replace_once('    "chest": Vector2(0, -106),\n    "neck": Vector2(0, -153),', '    "chest": Vector2(0, -106),\n    "breath": Vector2(0, -106),\n    "neck": Vector2(0, -153),', 'breath bind')
replace_once('    "chest":"torso",\n    "neck":"chest",', '    "chest":"torso",\n    "breath":"torso",\n    "neck":"chest",', 'breath parent')
replace_once('var bones := {}\nvar test_mode := "neutral"', 'var bones := {}\nvar texture_image: Image\nvar test_mode := "neutral"', 'texture image variable')
replace_once('    skin.texture = BODY_TEXTURE\n    skin.antialiased = true', '    skin.texture = BODY_TEXTURE\n    skin.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR\n    texture_image = BODY_TEXTURE.get_image()\n    skin.antialiased = true', 'texture image setup')

old_grid = '''            tris.append(PackedInt32Array([a,b,c]))\n            tris.append(PackedInt32Array([a,c,d]))'''
new_grid = '''            if _cell_has_body(i,j):\n                tris.append(PackedInt32Array([a,b,c]))\n                tris.append(PackedInt32Array([a,c,d]))'''
replace_once(old_grid, new_grid, 'masked triangle generation')

insert_anchor = 'func _build_grid_mesh() -> void:\n'
cell_func = '''func _cell_has_body(i: int, j: int) -> bool:\n    if texture_image == null or texture_image.is_empty():\n        return true\n    var x0 := float(i) * TEX_W / float(COLS - 1)\n    var x1 := float(i + 1) * TEX_W / float(COLS - 1)\n    var y0 := float(j) * TEX_H / float(ROWS - 1)\n    var y1 := float(j + 1) * TEX_H / float(ROWS - 1)\n    var samples := [\n        Vector2(x0,y0), Vector2(x1,y0), Vector2(x1,y1), Vector2(x0,y1),\n        Vector2((x0+x1)*0.5,(y0+y1)*0.5),\n        Vector2((x0+x1)*0.5,y0), Vector2((x0+x1)*0.5,y1),\n        Vector2(x0,(y0+y1)*0.5), Vector2(x1,(y0+y1)*0.5)\n    ]\n    for sample in samples:\n        var sx := clampi(int(round(sample.x)),0,int(TEX_W)-1)\n        var sy := clampi(int(round(sample.y)),0,int(TEX_H)-1)\n        if texture_image.get_pixel(sx,sy).a > 0.035:\n            return true\n    return false\n\n'''
replace_once(insert_anchor, cell_func + insert_anchor, 'cell alpha mask function')

old_center = '''    elif py < 190.0:\n        var t := clampf((py - 125.0) / 65.0, 0.0, 1.0)\n        out["chest"] = 1.0 - 0.35*t\n        out["torso"] = 0.35*t'''
new_center = '''    elif py < 190.0:\n        var t := clampf((py - 125.0) / 65.0, 0.0, 1.0)\n        var center_mask := clampf(1.0 - absf(px - TEX_W*0.5) / 62.0, 0.0, 1.0)\n        var vertical_mask := _bell(py, 151.0, 46.0)\n        var breath_w := 0.72 * center_mask * vertical_mask\n        var remaining := 1.0 - breath_w\n        out["breath"] = breath_w\n        out["chest"] = remaining * (1.0 - 0.35*t)\n        out["torso"] = remaining * (0.35*t)'''
replace_once(old_center, new_center, 'chest-only breath weighting')

old_breath = '''    if breathing:\n        var breath := sin(elapsed * 2.1)\n        bones["chest"].scale = Vector2(1.0 + 0.010*breath, 1.0 + 0.017*breath)\n        bones["torso"].scale = Vector2(1.0 + 0.004*breath, 1.0 + 0.008*breath)\n        bones["neck"].rotation = deg_to_rad(0.6) * breath'''
new_breath = '''    if breathing:\n        var breath := sin(elapsed * 1.75)\n        bones["breath"].scale = Vector2(1.0 + 0.008*breath, 1.0 + 0.003*breath)\n        bones["chest"].position = bones["chest"].rest.origin + Vector2(0.0, -0.45*breath)\n        bones["chest"].rotation = deg_to_rad(0.16) * breath\n        bones["neck"].rotation = deg_to_rad(0.12) * breath'''
replace_once(old_breath, new_breath, 'breathing motion')

old_arm = '''    if test_mode == "arm":\n        var p := sin(elapsed * 1.9)\n        bones["upper_arm_L"].rotation = deg_to_rad(28.0) * p\n        bones["forearm_L"].rotation = deg_to_rad(24.0) * maxf(0.0,p)\n        bones["hand_L"].rotation = -deg_to_rad(10.0) * p\n        bones["upper_arm_R"].rotation = -deg_to_rad(28.0) * p\n        bones["forearm_R"].rotation = -deg_to_rad(24.0) * maxf(0.0,-p)\n        bones["hand_R"].rotation = deg_to_rad(10.0) * p'''
new_arm = '''    if test_mode == "arm":\n        var p := sin(elapsed * 1.55)\n        var q := 0.5 + 0.5 * sin(elapsed * 1.55 + 1.0)\n        bones["upper_arm_L"].rotation = deg_to_rad(17.0) * p\n        bones["forearm_L"].rotation = deg_to_rad(28.0) * q\n        bones["hand_L"].rotation = -deg_to_rad(6.0) * p\n        bones["upper_arm_R"].rotation = -deg_to_rad(17.0) * p\n        bones["forearm_R"].rotation = -deg_to_rad(28.0) * q\n        bones["hand_R"].rotation = deg_to_rad(6.0) * p'''
replace_once(old_arm, new_arm, 'arm motion')

old_leg = '''    elif test_mode == "leg":\n        var p := sin(elapsed * 1.8)\n        bones["thigh_L"].rotation = deg_to_rad(10.0) * p\n        bones["shin_L"].rotation = deg_to_rad(18.0) * maxf(0.0,-p)\n        bones["foot_L"].rotation = -deg_to_rad(7.0) * p\n        bones["thigh_R"].rotation = -deg_to_rad(10.0) * p\n        bones["shin_R"].rotation = -deg_to_rad(18.0) * maxf(0.0,p)\n        bones["foot_R"].rotation = deg_to_rad(7.0) * p'''
new_leg = '''    elif test_mode == "leg":\n        var p := sin(elapsed * 1.45)\n        var lift_l := maxf(0.0, p)\n        var lift_r := maxf(0.0, -p)\n        bones["thigh_L"].rotation = deg_to_rad(7.0) * p\n        bones["shin_L"].rotation = -deg_to_rad(20.0) * lift_l\n        bones["foot_L"].rotation = deg_to_rad(7.0) * lift_l - deg_to_rad(3.0) * p\n        bones["thigh_R"].rotation = -deg_to_rad(7.0) * p\n        bones["shin_R"].rotation = deg_to_rad(20.0) * lift_r\n        bones["foot_R"].rotation = -deg_to_rad(7.0) * lift_r + deg_to_rad(3.0) * p'''
replace_once(old_leg, new_leg, 'leg motion')

old_aim = '''    elif test_mode == "aim":\n        bones["upper_arm_L"].rotation = deg_to_rad(57.0)\n        bones["forearm_L"].rotation = deg_to_rad(30.0)\n        bones["hand_L"].rotation = -deg_to_rad(18.0)\n        bones["upper_arm_L"].scale = Vector2(0.82,0.68)\n        bones["forearm_L"].scale = Vector2(0.86,0.62)\n        bones["upper_arm_R"].rotation = -deg_to_rad(57.0)\n        bones["forearm_R"].rotation = -deg_to_rad(30.0)\n        bones["hand_R"].rotation = deg_to_rad(18.0)\n        bones["upper_arm_R"].scale = Vector2(0.82,0.68)\n        bones["forearm_R"].scale = Vector2(0.86,0.62)\n        bones["chest"].scale *= Vector2(1.015,0.985)'''
new_aim = '''    elif test_mode == "aim":\n        bones["upper_arm_L"].rotation = deg_to_rad(43.0)\n        bones["forearm_L"].rotation = deg_to_rad(31.0)\n        bones["hand_L"].rotation = -deg_to_rad(8.0)\n        bones["upper_arm_R"].rotation = -deg_to_rad(43.0)\n        bones["forearm_R"].rotation = -deg_to_rad(31.0)\n        bones["hand_R"].rotation = deg_to_rad(8.0)\n        var fl: Vector2 = bones["forearm_L"].rest.origin\n        var fr: Vector2 = bones["forearm_R"].rest.origin\n        var hl: Vector2 = bones["hand_L"].rest.origin\n        var hr: Vector2 = bones["hand_R"].rest.origin\n        bones["forearm_L"].position = Vector2(fl.x*0.78, fl.y*0.70)\n        bones["forearm_R"].position = Vector2(fr.x*0.78, fr.y*0.70)\n        bones["hand_L"].position = Vector2(hl.x*0.72, hl.y*0.58)\n        bones["hand_R"].position = Vector2(hr.x*0.72, hr.y*0.58)'''
replace_once(old_aim, new_aim, 'aim motion')

replace_once('D2D.18 — CONTINUOUS SKINNED BODY MESH', 'D2D.19 — CALIBRATED CONTINUOUS SKINNED MESH', 'title')
replace_once('South prototype • one continuous underwear-covered texture • weighted 2D skin', 'South prototype • chest-only breathing • alpha-masked weighted mesh • localized joints', 'subtitle')
replace_once('No cut-up limbs. Bone weights deform one intact texture.', 'One intact texture. Mesh triangles follow the body alpha; chest breathing does not scale limbs.', 'note')
replace_once('• breathing without seams\n• elbows/wrists bend continuously\n• knees/ankles stay connected\n• aim moves upper body only', '• chest-only subtle breathing\n• head/arms sway without scaling\n• localized elbow/knee bending\n• aim uses compressed bone lengths, not stretched textures', 'footer')

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$', 'version/code=92', e, count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.19"', e, count=1)
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"', 'const GAME_VERSION := "0.21.0D2D.19"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.19 chest-only breathing and localized alpha-masked mesh calibration.")
