extends Node2D
## v261: actual alpha silhouettes, world-accurate GPU tree ellipse clipping.
## Unlike v259/v260, no CPU source-pixel query and no per-tile visibility
## decisions. Actual upper/waist/leg/gun sprites and cached enemy renders
## are shaded only where genuinely beneath WorldChunk's canopy ellipses.
const MASK_SHADER = preload("res://occlusion/v261_mask.gdshader")
const LEG_SCRIPT = preload("res://occlusion/v261_leg_mask.gd")
const GUN_SCRIPT = preload("res://assets/sp_melee/FirearmVisual.gd")
const ZOMBIE_MASK: Texture2D = preload("res://assets/sp_melee/v261_zombie_mask.png")
const MAX_CANOPIES: int = 24
const MAX_NPC_MASKS: int = 12
const CAPTURE_PIXELS: int = 128
var world_manager: Node = null
var _actors: Array[Node2D] = []
var _states: Dictionary = {}
var _redraw_accumulator: float = 0.0
var _last_mask_queries: int = 0
var _last_mask_texture_tiles: int = 0
var _last_canvas_masks: int = 0
var _last_npc_capture_updates: int = 0

func setup(manager_value: Node) -> void:
    world_manager = manager_value
    z_index = 40
    set_process(true)

func _collect_actors() -> void:
    _actors.clear()
    var seen: Dictionary = {}
    for group_name in ["player_actor","hostile_actor","friendly_npc"]:
        for node in get_tree().get_nodes_in_group(group_name):
            if node is Node2D and is_instance_valid(node):
                var id: int = node.get_instance_id()
                if not seen.has(id):
                    seen[id] = true
                    _actors.append(node as Node2D)

func _new_material() -> ShaderMaterial:
    var mat := ShaderMaterial.new()
    mat.shader = MASK_SHADER
    mat.set_shader_parameter("canopy_count", 0)
    var blank := PackedVector2Array()
    blank.resize(MAX_CANOPIES)
    mat.set_shader_parameter("canopy_centers", blank)
    return mat

func _copy_sprite(source: Sprite2D, owner: Node2D, mat: ShaderMaterial) -> Sprite2D:
    var copy := Sprite2D.new()
    copy.name = "ActualSourceAlphaMask"
    copy.texture = source.texture
    copy.centered = source.centered
    copy.offset = source.offset
    copy.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    copy.material = mat
    owner.add_child(copy)
    copy.global_transform = source.global_transform
    return copy

func _player_state(actor: Node2D, state: Dictionary) -> bool:
    var rig: Node2D = actor._sp_sprite
    if rig == null or not rig.visible or rig.upper == null:
        return false
    var root_mask := Node2D.new()
    root_mask.name = "ApprovedPlayerExactSilhouette"
    add_child(root_mask)
    state["node"] = root_mask
    state["mode"] = "player"
    var mat: ShaderMaterial = state["material"]
    var copies: Array = []
    for source in [rig.fixed_waist,rig.upper,
                   rig.near_hip.get_child(0),rig.far_hip.get_child(0)]:
        copies.append(_copy_sprite(source,root_mask,mat))
    state["copies"] = copies
    var legs: Node2D = LEG_SCRIPT.new()
    legs.name = "B2BExactMovingLegMask"
    legs.material = mat
    root_mask.add_child(legs)
    state["legs"] = legs
    var gun: Node2D = GUN_SCRIPT.new()
    gun.name = "ActualPixelGunAndHandsMask"
    root_mask.add_child(gun)
    gun.material = mat
    for child in gun.get_children():
        if child is CanvasItem:
            child.use_parent_material = true
    gun.set_process(false)
    state["gun"] = gun
    return true

func _zombie_state(actor: Node2D, state: Dictionary) -> bool:
    var root_mask := Node2D.new()
    root_mask.name = "ExactZombieDrawSilhouette"
    add_child(root_mask)
    state["node"] = root_mask
    state["mode"] = "zombie"
    var sprite := Sprite2D.new()
    sprite.texture = ZOMBIE_MASK
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    sprite.material = state["material"]
    root_mask.add_child(sprite)
    state["sprite"] = sprite
    return true

func _safe_node_property(actor: Node2D, key: String) -> Variant:
    for property in actor.get_property_list():
        if String(property.get("name","")) == key:
            return actor.get(key)
    return null

