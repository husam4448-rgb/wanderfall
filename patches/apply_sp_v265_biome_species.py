#!/usr/bin/env python3
"""v265 art correction: actual trees and canopy sprites must match macro biome.
Keep tree harvesting, save IDs, collision generation and original controls.
"""
from pathlib import Path
import sys
game=Path(sys.argv[1]).resolve()
def rewrite(path,old,new,label):
    full=game/path
    text=full.read_text(encoding="utf-8")
    count=text.count(old)
    if count!=1:
        raise SystemExit(f"SP_V265_SPECIES_PATCH_FAIL {label}: {count} anchors")
    full.write_text(text.replace(old,new,1),encoding="utf-8")

rewrite("scripts/world/world_chunk.gd",
"""        if _near_road(p, 72.0):
            continue
        if i % 4 == 0:""",
"""        if _near_road(p, 72.0):
            continue
        # Preserve every 4th interactive lumber node and its stable save ID.
        # Only thin decorative broadleaf trees in open/harsh climates.
        if macro_biome_id == 4 and i % 4 != 0:
            continue
        if macro_biome_id == 2 and i % 4 != 0 and i % 3 != 0:
            continue
        if i % 4 == 0:""",
"biome-specific tree counts")
rewrite("scripts/world/world_chunk.gd",
"""            if keep_value > grass_density:
                continue
            var scale_jitter :=""",
"""            if keep_value > grass_density:
                continue
            # Sparse burnt grass in arid soil, without impacting collectables.
            if macro_biome_id == 4 and posmod(gh, 5) != 0:
                continue
            var scale_jitter :=""",
"dryland grass thinning")

rewrite("scripts/world/tree_canopy_overlay.gd",
"""const PROPS_ATLAS: Texture2D = preload("res://assets/production/props/props_atlas.png")""",
"""const PROPS_ATLAS: Texture2D = preload("res://assets/production/props/props_atlas.png")
const V265_RASTER = preload("res://scripts/world/world_biome_raster.gd")""",
"overlay raster import")
rewrite("scripts/world/tree_canopy_overlay.gd",
"""            draw_texture_rect_region(PROPS_ATLAS, Rect2(p - Vector2(53, 106), Vector2(106, 111)), source)""",
"""            var macro_id: int = int(chunk_ref.get("macro_biome_id"))
            if V265_RASTER.BIOME_NAMES.has(macro_id):
                var variation: int = posmod(int(p.x*13.0 + p.y*17.0), 3)
                var raster: Texture2D = V265_RASTER._get_texture(
                    macro_id, variation, "foliage")
                if raster != null:
                    draw_texture_rect(raster,
                        Rect2(p - Vector2(56, 99), Vector2(112, 112)), false)
            else:
                draw_texture_rect_region(PROPS_ATLAS,
                    Rect2(p - Vector2(53, 106), Vector2(106, 111)), source)""",
"replace round decorative canopy silhouettes")
rewrite("scripts/ecology/natural_resource.gd",
"""const PROPS_ATLAS: Texture2D = preload("res://assets/production/props/props_atlas.png")""",
"""const PROPS_ATLAS: Texture2D = preload("res://assets/production/props/props_atlas.png")
const V265_RASTER = preload("res://scripts/world/world_biome_raster.gd")""",
"resource raster import")
rewrite("scripts/ecology/natural_resource.gd",
"""        _tree_canopy_sprite.scale = Vector2(1.325,1.325)

func _sync_tree_layer_sprites()""",
"""        _tree_canopy_sprite.scale = Vector2(1.325,1.325)
        var owner_chunk: Node = get_parent()
        if owner_chunk != null:
            var macro: int = int(owner_chunk.get("macro_biome_id"))
            if V265_RASTER.BIOME_NAMES.has(macro):
                var variant: int = posmod(generation_seed,3)
                var image: Texture2D = V265_RASTER._get_texture(
                    macro,variant,"foliage")
                if image != null:
                    _tree_canopy_sprite.texture = image
                    _tree_canopy_sprite.scale = Vector2.ONE
                    _tree_canopy_sprite.position = Vector2(0,-39)

func _sync_tree_layer_sprites()""",
"reskinned interactive canopy")
rewrite("scripts/ecology/natural_resource.gd",
"""    _tree_trunk_sprite.visible = active
    _tree_canopy_sprite.visible = active""",
"""    var parent_chunk: Node = get_parent()
    var macro: int = -1
    if parent_chunk != null:
        macro = int(parent_chunk.get("macro_biome_id"))
    _tree_trunk_sprite.visible = active and macro != 2 and macro != 4
    _tree_canopy_sprite.visible = active""",
"remove oversized timber under shrubs")
print("SP_V265_SPECIES_ART_PASS: dryland broadleaf removal and foliage silhouettes updated; interactive resource/save behavior retained")
