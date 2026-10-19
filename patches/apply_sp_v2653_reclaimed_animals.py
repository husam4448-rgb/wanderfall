#!/usr/bin/env python3
"""v265.3: replace only resource/building/container presentation and animal
sprite animation. Preserve all existing world, collision, AI and save logic.
"""
from pathlib import Path
import re, sys
game=Path(sys.argv[1]).resolve()
assert len(list((game/"assets/biomes/v2653").glob("*.png")))==114,"Missing v2653 raster assets"
protected=["scripts/player.gd","scripts/mobile_hud.gd","scripts/virtual_joystick.gd",
    "scripts/save/save_manager.gd","scripts/world/world_manager.gd"]
before={p:(game/p).read_bytes() for p in protected}
def once(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"SP2653 {label} anchor {n}")
    return s.replace(a,b,1)
def region(s,start,end,replacement,label):
    if s.count(start)!=1 or s.count(end)!=1:raise RuntimeError(f"SP2653 {label} non-unique")
    a=s.index(start);b=s.index(end,a+len(start))
    return s[:a]+replacement+s[b:]
def edit(p,fn):
    f=game/p;s=f.read_text();out=fn(s)
    assert out!=s,p
    f.write_text(out)

def natural(s):
    s=once(s,'const PROPS_ATLAS: Texture2D = preload("res://assets/production/props/props_atlas.png")',
'''const PROPS_ATLAS: Texture2D = preload("res://assets/production/props/props_atlas.png")
static var _v2653_berry_cache: Dictionary = {}
static func _v2653_berry_image(biome: int, variant: int) -> Texture2D:
    var key: String = "%d_%d" % [biome,variant]
    if not _v2653_berry_cache.has(key):
        _v2653_berry_cache[key] = load("res://assets/biomes/v2653/berry_%d_%d.png" % [biome,variant])
    return _v2653_berry_cache[key]
''',"berry cache")
    s=once(s,'''        "berry_bush":
            var tint := Color(.58,.58,.58,.72) if _depleted else Color.WHITE
            draw_texture_rect_region(PROPS_ATLAS,Rect2(-32,-34,64,56),BUSH_REGION,tint)''',
'''        "berry_bush":
            var tint := Color(.58,.58,.58,.72) if _depleted else Color.WHITE
            var owner_chunk: Node = get_parent()
            var macro: int = 0
            if owner_chunk != null:
                macro = clampi(int(owner_chunk.get("macro_biome_id")),0,8)
            var foliage: Texture2D = _v2653_berry_image(macro,posmod(generation_seed,4))
            if foliage != null:
                draw_texture_rect(foliage,Rect2(-46,-49,92,76),false,tint)''',
"berry renderer")
    return s
edit("scripts/ecology/natural_resource.gd",natural)

def chunk(s):
    s=once(s,'const STRUCTURES_ATLAS: Texture2D = preload("res://assets/production/structures/structures_atlas.png")',
'''const STRUCTURES_ATLAS: Texture2D = preload("res://assets/production/structures/structures_atlas.png")
static var _v2653_structures: Dictionary = {}
static func _v2653_structure_tex(kind: int,variant: int) -> Texture2D:
    var key: String = "%d_%d" % [kind,variant]
    if not _v2653_structures.has(key):
        _v2653_structures[key] = load("res://assets/biomes/v2653/building_%d_%d.png" % [kind,variant])
    return _v2653_structures[key]
''',"structure cache")
    s=region(s,'func _draw_buildings() -> void:\n','func _draw_prop(',
'''func _draw_buildings() -> void:
    var kind: int = ["house","store","garage","cabin","bunker_entrance"].find(poi_type)
    if kind < 0:
        return
    var variant: int = posmod(chunk_coord.x*113+chunk_coord.y*171+world_seed,2)
    var picture: Texture2D = _v2653_structure_tex(kind,variant)
    for rect in _building_rects:
        if picture != null:
            draw_texture_rect(picture,rect.grow(11.0),false)
        # Keep placement and interactive contents at their original coordinates.
        if poi_type != "bunker_entrance":
            _draw_site_prop("fence", Rect2(rect.position + Vector2(-20,-36),
                Vector2(minf(150.0,rect.size.x*.72),48)))
            _draw_site_prop("barrel",Rect2(Vector2(rect.position.x-30,rect.end.y-48),Vector2(38,62)))
            _draw_site_prop("pallet",Rect2(Vector2(rect.end.x-34,rect.end.y-32),Vector2(62,44)))
            if posmod(chunk_coord.x*11+chunk_coord.y*31+world_seed,2)==0:
                _draw_site_prop("tire",Rect2(Vector2(rect.end.x+8,
                    rect.position.y+rect.size.y*.52),Vector2(46,34)))
        else:
            _draw_site_prop("sign",Rect2(Vector2(rect.end.x+12,rect.position.y+6),Vector2(36,70)))
            _draw_site_prop("rubble",Rect2(Vector2(rect.position.x-34,rect.end.y-30),Vector2(70,44)))

''',"building renderer")
    s=once(s,'''func _draw_site_prop(key: String, destination: Rect2) -> void:
    var region: Rect2 = SITE_PROP_REGIONS.get(key, Rect2())
    if region.size != Vector2.ZERO:
        draw_texture_rect_region(SITE_PROPS_ATLAS, destination, region)''',
'''func _draw_site_prop(key: String, destination: Rect2) -> void:
    var keys: Array[String] = ["barrel","tire","pallet","fence","sign","rubble"]
    var kind: int = keys.find(key)
    if kind >= 0:
        var tex: Texture2D = V2651_CLUTTER._sprite(clampi(macro_biome_id,0,8),kind)
        if tex != null:
            draw_texture_rect(tex,destination,false)''',"site props renderer")
    return s
