extends Node2D
## SP283: one visual adapter for human NPCs.
## Both sexes use an anatomy-preserving survivor skeleton plus authentic role-specific
## outfit pixels. Scale/weapon anchors are independent of the human gait.
## No NPC AI, collision, combat, trade or population behavior lives here.
const SP_SURVIVOR = preload("res://assets/sp_melee/SurvivorWalkSprite.gd")
const SP_GUN = preload("res://assets/sp_melee/FirearmVisual.gd")
## All NPCs now use the same original textured pixel art survivor.
const LEGACY_WEAPON = preload("res://scripts/art/weapon_visual.gd")

var sprite: Node2D = null
var firearm: Node2D = null
var melee: Node2D = null
var weapon_holder: Node2D = null
var body_type: String = "male"
var actor_role: String = "friendly"
var current_weapon: String = ""
var _last_facing: Vector2 = Vector2(0, 0)
var _last_moving: bool = false
var _update_count: int = 0
var _idle_skips: int = 0
var appearance_role: String = "civilian"
var _variant_texture_path: String = ""
var _stable_face_right: bool = true
var _candidate_right: bool = true
var _candidate_duration: float = 0.0
var _flip_cooldown: float = 0.0
var _flip_count: int = 0

func _role_key(raw_role: String) -> String:
    match raw_role.to_lower():
        "bandit", "raider", "outlaw":
            return "bandit"
        "guard", "mercenary", "soldier", "roadwarden", "roadwardens":
            return "guard"
        "medic", "doctor", "nurse":
            return "medic"
        "scientist", "researcher", "chemist":
            return "scientist"
        "mechanic", "builder", "engineer":
            return "mechanic"
        "trader", "merchant", "vendor":
            return "trader"
        "scavenger", "hunter":
            return "scavenger"
        _:
            return "civilian"

func _stabilize_side(aim: Vector2, motion: Vector2, delta: float) -> bool:
    # The old "aim.x >= 0" became right/left/right/left whenever an
    # NPC scanned nearly vertical or small navigation corrections occurred.
    # Keep a committed side until an opposite direction is sustained.
    var dt: float = clampf(delta, 0.0, 0.08)
    _flip_cooldown = maxf(0.0, _flip_cooldown - dt)
    var intentional: bool = false
    var right_candidate: bool = _stable_face_right
    if absf(aim.x) >= 0.52:
        intentional = true
        right_candidate = aim.x > 0.0
    elif motion.length_squared() > 900.0 and absf(motion.normalized().x) >= 0.70:
        intentional = true
        right_candidate = motion.x > 0.0
    if not intentional or right_candidate == _stable_face_right:
        _candidate_duration = 0.0
        _candidate_right = _stable_face_right
    elif right_candidate != _candidate_right:
        _candidate_right = right_candidate
        _candidate_duration = dt
    else:
        _candidate_duration += dt
        if _candidate_duration >= 0.22 and _flip_cooldown <= 0.0:
            _stable_face_right = right_candidate
            _flip_count += 1
            _flip_cooldown = 0.38
            _candidate_duration = 0.0
    return _stable_face_right

func _palette_for_role(role: String, name_seed: String) -> Color:
    var palettes: Array[Color] = []
    match role:
        "bandit":
            palettes = [Color("d4afb0"), Color("c9a3a3"), Color("af9297")]
        "roadwardens":
            palettes = [Color("b9c6ae"), Color("b5beaa"), Color("9fb5a0")]
        "independent":
            palettes = [Color("c8c5b0"), Color("b3c5ad"), Color("c7b8a2")]
        _:
            palettes = [Color("bfcab6"), Color("c4bdad"), Color("b5bbb1")]
    return palettes[posmod(name_seed.hash(), palettes.size())]

