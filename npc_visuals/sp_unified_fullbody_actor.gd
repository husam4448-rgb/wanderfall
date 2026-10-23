extends Node2D
## EXPERIMENTAL full-body animation renderer — exactly one Sprite2D per actor.
## IMPORTANT: Source frames are 64x96 WHOLE characters, not layered torsos and legs.
## Uses original SurvivorWalkSprite.advance(velocity,delta,facing) API.
const PIXEL_SCALE: float = 0.58
const ROOT: String = "res://assets/sp_unified_character/"
var upper: Sprite2D = null
var gait_weight: float = 0.0
var gait_phase: float = 0.0
var breathing_phase: float = 0.0
var face_right: bool = true
var move_velocity: Vector2 = Vector2.ZERO
var skin_id: String = "player"
var _clip: String = "idle"
var _frame: int = -1
var _frame_cache: Dictionary = {}

func _ready() -> void:
    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    upper = Sprite2D.new()
    upper.name = "ONE_COMPLETE_CHARACTER_NO_SECOND_SKELETON"
    upper.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    add_child(upper)
    scale = Vector2(PIXEL_SCALE, PIXEL_SCALE)
    position.y = -8.0
    _display("idle", 0)

func set_skin(id: String) -> void:
    assert(id == "player" or id == "bandit01", "Missing full-body frames: " + id)
    skin_id = id
    _frame_cache.clear()
    _frame = -1
    _display("idle", 0)

func _display(clip: String, frame: int) -> void:
    if upper == null: return
    if _clip == clip and _frame == frame and upper.texture != null: return
    var file: String = ROOT + skin_id + "/" + clip + ("/%02d.png" % frame)
    var texture: Texture2D = load(file) as Texture2D
    assert(texture != null, "Complete sprite frame not found: " + file)
    assert(texture.get_width() == 64 and texture.get_height() == 96)
    upper.texture = texture
    _clip = clip
    _frame = frame

func advance(velocity_world: Vector2, delta: float, facing_right: bool) -> void:
    if upper == null: return
    move_velocity = velocity_world
    face_right = facing_right
    scale.x = PIXEL_SCALE if facing_right else -PIXEL_SCALE
    scale.y = PIXEL_SCALE
    var dt: float = clampf(delta, 0.0, 0.09)
    var speed: float = velocity_world.length()
    var moving: bool = speed > 8.0
    gait_weight = move_toward(gait_weight, 1.0 if moving else 0.0, dt * 8.0)
    if moving:
        # Identical motion speed for player and NPC using this renderer.
        var running: bool = speed >= 210.0
        gait_phase = fposmod(gait_phase + dt * (10.2 if running else 6.5), TAU)
        _display("run" if running else "walk", int(floor(gait_phase/TAU*16.0)) % 16)
    else:
        breathing_phase = fposmod(breathing_phase + dt * TAU * 0.84, TAU)
        _display("idle", int(floor(breathing_phase/TAU*8.0)) % 8)
    # There is NO _draw(), no overlaid static torso, no second leg skeleton,
    # no near_hip/far_hip Sprite2Ds, and no duplicated constant body layer.
