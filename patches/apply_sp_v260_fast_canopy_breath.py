#!/usr/bin/env python3
"""SP v260: expensive canopy per-pixel CPU checks -> bounded texture tiles.
Breathe via upper torso/head movement over an overlapping, STATIC waist.
Applied only inside temporary reconstructed game after v259 patches.
No change to original historical terrain/HUD/world assets or gameplay collision.
"""
from pathlib import Path
import sys
from PIL import Image
root = Path(sys.argv[1]).resolve()
protected = ("scripts/mobile_hud.gd","scripts/virtual_joystick.gd",
             "scripts/world/world_chunk.gd","scripts/world/world_manager.gd")
before = {f:(root/f).read_bytes() for f in protected}

def replace_once(path, old, new, label):
    p=root/path
    s=p.read_text(encoding="utf-8")
    n=s.count(old)
    if n != 1:
        raise SystemExit(f"SP_V260_ANCHOR_ERROR {label}: {n} matches")
    p.write_text(s.replace(old,new,1),encoding="utf-8")

# Preserve exact source artwork by splitting ONLY its duplicate display layers.
assets=root/"assets/sp_melee"
src=Image.open(assets/"approved_upper.png").convert("RGBA")
assert src.size == (64,96), f"SP v260 approved sprite unexpected size {src.size}"
top=src.copy()
waist=src.copy()
# 9-source-pixel overlap makes the two layers impossible to separate visually
# with <=1.25-pixel breathing translation; no scaling/stretching whatsoever.
for y in range(96):
    for x in range(64):
        if y >= 78: top.putpixel((x,y),(0,0,0,0))
        if y < 69: waist.putpixel((x,y),(0,0,0,0))
top.save(assets/"approved_breath_upper.png")
waist.save(assets/"approved_static_pelvis.png")
assert src.getpixel((32,70)) == top.getpixel((32,70)) == waist.getpixel((32,70))

rig="assets/sp_melee/SurvivorWalkSprite.gd"
replace_once(rig, "var upper: Sprite2D\n", "var upper: Sprite2D\nvar fixed_waist: Sprite2D\n", "static waist member")
replace_once(rig, "var _upper_alpha: Image\n", "var _upper_alpha: Image\nvar _waist_alpha: Image\n", "static waist alpha member")
replace_once(rig,
'''    upper.texture = load("res://assets/sp_melee/approved_upper.png")
    upper.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    upper.z_index = 2
    add_child(upper)''',
'''    # Waist stays fixed above moving legs, beneath breathing upper torso.
    fixed_waist = Sprite2D.new()
    fixed_waist.name = "FixedApprovedPelvisNoGaps"
    fixed_waist.texture = load("res://assets/sp_melee/approved_static_pelvis.png")
    fixed_waist.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    fixed_waist.z_index = 1
    add_child(fixed_waist)
    upper.texture = load("res://assets/sp_melee/approved_breath_upper.png")
    upper.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    upper.z_index = 2
    add_child(upper)''',"insert connected pelvis")
replace_once(rig, "    _upper_alpha = upper.texture.get_image()\n",
             "    _upper_alpha = upper.texture.get_image()\n    _waist_alpha = fixed_waist.texture.get_image()\n",
             "cache waist alpha")
replace_once(rig,
'''    upper.scale.y = 1.0 + (0.003 * sin(breathing_phase) if not moving else 0.0)
    position.y = -8.0 - (0.18 * absf(sin(gait_phase)) * gait_weight)''',
'''    # Only HEAD/CHEST/BACKPACK translate up/down; pelvis and feet stay intact.
    # Two pixel layers overlap for 9 original pixels at the waist; amplitude
    # <=1.25 source pixels, so no transparent seam can ever become visible.
    upper.scale = Vector2.ONE
    upper.position.y = (-1.25 * (0.5 + 0.5*sin(breathing_phase))) if not moving else 0.0
    fixed_waist.position = Vector2.ZERO
    position.y = -8.0 - (0.18 * absf(sin(gait_phase)) * gait_weight)''',
             "torso-only breathing translation")
replace_once(rig,
'''    if _inside_image(upper, _upper_alpha, world_point):
        return true
    if gait_weight > 0.08:''',
'''    if _inside_image(upper, _upper_alpha, world_point):
        return true
    if _inside_image(fixed_waist, _waist_alpha, world_point):
        return true
    if gait_weight > 0.08:''',
             "silhouette covers fixed waist")