func _capture_state(actor: Node2D, state: Dictionary) -> bool:
    var visual: Node2D = _safe_node_property(actor,"_actor_visual") as Node2D
    var baked: Node2D = _safe_node_property(actor,"_baked_visual") as Node2D
    var source: Node2D = visual if visual != null and visual.visible else baked
    if source == null or not source.visible or source.get_script() == null:
        return false
    var viewport := SubViewport.new()
    viewport.name = "CachedTrueNPCVisualRGBA"
    viewport.size = Vector2i(CAPTURE_PIXELS,CAPTURE_PIXELS)
    viewport.transparent_bg = true
    viewport.disable_3d = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
    viewport.render_target_clear_mode = SubViewport.CLEAR_MODE_ALWAYS
    add_child(viewport)
    var canvas := Node2D.new()
    canvas.position = Vector2(CAPTURE_PIXELS*0.5,CAPTURE_PIXELS*0.5)
    viewport.add_child(canvas)
    var duplicate: Node2D = source.get_script().new()
    if source == baked and duplicate.has_method("setup_equipment"):
        duplicate.setup_equipment(actor.equipment,actor.body_type)
    elif duplicate.has_method("setup_static"):
        duplicate.setup_static(actor.body_type,source.role,actor.equipped_visual_gear)
    else:
        viewport.queue_free()
        return false
    duplicate.position = source.position
    duplicate.scale = source.scale
    canvas.add_child(duplicate)
    state["preview_actor"] = duplicate
    var weapon_source: Node2D = actor.get("_weapon_visual") as Node2D
    if weapon_source != null and weapon_source.visible:
        var weapon: Node2D = weapon_source.get_script().new()
        weapon.position = weapon_source.position
        weapon.scale = weapon_source.scale
        canvas.add_child(weapon)
        weapon.setup_static(actor.equipped_weapon_id,actor.weapon_attachments)
        state["preview_weapon"] = weapon
    var root_mask := Node2D.new()
    root_mask.name = "AccurateCachedLayeredActor"
    add_child(root_mask)
    var sprite := Sprite2D.new()
    sprite.name = "ActualRenderedLayeredNPCAlpha"
    sprite.texture = viewport.get_texture()
    sprite.material = state["material"]
    root_mask.add_child(sprite)
    state["node"] = root_mask
    state["viewport"] = viewport
    state["sprite"] = sprite
    state["mode"] = "capture"
    state["capture_time"] = -1.0
    return true

func _new_actor_state(actor: Node2D) -> Dictionary:
    var state: Dictionary = {"material":_new_material(),"actor":actor}
    var ok: bool = false
    if actor.is_in_group("player_actor"):
        if actor.get("body_type") == "male":
            ok = _player_state(actor,state)
        else:
            ok = _capture_state(actor,state)
    elif actor.get_script() != null and String(actor.get_script().resource_path).ends_with("/zombie.gd"):
        ok = _zombie_state(actor,state)
    elif _safe_node_property(actor,"_actor_visual") != null or _safe_node_property(actor,"_baked_visual") != null:
        ok = _capture_state(actor,state)
    if not ok:
        # No rectangle, circles, or invented fallback for unknown actors.
        return {}
    return state

func _dispose(state: Dictionary) -> void:
    if state.has("node") and is_instance_valid(state["node"]):
        state["node"].queue_free()
    if state.has("viewport") and is_instance_valid(state["viewport"]):
        state["viewport"].queue_free()

func _nearby_centers(actor: Node2D) -> PackedVector2Array:
    var out := PackedVector2Array()
    var chunks: Variant = world_manager.get("_loaded_chunks")
    if not chunks is Dictionary:
        return out
    var origin: Vector2 = actor.global_position
    # Static and interactive trees use the SAME ellipse centers/radii as
    # WorldChunk.is_world_point_under_tree_canopy. One lookup per actor,
    # updated ~8Hz. No per-pixel or per-tile world manager RPC.
    for chunk in chunks.values():
        if not is_instance_valid(chunk):
            continue
        var center: Vector2 = chunk.global_position
        var positions: Variant = chunk.get("_tree_positions")
        if positions is Array:
            for p in positions:
                if p is Vector2:
                    var canopy: Vector2 = center + p + Vector2(0,-49)
                    if absf(canopy.x-origin.x) < 105.0 and absf(canopy.y-origin.y) < 114.0:
                        out.append(canopy)
                        if out.size() >= MAX_CANOPIES:
                            return out
        for child in chunk.get_children():
            if child is NaturalResource and child.resource_type == "tree":
                if child.has_method("has_active_tree_canopy") and child.has_active_tree_canopy():
                    var canopy: Vector2 = child.global_position + Vector2(0,-49)
                    if absf(canopy.x-origin.x) < 105.0 and absf(canopy.y-origin.y) < 114.0:
                        out.append(canopy)
                        if out.size() >= MAX_CANOPIES:
                            return out
    return out

