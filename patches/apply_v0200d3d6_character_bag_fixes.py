#!/usr/bin/env python3
"""v0.20.0D3D.6: player scale/breathing/apparel/gun grip + icon-mode bag fixes."""
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

def must_replace(path: Path, old: str, new: str, label: str):
    s = path.read_text(encoding="utf-8")
    if old not in s:
        raise SystemExit(f"D3D.6 anchor missing ({label}) in {path}")
    path.write_text(s.replace(old, new, 1), encoding="utf-8")

visual = root / "scripts/art/production_survivor_visual.gd"
v = visual.read_text(encoding="utf-8")

# Additional authored outfit option already fetched by Android CI.
v = v.replace(
    'const OUTFIT_SCENE: PackedScene = preload("res://assets/models/superhero_male/Male_Peasant.gltf")\n',
    'const OUTFIT_SCENE: PackedScene = preload("res://assets/models/superhero_male/Male_Peasant.gltf")\n'
    'const RANGER_SCENE: PackedScene = preload("res://assets/models/superhero_male/Male_Ranger.gltf")\n',
    1,
)

v = v.replace(
    'var outfit_model: Node3D\nvar body_skeleton: Skeleton3D\nvar outfit_skeleton: Skeleton3D\n',
    'var outfit_model: Node3D\nvar ranger_model: Node3D\n'
    'var body_skeleton: Skeleton3D\nvar outfit_skeleton: Skeleton3D\nvar ranger_skeleton: Skeleton3D\n',
    1,
)

v = v.replace(
    'func refresh_gear() -> void:\n    _pose_dirty = true\n',
    'func refresh_gear() -> void:\n'
    '    _sync_apparel_visuals()\n'
    '    _pose_dirty = true\n'
    '    if viewport != null:\n'
    '        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE\n',
    1,
)

# Add Ranger alongside Peasant, but render only one clothing model at a time.
pat = re.compile(
    r'(\s+outfit_model = OUTFIT_SCENE\.instantiate\(\)\n'
    r'\s+outfit_model\.name = "[^"]+"\n'
    r'\s+actor_root\.add_child\(outfit_model\)\n'
    r'\s+body_skeleton = _find_skeleton\(body_model\)\n'
    r'\s+outfit_skeleton = _find_skeleton\(outfit_model\)\n)'
)
m = pat.search(v)
if not m:
    raise SystemExit("D3D.6 outfit instantiation block missing")
block = m.group(1)
new_block = block.replace(
    '    body_skeleton = _find_skeleton(body_model)\n',
    '    ranger_model = RANGER_SCENE.instantiate()\n'
    '    ranger_model.name = "SurvivorRangerOutfit"\n'
    '    ranger_model.visible = false\n'
    '    actor_root.add_child(ranger_model)\n\n'
    '    body_skeleton = _find_skeleton(body_model)\n'
).replace(
    '    outfit_skeleton = _find_skeleton(outfit_model)\n',
    '    outfit_skeleton = _find_skeleton(outfit_model)\n'
    '    ranger_skeleton = _find_skeleton(ranger_model)\n'
    '    _sync_apparel_visuals()\n'
)
v = v[:m.start()] + new_block + v[m.end():]

v = v.replace(
    'for skel in [body_skeleton, outfit_skeleton]:',
    'for skel in [body_skeleton, outfit_skeleton, ranger_skeleton]:',
)

# Increase visible actor size ~50% over D3D.5 while preserving gameplay collision scale.
v = v.replace(
    'viewport_sprite.scale = Vector2(0.22, 0.22)',
    'viewport_sprite.scale = Vector2(0.30, 0.30)',
    1,
)

# Low-cost breathing: animate the 2D render texture itself while idle, so the
# demand-rendered 3D SubViewport stays performance-friendly.
old = '''    if viewport_sprite != null:
        var bob := -absf(sin(gait_phase)) * (0.90 if sprinting else 0.45) if moving else 0.0
        viewport_sprite.position.y = -3.0 + bob + (1.2 if crouching else 0.0)
'''
new = '''    if viewport_sprite != null:
        var bob := -absf(sin(gait_phase)) * (0.90 if sprinting else 0.45) if moving else 0.0
        var breath := 0.0 if moving else sin(idle_phase) * 0.012
        viewport_sprite.scale = Vector2(0.30 * (1.0 - breath * 0.22), 0.30 * (1.0 + breath))
        viewport_sprite.position.y = -3.0 + bob - breath * 7.0 + (1.2 if crouching else 0.0)
'''
if old not in v:
    raise SystemExit("D3D.6 idle sprite block missing")
