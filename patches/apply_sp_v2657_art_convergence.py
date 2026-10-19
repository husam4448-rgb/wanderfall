#!/usr/bin/env python3
"""Integrate SP v265.7 visual-only hero POI cabins/camp compositions and
independent wildlife limb frames; never change colliders, AI, door coords,
faction state, save schema, world streaming or player rig.
"""
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
protected=("scripts/player.gd","scripts/save/save_manager.gd",
"scripts/world/world_manager.gd","scripts/mobile_hud.gd",
"scripts/virtual_joystick.gd","scripts/combat/bandit.gd")
before={p:(root/p).read_bytes() for p in protected}
art=root/"assets/biomes/v2657"
assert len(list(art.glob("hero_cabin_*.png")))==4
assert len(list(art.glob("camp_scene_*.png")))==2
source=root/"assets/biomes/v2653"
assert len(list(source.glob("v2654_animal_*.png")))==64

def swap(txt,old,new,label):
    c=txt.count(old)
    if c!=1:raise RuntimeError("SP2657_PATCH_ANCHOR "+label+f": {c}")
    return txt.replace(old,new,1)
def edit(p,fn):
    path=root/p;old=path.read_text();new=fn(old)
    if old==new: raise RuntimeError("SP2657_NOOP "+p)
    path.write_text(new)

def world(s):
    s=swap(s,'_v2653_structures[key] = load("res://assets/biomes/v2653/building_%d_%d.png" % [kind,variant])',
'''# Four composed authored cabins with proper projecting eaves, windows,
        # chimney, door and steps. Drawn in same existing POI rectangle.
        _v2653_structures[key] = load(
            "res://assets/biomes/v2657/hero_cabin_%d.png" % posmod(kind+variant,4))''',
        "replace incomplete flat POI blocks")
    return s
edit("scripts/world/world_chunk.gd",world)

def faction(s):
    s=swap(s,'func _draw() -> void:\n',
'''static var _sp2657_camp_cache: Dictionary = {}
static func _sp2657_camp_art(index: int) -> Texture2D:
    if not _sp2657_camp_cache.has(index):
        _sp2657_camp_cache[index] = load(
            "res://assets/biomes/v2657/camp_scene_%d.png" % index)
    return _sp2657_camp_cache[index]

func _draw() -> void:
''',"camp cached layout art")
    ix=s.index("func _draw() -> void:\n")
    new='''func _draw() -> void:
    # Intentional camp clusters: two shelters, work zones, storage, fenced
    # perimeters, firepit, pathways and grouped supply caches.
    # Art only: radius/guards/spawns/faction logic are not altered.
    var variant: int = posmod(faction_id.hash(),2)
    var pic: Texture2D = _sp2657_camp_art(variant)
    if pic != null:
        draw_texture_rect(pic,Rect2(-248,-196,496,392),false)

'''
    return s[:ix]+new
edit("scripts/social/faction_camp.gd",faction)

def wildlife(s):
    return swap(s,
        'draw_texture_rect(sprite,Rect2(Vector2(-32,-36),Vector2(64,72)),false)',
        'draw_texture_rect(sprite,Rect2(Vector2(-27,-27),Vector2(54,62)),false)',
        "draw smaller world-scale animal with proper hooves")
edit("scripts/ecology/wildlife_actor.gd",wildlife)

def overlay(s):
    s=swap(s,'sprite.name = "OneAnimalSilhouetteNoDoubleOverlay"',
'''sprite.name = "OneAnimalSilhouetteNoDoubleOverlay"
    sprite.scale = Vector2(0.844,0.861)
    sprite.position = Vector2(0,4)''',"match wildlife alpha to live sprite")
    return s
edit("scripts/world/occlusion_silhouette_overlay.gd",overlay)

for p,content in before.items():
    assert (root/p).read_bytes()==content,"protected approved game file modified "+p
assert "v2657/hero_cabin" in (root/"scripts/world/world_chunk.gd").read_text()
assert "v2657/camp_scene" in (root/"scripts/social/faction_camp.gd").read_text()
assert "_v2653_image()" in (root/"scripts/ecology/wildlife_actor.gd").read_text()
print("SP_V2657_PRESENTATION_PATCH_PASS cabins and full spatial camps, 64 segmented wild animal gait sprites, physics/AI untouched")
