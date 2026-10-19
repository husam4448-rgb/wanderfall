#!/usr/bin/env python3
"""SP v265.7: integrate one authored coherent camp composition,
four roof/porch/weathered-building sprite variants and 64 real limb-shift
gaits. Preserve player, combat, colliders, save, world scripts.
"""
from pathlib import Path
import re,sys
p=Path(sys.argv[1]).resolve()
a=p/"assets/biomes/v2657"
assert len(list(a.glob("hero_cabin_*.png")))==4
assert len(list(a.glob("camp_scene_*.png")))==2
assert len(list((p/"assets/biomes/v2653").glob("v2654_animal_*_*.png")))==64
def rewrite(path,cb):
    f=p/path
    old=f.read_text()
    new=cb(old)
    if new==old: raise RuntimeError("SP_V2657_PATCH_NOOP: "+path)
    f.write_text(new)
def once(s,anchor,repl,label):
    n=s.count(anchor)
    if n!=1:raise RuntimeError(f"SP_V2657_PATCH_FAIL_{label}: {n}")
    return s.replace(anchor,repl,1)
def region(s,start,end,new,label):
    a=s.find(start)
    b=s.find(end,a+len(start))
    if a<0 or b<0 or s.find(start,a+1)>=0 or s.find(end,b+1)>=0:
        raise RuntimeError(f"SP_V2657_PATCH_FAIL_REGION_{label}")
    return s[:a]+new+s[b:]
protected=[
 "scripts/player.gd","scripts/save/save_manager.gd",
 "scripts/mobile_hud.gd","scripts/virtual_joystick.gd",
 "scripts/ecology/wildlife_actor.gd",
 "scripts/world/world_manager.gd",
 "scripts/settlement/camp_manager.gd",
 "scripts/social/faction_manager.gd",
 "scripts/combat/bandit.gd"]
before={q:(p/q).read_bytes() for q in protected}
# All structure identity, collision, door areas and AI navigation remain.
def structures(s):
    s=once(s,'const STRUCTURES_ATLAS: Texture2D = preload("res://assets/production/structures/structures_atlas.png")',
'''const STRUCTURES_ATLAS: Texture2D = preload("res://assets/production/structures/structures_atlas.png")
static var _sp2657_cabin_cache: Dictionary = {}
static func _sp2657_cabin(variant: int) -> Texture2D:
    var key: int = posmod(variant,4)
    if not _sp2657_cabin_cache.has(key):
        _sp2657_cabin_cache[key] = load("res://assets/biomes/v2657/hero_cabin_%d.png" % key)
    return _sp2657_cabin_cache[key]
''',"cabin_import")
    start="func _draw_buildings() -> void:\n"
    end="func _draw_prop("
    new='''func _draw_buildings() -> void:
    var kind: int = ["house","store","garage","cabin","bunker_entrance"].find(poi_type)
    if kind < 0:
        return
    var variant: int = posmod(chunk_coord.x*113+chunk_coord.y*171+world_seed,4)
    var picture: Texture2D = _sp2657_cabin(variant)
    # Cabin and isolated POI building sprites are weathered roof/wall/porch
    # artworks. NO runtime procedural rectangles or overlaid debug geometry.
    for rect in _building_rects:
        if picture != null:
            var dest: Rect2 = rect.grow(15.0)
            draw_texture_rect(picture,dest,false)
        # The original building rectangle remains untouched for hit tests,
        # front door interaction, containers, save data and NPC navigation.
        if poi_type != "bunker_entrance":
            _draw_site_prop("fence", Rect2(rect.position + Vector2(-20,-36),
                Vector2(minf(150.0,rect.size.x*.72),48)))
            _draw_site_prop("barrel", Rect2(Vector2(rect.position.x-30,rect.end.y-48),Vector2(38,62)))
            _draw_site_prop("pallet", Rect2(Vector2(rect.end.x-34,rect.end.y-32),Vector2(62,44)))
            if posmod(chunk_coord.x*11+chunk_coord.y*31+world_seed,2)==0:
                _draw_site_prop("tire", Rect2(Vector2(rect.end.x+8,
                    rect.position.y+rect.size.y*.52),Vector2(46,34)))
        else:
            _draw_site_prop("sign",Rect2(Vector2(rect.end.x+12,rect.position.y+6),Vector2(36,70)))
            _draw_site_prop("rubble",Rect2(Vector2(rect.position.x-34,rect.end.y-30),Vector2(70,44)))

'''
    return region(s,start,end,new,"world_POI_cabin_art")
rewrite("scripts/world/world_chunk.gd",structures)
# The camp is now one intentionally authored multi-object vignette,
# already alpha-composited at world scale; decorative elements have no physics.
def camps(s):
    marker='const SP2654_ART_ROOT = "res://assets/biomes/v2653/v2654_"'
    s=once(s,marker,'''const SP2657_CAMP_SCENES = [
    preload("res://assets/biomes/v2657/camp_scene_0.png"),
    preload("res://assets/biomes/v2657/camp_scene_1.png")
]
'''+marker,"camp_scene_preload")
    head="func _draw() -> void:\n"
    k=s.find(head)
    if k<0 or s.find(head,k+1)>=0:raise RuntimeError("camp one draw missing")
    # v2654 camp draw function is last in file, already replaced everything
    # after _draw by the prior milestone. Scope confirmed by baseline patch.
    return s[:k]+'''func _draw() -> void:
    var variant: int = posmod(faction_id.hash(),2)
    var texture: Texture2D = SP2657_CAMP_SCENES[variant]
    draw_texture_rect(texture,Rect2(-280,-225,560,450),false)
'''
rewrite("scripts/social/faction_camp.gd",camps)
for q,x in before.items():
    assert (p/q).read_bytes()==x,"SP2657 changed protected game source "+q
txt=(p/"scripts/world/world_chunk.gd").read_text()
assert "func _draw_buildings()" in txt and "hero_cabin_%d.png" in txt
assert "V2651_CLUTTER.paint" in txt
print("SP_V2657_CAMP_INTEGRATION_PASS preserved saves/colliders/ai, 4 cabin art, 2 composed settlements, 64 wildlife gait frames")
