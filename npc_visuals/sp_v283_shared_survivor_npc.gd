extends Node2D
## SP283: one visual adapter for human NPCs.
## Males use the exact approved player SurvivorWalkSprite. Females use the
## player's own BakedActorVisual. Only outfit color/palette and worn gear differ.
## No NPC AI, collision, combat, trade or population behavior lives here.
const SP_SURVIVOR = preload("res://assets/sp_melee/SurvivorWalkSprite.gd")
const SP_GUN = preload("res://assets/sp_melee/FirearmVisual.gd")
const PLAYER_FEMALE = preload("res://scripts/art/baked_actor_visual.gd")
const LEGACY_WEAPON = preload("res://scripts/art/weapon_visual.gd")

var sprite: Node2D = null
var firearm: Node2D = null
var melee: Node2D = null
var body_type: String = "male"
var actor_role: String = "friendly"
var current_weapon: String = ""
var _last_facing: Vector2 = Vector2(0, 0)
var _last_moving: bool = false
var _update_count: int = 0
var _idle_skips: int = 0

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
    current_weapon = weapon_id
    if sprite != null:
        sprite.queue_free()
    if firearm != null:
        firearm.queue_free()
    if melee != null:
        melee.queue_free()
    if body_type == "male":
        sprite = SP_SURVIVOR.new()
    else:
        sprite = PLAYER_FEMALE.new()
    sprite.name = "SharedPlayerCharacterAppearance"
    sprite.z_index = 0
    add_child(sprite)
    if body_type == "female":
        sprite.setup_static(body_type, "bandit" if role == "bandit" else "friendly", outfit)
        sprite.set_process(false)
    # Shared templates/resources; no duplicate bitmap per NPC.
    sprite.modulate = _palette_for_role(role, identity)
    firearm = SP_GUN.new()
    firearm.name = "SharedPlayerFirearmVisual"
    firearm.z_index = 4
    add_child(firearm)
    firearm.configure_equipped(current_weapon, ItemDatabase.get_category(current_weapon))
    melee = LEGACY_WEAPON.new()
    melee.z_index = 3
    add_child(melee)
    melee.setup_static(current_weapon, {"laser":"","light":"","optic":"","muzzle":""})
    _last_facing = Vector2.ZERO
    _last_moving = false
    set_state(Vector2.ZERO, Vector2.RIGHT, 0.05)

func set_state(motion: Vector2, aim: Vector2, delta: float) -> void:
    if sprite == null or not is_instance_valid(sprite):
        return
    var facing: Vector2 = aim.normalized() if aim.length_squared() > 0.001 else Vector2.RIGHT
    var changed: bool = _last_facing.length_squared() < 0.001 or _last_facing.distance_squared_to(facing) > 0.0025
    var moving: bool = motion.length_squared() > 64.0
    if body_type == "male":
        var recovery: bool = float(sprite.get("gait_weight")) > 0.01
        if moving or recovery or _last_moving or changed:
            sprite.advance(motion, maxf(delta, 0.0), facing.x >= 0.0)
            _update_count += 1
        else:
            _idle_skips += 1
    else:
        if moving or changed or _last_moving:
            sprite.set_motion_state(motion, false, false)
            if changed:
                sprite.set_facing(facing)
            _update_count += 1
        else:
            _idle_skips += 1
        sprite.set_process(moving)
    var gun_visible: bool = firearm != null and String(firearm.weapon_family) != ""
    if firearm != null:
        firearm.visible = gun_visible
        if changed:
            firearm.position = Vector2(4 if facing.x >= 0.0 else -4, -6)
            firearm.set_aim_vector(facing)
    if melee != null:
        melee.visible = not gun_visible and not current_weapon.is_empty()
        if changed:
            melee.set_facing(facing)
    _last_facing = facing
    _last_moving = moving
