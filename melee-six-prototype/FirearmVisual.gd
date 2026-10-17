extends Node2D
const HandVisual = preload("res://HandVisual.gd")
const COMPACT_SCALE: float = 0.73
var grip_hand: Node2D
var support_hand: Node2D
## SP v254: firearm art for the two-sided approved character.
## This REPLACES the old Line2D grey pole. All weapons face local +X.
## Actual equipment, ammunition, aiming and shooting stay in player.gd.
const OUTLINE: Color = Color("#151719")
const RECEIVER: Color = Color("#3b4347")
const STEEL: Color = Color("#687479")
const HIGHLIGHT: Color = Color("#879094")
const GRIP: Color = Color("#43352c")
const WOOD: Color = Color("#73523c")
const DARK: Color = Color("#202428")
var current_weapon_id: String = ""
var weapon_family: String = ""
var current_aim: Vector2 = Vector2.RIGHT
var muzzle_flash_time: float = 0.0

func _ready() -> void:
    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    z_index = 4
    set_process(true)
    visible = false
    grip_hand = HandVisual.new()
    grip_hand.name = "GrippingHandChildOfGun"
    add_child(grip_hand)
    support_hand = HandVisual.new()
    support_hand.name = "SupportHandChildOfGun"
    add_child(support_hand)
    _place_hands()

func configure_equipped(item_id: String, category: String) -> void:
    current_weapon_id = item_id
    var id: String = item_id.to_lower()
    var cat: String = category.to_lower()
    if cat != "firearm" or id.is_empty():
        weapon_family = ""
    elif id.contains("shotgun"):
        weapon_family = "shotgun"
    elif id.contains("smg") or id.contains("submachine"):
        weapon_family = "smg"
    elif id.contains("rifle") or id.contains("ak") or id.contains("carbine"):
        weapon_family = "rifle"
    elif id.contains("pistol") or id.contains("revolver") or id.contains("9mm") or id.contains("9_mm"):
        weapon_family = "pistol"
    else:
        # Fallback to a recognizable compact pistol, NEVER to a line/pole.
        weapon_family = "pistol"
    _place_hands()
    queue_redraw()

func set_aim_vector(direction: Vector2) -> void:
    if direction.length_squared() <= 0.001:
        return
    current_aim = direction.normalized()
    rotation = current_aim.angle()
    # Prevent guns rotating upside-down when mirrored to face left.
    scale = Vector2(COMPACT_SCALE, -COMPACT_SCALE if current_aim.x < 0.0 else COMPACT_SCALE)

func _place_hands() -> void:
    if grip_hand == null or support_hand == null:
        return
    # Same circular hands follow the weapon's rotation/position/visibility.
    match weapon_family:
        "pistol":
            grip_hand.position = Vector2(10, 8)
            support_hand.position = Vector2(18, 4)
            support_hand.visible = true
        "rifle":
            grip_hand.position = Vector2(8, 9)
            support_hand.position = Vector2(24, 8)
            support_hand.visible = true
        "smg":
            grip_hand.position = Vector2(10, 9)
            support_hand.position = Vector2(23, 8)
            support_hand.visible = true
        "shotgun":
            grip_hand.position = Vector2(7, 8)
            support_hand.position = Vector2(27, 7)
            support_hand.visible = true
        _:
            grip_hand.visible = false
            support_hand.visible = false
            return
    grip_hand.visible = true

func fired() -> void:
    if weapon_family.is_empty():
        return
    muzzle_flash_time = 0.055
    queue_redraw()

func _process(delta: float) -> void:
    if muzzle_flash_time > 0.0:
        muzzle_flash_time = maxf(0.0, muzzle_flash_time - delta)
        queue_redraw()

func _rect(x: float, y: float, width: float, height: float, color: Color) -> void:
    draw_rect(Rect2(x, y, width, height), color, true)