func _sync_capture(actor: Node2D,state: Dictionary) -> void:
    var preview: Node2D = state.get("preview_actor") as Node2D
    var viewport: SubViewport = state.get("viewport") as SubViewport
    if preview == null or viewport == null:
        return
    var facing_value: Variant = actor.get("_visual_facing")
    if actor.is_in_group("player_actor"):
        facing_value = actor._facing
    var aim: Vector2 = facing_value if facing_value is Vector2 else Vector2.RIGHT
    if preview.has_method("set_facing"):
        preview.set_facing(aim)
    if preview.has_method("set_motion_state"):
        var current_velocity: Vector2 = actor.velocity if actor is CharacterBody2D else Vector2.ZERO
        preview.set_motion_state(current_velocity,current_velocity.length()>120,false)
    if state.has("preview_weapon"):
        var weapon: Node2D = state["preview_weapon"]
        if is_instance_valid(weapon) and weapon.has_method("set_facing"):
            weapon.set_facing(aim)
    viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
    _last_npc_capture_updates += 1

func _sync_actor(actor: Node2D,state: Dictionary) -> void:
    var root_mask: Node2D = state["node"]
    if state["mode"] == "player":
        var rig: Node2D = actor._sp_sprite
        if rig == null or not rig.visible:
            root_mask.visible = false
            return
        var originals: Array = [rig.fixed_waist,rig.upper,
                               rig.near_hip.get_child(0),rig.far_hip.get_child(0)]
        var copies: Array = state["copies"]
        for i in range(copies.size()):
            var original: Sprite2D = originals[i]
            var clone: Sprite2D = copies[i]
            clone.texture = original.texture
            clone.visible = original.is_visible_in_tree()
            clone.global_transform = original.global_transform
        var legs: Node2D = state["legs"]
        legs.synchronize(rig)
        var gun: Node2D = state["gun"]
        var gun_original: Node2D = actor._sp_firearm_visual
        gun.visible = gun_original != null and gun_original.visible
        if gun.visible:
            var id: String = actor.equipment.equipped_weapon_id
            var category: String = actor.equipment.get_weapon_category()
            gun.configure_equipped(id,category)
            gun.global_transform = gun_original.global_transform
        root_mask.visible = true
    else:
        root_mask.global_position = actor.global_position
        root_mask.visible = true

func _refresh() -> void:
    if world_manager == null or not is_instance_valid(world_manager):
        return
    _collect_actors()
    var active: Dictionary = {}
    var npc_masks: int = 0
    for actor in _actors:
        if not is_instance_valid(actor) or not actor.visible:
            continue
        var id: int = actor.get_instance_id()
        var centers: PackedVector2Array = _nearby_centers(actor)
        if centers.is_empty():
            if _states.has(id):
                _states[id]["node"].visible = false
            continue
        if not actor.is_in_group("player_actor"):
            npc_masks += 1
            if npc_masks > MAX_NPC_MASKS:
                continue
        if not _states.has(id):
            var state: Dictionary = _new_actor_state(actor)
            if state.is_empty():
                continue
            _states[id] = state
        var existing: Dictionary = _states[id]
        active[id] = true
        var buffer := PackedVector2Array()
        buffer.resize(MAX_CANOPIES)
        for i in range(centers.size()):
            buffer[i] = centers[i]
        var material: ShaderMaterial = existing["material"]
        material.set_shader_parameter("canopy_centers",buffer)
        material.set_shader_parameter("canopy_count",centers.size())
        existing["node"].visible = true
        if existing["mode"] == "capture":
            _sync_capture(actor,existing)
        _last_canvas_masks += 1
    for id in _states.keys():
        if not active.has(id):
            var state: Dictionary = _states[id]
            if not is_instance_valid(state["actor"]):
                _dispose(state)
                _states.erase(id)
            else:
                state["node"].visible = false
    _last_mask_queries = 0
    _last_mask_texture_tiles = 0

func _process(delta: float) -> void:
    _redraw_accumulator += delta
    if _redraw_accumulator >= 0.12:
        _redraw_accumulator = 0.0
        _last_canvas_masks = 0
        _last_npc_capture_updates = 0
        _refresh()
    for state in _states.values():
        var actor: Node2D = state["actor"]
        if is_instance_valid(actor) and state["node"].visible:
            _sync_actor(actor,state)

func _draw_partial_silhouette(actor: Node2D) -> void:
    # Compatibility with older QA: no CPU geometry draw path remains.
    if actor == null:
        return

func _draw() -> void:
    pass
