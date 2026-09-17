#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not root.is_dir():
    raise SystemExit(f"Game root not found: {root}")

mobile_path = root / "scripts/mobile_hud.gd"
world_path = root / "scripts/world/world_chunk.gd"
resource_path = root / "scripts/ecology/natural_resource.gd"
save_path = root / "scripts/save/save_manager.gd"
for p in (mobile_path, world_path, resource_path, save_path):
    if not p.is_file():
        raise SystemExit(f"Missing required C2 runtime file: {p}")

mobile = mobile_path.read_text(encoding="utf-8")
if '"crouch_v0185"' in mobile:
    mobile = mobile.replace('"crouch_v0185"', '"crouch_v0190c2"', 1)

old_layout = '''    sprint_button.position = Vector2(viewport_size.x * 0.5 - action.x * 1.55 - gap, center_y)\n    crouch_button.position = Vector2(viewport_size.x * 0.5 - action.x * 0.5, center_y)\n    interact_button.position = Vector2(viewport_size.x * 0.5 + action.x * 0.55 + gap, center_y)\n'''
new_layout = '''    sprint_button.position = Vector2(viewport_size.x * 0.5 - action.x * 1.55 - gap, center_y)\n    # C2: CROUCH lives above RUN in the left action cluster so the middle/right\n    # interaction lane remains clear when context-sensitive USE appears.\n    crouch_button.position = Vector2(sprint_button.position.x, center_y - gap - action.y)\n    interact_button.position = Vector2(viewport_size.x * 0.5 + action.x * 0.55 + gap, center_y)\n'''
if old_layout not in mobile:
    raise SystemExit("C2 HUD responsive CROUCH anchor missing")
mobile = mobile.replace(old_layout, new_layout, 1)
mobile_path.write_text(mobile, encoding="utf-8")

r = resource_path.read_text(encoding="utf-8")
if 'func get_interaction_display_name() -> String:' not in r:
    anchor = 'func interact(inventory: InventoryComponent) -> String:\n'
    if anchor not in r:
        raise SystemExit("C2 NaturalResource interaction anchor missing")
    block = '''func get_interaction_display_name() -> String:\n    match resource_type:\n        "surface_water": return "Surface Water"\n        "fishing_spot": return "Fishing Spot"\n        "tree": return "Tree"\n        "berry_bush": return "Berry Bush"\n        "mushroom_patch": return "Mushroom Patch"\n    return resource_type.replace("_", " ").capitalize()\n\nfunc interact_player(player_node: Node) -> String:\n    if resource_type != "surface_water":\n        return interact(player_node.get("inventory") as InventoryComponent)\n    if player_node == null:\n        return "No one is close enough to the water."\n    var stats: Variant = player_node.get("survival_stats")\n    if stats == null or not stats.has_method("apply_consumable"):\n        return "You found untreated surface water."\n    var before: float = float(stats.get("thirst"))\n    if before >= 99.5:\n        return "You are not thirsty. This is untreated surface water."\n    stats.call("apply_consumable", 0.0, 22.0, 0.0, 0.0)\n    var after: float = float(stats.get("thirst"))\n    var gained: int = maxi(1, int(round(after - before)))\n    return "Drank untreated surface water (+%d hydration)." % gained\n\n'''
    r = r.replace(anchor, block + anchor, 1)

if '        "surface_water":\n            return "Untreated surface water. Use the shoreline interaction to drink."\n' not in r:
    old = '''        "fishing_spot":\n            return _fish(inventory)\n    return "Nothing useful here."\n'''
    new = '''        "fishing_spot":\n            return _fish(inventory)\n        "surface_water":\n            return "Untreated surface water. Use the shoreline interaction to drink."\n    return "Nothing useful here."\n'''
    if old not in r:
        raise SystemExit("C2 NaturalResource match anchor missing")
    r = r.replace(old, new, 1)

if '        "surface_water":\n            draw_arc(Vector2.ZERO, 18.0' not in r:
    old = '''        "fishing_spot":\n            draw_arc(Vector2.ZERO,21,0,TAU,20,Color(.72,.92,1,.5),2)\n            draw_arc(Vector2.ZERO,12,0,TAU,20,Color(.72,.92,1,.38),1.5)\n            if not _depleted:\n                draw_circle(Vector2(3,-2),3.5,Color("e8d271"))\n'''
    new = '''        "fishing_spot":\n            draw_arc(Vector2.ZERO,21,0,TAU,20,Color(.72,.92,1,.5),2)\n            draw_arc(Vector2.ZERO,12,0,TAU,20,Color(.72,.92,1,.38),1.5)\n            if not _depleted:\n                draw_circle(Vector2(3,-2),3.5,Color("e8d271"))\n        "surface_water":\n            draw_arc(Vector2.ZERO, 18.0, 0.08, PI * 0.92, 12, Color(.72,.92,1,.48), 1.5)\n            draw_arc(Vector2(6, 5), 11.0, PI * 1.08, PI * 1.82, 10, Color(.72,.92,1,.32), 1.2)\n'''
    if old not in r:
        raise SystemExit("C2 NaturalResource draw anchor missing")
    r = r.replace(old, new, 1)
