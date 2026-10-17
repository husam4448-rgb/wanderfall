extends Node2D
## Native damage receptor used in real Godot combat tests.
var melee_radius: float = 3.0
var hits: int = 0
var total_damage: float = 0.0
func _ready() -> void:
    add_to_group("damageable")
func take_damage(amount: float) -> void:
    hits += 1
    total_damage += amount
