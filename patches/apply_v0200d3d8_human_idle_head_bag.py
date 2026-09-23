#!/usr/bin/env python3
"""v0.20.0D3D.8: head restoration, natural idle, color correction, backpack shape, corrected scale."""
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
visual = root / "scripts/art/production_survivor_visual.gd"
v = visual.read_text(encoding="utf-8")

# D3D.7 doubled SubViewport resolution. Compensate sprite scale so apparent world
# size returns close to D3D.6 while keeping the higher internal resolution.
v = v.replace('viewport_sprite.scale = Vector2(0.30, 0.30)', 'viewport_sprite.scale = Vector2(0.15, 0.15)', 1)
v = v.replace(
    'viewport_sprite.scale = Vector2(0.30 * (1.0 - breath * 0.18), 0.30 * (1.0 + breath))',
    'viewport_sprite.scale = Vector2(0.15 * (1.0 - breath * 0.14), 0.15 * (1.0 + breath))',
    1,
)

# More human idle breathing but less whole-body rubber scaling; add vertical chest rise.
v = v.replace(
    'var breath := 0.0 if moving else sin(idle_phase) * 0.026',
    'var breath := 0.0 if moving else sin(idle_phase) * 0.032',
    1,
)
v = v.replace(
    'viewport_sprite.position.y = -3.0 + bob - breath * 11.0 + (1.2 if crouching else 0.0)',
    'viewport_sprite.position.y = -3.0 + bob - breath * 8.0 + (1.2 if crouching else 0.0)',
    1,
)

# Remove the D3D.7 full-mesh tinting path entirely; preserve authored albedo/skin colors.
start = v.find('func _appearance_color(key: String) -> Color:\n')
sync = v.find('func _sync_apparel_visuals() -> void:\n', start)
if start >= 0 and sync > start:
    v = v[:start] + v[sync:]

# Replace apparel sync helper with source-color model switching only.
start = v.find('func _sync_apparel_visuals() -> void:\n')
end = v.find('\nfunc _weapon_category() -> String:\n', start)
if start < 0 or end < 0:
    raise SystemExit('D3D.8 apparel helper missing')
helper = '''func _sync_apparel_visuals() -> void:
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

    body_model.visible = not has_clothes
    outfit_model.visible = has_clothes and not use_ranger
    if ranger_model != null:
        ranger_model.visible = has_clothes and use_ranger
    if backpack_root != null:
        backpack_root.visible = not back.is_empty()

'''
v = v[:start] + helper + v[end:]

# Transfer only the detailed base-character head, eyes and brows onto both outfit
# skeletons. Outfit assets intentionally omit the face.
face_helpers = r'''
func _is_head_vertex(vertex_index: int, joints: PackedInt32Array, weights: PackedFloat32Array, head_bone: int, neck_bone: int) -> bool:
    var strongest_weight := -1.0
    var strongest_bone := -1
    for influence in 4:
        var weight: float = weights[vertex_index * 4 + influence]
        if weight > strongest_weight:
            strongest_weight = weight
            strongest_bone = joints[vertex_index * 4 + influence]
    return strongest_bone == head_bone or strongest_bone == neck_bone

func _extract_head_mesh(source_mesh: Mesh, source_skeleton: Skeleton3D) -> ArrayMesh:
    var source_arrays := source_mesh.surface_get_arrays(0)
    var indices: PackedInt32Array = source_arrays[Mesh.ARRAY_INDEX]
    var joints: PackedInt32Array = source_arrays[Mesh.ARRAY_BONES]
    var weights: PackedFloat32Array = source_arrays[Mesh.ARRAY_WEIGHTS]
    var head_bone := source_skeleton.find_bone("Head")
    var neck_bone := source_skeleton.find_bone("neck_01")
    var head_indices := PackedInt32Array()
    for triangle_start in range(0, indices.size(), 3):
        var a: int = indices[triangle_start]
        var b: int = indices[triangle_start + 1]
        var c: int = indices[triangle_start + 2]
        if _is_head_vertex(a, joints, weights, head_bone, neck_bone) and _is_head_vertex(b, joints, weights, head_bone, neck_bone) and _is_head_vertex(c, joints, weights, head_bone, neck_bone):
            head_indices.append(a)
            head_indices.append(b)
            head_indices.append(c)
    var arrays := []
    arrays.resize(Mesh.ARRAY_MAX)
    arrays[Mesh.ARRAY_VERTEX] = source_arrays[Mesh.ARRAY_VERTEX]
    arrays[Mesh.ARRAY_NORMAL] = source_arrays[Mesh.ARRAY_NORMAL]
    arrays[Mesh.ARRAY_TEX_UV] = source_arrays[Mesh.ARRAY_TEX_UV]
    arrays[Mesh.ARRAY_COLOR] = source_arrays[Mesh.ARRAY_COLOR]
    arrays[Mesh.ARRAY_BONES] = joints
    arrays[Mesh.ARRAY_WEIGHTS] = weights
    arrays[Mesh.ARRAY_INDEX] = head_indices
    var head_mesh := ArrayMesh.new()
    head_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
    head_mesh.surface_set_material(0, source_mesh.surface_get_material(0))
    return head_mesh

func _install_face_on_outfit(target_skeleton: Skeleton3D) -> void:
    if target_skeleton == null or body_skeleton == null:
        return
    if target_skeleton.get_node_or_null("HeadMesh") != null:
        return
    var source_body := body_skeleton.get_node_or_null("SuperHero_Male") as MeshInstance3D
    if source_body == null or source_body.mesh == null:
        return
    var head := MeshInstance3D.new()
    head.name = "HeadMesh"
    head.mesh = _extract_head_mesh(source_body.mesh, body_skeleton)
    head.skin = source_body.skin
    head.skeleton = NodePath("..")
    target_skeleton.add_child(head)
    for feature_name in ["Eyes", "Eyebrows"]:
        var source_feature := body_skeleton.get_node_or_null(NodePath(feature_name)) as MeshInstance3D
        if source_feature == null:
            continue
        var feature := source_feature.duplicate() as MeshInstance3D
        feature.name = feature_name
        feature.skeleton = NodePath("..")
        target_skeleton.add_child(feature)

'''
anchor='func _sync_apparel_visuals() -> void:\n'
if face_helpers.strip() not in v:
    v=v.replace(anchor,face_helpers+anchor,1)