resource_path.write_text(r, encoding="utf-8")

w = world_path.read_text(encoding="utf-8")
old_spawn = '''    for water_position in _water_centers:\n        _spawn_resource("fishing_spot", water_position + Vector2(86, 0), serial)\n        serial += 1\n'''
new_spawn = '''    for water_position in _water_centers:\n        _spawn_resource("surface_water", water_position + Vector2(-92, 18), serial)\n        serial += 1\n        _spawn_resource("fishing_spot", water_position + Vector2(92, -10), serial)\n        serial += 1\n'''
if old_spawn not in w:
    raise SystemExit("C2 water resource spawn anchor missing")
w = w.replace(old_spawn, new_spawn, 1)

pattern = r'func _draw_water\(\) -> void:\n.*?(?=\nfunc _draw_roads\(\) -> void:)'
replacement = '''func _lake_points(center: Vector2, lake_index: int, scale_value: float) -> PackedVector2Array:\n    var points := PackedVector2Array()\n    var phase: float = float(posmod(abs(chunk_coord.x * 43 + chunk_coord.y * 67 + world_seed * 13 + lake_index * 109), 628)) / 100.0\n    var count := 28\n    for i in range(count):\n        var angle: float = TAU * float(i) / float(count)\n        var wobble: float = 1.0 + 0.13 * sin(angle * 3.0 + phase) + 0.075 * sin(angle * 7.0 + phase * 1.7) + 0.035 * sin(angle * 11.0 - phase * 0.6)\n        var rx: float = 126.0 * scale_value * wobble\n        var ry: float = 88.0 * scale_value * (1.0 + (wobble - 1.0) * 0.72)\n        points.append(center + Vector2(cos(angle) * rx, sin(angle) * ry))\n    return points\n\nfunc _draw_water() -> void:\n    for lake_index in range(_water_centers.size()):\n        var p: Vector2 = _water_centers[lake_index]\n        var bank := _lake_points(p, lake_index, 1.10)\n        var surface := _lake_points(p, lake_index, 1.00)\n        var inner := _lake_points(p + Vector2(3, 2), lake_index, 0.84)\n        draw_colored_polygon(bank, Color(0.29, 0.34, 0.22, 0.82))\n        draw_colored_polygon(surface, Color(0.22, 0.49, 0.57, 0.98))\n        draw_colored_polygon(inner, Color(0.16, 0.42, 0.53, 0.84))\n        var closed_surface := PackedVector2Array(surface)\n        if not surface.is_empty():\n            closed_surface.append(surface[0])\n        draw_polyline(closed_surface, Color(0.63, 0.77, 0.69, 0.58), 2.0, false)\n        var ripple_seed: int = abs(chunk_coord.x * 131 + chunk_coord.y * 197 + world_seed * 23 + lake_index * 317)\n        for ripple_index in range(11):\n            var angle: float = float(posmod(ripple_seed + ripple_index * 73, 628)) / 100.0\n            var radial: float = 0.20 + 0.055 * float(posmod(ripple_seed + ripple_index * 19, 9))\n            var ripple_center := p + Vector2(cos(angle) * 104.0 * radial, sin(angle) * 70.0 * radial)\n            var radius: float = 6.0 + float(posmod(ripple_seed + ripple_index * 11, 9))\n            var start_angle: float = angle + 0.25\n            draw_arc(ripple_center, radius, start_angle, start_angle + PI * 0.88, 10, Color(0.72, 0.91, 0.95, 0.46), 1.25)\n        for wave_index in range(7):\n            var wx: float = p.x - 70.0 + float(posmod(ripple_seed + wave_index * 47, 135))\n            var wy: float = p.y - 42.0 + float(posmod(ripple_seed + wave_index * 31, 84))\n            var length: float = 12.0 + float(posmod(ripple_seed + wave_index * 17, 19))\n            draw_line(Vector2(wx, wy), Vector2(wx + length, wy + float(posmod(wave_index, 3) - 1)), Color(0.74, 0.91, 0.94, 0.30), 1.0)\n'''
w, count = re.subn(pattern, replacement.rstrip(), w, count=1, flags=re.S)
if count != 1:
    raise SystemExit("C2 could not replace _draw_water")
world_path.write_text(w, encoding="utf-8")

s = save_path.read_text(encoding="utf-8")
if 'const GAME_VERSION := "0.19.0C1"' not in s:
    raise SystemExit("C2 expected v0.19.0C1 save version anchor missing")
s = s.replace('const GAME_VERSION := "0.19.0C1"', 'const GAME_VERSION := "0.19.0C2"', 1)
save_path.write_text(s, encoding="utf-8")

print("Applied v0.19.0C2: CROUCH moved out of interaction lane; lakes are irregular/rippled and provide untreated surface water.")
