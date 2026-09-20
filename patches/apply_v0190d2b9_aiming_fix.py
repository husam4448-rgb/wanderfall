#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/production_survivor_visual.gd"
s=p.read_text(encoding="utf-8")

s=s.replace(
'''        var grip := Vector2(0.0, -3.2 + body_y) + aim * 9.0 - perp * 0.8
        var support := Vector2(0.0, -3.2 + body_y) + aim * 12.0 + perp * 1.3
        var re := (rs + grip) * 0.5 - perp * 3.8
        var le := (ls + support) * 0.5 + perp * 4.0''',
'''        var grip := Vector2(0.0, -3.4 + body_y) + aim * 14.5 - perp * 1.0
        var support := Vector2(0.0, -3.4 + body_y) + aim * 18.0 + perp * 1.6
        var re := rs.lerp(grip, 0.56) - perp * 4.2 - aim * 1.8
        var le := ls.lerp(support, 0.54) + perp * 4.6 - aim * 2.0''',
1)

s=s.replace(
'''    match pose_key:
        "right":
            l_upper.visible = false
            l_fore.visible = false
        "left":
            r_upper.visible = false
            r_fore.visible = false
        "up_right":
            r_upper.visible = false
            l_fore.visible = false
        "up_left":
            l_upper.visible = false
            r_fore.visible = false
''',
'''    for part in [l_upper, r_upper, l_fore, r_fore]:
        part.visible = true
        part.modulate = Color(1.0,1.0,1.0,1.0)
        part.self_modulate = Color(1.0,1.0,1.0,1.0)
''',
1)

s=s.replace(
'''    if back:
        l_upper.z_index = -3
        l_fore.z_index = -2
        r_upper.z_index = -3
        r_fore.z_index = -2
        core.z_index = 1''',
'''    if back:
        l_upper.z_index = -1
        l_fore.z_index = 3
        r_upper.z_index = -1
        r_fore.z_index = 4
        core.z_index = 0''',
1)

s=s.replace(
'''        "back_view": pose_key in ["up", "up_left", "up_right"]''',
'''        "back_view": false''',
1)

p.write_text(s,encoding="utf-8")

sp=root/"scripts/save/save_manager.gd"
if sp.is_file():
    x=sp.read_text(encoding="utf-8")
    x=x.replace('const GAME_VERSION := "0.19.0D2B.8"','const GAME_VERSION := "0.19.0D2B.9"')
    sp.write_text(x,encoding="utf-8")

print("Applied v0.19.0D2B.9 hand opacity, aiming reach, and hand/weapon layering fix.")
