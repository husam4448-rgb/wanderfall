#!/usr/bin/env python3
"""Survival Paradise W03: genuine CC0 survival camps and scavenging prop art.
No decorative polygon tents: real source sprites from rubberduck's CC0
"Isometric props and tents", OpenGameArt. World population is deterministic.
"""
from pathlib import Path
from PIL import Image,ImageEnhance
import sys,shutil
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
source=Path(sys.argv[2] if len(sys.argv)>2 else "/tmp/props-cc0/props_2x2.png")
if not source.is_file():raise SystemExit("Missing verified CC0 camp props sheet")
raw=Image.open(source).convert("RGBA")
if raw.size!=(2048,1280):raise SystemExit(f"Unexpected source format: {raw.size}")
# Source: 8 columns x 5 rows, a 256-pixel cell per item/view.
# Keep source transparency and its artist-authored ground shadows intact.
cells=[(5,0),(1,2),(5,2),(3,3),(0,4),(0,3),(2,2),(4,1)]
out=Image.new("RGBA",(1024,512),(0,0,0,0))
for i,(col,row) in enumerate(cells):
    sprite=raw.crop((col*256,row*256,(col+1)*256,(row+1)*256))
    if sprite.getchannel("A").getbbox() is None:raise SystemExit(f"Empty source cell {col},{row}")
    # Restrained grade keeps cloth and wood brown/olive rather than saturated fantasy.
    alpha=sprite.getchannel("A")
    sprite=ImageEnhance.Color(sprite).enhance(.83)
    sprite.putalpha(alpha)
    out.alpha_composite(sprite,((i%4)*256,(i//4)*256))
target=root/"assets/production/props/camp_w03.png"
target.parent.mkdir(parents=True,exist_ok=True)
out.save(target,optimize=True)

world_path=root/"scripts/world/world_chunk.gd"
w=world_path.read_text(encoding="utf-8")
if "SP_WORLD_CAMP_W03" in w:raise SystemExit("Already patched W03")
anchor='const FOREST_W02: Texture2D = preload("res://assets/production/props/forest_w02.png")\n'
if w.count(anchor)!=1:raise SystemExit("W02 forest atlas missing")
w=w.replace(anchor,anchor+'const CAMP_W03: Texture2D = preload("res://assets/production/props/camp_w03.png")\n',1)

anchor='    _draw_buildings()\n'
if w.count(anchor)!=1:raise SystemExit("Draw order anchor missing")
w=w.replace(anchor,anchor+'    _sp_draw_camps_w03()\n',1)
# Stable origin-area starter landmark, deterministic rare forest lean-tos, and
# POI associated camp props. Does not alter the world generator or save schema.
w += """
# SP_WORLD_CAMP_W03: authored real-world static art with seeded coherent placement.
func _sp_site_w03() -> Vector2:
    if chunk_coord == Vector2i(-1, 0):
        return Vector2(435.0, 134.0)
    if not _building_rects.is_empty() and (poi_type == "cabin" or poi_type == "house"):
        var r: Rect2 = _building_rects[0]
        var x: float = r.end.x + 105.0
        if x > CHUNK_SIZE - 100.0:
            x = r.position.x - 100.0
        var y: float = clampf(r.get_center().y + 46.0, 120.0, CHUNK_SIZE - 140.0)
        return Vector2(x, y)
    if not (_has_horizontal_road or _has_vertical_road):
        if posmod(_chunk_hash(chunk_coord, world_seed), 19) == 2:
            return Vector2(310.0, 315.0)
    return Vector2(-10000.0, -10000.0)

func _sp_draw_w03_prop(sprite_id: int, center: Vector2, size: Vector2) -> void:
    var src := Rect2(float(posmod(sprite_id, 4)) * 256.0, float(int(sprite_id / 4)) * 256.0, 256.0, 256.0)
    draw_texture_rect_region(CAMP_W03, Rect2(center - size * 0.5, size), src)

func _sp_draw_camps_w03() -> void:
    var p: Vector2 = _sp_site_w03()
    if p.x < -1000.0:
        return
    # Each site has recognizable survivor purpose: sleeping, cooking, supplies.
    # The transparent source sprites already include contact shadows.
    _sp_draw_w03_prop(1, p + Vector2(-67.0, -15.0), Vector2(198.0, 170.0))
    _sp_draw_w03_prop(2, p + Vector2(111.0, -45.0), Vector2(156.0, 125.0))
    _sp_draw_w03_prop(3, p + Vector2(36.0, 108.0), Vector2(88.0, 78.0))
    _sp_draw_w03_prop(4, p + Vector2(35.0, 76.0), Vector2(83.0, 105.0))
    if posmod(_chunk_hash(chunk_coord, world_seed), 2) == 0:
        _sp_draw_w03_prop(5, p + Vector2(-108.0, 91.0), Vector2(70.0, 58.0))
"""
world_path.write_text(w,encoding="utf-8")
print("SP_W03_PASS: Authored camps and campfire/lean-to art integrated into real world renderer")
