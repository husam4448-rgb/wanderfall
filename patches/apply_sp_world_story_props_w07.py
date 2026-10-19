#!/usr/bin/env python3
"""SP W07 source-authored CC0 prop atlas / believable homestead & workshop layouts.
Artwork: rubberduck, https://opengameart.org/content/isometric-medieval-props (CC0).
No gameplay, save, physics, NPC or controls modifications.
"""
from pathlib import Path
from PIL import Image, ImageEnhance
import io,sys,zipfile

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
archive=Path(sys.argv[2] if len(sys.argv)>2 else "/tmp/sp-w07-props.zip")
source="medieval_props_2x2_128x64_shaded.png"
if not archive.is_file():raise SystemExit("Missing CC0 environmental sprites")
with zipfile.ZipFile(archive) as z:
    names=[n for n in z.namelist() if n.endswith(source)]
    if len(names)!=1:raise SystemExit("Unexpected source sheet")
    sheet=Image.open(io.BytesIO(z.read(names[0]))).convert("RGBA")
if sheet.size!=(2048,768):raise SystemExit("Unexpected source sprite dimensions")
atlas=Image.new("RGBA",(768,960))
for i in range(18):
    sprite=sheet.crop(((i%8)*256,(i//8)*256,(i%8+1)*256,(i//8+1)*256))
    box=sprite.getchannel("A").getbbox()
    if not box:raise SystemExit("Empty source sprite "+str(i))
    sprite=sprite.crop(box)
    sprite.thumbnail((180,171),Image.Resampling.LANCZOS)
    alpha=sprite.getchannel("A")
    sprite=ImageEnhance.Color(sprite).enhance(.87)
    sprite.putalpha(alpha)
    atlas.alpha_composite(sprite,((i%4)*192+(192-sprite.width)//2,(i//4)*192+188-sprite.height))
dest=root/"assets/production/props/settlement_props_w07.png"
dest.parent.mkdir(parents=True,exist_ok=True)
atlas.save(dest,optimize=True)

wp=root/"scripts/world/world_chunk.gd"
w=wp.read_text(encoding="utf-8")
if "SP_WORLD_STORY_PROPS_W07" in w:raise SystemExit("Already applied")
if "SP_WORLD_ROCKS_W06" not in w:raise SystemExit("W06 rock integration required")
preload='const BUILDINGS_W05: Texture2D = preload("res://assets/production/structures/wooden_cabins_w05.png")\n'
if w.count(preload)!=1:raise SystemExit("W05 preload not found")
w=w.replace(preload,preload+'const SETTLEMENT_W07: Texture2D = preload("res://assets/production/props/settlement_props_w07.png")\n',1)
# User rejected W01 decal overlay. Preserve existing terrain tile renderer.
ground='    _sp_draw_ground_detail_w01()\n'
if w.count(ground)!=1:raise SystemExit("W01 ground call not found")
w=w.replace(ground,'    # W07: rejected W01 noisy ground overlay disabled.\n',1)
old='    _draw_buildings()\n    _sp_draw_homestead_w05()\n'
new='    _draw_buildings()\n    _sp_draw_story_sites_w07()\n    _sp_draw_homestead_w05()\n    _sp_draw_starter_site_w07()\n'
if w.count(old)!=1:raise SystemExit("World draw ordering changed")
w=w.replace(old,new,1)
w+='''
# SP_WORLD_STORY_PROPS_W07: 18 genuinely authored variants, zero new nodes.
func _sp_draw_w07_prop(index: int, center: Vector2, draw_size: Vector2) -> void:
    var col: int = posmod(index,4)
    var row: int = int(index/4)
    draw_texture_rect_region(SETTLEMENT_W07,
        Rect2(center-draw_size*0.5,draw_size),
        Rect2(float(col)*192.0,float(row)*192.0,192.0,192.0))

func _sp_draw_starter_site_w07() -> void:
    # One established remote homestead rather than identical random objects.
    # Uses the original W05 cabin/physics; adds only source-authored utilities.
    if chunk_coord != Vector2i(-1,-1):
        return
    var p:=Vector2(425.0,470.0)
    _sp_draw_w07_prop(4,p+Vector2(166.0,-20.0),Vector2(81,95))
    _sp_draw_w07_prop(0,p+Vector2(167.0,77.0),Vector2(92,67))
    _sp_draw_w07_prop(8,p+Vector2(-111.0,102.0),Vector2(87,74))
    _sp_draw_w07_prop(14,p+Vector2(64.0,126.0),Vector2(87,69))

func _sp_draw_story_sites_w07() -> void:
    if _building_rects.is_empty():
        return
    var rect: Rect2 = _building_rects[0]
    var hash_id: int = posmod(_chunk_hash(chunk_coord,world_seed),2147483647)
    var side: float = 1.0 if rect.get_center().x < CHUNK_SIZE*0.5 else -1.0
    var side_x: float = clampf(rect.get_center().x + side*(rect.size.x*0.5+78.0),64.0,CHUNK_SIZE-64.0)
    var front_y: float = clampf(rect.end.y+46.0,60.0,CHUNK_SIZE-60.0)
    var back_y: float = clampf(rect.position.y-28.0,60.0,CHUNK_SIZE-60.0)
    var yard := Vector2(side_x,front_y)
    if _near_road(yard,65.0):
        yard.y=back_y
    if _near_road(yard,65.0):
        yard.x=clampf(rect.get_center().x+side*145.0,65.0,CHUNK_SIZE-65.0)
    if _near_road(yard,65.0):
        return
    match poi_type:
        "house":
            _sp_draw_w07_prop(4+posmod(hash_id,2),yard+Vector2(-33.0,-20.0),Vector2(85,95))
            _sp_draw_w07_prop(posmod(int(hash_id/7),4),yard+Vector2(55.0,22.0),Vector2(80,62))
            _sp_draw_w07_prop(8+posmod(int(hash_id/31),2),yard+Vector2(1.0,81.0),Vector2(75,61))
        "store":
            _sp_draw_w07_prop(10+posmod(hash_id,2),yard+Vector2(-38.0,4.0),Vector2(117,109))
            _sp_draw_w07_prop(12+posmod(int(hash_id/17),2),yard+Vector2(69.0,13.0),Vector2(112,103))
            _sp_draw_w07_prop(0,yard+Vector2(13.0,105.0),Vector2(85,62))
        "garage":
            _sp_draw_w07_prop(posmod(hash_id,4),yard+Vector2(-33.0,5.0),Vector2(112,87))
            _sp_draw_w07_prop(14+posmod(int(hash_id/13),2),yard+Vector2(56.0,-18.0),Vector2(108,87))
            _sp_draw_w07_prop(8,yard+Vector2(37.0,66.0),Vector2(86,67))
        "cabin":
            _sp_draw_w07_prop(4+posmod(hash_id,2),yard+Vector2(-39.0,-10.0),Vector2(89,96))
            _sp_draw_w07_prop(6+posmod(int(hash_id/9),2),yard+Vector2(63.0,3.0),Vector2(113,104))
            _sp_draw_w07_prop(posmod(int(hash_id/19),4),yard+Vector2(13.0,100.0),Vector2(86,61))
'''
wp.write_text(w,encoding="utf-8")
print("SP_W07_PASS: 18 hand-authored CC0 prop variations; POI-specific layouts; W01 ground decal overlay disabled")
