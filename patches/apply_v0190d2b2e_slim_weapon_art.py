#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/art/weapon_visual.gd"
if not p.is_file():
    raise SystemExit(f"Missing D2B.2E target: {p}")
s = p.read_text(encoding="utf-8")

repls = [
('''        "pistol_9mm": return 26.0
        "revolver_357": return 29.0
        "smg_9mm": return 34.0
        "rifle_556": return 42.0
        "shotgun_12g": return 45.0
        "hunting_rifle": return 48.0
''',
'''        "pistol_9mm": return 20.0
        "revolver_357": return 22.0
        "smg_9mm": return 29.0
        "rifle_556": return 36.0
        "shotgun_12g": return 40.0
        "hunting_rifle": return 42.0
'''),
('''func _draw_pistol(c: Color) -> void:
    draw_rect(Rect2(7,-3,17,6), c, true)
    draw_rect(Rect2(10,-5,13,2), c.lightened(0.12), true)
    draw_colored_polygon(PackedVector2Array([Vector2(11,3),Vector2(18,3),Vector2(15,14),Vector2(10,14)]), c.darkened(0.18))
''',
'''func _draw_pistol(c: Color) -> void:
    draw_rect(Rect2(5,-2.0,15,4.0), c.darkened(0.04), true)
    draw_rect(Rect2(7,-3.1,12,1.2), c.lightened(0.13), true)
    draw_colored_polygon(PackedVector2Array([Vector2(8,2),Vector2(13,2),Vector2(12,9),Vector2(8.5,9)]), c.darkened(0.20))
    draw_rect(Rect2(18,-1.4,2,2.8), c.darkened(0.14), true)
'''),
('''func _draw_revolver(c: Color) -> void:
    draw_rect(Rect2(7,-3,20,5), c, true)
    draw_circle(Vector2(15,2), 5.0, c.lightened(0.08))
    draw_circle(Vector2(15,2), 2.2, c.darkened(0.22))
    draw_colored_polygon(PackedVector2Array([Vector2(10,5),Vector2(16,5),Vector2(14,15),Vector2(9,15)]), c.darkened(0.18))
''',
'''func _draw_revolver(c: Color) -> void:
    draw_rect(Rect2(5,-1.8,17,3.6), c, true)
    draw_circle(Vector2(11,1.4), 3.4, c.lightened(0.08))
    draw_circle(Vector2(11,1.4), 1.4, c.darkened(0.22))
    draw_colored_polygon(PackedVector2Array([Vector2(7,3),Vector2(12,3),Vector2(11,10),Vector2(7.5,10)]), c.darkened(0.19))
'''),
('''func _draw_smg(c: Color) -> void:
    draw_rect(Rect2(5,-4,26,8), c, true)
    draw_rect(Rect2(1,-2,8,5), c.darkened(0.18), true)
    draw_colored_polygon(PackedVector2Array([Vector2(12,4),Vector2(18,4),Vector2(20,16),Vector2(13,16)]), c.darkened(0.10))
    draw_rect(Rect2(29,-2,5,4), c.darkened(0.12), true)
''',
'''func _draw_smg(c: Color) -> void:
    draw_rect(Rect2(4,-2.5,23,5), c, true)
    draw_rect(Rect2(1,-1.4,6,3.2), c.darkened(0.18), true)
    draw_colored_polygon(PackedVector2Array([Vector2(10,2.5),Vector2(15,2.5),Vector2(16,10),Vector2(11,10)]), c.darkened(0.12))
    draw_rect(Rect2(26,-1.3,4,2.6), c.darkened(0.12), true)
'''),
('''func _draw_carbine(c: Color) -> void:
    draw_colored_polygon(PackedVector2Array([Vector2(1,-3),Vector2(10,-5),Vector2(15,-3),Vector2(15,3),Vector2(6,5),Vector2(1,3)]), c.darkened(0.18))
    draw_rect(Rect2(12,-4,18,8), c, true)
    draw_colored_polygon(PackedVector2Array([Vector2(18,4),Vector2(24,4),Vector2(27,15),Vector2(20,15)]), c.darkened(0.10))
    draw_rect(Rect2(29,-2,13,4), c.darkened(0.05), true)
''',
'''func _draw_carbine(c: Color) -> void:
    draw_colored_polygon(PackedVector2Array([Vector2(1,-2),Vector2(8,-3.3),Vector2(12,-2),Vector2(12,2),Vector2(5,3.5),Vector2(1,2)]), c.darkened(0.18))
    draw_rect(Rect2(10,-2.5,17,5), c, true)
    draw_colored_polygon(PackedVector2Array([Vector2(16,2.5),Vector2(21,2.5),Vector2(22.5,10),Vector2(18,10)]), c.darkened(0.11))
    draw_rect(Rect2(26,-1.3,10,2.6), c.darkened(0.05), true)
''')
]

changed=0
for old,new in repls:
    if new in s:
        continue
    if old not in s:
        raise SystemExit("D2B.2E weapon geometry anchor missing")
    s=s.replace(old,new,1)
    changed+=1

p.write_text(s,encoding="utf-8")
print(f"Applied v0.19.0D2B.2E slimmer firearm geometry ({changed} refinements).")