# Rebuild only the separate silhouette overlay (never chunk/terrain tree draws).
# Expensive v259: ~2500 image/RPC calls per actor at 15Hz.
# v260: a few dozen cached texture tiles + 2 world probes per tile maximum.
overlay = r'''extends Node2D
## v260: draw true approved alpha-mask on the GPU. Never call per-pixel
## texture.get_pixel(), _inside_b2b_leg or actor.call() inside a dense grid.
## Single center world-canopy query per 12x12 source tile, only when near trees.
const TILE: int = 12
const COLOR: Color = Color(1.0, 0.62, 0.30, 0.70)
const LEG_COLOR: Color = Color(1.0, 0.51, 0.11, 0.66)
var world_manager: Node = null
var _actors: Array[Node2D] = []
var _redraw_accumulator: float = 0.0
var _tile_cache: Dictionary = {}
var _last_mask_queries: int = 0
var _last_mask_texture_tiles: int = 0

func setup(manager_value: Node) -> void:
    world_manager = manager_value
    z_index = 40
    set_process(true)
    queue_redraw()

func _process(delta: float) -> void:
    _redraw_accumulator += delta
    if _redraw_accumulator >= 0.066:
        _redraw_accumulator = 0.0
        queue_redraw()

func _collect_actors() -> void:
    _actors.clear()
    for group_name in ["player_actor", "friendly_npc", "hostile_actor"]:
        for node in get_tree().get_nodes_in_group(group_name):
            if node is Node2D and is_instance_valid(node) and not _actors.has(node):
                _actors.append(node as Node2D)

func _hidden(world_pos: Vector2) -> bool:
    _last_mask_queries += 1
    return bool(world_manager.call("is_world_point_tree_occluded",world_pos))

func _actor_may_be_occluded(actor: Node2D) -> bool:
    # Quick gate: do not enter texture loop away from tree canopies.
    for p in [Vector2(-10,-20),Vector2(9,-18),Vector2(0,-8),
              Vector2(-10,0),Vector2(10,0),Vector2(0,13)]:
        if _hidden(actor.global_position+p):
            return true
    return false

func _tiles_for(sprite: Sprite2D) -> Array:
    if sprite == null or sprite.texture == null:
        return []
    var texture_id: int = sprite.texture.get_instance_id()
    if _tile_cache.has(texture_id):
        return _tile_cache[texture_id]
    var img: Image = sprite.texture.get_image()
    var tiles: Array = []
    # Build once on load: GPU-alpha controls the final exact shape.
    # CPU alpha scan at startup excludes fully transparent 12x12 tiles.
    for y in range(0,img.get_height(),TILE):
        for x in range(0,img.get_width(),TILE):
            var w: int = mini(TILE,img.get_width()-x)
            var h: int = mini(TILE,img.get_height()-y)
            var opaque: bool = false
            for iy in range(y,y+h):
                if opaque:
                    break
                for ix in range(x,x+w):
                    if img.get_pixel(ix,iy).a > 0.03:
                        opaque = true
                        break
            if opaque:
                tiles.append(Rect2(x,y,w,h))
    _tile_cache[texture_id] = tiles
    return tiles

func _draw_sprite_mask(sprite: Sprite2D) -> void:
    if sprite == null or not sprite.visible or sprite.texture == null:
        return
    var rel: Transform2D = global_transform.affine_inverse() * sprite.global_transform
    var texture: Texture2D = sprite.texture
    var half: Vector2 = texture.get_size()*0.5
    draw_set_transform_matrix(rel)
    for tile in _tiles_for(sprite):
        var center: Vector2 = Vector2(tile.position+tile.size*0.5)-half
        if not _hidden(sprite.to_global(center)):
            continue
        _last_mask_texture_tiles += 1
        # The actual sprite RGBA alpha is sampled by Godot's renderer,
        # giving the original head, torso, pelvis and backpack outline.
        draw_texture_rect_region(texture, Rect2(tile.position-half,tile.size),
                                 tile, COLOR, false, true)
    draw_set_transform_matrix(Transform2D.IDENTITY)

func _draw_bone(hip: Vector2,knee: Vector2,ankle: Vector2) -> void:
    # Only a handful of segment probes instead of polygon/per-pixel scanning.
    for bone in [Rect2(hip+Vector2(-5,0),Vector2(11,9)),
                 Rect2(knee+Vector2(-5,0),Vector2(11,7)),
                 Rect2(ankle+Vector2(-5,-1),Vector2(11,6))]:
        var mid: Vector2 = bone.position+bone.size*0.5
        if _hidden(_rig.to_global(mid)):
            draw_rect(bone,LEG_COLOR,true)

var _rig: Node2D

func _draw_approved_actor(actor: Node2D) -> void:
    _rig = actor._sp_sprite
    if _rig == null or not _rig.visible:
        return
    # Original actor no-longer-painted anatomy silhouette is never consulted.
    _draw_sprite_mask(_rig.fixed_waist)
    _draw_sprite_mask(_rig.upper)
    if _rig.gait_weight <= 0.08:
        _draw_sprite_mask(_rig.near_hip.get_child(0))
        _draw_sprite_mask(_rig.far_hip.get_child(0))
    else:
        draw_set_transform_matrix(global_transform.affine_inverse()*_rig.global_transform)
        _draw_bone(_rig.FAR_HIP,_rig.far_knee,_rig.far_ankle)
        _draw_bone(_rig.NEAR_HIP,_rig.near_knee,_rig.near_ankle)
        draw_set_transform_matrix(Transform2D.IDENTITY)
    # Weapon is a separately rotating object. Draw limited true-component
    # rectangle shapes; skip expensive GDScript pixel-scanning entirely.
    var gun: Node2D = actor._sp_firearm_visual
    if gun != null and gun.visible and gun.weapon_family != "":
        var parts: Array[Rect2] = []
        match gun.weapon_family:
            "pistol":
                parts = [Rect2(1,-5,25,9),Rect2(6,2,9,15),Rect2(15,2,7,2)]
            "rifle":
                parts = [Rect2(-21,-4,20,9),Rect2(-4,-7,27,12),
                         Rect2(21,-5,25,6),Rect2(5,5,8,16)]
            "smg":
                parts = [Rect2(-11,-4,10,6),Rect2(-2,-7,29,12),
                         Rect2(26,-4,12,5),Rect2(6,5,7,14)]
            "shotgun":
                parts = [Rect2(-19,-5,19,11),Rect2(-1,-6,21,11),
                         Rect2(19,-5,28,5),Rect2(3,5,9,13)]
        draw_set_transform_matrix(global_transform.affine_inverse()*gun.global_transform)
        for rect in parts:
            if _hidden(gun.to_global(rect.position+rect.size*0.5)):
                draw_rect(rect,LEG_COLOR,true)
        draw_set_transform_matrix(Transform2D.IDENTITY)

func _inside_actor_silhouette(p: Vector2) -> bool:
    # Legacy NPC fallback, not used for approved male player.
    if (p-Vector2(0,-18)).length_squared() <= 45.0:
        return true
    if p.y >= -12.5 and p.y <= 11 and absf(p.x) < 10:
        return true
    return p.y > 10 and p.y <= 27 and absf(absf(p.x)-4.3)<3

func _draw_partial_silhouette(actor: Node2D) -> void:
    if not _actor_may_be_occluded(actor):
        return
    if actor.is_in_group("player_actor") and actor.has_method("_sp_occlusion_shape_contains") and actor.get("body_type") == "male":
        _draw_approved_actor(actor)
        return
    # Preserve a cheap generic treatment for NPCs only.
    var origin: Vector2 = to_local(actor.global_position)
    for y in range(-25,28,8):
        for x in range(-14,15,8):
            var offset: Vector2 = Vector2(x,y)
            if _inside_actor_silhouette(offset) and _hidden(actor.global_position+offset):
                draw_rect(Rect2(origin+offset-Vector2(3,3),Vector2(6,6)),
                          LEG_COLOR,true)

func _draw() -> void:
    _last_mask_queries = 0
    _last_mask_texture_tiles = 0
    if world_manager == null or not is_instance_valid(world_manager):
        return
    _collect_actors()
    for actor in _actors:
        if actor != null and is_instance_valid(actor):
            _draw_partial_silhouette(actor)
'''
(root/"scripts/world/occlusion_silhouette_overlay.gd").write_text(overlay,encoding="utf-8")
for path,previous in before.items():
    if (root/path).read_bytes()!=previous:
        raise SystemExit("SP_V260_UNEXPECTED_WORLD_HUD_MUTATION "+path)
print("SP_V260_FOLIAGE_OPT_PASS GPU sprite alpha tiles, cached textures, bounded queries, no per-pixel RPC")
print("SP_V260_BREATH_CONNECTED_PASS upper-only 1.25px breath, 9px fixed-waist overlap, never torso-leg separation")