func _pistol() -> void:
    # Compact 9mm silhouette: separate slide, barrel, muzzle, grip,
    # trigger guard and visible steel highlight. No disconnected arms.
    _rect(1, -5, 25, 9, OUTLINE)
    _rect(2, -4, 22, 6, RECEIVER)
    _rect(3, -4, 18, 2, HIGHLIGHT)
    _rect(20, -2, 4, 2, STEEL)
    _rect(24, -2, 3, 3, DARK)
    _rect(6, 2, 9, 15, OUTLINE)
    _rect(7, 3, 7, 12, GRIP)
    _rect(8, 5, 2, 8, WOOD)
    _rect(15, 2, 7, 2, OUTLINE)
    _rect(20, 4, 2, 6, OUTLINE)
    _rect(15, 9, 6, 2, OUTLINE)
    _rect(2, -7, 4, 2, DARK)

func _rifle() -> void:
    # Rifle with a clearly distinct buttstock, receiver, magazine and
    # long barrel; receiver shape has constant square-edged pixel profile.
    _rect(-21, -4, 20, 9, OUTLINE)
    _rect(-19, -3, 16, 6, WOOD)
    _rect(-22, -4, 3, 9, DARK)
    _rect(-4, -7, 27, 12, OUTLINE)
    _rect(-2, -5, 24, 8, RECEIVER)
    _rect(0, -5, 18, 2, HIGHLIGHT)
    _rect(21, -5, 21, 6, DARK)
    _rect(23, -4, 17, 3, STEEL)
    _rect(40, -5, 6, 5, OUTLINE)
    _rect(5, 5, 8, 16, OUTLINE)
    _rect(6, 6, 6, 13, GRIP)
    _rect(15, 5, 11, 16, OUTLINE)
    _rect(16, 6, 9, 13, RECEIVER)
    _rect(5, -10, 13, 3, OUTLINE)

func _smg() -> void:
    _rect(-11, -4, 10, 6, OUTLINE)
    _rect(-9, -3, 8, 3, STEEL)
    _rect(-2, -7, 29, 12, OUTLINE)
    _rect(0, -5, 25, 8, RECEIVER)
    _rect(2, -5, 14, 2, HIGHLIGHT)
    _rect(26, -4, 12, 5, DARK)
    _rect(27, -3, 10, 3, STEEL)
    _rect(6, 5, 7, 14, OUTLINE)
    _rect(7, 6, 5, 12, GRIP)
    _rect(19, 5, 7, 18, OUTLINE)
    _rect(20, 6, 5, 15, STEEL)

func _shotgun() -> void:
    _rect(-19, -5, 19, 11, OUTLINE)
    _rect(-17, -4, 16, 8, WOOD)
    _rect(-1, -6, 21, 11, OUTLINE)
    _rect(0, -5, 18, 8, RECEIVER)
    _rect(19, -5, 28, 5, OUTLINE)
    _rect(20, -4, 26, 3, STEEL)
    _rect(24, 1, 13, 4, WOOD)
    _rect(3, 5, 9, 13, OUTLINE)
    _rect(4, 6, 7, 11, GRIP)

func _muzzle_x() -> float:
    match weapon_family:
        "rifle", "shotgun":
            return 46.0
        "smg":
            return 39.0
        _:
            return 27.0

func _draw() -> void:
    match weapon_family:
        "pistol":
            _pistol()
        "rifle":
            _rifle()
        "smg":
            _smg()
        "shotgun":
            _shotgun()
        _:
            return
    if muzzle_flash_time > 0.0:
        var mx: float = _muzzle_x()
        draw_colored_polygon(PackedVector2Array([
            Vector2(mx - 1, -4), Vector2(mx + 5, -2),
            Vector2(mx + 11, 0), Vector2(mx + 5, 3),
            Vector2(mx - 1, 4)
        ]), Color("#ffe59b"))
        _rect(mx, -1, 8, 2, Color("#ffffff"))