edit("scripts/world/world_chunk.gd",chunk)

def loot(s):
    s=once(s,'class_name LootContainer\nextends Node2D',
'''class_name LootContainer
extends Node2D
static var _v2653_crates: Dictionary = {}
static func _v2653_crate_image(index: int) -> Texture2D:
    if not _v2653_crates.has(index):
        _v2653_crates[index] = load("res://assets/biomes/v2653/crate_%d.png" % index)
    return _v2653_crates[index]
''',"crate cache")
    s=region(s,'func _draw() -> void:\n','func _draw_ellipse(',
'''func _draw() -> void:
    var empty: bool = is_empty()
    var style: int = posmod(generation_seed + (1 if loot_profile=="bandit" else 0),4)
    var icon: Texture2D = _v2653_crate_image(style)
    if icon != null:
        draw_texture_rect(icon,Rect2(-29,-25,58,48),false,
            Color(0.67,0.66,0.63,0.70) if empty else Color.WHITE)

''',"loot visuals")
    return s
edit("scripts/items/loot_container.gd",loot)

def animals(s):
    s=once(s,'const SP_V2652_ANIMALS = {',
'''static var _v2653_anim_cache: Dictionary = {}
var _v2653_face: String = "right"
var _v2653_phase: float = 0.0
var _v2653_frame: int = 0
var _v2653_walking: bool = false

func _v2653_image() -> Texture2D:
    if _dead:
        return SP_V2652_ANIMALS["dead"]
    var frame: int = _v2653_frame if _v2653_walking else 0
    var key: String = "%s_%s_%d" % [species_id,_v2653_face,frame]
    if not _v2653_anim_cache.has(key):
        _v2653_anim_cache[key] = load("res://assets/biomes/v2653/animal_%s.png" % key)
    return _v2653_anim_cache[key]

const SP_V2652_ANIMALS = {''',"animal art cache")
    s=once(s,'''    move_and_slide()
    if velocity.length_squared() > 1.0 and _visual_redraw_accum >= 0.05:
        _visual_redraw_accum = 0.0
        queue_redraw()''',
'''    move_and_slide()
    var walking: bool = velocity.length_squared()>16.0
    var previous: int = _v2653_frame
    var facing: String = _v2653_face
    if absf(velocity.x)>1.0:
        _v2653_face = "right" if velocity.x>0.0 else "left"
    if walking:
        _v2653_phase += delta*(10.0 if _flee_timer>0.0 else 7.5)
        _v2653_frame = posmod(int(floor(_v2653_phase)),8)
    else:
        _v2653_frame = 0
    var changed: bool = (walking!=_v2653_walking or previous!=_v2653_frame or facing!=_v2653_face)
    _v2653_walking = walking
    if changed:
        queue_redraw()
    if _visual_redraw_accum >= 0.11:
        _visual_redraw_accum = 0.0''',"animal animation")
    s=once(s,'''    var appearance: String = "dead" if _dead else species_id
    var sprite: Texture2D = SP_V2652_ANIMALS.get(appearance)''',
'''    var sprite: Texture2D = _v2653_image()''',"animal new frame drawing")
    return s
edit("scripts/ecology/wildlife_actor.gd",animals)

def occlusion(s):
    return once(s,'''        sprite.texture = WILDLIFE_TEXTURES["dead"] if dead else WILDLIFE_TEXTURES[state["species"]]''',
'''        if actor.has_method("_v2653_image"):
            sprite.texture = actor.call("_v2653_image")
        else:
            sprite.texture = WILDLIFE_TEXTURES["dead"] if dead else WILDLIFE_TEXTURES[state["species"]]''',"moving animal alpha mask")
edit("scripts/world/occlusion_silhouette_overlay.gd",occlusion)
for p,v in before.items():
    assert (game/p).read_bytes()==v, "Protected gameplay source changed: "+p
assert "V2651_CLUTTER.paint" in (game/"scripts/world/world_chunk.gd").read_text()
assert "V2651_CANOPY.hit" in (game/"scripts/world/world_chunk.gd").read_text()
print("SP_V2653_PRESENTATION_PATCH_PASS organic berries/weathered building and crate art; two-sided 8-frame moving animal limbs/head; gameplay protected")