func setup_npc(gender: String, role: String, identity: String, outfit: Dictionary, weapon_id: String) -> void:
    body_type = "female" if gender == "female" else "male"
    actor_role = role
    appearance_role = _role_key(role)
    current_weapon = weapon_id
    if sprite != null:
        sprite.queue_free()
    if firearm != null:
        firearm.queue_free()
    if melee != null:
        melee.queue_free()
    sprite = SP_SURVIVOR.new()
    sprite.name = "SharedPlayerCharacterAppearance"
    sprite.z_index = 0
    add_child(sprite)
    # v286 artwork starts from the APPROVED anatomy mask, then adds
    # shaded role clothing/headwear within it. No face cutoff, black
    # transparent rectangular patches or floating equipment squares.
    var variant: int = posmod(identity.hash(), 3)
    _variant_texture_path = "res://assets/sp_npc286/sp286_%s_%s_%d.png" % [appearance_role, body_type, variant]
    var variant_texture: Texture2D = load(_variant_texture_path) as Texture2D
    assert(variant_texture != null, "SP285 authored NPC texture missing: " + _variant_texture_path)
    var upper_node: Sprite2D = sprite.get("upper") as Sprite2D
    if upper_node != null and variant_texture != null:
        upper_node.texture = variant_texture
    # Artwork already contains a distinctive coat, armor, head and satchels.
    # Mild modulate preserves natural facial color and authored outfit hues.
    sprite.modulate = Color(0.985, 0.985, 0.98)
    # Separate parent transform preserves correct character-to-weapon scale
    # when FirearmVisual.set_aim_vector changes its own local .73 scale.
    # v285 gave NPC guns a much larger on-screen size than their bodies.
    weapon_holder = Node2D.new()
    weapon_holder.name = "NPCWeaponAnatomicalAnchor"
    weapon_holder.scale = Vector2(0.66, 0.66)
    weapon_holder.position = Vector2(5, -6)
    weapon_holder.z_index = 4
    add_child(weapon_holder)
    firearm = SP_GUN.new()
    firearm.name = "SharedPlayerFirearmVisual"
    firearm.z_index = 0
    weapon_holder.add_child(firearm)
    firearm.call("configure_equipped",current_weapon, ItemDatabase.get_category(current_weapon))
    melee = LEGACY_WEAPON.new()
    melee.z_index = 1
    weapon_holder.add_child(melee)
    melee.call("setup_static",current_weapon, {"laser":"","light":"","optic":"","muzzle":""})
    _last_facing = Vector2.ZERO
    _last_moving = false
    _stable_face_right = true
    _candidate_right = true
    _candidate_duration = 0.0
    _flip_cooldown = 0.0
    _flip_count = 0
    set_state(Vector2.ZERO, Vector2.RIGHT, 0.05)

func set_state(motion: Vector2, aim: Vector2, delta: float) -> void:
    if sprite == null or not is_instance_valid(sprite):
        return
    var facing: Vector2 = aim.normalized() if aim.length_squared() > 0.001 else (_last_facing if _last_facing.length_squared() > 0.01 else Vector2.RIGHT)
    var face_right: bool = _stabilize_side(facing, motion, delta)
    # Until the requested side has been stable for 220ms, keep the gun and
    # sprite on the SAME displayed side. This is visual only; shooting/AI
    # decisions retain their original untouched gameplay-facing vectors.
    var display_facing: Vector2 = facing
    if (display_facing.x > 0.0) != face_right and absf(display_facing.x) > 0.005:
        display_facing.x = 0.05 if face_right else -0.05
        display_facing = display_facing.normalized()
    var changed: bool = _last_facing.length_squared() < 0.001 or _last_facing.distance_squared_to(display_facing) > 0.015
    var moving: bool = motion.length_squared() > 64.0
    var recovery: bool = float(sprite.get("gait_weight")) > 0.01
    if moving or recovery or _last_moving or changed:
        sprite.call("advance", motion, maxf(delta, 0.0), face_right)
        # v284 multiplied female width by 0.93 EVERY ANIMATION TICK,
        # causing progressive shrink. Use an absolute, signed width.
        if body_type == "female":
            sprite.scale.x = (0.58 if face_right else -0.58) * 0.93
            sprite.scale.y = 0.58
        _update_count += 1
    else:
        _idle_skips += 1
    var gun_visible: bool = firearm != null and String(firearm.get("weapon_family")) != ""
    if firearm != null:
        firearm.visible = gun_visible
        if changed:
            firearm.position = Vector2.ZERO
            if weapon_holder != null:
                weapon_holder.position = Vector2(5 if face_right else -5, -6)
            firearm.call("set_aim_vector",display_facing)
    if melee != null:
        melee.visible = not gun_visible and not current_weapon.is_empty()
        if changed:
            melee.call("set_facing",display_facing)
    _last_facing = display_facing
    _last_moving = moving
