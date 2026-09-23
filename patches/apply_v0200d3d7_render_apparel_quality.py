#!/usr/bin/env python3
"""v0.20.0D3D.7: render-quality, breathing-strength and apparel-visibility pass."""
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
visual = root / "scripts/art/production_survivor_visual.gd"
v = visual.read_text(encoding="utf-8")

# Higher internal resolution while retaining demand-driven SubViewport rendering.
v, n = re.subn(r'const VIEW_SIZE := Vector2i\(144, 192\)', 'const VIEW_SIZE := Vector2i(288, 384)', v, count=1)
if not n:
    raise SystemExit("D3D.7 VIEW_SIZE anchor missing")
v = v.replace(
    'viewport_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST',
    'viewport_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR',
    1,
)

# Stronger but still subtle breathing. Keep it on the 2D composited texture so
# the 3D viewport remains UPDATE_ONCE for performance.
old = '''        var breath := 0.0 if moving else sin(idle_phase) * 0.012
        viewport_sprite.scale = Vector2(0.30 * (1.0 - breath * 0.22), 0.30 * (1.0 + breath))
        viewport_sprite.position.y = -3.0 + bob - breath * 7.0 + (1.2 if crouching else 0.0)
'''
new = '''        var breath := 0.0 if moving else sin(idle_phase) * 0.026
        viewport_sprite.scale = Vector2(0.30 * (1.0 - breath * 0.18), 0.30 * (1.0 + breath))
        viewport_sprite.position.y = -3.0 + bob - breath * 11.0 + (1.2 if crouching else 0.0)
'''
if old not in v:
    raise SystemExit("D3D.7 breathing anchor missing")
v = v.replace(old, new, 1)

# Replace D3D.6 apparel synchronization with exclusive model visibility plus
# deterministic visible clothing tints derived from the equipped/transmog item.
start = v.find("func _sync_apparel_visuals() -> void:\n")
end = v.find("\nfunc _weapon_category() -> String:\n", start)
if start < 0 or end < 0:
    raise SystemExit("D3D.7 apparel helper block missing")
helper = '''func _appearance_color(key: String) -> Color:
    if key.is_empty():
        return Color.WHITE
    var palette := [
        Color(0.34, 0.42, 0.30, 1.0),
        Color(0.28, 0.34, 0.46, 1.0),
        Color(0.46, 0.33, 0.25, 1.0),
        Color(0.40, 0.37, 0.30, 1.0),
        Color(0.24, 0.42, 0.40, 1.0),
        Color(0.44, 0.28, 0.30, 1.0),
    ]
    var idx := absi(key.hash()) % palette.size()
    return palette[idx]

func _apply_model_tint(root_node: Node, tint: Color) -> void:
    if root_node == null:
        return
    if root_node is MeshInstance3D:
        var mesh_instance := root_node as MeshInstance3D
        if mesh_instance.mesh != null:
            for surface in range(mesh_instance.mesh.get_surface_count()):
                var base := mesh_instance.get_active_material(surface)
                if base is BaseMaterial3D:
                    var mat := (base as BaseMaterial3D).duplicate() as BaseMaterial3D
                    mat.albedo_color = tint
                    mesh_instance.set_surface_override_material(surface, mat)
    for child in root_node.get_children():
        _apply_model_tint(child, tint)

func _sync_apparel_visuals() -> void:
    if body_model == null or outfit_model == null:
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

    # Exactly one authored body source is visible. This prevents the base body
    # and outfit geometry from occupying the same pixels and looking muddy.
    body_model.visible = not has_clothes
    outfit_model.visible = has_clothes and not use_ranger
    if ranger_model != null:
        ranger_model.visible = has_clothes and use_ranger

    # Ordinary clothing that shares the same Peasant mesh still gets an obvious
    # appearance change by tinting from its visual item IDs.
    var appearance_key := torso + "|" + armor + "|" + legs + "|" + hands + "|" + feet
    var tint := _appearance_color(appearance_key)
    if outfit_model.visible:
        _apply_model_tint(outfit_model, tint)
    if ranger_model != null and ranger_model.visible:
        _apply_model_tint(ranger_model, tint.lightened(0.05))

    if backpack_root != null:
        backpack_root.visible = not back.is_empty()

'''
v = v[:start] + helper + v[end:]

visual.write_text(v, encoding="utf-8")

# Version identity.
preset = root / "export_presets.cfg"
ep = preset.read_text(encoding="utf-8")
ep, n1 = re.subn(r'(?m)^version/code=\d+$', 'version/code=36', ep, count=1)
ep, n2 = re.subn(r'(?m)^version/name="[^"]*"$', 'version/name="0.20.0D3D.7"', ep, count=1)
if not n1 or not n2:
    raise SystemExit("D3D.7 export version fields missing")
preset.write_text(ep, encoding="utf-8")

save = root / "scripts/save/save_manager.gd"
if save.is_file():
    s = save.read_text(encoding="utf-8")
    s, _ = re.subn(r'const GAME_VERSION := "[^"]+"', 'const GAME_VERSION := "0.20.0D3D.7"', s, count=1)
    save.write_text(s, encoding="utf-8")

print("Applied v0.20.0D3D.7: 2x character render resolution, linear filtering, stronger breathing, exclusive body/outfit visibility, and visible apparel changes.")