# Install transferred faces immediately after skeleton discovery.
needle='    ranger_skeleton = _find_skeleton(ranger_model)\n    _sync_apparel_visuals()\n'
replacement='    ranger_skeleton = _find_skeleton(ranger_model)\n    _install_face_on_outfit(outfit_skeleton)\n    _install_face_on_outfit(ranger_skeleton)\n    _sync_apparel_visuals()\n'
if needle not in v:
    raise SystemExit('D3D.8 skeleton setup anchor missing')
v=v.replace(needle,replacement,1)

# Armed does not mean actively aiming. Only use the compact two-hand firearm pose
# while the right stick is actually held for aim.
v=v.replace(
    'func _apply_skeleton_pose(armed: bool, moving: bool) -> void:',
    'func _apply_skeleton_pose(armed: bool, moving: bool, aiming: bool = false) -> void:',
    1,
)
v=v.replace(
    '        _apply_skeleton_pose(armed, moving)',
    '        _apply_skeleton_pose(armed, moving, aiming)',
    1,
)

# Introduce aim state next to armed state and make it participate in pose changes.
armed_line='    var armed := _weapon_category() == "firearm"\n'
if armed_line not in v:
    raise SystemExit('D3D.8 armed state anchor missing')
v=v.replace(
    armed_line,
    armed_line + '    var aiming := armed and InputState.mobile_aim_active and InputState.mobile_aim.length_squared() > 0.04\n',
    1,
)
v=v.replace(
    'var _last_armed := false\n',
    'var _last_armed := false\nvar _last_aiming := false\n',
    1,
)
v=v.replace(
    '        armed != _last_armed\n',
    '        armed != _last_armed\n        or aiming != _last_aiming\n',
    1,
)
v=v.replace(
    '    _last_armed = armed\n',
    '    _last_armed = armed\n    _last_aiming = aiming\n',
    1,
)

# Compact firearm stance only while aiming; relax arms naturally otherwise.
v=v.replace('    if armed:\n        _point_bone_fast(skel, "lowerarm_r", "hand_r", Vector3(-0.04, -0.10, 0.99))',
            '    if armed and aiming:\n        _point_bone_fast(skel, "lowerarm_r", "hand_r", Vector3(-0.08, -0.20, 0.975))',1)
v=v.replace(
    '            var grip_target := skel.get_bone_global_pose(r_hand_idx).origin + Vector3(-0.055, -0.015, 0.025)',
    '            var grip_target := skel.get_bone_global_pose(r_hand_idx).origin + Vector3(-0.040, -0.025, 0.015)',
    1,
)

