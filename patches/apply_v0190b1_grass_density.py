#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not root.is_dir():
    raise SystemExit(f"Game root not found: {root}")

settings_path = root / "scripts/settings/game_settings.gd"
hud_path = root / "scripts/settings/settings_hud.gd"
world_path = root / "scripts/world/world_chunk.gd"
manager_path = root / "scripts/world/world_manager.gd"
save_path = root / "scripts/save/save_manager.gd"
for path in (settings_path, hud_path, world_path, manager_path):
    if not path.is_file():
        raise SystemExit(f"Missing expected runtime file: {path}")

s = settings_path.read_text(encoding="utf-8")
if "signal grass_density_changed" not in s:
    anchor = "signal quick_items_changed\n"
    if anchor not in s: raise SystemExit("GameSettings signal anchor missing")
    s = s.replace(anchor, anchor + "signal grass_density_changed(level: int, multiplier: float)\n", 1)

if "GRASS_DENSITY_NAMES" not in s:
    anchor = 'const PRESETS := ["Standard", "Relaxed", "Exploration", "Hardcore", "Creative"]\n'
    if anchor not in s: raise SystemExit("GameSettings preset anchor missing")
    s = s.replace(anchor, '''const PRESETS := ["Standard", "Relaxed", "Exploration", "Hardcore", "Creative"]
const GRASS_DENSITY_NAMES: Array[String] = ["Off", "Low", "Medium", "High", "Ultra"]
const GRASS_DENSITY_MULTIPLIERS: Array[float] = [0.0, 0.18, 0.40, 0.70, 1.0]
''', 1)

if "var grass_density_level :=" not in s:
    anchor = "var sfx_volume := 1.0\n"
    if anchor not in s: raise SystemExit("GameSettings visual-setting anchor missing")
    s = s.replace(anchor, anchor + "# v0.19.0B1 decorative world grass. 0=Off ... 4=Ultra.\nvar grass_density_level := 2\n", 1)

if '"grass_density_level": grass_density_level' not in s:
    anchor = '        "sfx_volume": sfx_volume,\n'
    if anchor not in s: raise SystemExit("GameSettings serialize anchor missing")
    s = s.replace(anchor, anchor + '        "grass_density_level": grass_density_level,\n', 1)

if "grass_density_level = clampi(int(data.get(\"grass_density_level\"" not in s:
    anchor = "    sfx_volume = clampf(float(data.get(\"sfx_volume\", sfx_volume)), 0.0, 1.0)\n"
    if anchor not in s: raise SystemExit("GameSettings deserialize anchor missing")
    s = s.replace(anchor, anchor + '    grass_density_level = clampi(int(data.get("grass_density_level", grass_density_level)), 0, GRASS_DENSITY_NAMES.size() - 1)\n', 1)

if "grass_density_changed.emit(grass_density_level, get_grass_density_multiplier())\n    quick_items_changed.emit()" not in s:
    anchor = "    settings_changed.emit()\n    quick_items_changed.emit()\n\nfunc set_movement_stick_sensitivity"
    if anchor not in s: raise SystemExit("GameSettings deserialize emit anchor missing")
    s = s.replace(anchor, "    settings_changed.emit()\n    grass_density_changed.emit(grass_density_level, get_grass_density_multiplier())\n    quick_items_changed.emit()\n\nfunc set_movement_stick_sensitivity", 1)

if "func cycle_grass_density()" not in s:
    anchor = "func set_movement_stick_sensitivity(value: float) -> float:\n"
    if anchor not in s: raise SystemExit("GameSettings method anchor missing")
    methods = '''func get_grass_density_name() -> String:
    return GRASS_DENSITY_NAMES[clampi(grass_density_level, 0, GRASS_DENSITY_NAMES.size() - 1)]

func get_grass_density_multiplier() -> float:
    return GRASS_DENSITY_MULTIPLIERS[clampi(grass_density_level, 0, GRASS_DENSITY_MULTIPLIERS.size() - 1)]

func set_grass_density_level(level: int) -> int:
    var next_level := clampi(level, 0, GRASS_DENSITY_NAMES.size() - 1)
    if next_level == grass_density_level:
        return grass_density_level
    grass_density_level = next_level
    current_preset = "Custom"
    grass_density_changed.emit(grass_density_level, get_grass_density_multiplier())
    settings_changed.emit()
    return grass_density_level

func cycle_grass_density() -> int:
    return set_grass_density_level((grass_density_level + 1) % GRASS_DENSITY_NAMES.size())

'''
    s = s.replace(anchor, methods + anchor, 1)
settings_path.write_text(s, encoding="utf-8")

h = hud_path.read_text(encoding="utf-8")
if "var grass_density_button: Button" not in h:
    anchor = "var ui_buttons: Dictionary = {}\n"
    if anchor not in h: raise SystemExit("Settings HUD variable anchor missing")
    h = h.replace(anchor, anchor + "var grass_density_button: Button\n", 1)

