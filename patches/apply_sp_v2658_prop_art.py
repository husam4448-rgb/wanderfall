#!/usr/bin/env python3
"""Visual-only v265.8 replacement of all actually used v2654 camp props.
Patch AFTER v2657 hero-camp restoration. No AI/nav/loot/collision/save edits.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
art=root/"assets/biomes/v2658"
assert len(list(art.glob("*.png")))==24*2+2,(len(list(art.glob("*.png"))))
keep=["scripts/player.gd","scripts/social/faction_manager.gd",
"scripts/settlement/camp_manager.gd","scripts/world/world_manager.gd",
"scripts/save/save_manager.gd","scripts/mobile_hud.gd",
"scripts/virtual_joystick.gd","scripts/combat/bandit.gd",
"scripts/ecology/wildlife_actor.gd"]
before={p:(root/p).read_bytes() for p in keep}
def one(s,old,new,label):
    n=s.count(old)
    if n!=1:raise RuntimeError(f"SP_V2658_SAFE_PATCH_ABORT {label}: {n}")
    return s.replace(old,new,1)
def edit(p,fn):
    file=root/p
    s=file.read_text(encoding="utf-8");changed=fn(s)
    assert changed!=s,p
    file.write_text(changed,encoding="utf-8")
def world(s):
    old='''        _sp2654_site_cache[key] = load(
            "res://assets/biomes/v2653/v2654_%s.png" % key)'''
    new='''        # Material-authored independent v2658 sprites with all previous
        # prop families left available as fallback. Existing scene collision,
        # door approaches and streamed placement remain unchanged.
        var new_path: String = "res://assets/biomes/v2658/%s.png" % key
        if ResourceLoader.exists(new_path):
            _sp2654_site_cache[key] = load(new_path)
        else:
            _sp2654_site_cache[key] = load(
                "res://assets/biomes/v2653/v2654_%s.png" % key)'''
    return one(s,old,new,"POI prop cache")
edit("scripts/world/world_chunk.gd",world)
def faction(s):
    return one(s,'"res://assets/biomes/v2657/camp_scene_%d.png" % index',
        '"res://assets/biomes/v2658/camp_scene_%d.png" % index',
        "composed faction camp art")
edit("scripts/social/faction_camp.gd",faction)
def regular(s):
    old='''        _sp2654_cache[key] = load(SP2654_ART_ROOT + key + ".png")'''
    new='''        var new_path: String = "res://assets/biomes/v2658/" + key + ".png"
        _sp2654_cache[key] = (load(new_path) if ResourceLoader.exists(new_path)
            else load(SP2654_ART_ROOT + key + ".png"))'''
    return one(s,old,new,"interactive buildable/encounter prop fallback")
for p in ("scripts/settlement/buildable_structure.gd",
          "scripts/settlement/camp_site.gd",
          "scripts/events/dynamic_event_site.gd"):
    edit(p,regular)
for p,c in before.items():
    assert (root/p).read_bytes()==c,"protected game behavior changed: "+p
assert 'v2658/camp_scene' in (root/"scripts/social/faction_camp.gd").read_text()
assert 'v2658/%s.png' in (root/"scripts/world/world_chunk.gd").read_text()
print("SP_V2658_RUNTIME_INTEGRATION_PASS 48 distinct prop raster variants; 2 composed faction camps; old game systems/POI placements preserved")
