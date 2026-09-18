#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

def read(rel):
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"Missing D1c target: {p}")
    return p, p.read_text(encoding="utf-8")

def replace_once(rel, old, new):
    p, s = read(rel)
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"D1c anchor missing in {rel}: {old[:120]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

utility_path = root / "scripts/building/interior_utility.gd"
utility_path.parent.mkdir(parents=True, exist_ok=True)
utility_path.write_text("""class_name InteriorUtility
extends Node2D

var utility_type := "bed"
var display_name := "Bed"
var recipe_profile := "household"

func setup(type_value: String, label_value: String, profile_value: String = "household") -> void:
    utility_type = type_value
    display_name = label_value
    recipe_profile = profile_value

func _ready() -> void:
    z_index = 16
    add_to_group("settlement_interactable")
    queue_redraw()

func get_interaction_display_name() -> String:
    return display_name

func interact(inventory: InventoryComponent) -> String:
    if utility_type == "bed":
        return _rest()
    if utility_type == "workbench":
        return _craft(inventory)
    return "%s is ready." % display_name

func _rest() -> String:
    var scene := get_tree().current_scene
    var player := scene.get_node_or_null("Player") if scene != null else null
    if player == null or player.get("survival_stats") == null:
        return "%s is ready for rest." % display_name
    var stats = player.survival_stats
    stats.fatigue = maxf(0.0, stats.fatigue - 65.0)
    stats.hunger = maxf(0.0, stats.hunger - 3.0)
    stats.thirst = maxf(0.0, stats.thirst - 4.0)
    stats.changed.emit()
    return "You rest on %s. Fatigue greatly reduced." % display_name

func _craft(inventory: InventoryComponent) -> String:
    if recipe_profile == "mechanic":
        if inventory.count_item("scrap_metal") <= 0 or inventory.count_item("wire") <= 0:
            return "%s: Scrap Metal + Wire can be worked into Nails." % display_name
        inventory.remove_item("scrap_metal", 1)
        inventory.remove_item("wire", 1)
        var leftover := inventory.add_item("nails", 4)
        if leftover > 0:
            inventory.add_item("scrap_metal", 1)
            inventory.add_item("wire", 1)
            inventory.remove_item("nails", 4 - leftover)
            return "Your bag needs room for the crafted Nails."
        return "%s crafted Nails ×4." % display_name

    if inventory.count_item("cloth") < 2:
        return "%s: 2 Cloth can be turned into one Bandage." % display_name
    inventory.remove_item("cloth", 2)
    var leftover := inventory.add_item("bandage", 1)
    if leftover > 0:
        inventory.add_item("cloth", 2)
        return "Your bag needs room for the Bandage."
    return "%s crafted one Bandage." % display_name

func _draw() -> void:
    draw_circle(Vector2(0, 7), 15.0, Color(0.03, 0.04, 0.04, 0.25))
    if utility_type == "bed":
        draw_rect(Rect2(-25, -12, 50, 28), Color("7f7765"), true)
        draw_rect(Rect2(-23, -10, 16, 24), Color("c4b89b"), true)
        draw_rect(Rect2(-5, -9, 27, 22), Color("5b6d67"), true)
        return
    draw_rect(Rect2(-27, -10, 54, 22), Color("6f5135"), true)
    draw_rect(Rect2(-29, -14, 58, 7), Color("9a7145"), true)
    draw_line(Vector2(-20, 12), Vector2(-20, 23), Color("4a3828"), 5.0)
    draw_line(Vector2(20, 12), Vector2(20, 23), Color("4a3828"), 5.0)
    if recipe_profile == "mechanic":
        draw_line(Vector2(-12, -16), Vector2(8, -2), Color("7f8b8e"), 4.0)
""", encoding="utf-8")

replace_once(
    "scripts/building/building_level_manager.gd",
    'const PortalScript = preload("res://scripts/building/level_portal.gd")\n',
    'const PortalScript = preload("res://scripts/building/level_portal.gd")\nconst InteriorUtilityScript = preload("res://scripts/building/interior_utility.gd")\nconst LootContainerScript = preload("res://scripts/items/loot_container.gd")\n',
)

replace_once(
    "scripts/building/building_level_manager.gd",
    '''    _spawn_floor(center, floor_size, floor_id, poi_name, floor_color, poi_type)
    var entry := center + Vector2(-floor_size.x * 0.5 + 78.0, floor_size.y * 0.5 - 76.0)
''',
    '''    _spawn_floor(center, floor_size, floor_id, poi_name, floor_color, poi_type)
    _spawn_interior_utilities(center, floor_id, poi_type, poi_name)
    var entry := center + Vector2(-floor_size.x * 0.5 + 78.0, floor_size.y * 0.5 - 76.0)
''',
)

replace_once(
    "scripts/building/building_level_manager.gd",
    "func _spawn_portal(label_value: String, position_value: Vector2, target_value: Vector2, floor_value: String, kind_value: String) -> void:\n",
    '''func _spawn_interior_utilities(center: Vector2, floor_id: String, poi_type: String, poi_name: String) -> void:
    var storage_position := center + Vector2(150, 90)
    var bed_position := center + Vector2(85, -105)
    var bench_position := center + Vector2(-145, -55)
    var storage_label := "%s Storage" % poi_name
    var bench_label := "Workbench"
    var bench_profile := "household"
    var include_bed := true

    match poi_type:
        "store":
            storage_position = center + Vector2(10, 105)
            bench_position = center + Vector2(-190, -105)
            bench_label = "Packing Workbench"
            include_bed = false
        "garage":
            storage_position = center + Vector2(120, 95)
            bench_position = center + Vector2(-45, 85)
            bench_label = "Mechanic Workbench"
            bench_profile = "mechanic"
            include_bed = false
        "cabin":
            storage_position = center + Vector2(-125, 95)
            bed_position = center + Vector2(105, -100)
            bench_position = center + Vector2(-125, -25)
            bench_label = "Survival Workbench"
        "bunker_entrance":
            storage_position = center + Vector2(135, 90)
            bed_position = center + Vector2(105, -105)
            bench_position = center + Vector2(-70, 85)
            bench_label = "Bunker Workbench"
        _:
            storage_position = center + Vector2(115, 95)
            bed_position = center + Vector2(105, -105)
            bench_position = center + Vector2(-135, -45)
            bench_label = "Household Workbench"

    var storage := LootContainerScript.new()
    var seed_value := floor_id.hash() & 0x7fffffff
    storage.setup("interior_storage_%s" % floor_id, seed_value, poi_type, storage_label)
    add_child(storage)
    storage.global_position = storage_position

    var bench := InteriorUtilityScript.new()
    bench.setup("workbench", bench_label, bench_profile)
    add_child(bench)
    bench.global_position = bench_position

    if include_bed:
        var bed := InteriorUtilityScript.new()
        bed.setup("bed", "%s Bed" % poi_name)
        add_child(bed)
        bed.global_position = bed_position

func _spawn_portal(label_value: String, position_value: Vector2, target_value: Vector2, floor_value: String, kind_value: String) -> void:
''',
)

replace_once(
    "scripts/save/save_manager.gd",
    'const GAME_VERSION := "0.19.0C6"\n',
    'const GAME_VERSION := "0.19.0D1"\n',
)

print("Applied v0.19.0D1c functional generated-building utilities and version bump.")
