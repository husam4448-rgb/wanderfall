#!/usr/bin/env python3
"""SP v265.2: replace visible primitive grass, stone, water and animal art.
Apply AFTER v265.1 source patch. Gameplay/saves/collision unchanged.
"""
from pathlib import Path
import re,shutil,sys
game=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
protected=[
 "scripts/player.gd","scripts/mobile_hud.gd","scripts/virtual_joystick.gd",
 "scripts/save/save_manager.gd","scripts/world/world_manager.gd",
 "scripts/world/occlusion_silhouette_overlay.gd",
]
before={p:(game/p).read_bytes() for p in protected}
assets=game/"assets/biomes/v2652"
assert len(list(assets.glob("*.png")))==90,"v265.2 asset build incomplete"
src=repo/"worldgen/v2652_organic_world.gd"
dst=game/"scripts/world/v2652_organic_world.gd"
shutil.copy2(src,dst)
def one(s,a,b,label):
    n=s.count(a)
    if n!=1:raise SystemExit(f"SP_V2652_PATCH_ABORT {label}: {n}")
    return s.replace(a,b,1)
def replace_region(s,pattern,replacement,label):
    found=re.findall(pattern,s,flags=re.S)
    if len(found)!=1:raise SystemExit(f"SP_V2652_PATCH_ABORT {label}: {len(found)}")
    return re.sub(pattern,lambda _:replacement,s,count=1,flags=re.S)
chunk=game/"scripts/world/world_chunk.gd"
s=chunk.read_text()
s=one(s,
 'const V2651_CANOPY = preload("res://scripts/world/v2651_canopy_hit.gd")',
 '''const V2651_CANOPY = preload("res://scripts/world/v2651_canopy_hit.gd")
const V2652_ORGANIC = preload("res://scripts/world/v2652_organic_world.gd")''',
 "new organic renderer import")
# Water placement/road/building exclusion stay from approved v2651.
s=replace_region(s,
 r'func _draw_water\(\) -> void:\n.*?(?=func _draw_roads\(\) -> void:)',
 '''func _draw_water() -> void:
    # Native baked pond sprite: irregular bank, silt, reeds and water texture.
    # Lake centers and original occupancy/collision checks are unchanged.
    V2652_ORGANIC.paint_ponds(self,_water_centers,chunk_coord,world_seed,float(CHUNK_SIZE))

''',"remove radial geometric lake polygons")
# Replace the entire giant repeated grass family with connected mask + organic sprites.
s=replace_region(s,
 r'    var grass_key := "grass_dry".*?(?=    for i in range\(_quality_count\(_flower_positions.size\(\), detail_density\)\):)',
 '''    V2652_ORGANIC.paint_grass(self,_grass_tuft_positions,chunk_coord,
        world_seed,float(CHUNK_SIZE),grass_density)
''',"remove repeated straight comb tuft sprites")
s=one(s,
 '        _draw_prop("rock", Rect2(p - Vector2(32, 30), Vector2(64, 56)))',
 '''        V2652_ORGANIC.paint_rocks(self,[p],chunk_coord,world_seed,float(CHUNK_SIZE))''',
 "replace single generic rock geometry; retain collider")
chunk.write_text(s)

# Original wildlife class owns health, behavior, drops, persistence, hitboxes.
# Only substitute _draw() pixel art; GPU occlusion loads the same re-baked PNG.
wild=game/"scripts/ecology/wildlife_actor.gd"
s=wild.read_text()
s=one(s,'extends CharacterBody2D\n',
'''extends CharacterBody2D
const SP_V2652_ANIMALS = {
    "deer": preload("res://assets/sp_melee/v262_animal_deer.png"),
    "boar": preload("res://assets/sp_melee/v262_animal_boar.png"),
    "chicken": preload("res://assets/sp_melee/v262_animal_chicken.png"),
    "rat": preload("res://assets/sp_melee/v262_animal_rat.png"),
    "dead": preload("res://assets/sp_melee/v262_animal_dead.png"),
}
''',"wildlife sprites")
replacement='''func _draw() -> void:
    if _looted:
        return
    var appearance: String = "dead" if _dead else species_id
    var sprite: Texture2D = SP_V2652_ANIMALS.get(appearance)
    if sprite != null:
        draw_texture_rect(sprite,Rect2(Vector2(-32,-36),Vector2(64,72)),false)
    if not _dead and health < max_health:
        var ratio: float = clampf(health/max_health,0.0,1.0)
        draw_rect(Rect2(-15,-20,30,3),Color(0.15,0.12,0.12,0.8),true)
        draw_rect(Rect2(-15,-20,30*ratio,3),Color("cf6b58"),true)

'''
s=replace_region(s,r'func _draw\(\) -> void:\n.*?(?=func _draw_ellipse\()',replacement,
 "replace old animal circles with species-contoured authentic raster sprites")
wild.write_text(s)
for p,v in before.items():
    if (game/p).read_bytes()!=v:
        raise SystemExit(f"SP_V2652_PROTECTED_GAMEPLAY_CHANGED {p}")
assert s.count("SP_V2652_ANIMALS")==2
assert not chunk.read_text().count('        _draw_prop("rock",')
assert not chunk.read_text().count('    var grass_key := "grass_dry"')
assert "V2651_CLUTTER.paint" in chunk.read_text()
assert "V2651_CANOPY.hit" in chunk.read_text()
print("SP_V2652_ORGANIC_INTEGRATION_PASS: 90 PNGs, all 9 biome grass/rocks/ponds, 4 animal species+carcass, original gameplay intact")