if 'graphics_title.text = "GRAPHICS / WORLD DETAIL"' not in h:
    anchor = '''    var ui_title := Label.new()
    ui_title.text = "UI / HUD CUSTOMIZATION"
'''
    if anchor not in h: raise SystemExit("Settings HUD graphics insertion anchor missing")
    block = '''    var graphics_title := Label.new()
    graphics_title.text = "GRAPHICS / WORLD DETAIL"
    graphics_title.add_theme_font_size_override("font_size", 13)
    root.add_child(graphics_title)
    var graphics_hint := Label.new()
    graphics_hint.text = "Grass density changes decorative ground vegetation only. Lower levels reduce retained draw commands; performance profiles still cap the final density."
    graphics_hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    graphics_hint.add_theme_font_size_override("font_size", 10)
    root.add_child(graphics_hint)
    grass_density_button = _small_button("GRASS DENSITY")
    grass_density_button.pressed.connect(func(): GameSettings.cycle_grass_density())
    root.add_child(grass_density_button)

'''
    h = h.replace(anchor, block + anchor, 1)

if 'grass_density_button.text = "GRASS: %s"' not in h:
    anchor = '''    if edit_hud_button != null:
        edit_hud_button.text = "EDIT CONTROLS"
'''
    if anchor not in h: raise SystemExit("Settings HUD refresh anchor missing")
    h = h.replace(anchor, '''    if grass_density_button != null:
        grass_density_button.text = "GRASS: %s" % GameSettings.get_grass_density_name().to_upper()
    if edit_hud_button != null:
        edit_hud_button.text = "EDIT CONTROLS"
''', 1)
hud_path.write_text(h, encoding="utf-8")

w = world_path.read_text(encoding="utf-8")
w, count = re.subn(r"var tuft_count := 26 \+ biome_id \* 7", "var tuft_count := 120 + biome_id * 18", w, count=1)
if count != 1 and "var tuft_count := 120 + biome_id * 18" not in w:
    raise SystemExit("World grass pool anchor missing")

pattern = r"func _draw_environment_detail\(\) -> void:\n.*?(?=\nfunc _draw_nature\(\) -> void:)"
replacement = '''func _draw_environment_detail() -> void:
    var detail_density := PerformanceManager.get_detail_density()
    var grass_density := GameSettings.get_grass_density_multiplier() * detail_density
    var grass_key := "grass_dry" if biome_id == 2 else "grass_green"
    for i in range(_quality_count(_grass_tuft_positions.size(), grass_density)):
        var p: Vector2 = _grass_tuft_positions[i]
        var scale_jitter := 0.86 + float(posmod(i * 17 + chunk_coord.x * 3 + chunk_coord.y * 5, 7)) * 0.035
        var size := Vector2(32, 24) * scale_jitter
        _draw_prop(grass_key, Rect2(p - Vector2(size.x * 0.5, size.y * 0.74), size))
    for i in range(_quality_count(_flower_positions.size(), detail_density)):
        var p: Vector2 = _flower_positions[i]
        _draw_prop("flowers", Rect2(p - Vector2(16, 21), Vector2(32, 28)))
    for i in range(_quality_count(_debris_positions.size(), maxf(0.35, detail_density))):
        var p: Vector2 = _debris_positions[i]
        _draw_prop("trash" if _near_road(p, 76) else "debris", Rect2(p - Vector2(24, 24), Vector2(48, 36)))
    for i in range(_quality_count(_road_crack_positions.size(), maxf(0.35, detail_density))):
        var p: Vector2 = _road_crack_positions[i]
        draw_line(p + Vector2(-7, -2), p + Vector2(0, 2), Color("3f403e"), 1.5)
        draw_line(p + Vector2(0, 2), p + Vector2(8, -3), Color("3f403e"), 1.5)
'''
w, count = re.subn(pattern, replacement.rstrip(), w, count=1, flags=re.S)
if count != 1: raise SystemExit("Could not replace world environment-detail renderer")
world_path.write_text(w, encoding="utf-8")

m = manager_path.read_text(encoding="utf-8")
if "GameSettings.grass_density_changed.connect" not in m:
    anchor = "    PerformanceManager.quality_changed.connect(_on_quality_changed)\n"
    if anchor not in m: raise SystemExit("WorldManager ready anchor missing")
    m = m.replace(anchor, anchor + "    GameSettings.grass_density_changed.connect(_on_grass_density_changed)\n", 1)
if "func _on_grass_density_changed" not in m:
    anchor = "func get_active_chunk_count() -> int:\n"
    if anchor not in m: raise SystemExit("WorldManager method anchor missing")
    m = m.replace(anchor, '''func _on_grass_density_changed(_level: int, _multiplier: float) -> void:
    for chunk in _loaded_chunks.values():
        if chunk != null and is_instance_valid(chunk):
            chunk.queue_redraw()

''' + anchor, 1)
manager_path.write_text(m, encoding="utf-8")

if save_path.is_file():
    sv = save_path.read_text(encoding="utf-8")
    sv, count = re.subn(r'const GAME_VERSION\s*:?=\s*"[^"]+"', 'const GAME_VERSION := "0.19.0B1"', sv, count=1)
    if count != 1: raise SystemExit("Could not update GAME_VERSION")
    save_path.write_text(sv, encoding="utf-8")

print("Applied v0.19.0B1 persistent Off/Low/Medium/High/Ultra grass density with live world redraw.")