# Idle arm sway/breathing. Right hand carries pistol low; left hand rests closer
# to torso instead of both arms projecting forward.
old='''    else:
        var fore_swing := stride * 0.22 if moving else 0.0
        _point_bone_fast(skel, "lowerarm_l", "hand_l", Vector3(0.03, -0.99, -fore_swing))
        _point_bone_fast(skel, "lowerarm_r", "hand_r", Vector3(-0.03, -0.99, fore_swing))
'''
new='''    else:
        var fore_swing := stride * 0.22 if moving else 0.0
        var idle_sway := sin(idle_phase) * 0.055 if not moving else 0.0
        var idle_sway_b := sin(idle_phase + 0.9) * 0.040 if not moving else 0.0
        _point_bone_fast(skel, "lowerarm_l", "hand_l", Vector3(0.16 + idle_sway * 0.5, -0.96, -0.12 - fore_swing + idle_sway_b))
        _point_bone_fast(skel, "lowerarm_r", "hand_r", Vector3(-0.12 - idle_sway * 0.4, -0.96, 0.14 + fore_swing - idle_sway_b))
'''
if old not in v:
    raise SystemExit('D3D.8 relaxed arm block missing')
v=v.replace(old,new,1)

# Replace any primitive backpack visuals with a rounded, readable backpack shape.
bag_helper=r'''
func _rebuild_backpack_shape() -> void:
    if backpack_root == null:
        return
    for child in backpack_root.get_children():
        if child is VisualInstance3D:
            child.visible = false

    var fabric := StandardMaterial3D.new()
    fabric.albedo_color = Color(0.20, 0.18, 0.14, 1.0)
    fabric.roughness = 0.92

    var trim := StandardMaterial3D.new()
    trim.albedo_color = Color(0.10, 0.09, 0.075, 1.0)
    trim.roughness = 0.88

    var body := MeshInstance3D.new()
    body.name = "BackpackBody"
    var body_mesh := SphereMesh.new()
    body_mesh.radius = 0.22
    body_mesh.height = 0.44
    body.mesh = body_mesh
    body.scale = Vector3(0.82, 1.05, 0.42)
    body.material_override = fabric
    backpack_root.add_child(body)

    var flap := MeshInstance3D.new()
    flap.name = "BackpackFlap"
    var flap_mesh := SphereMesh.new()
    flap_mesh.radius = 0.15
    flap_mesh.height = 0.26
    flap.mesh = flap_mesh
    flap.scale = Vector3(0.82, 0.42, 0.48)
    flap.position = Vector3(0.0, 0.12, 0.035)
    flap.material_override = trim
    backpack_root.add_child(flap)

    for x in [-0.105, 0.105]:
        var strap := MeshInstance3D.new()
        var strap_mesh := BoxMesh.new()
        strap_mesh.size = Vector3(0.035, 0.34, 0.025)
        strap.mesh = strap_mesh
        strap.position = Vector3(x, 0.0, -0.075)
        strap.material_override = trim
        backpack_root.add_child(strap)

'''
anchor='func _update_equipment_3d(armed: bool) -> void:\n'
if anchor not in v:
    raise SystemExit('D3D.8 bag helper anchor missing')
v=v.replace(anchor,bag_helper+anchor,1)

# Invoke once after stage setup.
finish_anchor='    if body_skeleton != null:\n        call_deferred("_finish_rig_setup")\n'
if finish_anchor in v:
    v=v.replace(
        finish_anchor,
        '    if body_skeleton != null:\n        call_deferred("_finish_rig_setup")\n    call_deferred("_rebuild_backpack_shape")\n',
        1,
    )

visual.write_text(v, encoding='utf-8')

# Version identity.
preset=root/'export_presets.cfg'
ep=preset.read_text(encoding='utf-8')
ep,n1=re.subn(r'(?m)^version/code=\d+$','version/code=37',ep,count=1)
ep,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.8"',ep,count=1)
if not n1 or not n2:
    raise SystemExit('D3D.8 export version fields missing')
preset.write_text(ep,encoding='utf-8')

save=root/'scripts/save/save_manager.gd'
if save.is_file():
    s=save.read_text(encoding='utf-8')
    s,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.8"',s,count=1)
    save.write_text(s,encoding='utf-8')

print("Applied v0.20.0D3D.8: restored outfit head/face, natural relaxed armed idle, corrected colors, rounded backpack, and D3D.6-sized high-res character.")
