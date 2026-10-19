#!/usr/bin/env python3
"""SP v265.4: raster presentation only, preserving saved gameplay/physics."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
a=root/"assets/biomes/v2653"
assert len(list(a.glob("v2654_*.png")))==(30*2+36+64), "v2654 required raster assets missing"
protected=("scripts/world/world_manager.gd","scripts/save/save_manager.gd",
"scripts/virtual_joystick.gd","scripts/mobile_hud.gd",
"scripts/settlement/camp_manager.gd","scripts/social/faction_manager.gd")
before={p:(root/p).read_bytes() for p in protected}
def write(path,fn):
    f=root/path;s=f.read_text(encoding="utf-8")
    newer=fn(s)
    if s==newer:raise RuntimeError("v2654 NOOP "+path)
    f.write_text(newer,encoding="utf-8")
def swap(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"v2654 {label} anchor count={n}")
    return s.replace(a,b,1)
def function(s,start,end,new,label):
    if s.count(start)!=1 or s.count(end)!=1:
        raise RuntimeError("v2654 cannot safely patch "+label)
    i=s.index(start);j=s.index(end,i+len(start))
    if j<i:raise RuntimeError("order wrong: "+label)
    return s[:i]+new+s[j:]
def draw_utility():
    return '''const SP2654_ART_ROOT = "res://assets/biomes/v2653/v2654_"
static var _sp2654_cache: Dictionary = {}
static func _sp2654_get(kind: String, variant: int = 0) -> Texture2D:
    var key: String = "%s_%d" % [kind,variant]
    if not _sp2654_cache.has(key):
        _sp2654_cache[key] = load(SP2654_ART_ROOT + key + ".png")
    return _sp2654_cache[key]

'''
def insert_helper(s):
    return swap(s,"extends Node2D\n","extends Node2D\n"+draw_utility(),"cache")

def natural(s):
    return swap(s,"_v2653_berry_image(macro,posmod(generation_seed,4))",
     '''load("res://assets/biomes/v2653/v2654_berry_%d_%d.png" % [
                  macro,posmod(generation_seed,4)])''',"attached berries")
write("scripts/ecology/natural_resource.gd",natural)

def wild(s):
    return swap(s,'load("res://assets/biomes/v2653/animal_%s.png" % key)',
       'load("res://assets/biomes/v2653/v2654_animal_%s.png" % key)',
       "detailed wildlife raster")
write("scripts/ecology/wildlife_actor.gd",wild)

def structures(s):
    s=insert_helper(s)
    new='''func _draw() -> void:
    var index: int = posmod(structure_id.hash(),2)
    var sprite: Texture2D = _sp2654_get(structure_type,index)
    if sprite != null:
        draw_texture_rect(sprite,Rect2(-39,-33,78,67),false)
    # Only living crops get small leafy stems; empty plots show bare ground.
    if structure_type == "farm_plot" and crop_state == "ready":
        draw_texture_rect(_sp2654_get("farm_plot",1),Rect2(-39,-33,78,67),false,Color(0.8,1.0,0.78,0.60))

'''
    return function(s,"func _draw() -> void:\n","func serialize_runtime() -> Dictionary:",new,"built structures")
write("scripts/settlement/buildable_structure.gd",structures)

def camps(s):
    s=insert_helper(s)
    new='''func _draw() -> void:
    # Keep the faction gameplay camp radius, but remove the intrusive perfect
    # mint ring; physical signs are weathered props instead of colored geometry.
    var variant: int = posmod(faction_id.hash(),2)
    var shelter: Texture2D = _sp2654_get("shelter",variant)
    var tent: Texture2D = _sp2654_get("tarp",variant)
    if shelter != null:
        draw_texture_rect(shelter,Rect2(-185,-164,108,105),false)
        draw_texture_rect(shelter,Rect2(66,-166,110,103),false)
    if tent != null:
        draw_texture_rect(tent,Rect2(-173,50,103,93),false)
        draw_texture_rect(tent,Rect2(72,49,105,94),false)
    for item in [
        ["table",Rect2(-51,-109,101,68)],
        ["campfire",Rect2(-40,-44,81,82)],
        ["storage_box",Rect2(144,-39,74,59)],
        ["barrel",Rect2(-212,-12,54,62)],
        ["fence",Rect2(-200,-195,121,69)]]:
        var sprite: Texture2D = _sp2654_get(String(item[0]),variant)
        if sprite != null:
            draw_texture_rect(sprite,item[1],false)

'''
    return function(s,"func _draw() -> void:\n","",new,"faction camp") if False else re.sub(
        r'func _draw\(\) -> void:\n[\s\S]*\Z',new,s,count=1)
write("scripts/social/faction_camp.gd",camps)

def playercamp(s):
    s=insert_helper(s)
    return function(s,"func _draw() -> void:\n","\nNO_END_UNIQUE\n",
      "", "not used") if False else re.sub(
    r'func _draw\(\) -> void:\n[\s\S]*\Z','''func _draw() -> void:
    var tarp: Texture2D = _sp2654_get("shelter",0)
    var fire: Texture2D = _sp2654_get("campfire",1)
    if tarp != null: draw_texture_rect(tarp,Rect2(-32,-38,64,59),false)
    if fire != null: draw_texture_rect(fire,Rect2(-21,1,42,36),false)
''',s,count=1)
write("scripts/settlement/camp_site.gd",playercamp)

def events(s):
    s=insert_helper(s)
    new='''func _draw() -> void:
    var kind: String = "wreck" if site_tag == "wreck" else (
        "distress" if site_tag == "distress" else "cache")
    var empty: bool = WorldState.get_container_loot(
        site_id,generation_seed,loot_profile).is_empty()
    var sprite: Texture2D = _sp2654_get(kind,posmod(generation_seed,2))
    if sprite != null:
        draw_texture_rect(sprite,Rect2(-34,-35,68,69),false,
            Color(0.66,0.63,0.60,0.79) if empty else Color.WHITE)

'''
    return function(s,"func _draw() -> void:\n","func serialize() -> Dictionary:",new,"event prop")
write("scripts/events/dynamic_event_site.gd",events)

def world(s):
    s=swap(s,'    var keys: Array[String] = ["barrel","tire","pallet","fence","sign","rubble"]',
       '''    var keys: Array[String] = ["barrel","tire","pallet","fence","sign","rubble"]''',"prop routing")
    old='''        var tex: Texture2D = V2651_CLUTTER._sprite(clampi(macro_biome_id,0,8),kind)'''
    new='''        var resolved: String = "scrap" if key == "rubble" else key
        var tex: Texture2D = load("res://assets/biomes/v2653/v2654_%s_%d.png" % [
            resolved,posmod(chunk_coord.x*19+chunk_coord.y*23+world_seed,2)])'''
    return swap(s,old,new,"new source props")
write("scripts/world/world_chunk.gd",world)

# World scale presentation: source art remains exactly the user-approved pixels.
# Do not rescale physics nodes, hit shapes, AI search radius, save positions.
def male(s):
    return swap(s,"const VISUAL_SCALE: float = 0.58",
        "const VISUAL_SCALE: float = 0.51","male 12% shrink")
write("assets/sp_melee/SurvivorWalkSprite.gd",male)
def player(s):
    s=swap(s,"    _baked_visual.setup_equipment(equipment, body_type)",
       '''    _baked_visual.setup_equipment(equipment, body_type)
    _baked_visual.scale = Vector2(0.97,0.97)''',"female presentation size")
    s=swap(s,"    add_child(_sp_firearm_visual)",
       '''    add_child(_sp_firearm_visual)
    _sp_firearm_visual.scale = Vector2(0.88,0.88)''',"scale male held firearm visuals")
    return s
write("scripts/player.gd",player)
def npc(s):
    return swap(s,'    _actor_visual.setup_static(body_type, "friendly", equipped_visual_gear)\n    _weapon_visual = WeaponVisualScript.new()',
       '''    _actor_visual.setup_static(body_type, "friendly", equipped_visual_gear)
    _actor_visual.scale = Vector2(1.035,1.035)
    _weapon_visual = WeaponVisualScript.new()''',"slightly normalize NPC proportions")
write("scripts/social/friendly_npc.gd",npc)
for path,old in before.items():
    assert (root/path).read_bytes()==old,"v2654 unexpectedly changed protected gameplay: "+path
print("SP_V2654_PRESENTATION_PATCH_PASS camp/object rasters, 36 attached berry clusters, 64 animal poses, humanoid world scale; physics/saves unchanged")
