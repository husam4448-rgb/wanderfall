extends Node2D
## Knife points toward +X. Parent MeleeController rotates this layer; no arms.
func _ready() -> void:
    z_index = 2
    queue_redraw()

func _draw() -> void:
    draw_line(Vector2.ZERO, Vector2(10, 0), Color("#302017"), 7.0, false)
    draw_line(Vector2(1, 0), Vector2(8, 0), Color("#80503a"), 4.0, false)
    draw_line(Vector2(11, -5), Vector2(11, 5), Color("#17191a"), 3.0, false)
    draw_colored_polygon(PackedVector2Array([
        Vector2(12, -4), Vector2(31, -4), Vector2(36, 0),
        Vector2(31, 2), Vector2(12, 3)
    ]), Color("#23262c"))
    draw_colored_polygon(PackedVector2Array([
        Vector2(14, -2), Vector2(31, -2), Vector2(34, 0),
        Vector2(30, 1), Vector2(14, 1)
    ]), Color("#b9c6d0"))
    draw_line(Vector2(16, -2), Vector2(30, -2), Color("#f6f7f8"), 1.0, false)
