#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'game')
if not root.is_dir():
    raise SystemExit(f'Game root not found: {root}')

world_path = root / 'scripts/world/world_chunk.gd'
save_path = root / 'scripts/save/save_manager.gd'
for p in (world_path, save_path):
    if not p.is_file():
        raise SystemExit(f'Missing required C4 runtime file: {p}')

w = world_path.read_text(encoding='utf-8')

setup_old = '    _generate_nature()\n    _generate_poi_and_buildings()\n    _create_colliders()\n'
setup_new = '    _generate_nature()\n    _generate_poi_and_buildings()\n    _prune_building_overlap_clutter()\n    _create_colliders()\n'
if '_prune_building_overlap_clutter()' not in w:
    if setup_old not in w:
        raise SystemExit('C4 setup pruning anchor missing')
    w = w.replace(setup_old, setup_new, 1)

if 'func _prune_building_overlap_clutter() -> void:' not in w:
    anchor = 'func _create_colliders() -> void:\n'
    if anchor not in w:
        raise SystemExit('C4 collider anchor missing')

    arrays = [
        ('_tree_positions', 42.0),
        ('_resource_tree_positions', 46.0),
        ('_rock_positions', 38.0),
        ('_berry_positions', 36.0),
        ('_mushroom_positions', 34.0),
        ('_grass_tuft_positions', 26.0),
        ('_flower_positions', 28.0),
        ('_debris_positions', 34.0),
    ]
    for optional_name, margin in (
        ('_fallen_log_positions', 48.0),
        ('_scrap_pile_positions', 42.0),
        ('_wild_cache_positions', 56.0),
    ):
        if f'var {optional_name}:' in w:
            arrays.append((optional_name, margin))

    calls = ''.join(f'    _prune_points_from_buildings({name}, {margin:.1f})\n' for name, margin in arrays)
    if 'var _water_centers:' in w:
        calls += '    _prune_points_from_buildings(_water_centers, 168.0)\n'

    block = '''func _point_inside_building_clearance(point: Vector2, margin: float) -> bool:\n    if _building_rects.is_empty():\n        return false\n    for rect in _building_rects:\n        if rect.grow(margin).has_point(point):\n            return true\n        if poi_type != "bunker_entrance":\n            var apron := Rect2(\n                Vector2(rect.position.x - margin, rect.end.y - 12.0),\n                Vector2(rect.size.x + margin * 2.0, 86.0 + margin)\n            )\n            if apron.has_point(point):\n                return true\n    return false\n\nfunc _prune_points_from_buildings(points: Array[Vector2], margin: float) -> void:\n    for i in range(points.size() - 1, -1, -1):\n        if _point_inside_building_clearance(points[i], margin):\n            points.remove_at(i)\n\nfunc _prune_building_overlap_clutter() -> void:\n    if _building_rects.is_empty():\n        return\n''' + calls + '\n'
    w = w.replace(anchor, block + anchor, 1)

pattern = r'func _lake_points\(center: Vector2, lake_index: int, scale_value: float\) -> PackedVector2Array:\n.*?(?=\nfunc _draw_roads\(\) -> void:)'
replacement = '''func _lake_points(center: Vector2, lake_index: int, scale_value: float) -> PackedVector2Array:\n    var points := PackedVector2Array()\n    var phase: float = float(posmod(abs(chunk_coord.x * 43 + chunk_coord.y * 67 + world_seed * 13 + lake_index * 109), 628)) / 100.0\n    var count := 36\n    for i in range(count):\n        var angle: float = TAU * float(i) / float(count)\n        var wobble: float = 1.0 + 0.078 * sin(angle * 3.0 + phase) + 0.043 * sin(angle * 5.0 + phase * 1.37) + 0.018 * sin(angle * 2.0 - phase * 0.41)\n        var rx: float = 128.0 * scale_value * wobble\n        var ry: float = 89.0 * scale_value * (1.0 + (wobble - 1.0) * 0.62)\n        points.append(center + Vector2(cos(angle) * rx, sin(angle) * ry))\n    return points\n\nfunc _lake_core_points(center: Vector2, scale_value: float) -> PackedVector2Array:\n    var points := PackedVector2Array()\n    var count := 28\n    for i in range(count):\n        var angle: float = TAU * float(i) / float(count)\n        points.append(center + Vector2(cos(angle) * 111.0 * scale_value, sin(angle) * 75.0 * scale_value))\n    return points\n\nfunc _draw_water() -> void:\n    for lake_index in range(_water_centers.size()):\n        var p: Vector2 = _water_centers[lake_index]\n        var bank := _lake_points(p, lake_index, 1.10)\n        var surface := _lake_points(p, lake_index, 1.00)\n        var core := _lake_core_points(p, 1.00)\n        var inner := _lake_core_points(p + Vector2(3, 2), 0.76)\n        draw_colored_polygon(bank, Color(0.29, 0.34, 0.22, 0.82))\n        draw_colored_polygon(core, Color(0.20, 0.47, 0.57, 1.0))\n        draw_colored_polygon(surface, Color(0.22, 0.49, 0.57, 0.98))\n        draw_colored_polygon(inner, Color(0.15, 0.41, 0.53, 0.88))\n        var closed_surface := PackedVector2Array(surface)\n        if not surface.is_empty():\n            closed_surface.append(surface[0])\n        draw_polyline(closed_surface, Color(0.63, 0.77, 0.69, 0.58), 2.0, false)\n        var ripple_seed: int = abs(chunk_coord.x * 131 + chunk_coord.y * 197 + world_seed * 23 + lake_index * 317)\n        for ripple_index in range(11):\n            var angle: float = float(posmod(ripple_seed + ripple_index * 73, 628)) / 100.0\n            var radial: float = 0.20 + 0.055 * float(posmod(ripple_seed + ripple_index * 19, 9))\n            var ripple_center := p + Vector2(cos(angle) * 104.0 * radial, sin(angle) * 70.0 * radial)\n            var radius: float = 6.0 + float(posmod(ripple_seed + ripple_index * 11, 9))\n            var start_angle: float = angle + 0.25\n            draw_arc(ripple_center, radius, start_angle, start_angle + PI * 0.88, 10, Color(0.72, 0.91, 0.95, 0.46), 1.25)\n        for wave_index in range(7):\n            var wx: float = p.x - 70.0 + float(posmod(ripple_seed + wave_index * 47, 135))\n            var wy: float = p.y - 42.0 + float(posmod(ripple_seed + wave_index * 31, 84))\n            var length: float = 12.0 + float(posmod(ripple_seed + wave_index * 17, 19))\n            draw_line(Vector2(wx, wy), Vector2(wx + length, wy + float(posmod(wave_index, 3) - 1)), Color(0.74, 0.91, 0.94, 0.30), 1.0)\n'''
w, count = re.subn(pattern, replacement.rstrip(), w, count=1, flags=re.S)
if count != 1:
    raise SystemExit('C4 could not replace lake renderer')

world_path.write_text(w, encoding='utf-8')

s = save_path.read_text(encoding='utf-8')
s2, count = re.subn(r'const GAME_VERSION := "0\.19\.0C[23]"', 'const GAME_VERSION := "0.19.0C4"', s, count=1)
if count != 1 and 'const GAME_VERSION := "0.19.0C4"' not in s:
    raise SystemExit('C4 could not bump GAME_VERSION')
save_path.write_text(s2 if count else s, encoding='utf-8')

print('Applied v0.19.0C4: building-clearance clutter pruning and continuous natural lake fill.')