v = v.replace(old, new, 1)

# Move the gun farther forward from the wrist bone so the grip sits in the hand
# instead of appearing pulled behind it.
v = v.replace(
    'gun_root.position = actor_root.to_local(world_hand) + Vector3(0.0, 0.075, 0.055)',
    'gun_root.position = actor_root.to_local(world_hand) + Vector3(0.0, 0.060, 0.135)',
    1,
)

# Insert live apparel synchronization. get_visual_item() respects transmog.
anchor = 'func _weapon_category() -> String:\n'
if anchor not in v:
    raise SystemExit("D3D.6 apparel helper anchor missing")
helper = '''func _sync_apparel_visuals() -> void:
    if outfit_model == null:
        return
    var torso := ""
    var armor := ""
    var legs := ""
    var hands := ""
    var feet := ""
    var back := ""
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item"):
        torso = String(equipment.get_visual_item("torso"))
        armor = String(equipment.get_visual_item("armor"))
        legs = String(equipment.get_visual_item("legs"))
        hands = String(equipment.get_visual_item("hands"))
        feet = String(equipment.get_visual_item("feet"))
        back = String(equipment.get_visual_item("back"))

    var has_clothes := not torso.is_empty() or not armor.is_empty() or not legs.is_empty() or not hands.is_empty() or not feet.is_empty()
    var rugged_key := (torso + "|" + armor).to_lower()
    var use_ranger := (
        not armor.is_empty()
        or "jacket" in rugged_key
        or "coat" in rugged_key
        or "vest" in rugged_key
        or "military" in rugged_key
        or "tactical" in rugged_key
        or "ranger" in rugged_key
    )
    outfit_model.visible = has_clothes and not use_ranger
    if ranger_model != null:
        ranger_model.visible = has_clothes and use_ranger
    if backpack_root != null:
        backpack_root.visible = not back.is_empty()

'''
v = v.replace(anchor, helper + anchor, 1)
visual.write_text(v, encoding="utf-8")

# Player-side production visual node no longer shrinks the already-small render.
player = root / "scripts/player.gd"
p = player.read_text(encoding="utf-8")
p = p.replace('_production_visual.scale = Vector2(0.86, 0.86)', '_production_visual.scale = Vector2(1.0, 1.0)', 1)
player.write_text(p, encoding="utf-8")

# ---------------------------------------------------------------------------
# BAG / inventory icon mode.
# ---------------------------------------------------------------------------
mobile = root / "scripts/mobile_hud.gd"
s = mobile.read_text(encoding="utf-8")

# Give the window room to shrink on phones. Content still expands naturally.
s = s.replace(
    'inventory_panel.custom_minimum_size = Vector2(330, 370)',
    'inventory_panel.custom_minimum_size = Vector2(250, 270)',
    1,
)
s = s.replace(
    'inventory_scroll.custom_minimum_size = Vector2(0, 220)',
    'inventory_scroll.custom_minimum_size = Vector2(0, 120)',
    1,
)

# Preserve window geometry when +/- only changes icon scale. This stops the
# "-" button from appearing to act like a window-enlarge command.
old = '''func _change_inventory_icon_size(delta: int) -> void:
    GameSettings.inventory_icon_scale_index = clampi(GameSettings.inventory_icon_scale_index + delta, 0, 2)
    GameSettings.settings_changed.emit()
    _refresh_inventory()
'''
new = '''func _change_inventory_icon_size(delta: int) -> void:
    var previous_size := inventory_panel.size if inventory_panel != null else Vector2.ZERO
    var previous_position := inventory_panel.position if inventory_panel != null else Vector2.ZERO
    GameSettings.inventory_icon_scale_index = clampi(GameSettings.inventory_icon_scale_index + delta, 0, 2)
    GameSettings.settings_changed.emit()
    _refresh_inventory()
    if inventory_panel != null:
        inventory_panel.custom_minimum_size = Vector2(250, 270)
        if previous_size.x > 0.0 and previous_size.y > 0.0:
            inventory_panel.size = Vector2(maxf(250.0, previous_size.x), maxf(270.0, previous_size.y))
            inventory_panel.position = previous_position
        UIManager.ensure_fully_visible(inventory_panel)
'''
if old not in s:
    raise SystemExit("D3D.6 inventory icon callback missing")
