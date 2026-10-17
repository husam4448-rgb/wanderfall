extends Node2D
## Reusable tiny circular hand; ALWAYS a child of the held weapon, never torso.
## Color is matched to approved survivor skin (#e9a76f), no sleeves or arms.
@export var hand_radius: float = 3.25
@export var skin_color: Color = Color("#e9a76f")
@export var outline_color: Color = Color("#251b16")
func _ready() -> void:
    name = "AttachedPixelHand"
    z_index = 1
    queue_redraw()
func _draw() -> void:
    draw_circle(Vector2.ZERO, hand_radius + 1.0, outline_color)
    draw_circle(Vector2.ZERO, hand_radius, skin_color)
    # Tiny lighter knuckle mark; no floating limb or sleeve.
    draw_rect(Rect2(-1.0, -2.0, 2.0, 1.0), skin_color.lightened(0.13), true)
