#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d20_master_texture_islands.gd"
if not script.exists():
    raise SystemExit("D2D.21 requires D2D.20 master-texture islands")

s = script.read_text(encoding="utf-8")

old = '''    poly.texture = BODY_TEXTURE
    poly.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    poly.antialiased = true
    poly.z_index = z_value
    poly.skeleton = poly.get_path_to(skeleton)
    rig_root.add_child(poly)
'''
new = '''    poly.texture = BODY_TEXTURE
    poly.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    poly.antialiased = true
    poly.z_index = z_value

    # IMPORTANT: the Polygon2D must be in the scene tree before its skeleton
    # NodePath is resolved. D2D.20 resolved get_path_to() while poly was still
    # parentless, so the debug bones moved but the visual mesh stayed static.
    rig_root.add_child(poly)
    poly.skeleton = NodePath("../Skeleton2D")
'''
if old not in s:
    raise SystemExit("D2D.21 skeleton-binding anchor missing")
s = s.replace(old,new,1)

old = '    poly.internal_vertex_count = vertices.size()\n'
new = '''    # These vertices are explicitly triangulated through poly.polygons.
    # Do not mark the entire array as internal: doing so leaves no exterior
    # vertex set for Godot's Polygon2D skinning path.
    poly.internal_vertex_count = 0
'''
if old not in s:
    raise SystemExit("D2D.21 internal vertex anchor missing")
s = s.replace(old,new,1)

old = '        poly.add_bone(poly.get_path_to(bones[name]),weights)\n'
new = '''        var bone_path := poly.get_path_to(bones[name])
        if bone_path.is_empty():
            push_error("D2D.21 empty bone path for %s / %s" % [region,name])
        poly.add_bone(bone_path,weights)
'''
if old not in s:
    raise SystemExit("D2D.21 bone path anchor missing")
s = s.replace(old,new,1)

s = s.replace('D2D.20 — MASTER-TEXTURE MULTI-ISLAND SKIN',
              'D2D.21 — LIVE-BOUND MULTI-ISLAND SKIN',1)
s = s.replace('South prototype • same master texture • isolated arm/leg topology • chest-only breathing',
              'South prototype • live Skeleton2D binding • isolated topology • chest-only breathing',1)
s = s.replace('Arms and legs cannot pull pixels from the torso or shorts. All islands still sample one approved texture.',
              'Each island is now bound after entering the scene tree, then weighted to the live Skeleton2D.',1)

script.write_text(s,encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$','version/code=94',e,count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.21"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.21"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.21 live Skeleton2D binding fix for all mesh islands.")