s = s.replace(old, new, 1)

# Make the three icon sizes clearly distinct and base them on the actual current
# panel width instead of a hard 330px floor that fights manual resizing.
old = '''            var available_width := maxf(330.0, inventory_panel.size.x - 26.0)
            var target_tile := 92.0
            match GameSettings.inventory_icon_scale_index:
                0: target_tile = 68.0
                2: target_tile = 118.0
            var columns := clampi(int(floor((available_width + 6.0) / (target_tile + 6.0))), 2, 5)
            grid.columns = columns
            var tile_size := clampf((available_width - float(columns - 1) * 6.0) / float(columns), 62.0, 126.0)
'''
new = '''            var available_width := maxf(220.0, inventory_panel.size.x - 26.0)
            var target_tile := 86.0
            match GameSettings.inventory_icon_scale_index:
                0: target_tile = 58.0
                2: target_tile = 116.0
            var columns := clampi(int(floor((available_width + 6.0) / (target_tile + 6.0))), 2, 6)
            grid.columns = columns
            var fitted_tile := (available_width - float(columns - 1) * 6.0) / float(columns)
            var tile_size := clampf(minf(target_tile, fitted_tile), 52.0, 116.0)
'''
if old not in s:
    raise SystemExit("D3D.6 inventory grid sizing block missing")
s = s.replace(old, new, 1)
mobile.write_text(s, encoding="utf-8")

# Universal resize: panel content may have a large minimum in grid mode. Use a
# practical touch-window floor for BAG/STORAGE instead of blindly inheriting it.
ui = root / "scripts/ui/ui_manager.gd"
u = ui.read_text(encoding="utf-8")
old = '''    elif _gesture_mode == "resize":
        var min_size := _gesture_target.custom_minimum_size
        min_size.x = maxf(min_size.x, 230.0)
        min_size.y = maxf(min_size.y, 180.0)
        _gesture_target.size = Vector2(maxf(min_size.x, _gesture_start_size.x + delta.x), maxf(min_size.y, _gesture_start_size.y + delta.y))
'''
new = '''    elif _gesture_mode == "resize":
        var panel_id := String(_gesture_target.get_meta("wanderfall_panel_id", ""))
        var min_size := _gesture_target.custom_minimum_size
        if panel_id == "inventory" or panel_id == "storage":
            min_size = Vector2(250.0, 270.0)
        else:
            min_size.x = maxf(min_size.x, 230.0)
            min_size.y = maxf(min_size.y, 180.0)
        _gesture_target.size = Vector2(maxf(min_size.x, _gesture_start_size.x + delta.x), maxf(min_size.y, _gesture_start_size.y + delta.y))
'''
if old not in u:
    raise SystemExit("D3D.6 resize block missing")
u = u.replace(old, new, 1)
ui.write_text(u, encoding="utf-8")

# Version identity.
preset = root / "export_presets.cfg"
ep = preset.read_text(encoding="utf-8")
ep, n1 = re.subn(r'(?m)^version/code=\d+$', 'version/code=35', ep, count=1)
ep, n2 = re.subn(r'(?m)^version/name="[^"]*"$', 'version/name="0.20.0D3D.6"', ep, count=1)
if not n1 or not n2:
    raise SystemExit("D3D.6 export version fields missing")
preset.write_text(ep, encoding="utf-8")

save = root / "scripts/save/save_manager.gd"
if save.is_file():
    ss = save.read_text(encoding="utf-8")
    ss, _ = re.subn(r'const GAME_VERSION := "[^"]+"', 'const GAME_VERSION := "0.20.0D3D.6"', ss, count=1)
    save.write_text(ss, encoding="utf-8")

print("Applied v0.20.0D3D.6: larger breathing player, live apparel model switching, forward pistol grip, and corrected BAG icon/resize behavior.")
