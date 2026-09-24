#!/usr/bin/env python3
"""D3D.21: male/female reference templates, region-based skin occlusion, larger trees."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

# ---------- Female model sources ----------
const_anchor='''const HAIR_SCENE: PackedScene = preload("res://assets/models/superhero_male/Hair_SimpleParted.gltf")
'''
if const_anchor not in s:
    raise SystemExit("D3D.21 scene constant anchor missing")
s=s.replace(const_anchor,const_anchor+'''const FEMALE_BODY_SCENE: PackedScene = preload("res://assets/models/superhero_male/Superhero_Female_FullBody.gltf")
const FEMALE_OUTFIT_SCENE: PackedScene = preload("res://assets/models/superhero_male/Female_Peasant.gltf")
const FEMALE_RANGER_SCENE: PackedScene = preload("res://assets/models/superhero_male/Female_Ranger.gltf")
''',1)

state_anchor='''var gear_layers: Dictionary = {}
var gear_ids: Dictionary = {}
'''
if state_anchor not in s:
    raise SystemExit("D3D.21 skin region state anchor missing")
s=s.replace(state_anchor,state_anchor+'var skin_regions: Dictionary = {}\n',1)

# Runtime body switching must rebuild the small reference renderer.
old_set='''func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"
'''
new_set='''func set_body_type(value: String) -> void:
    var next_type := "female" if value == "female" else "male"
    if body_type == next_type:
        return
    body_type = next_type
    if viewport != null and is_instance_valid(viewport):
        remove_child(viewport)
        viewport.queue_free()
    viewport = null
    viewport_sprite = null
    world_root = null
    actor_root = null
    body_model = null
    outfit_model = null
    ranger_model = null
    body_skeleton = null
    outfit_skeleton = null
    ranger_skeleton = null
    camera = null
    gun_root = null
    pistol_hand_socket = null
    backpack_root = null
    gear_layers.clear()
    gear_ids.clear()
    skin_regions.clear()
    _rig_ready = false
    _pose_dirty = true
    _last_render_facing = Vector2(999.0,999.0)
    _ensure_3d_stage()
'''
if old_set not in s:
    raise SystemExit("D3D.21 set_body_type anchor missing")
s=s.replace(old_set,new_set,1)
s=s.replace('''func is_supported_visual() -> bool:
    return body_type == "male"
''','''func is_supported_visual() -> bool:
    return body_type == "male" or body_type == "female"
''',1)

# Dynamic male/female scene selection and a modest female scale reduction.
old_models='''    actor_root = Node3D.new()
    actor_root.name = "SurvivorActor3D"
    actor_root.scale = Vector3(1.085, 1.020, 1.085)
    world_root.add_child(actor_root)

    # Full base body restores the missing head/face. Peasant is retained as the
    # visible clothing layer; both skeletons receive the same compact pose pass.
    body_model = BODY_SCENE.instantiate()
    body_model.name = "SurvivorBody"
    actor_root.add_child(body_model)
    outfit_model = OUTFIT_SCENE.instantiate()
    outfit_model.name = "SurvivorPeasantOutfit"
    actor_root.add_child(outfit_model)
    ranger_model = RANGER_SCENE.instantiate()
    ranger_model.name = "SurvivorRangerOutfit"
    ranger_model.scale = Vector3(1.115, 1.035, 1.115)
    ranger_model.visible = false
    actor_root.add_child(ranger_model)
'''
new_models='''    actor_root = Node3D.new()
    actor_root.name = "SurvivorActor3D"
    actor_root.scale = Vector3(1.035,0.975,1.035) if body_type == "female" else Vector3(1.085,1.020,1.085)
    world_root.add_child(actor_root)

    var selected_body: PackedScene = FEMALE_BODY_SCENE if body_type == "female" else BODY_SCENE
    var selected_outfit: PackedScene = FEMALE_OUTFIT_SCENE if body_type == "female" else OUTFIT_SCENE
    var selected_ranger: PackedScene = FEMALE_RANGER_SCENE if body_type == "female" else RANGER_SCENE

    body_model = selected_body.instantiate()
    body_model.name = "SurvivorBody"
    actor_root.add_child(body_model)
    outfit_model = selected_outfit.instantiate()
    outfit_model.name = "SurvivorPeasantOutfit"
    actor_root.add_child(outfit_model)
    ranger_model = selected_ranger.instantiate()
    ranger_model.name = "SurvivorRangerOutfit"
    ranger_model.visible = false
    actor_root.add_child(ranger_model)
'''
if old_models not in s:
    raise SystemExit("D3D.21 model setup anchor missing")
s=s.replace(old_models,new_models,1)

# Generic source body names for both Quaternius body models.
old_source='''    var source_body := body_skeleton.get_node_or_null("SuperHero_Male") as MeshInstance3D
'''
new_source='''    var source_name := "Superhero_Female" if body_type == "female" else "SuperHero_Male"
    var source_body := body_skeleton.get_node_or_null(source_name) as MeshInstance3D
'''
if old_source not in s:
    raise SystemExit("D3D.21 face source anchor missing")
s=s.replace(old_source,new_source,1)

# ---------- Body-region mesh extraction ----------
sync_anchor='func _sync_apparel_visuals() -> void:\n'
if sync_anchor not in s:
    raise SystemExit("D3D.21 apparel insertion anchor missing")
segment_helpers=r'''func _source_body_mesh() -> MeshInstance3D:
    if body_skeleton == null:
        return null
    var source_name := "Superhero_Female" if body_type == "female" else "SuperHero_Male"
    return body_skeleton.get_node_or_null(source_name) as MeshInstance3D

func _vertex_body_region(vertex_index: int, joints: PackedInt32Array, weights: PackedFloat32Array) -> String:
    var strongest_weight := -1.0
    var strongest_bone := -1
    for influence in 4:
        var weight: float = weights[vertex_index * 4 + influence]
        if weight > strongest_weight:
            strongest_weight = weight
            strongest_bone = joints[vertex_index * 4 + influence]
    if strongest_bone < 0 or body_skeleton == null:
        return "torso"
    var bone := String(body_skeleton.get_bone_name(strongest_bone))
    if bone == "Head" or bone == "neck_01":
        return "head"
    if bone == "root" or bone == "pelvis":
        return "hips"
    if bone.begins_with("spine_") or bone.begins_with("clavicle_"):
        return "torso"
    if bone.begins_with("upperarm_"):
        return "upperarms"
    if bone.begins_with("lowerarm_"):
        return "forearms"
    if bone.begins_with("hand_") or bone.begins_with("index_") or bone.begins_with("middle_") or bone.begins_with("ring_") or bone.begins_with("pinky_") or bone.begins_with("thumb_"):
        return "hands"
    if bone.begins_with("thigh_") or bone.begins_with("calf_"):
        return "legs"
    if bone.begins_with("foot_") or bone.begins_with("ball_"):
        return "feet"
    return "torso"

func _extract_body_region_mesh(source_mesh: Mesh, target_region: String) -> ArrayMesh:
    var source_arrays := source_mesh.surface_get_arrays(0)
    var indices: PackedInt32Array = source_arrays[Mesh.ARRAY_INDEX]
    var joints: PackedInt32Array = source_arrays[Mesh.ARRAY_BONES]
    var weights: PackedFloat32Array = source_arrays[Mesh.ARRAY_WEIGHTS]
    var region_indices := PackedInt32Array()
    for triangle_start in range(0,indices.size(),3):
        var a: int = indices[triangle_start]
        var b: int = indices[triangle_start+1]
        var c: int = indices[triangle_start+2]
        var matches := 0
        if _vertex_body_region(a,joints,weights) == target_region: matches += 1
        if _vertex_body_region(b,joints,weights) == target_region: matches += 1
        if _vertex_body_region(c,joints,weights) == target_region: matches += 1
        if matches >= 2:
            region_indices.append(a)
            region_indices.append(b)
            region_indices.append(c)
    var arrays := []
    arrays.resize(Mesh.ARRAY_MAX)
    arrays[Mesh.ARRAY_VERTEX] = source_arrays[Mesh.ARRAY_VERTEX]
    arrays[Mesh.ARRAY_NORMAL] = source_arrays[Mesh.ARRAY_NORMAL]
    arrays[Mesh.ARRAY_TEX_UV] = source_arrays[Mesh.ARRAY_TEX_UV]
    arrays[Mesh.ARRAY_COLOR] = source_arrays[Mesh.ARRAY_COLOR]
    arrays[Mesh.ARRAY_BONES] = joints
    arrays[Mesh.ARRAY_WEIGHTS] = weights
    arrays[Mesh.ARRAY_INDEX] = region_indices
    var result := ArrayMesh.new()
    result.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
    result.surface_set_material(0,source_mesh.surface_get_material(0))
    return result

func _ensure_skin_regions() -> void:
    skin_regions.clear()
    var source := _source_body_mesh()
    if source == null or source.mesh == null or body_skeleton == null:
        return
    for region in ["head","torso","hips","upperarms","forearms","hands","legs","feet"]:
        var part := MeshInstance3D.new()
        part.name = "SkinRegion_" + region
        part.mesh = _extract_body_region_mesh(source.mesh,region)
        part.skin = source.skin
        part.skeleton = NodePath("..")
        part.visible = false
        body_skeleton.add_child(part)
        skin_regions[region] = part

func _set_skin_region(region: String, show: bool) -> void:
    var part: Variant = skin_regions.get(region)
    if part is MeshInstance3D:
        (part as MeshInstance3D).visible = show

func _scale_wearable_part(model: Node3D, node_name: String, scale_value: Vector3) -> void:
    if model == null:
        return
    var part := model.find_child(node_name,true,false)
    if part is MeshInstance3D:
        (part as MeshInstance3D).scale = scale_value

'''
s=s.replace(sync_anchor,segment_helpers+sync_anchor,1)

# Install regions once the body skeleton exists.
setup_anchor='''    ranger_skeleton = _find_skeleton(ranger_model)
    _install_face_on_outfit(outfit_skeleton)
'''
if setup_anchor not in s:
    raise SystemExit("D3D.21 skin setup anchor missing")
s=s.replace(setup_anchor,'''    ranger_skeleton = _find_skeleton(ranger_model)
    _ensure_skin_regions()
    _install_face_on_outfit(outfit_skeleton)
''',1)

# Replace slot visualization with dynamic male/female part names and per-region occlusion.
sync_a=s.find("func _sync_apparel_visuals() -> void:\n")
sync_b=s.find("\nfunc _weapon_category() -> String:\n",sync_a)
if sync_a<0 or sync_b<0:
    raise SystemExit("D3D.21 apparel bounds missing")
new_sync=r'''func _sync_apparel_visuals() -> void:
    if body_model == null:
        return
    for slot in gear_layers.keys():
        for primitive in gear_layers[slot]:
            if primitive is Node3D:
                (primitive as Node3D).visible = false
    if ranger_model == null or outfit_model == null:
        return

    var is_female := body_type == "female"
    outfit_model.scale = Vector3(1.065,1.00,1.065) if is_female else Vector3(1.11,1.015,1.11)
    ranger_model.scale = Vector3(1.06,0.995,1.06) if is_female else Vector3(1.105,1.000,1.105)
    var ranger_prefix := "Female_Ranger_" if is_female else "Male_Ranger_"
    var peasant_prefix := "Female_Peasant_" if is_female else "Male_Peasant_"

    var equipped: Dictionary = {}
    for slot in ["torso","armor","hands","legs","feet","head","eyes","lower_face","back"]:
        equipped[slot] = String(equipment.get_visual_item(slot)) if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item") else ""
    var shirt := not String(equipped["torso"]).is_empty()
    var armor := not String(equipped["armor"]).is_empty()
    var gloves := not String(equipped["hands"]).is_empty()
    var trousers := not String(equipped["legs"]).is_empty()
    var boots := not String(equipped["feet"]).is_empty()

    var source := _source_body_mesh()
    var segmented := shirt or gloves or trousers or boots
    if source != null:
        source.visible = not segmented
    for region in skin_regions.keys():
        _set_skin_region(String(region),false)
    if segmented:
        _set_skin_region("head",true)
        _set_skin_region("torso",not shirt)
        _set_skin_region("hips",not (shirt or trousers))
        _set_skin_region("upperarms",not shirt)
        _set_skin_region("forearms",not shirt)
        _set_skin_region("hands",not gloves)
        _set_skin_region("legs",not trousers)
        _set_skin_region("feet",not boots)

    ranger_model.visible = shirt or armor or gloves or boots
    outfit_model.visible = shirt or trousers
    _set_rigged_part(ranger_prefix+"Body",shirt)
    _set_rigged_part(ranger_prefix+"Arms",false)
    _set_rigged_part(ranger_prefix+("Feet" if is_female else "Feet_Boots"),boots)
    _set_rigged_part(ranger_prefix+"Legs",false)
    _set_rigged_part(ranger_prefix+"Arms_Bracer",gloves)
    _set_rigged_part(ranger_prefix+("Acc_Pauldrons" if is_female else "Acc_Pauldron"),armor)
    _set_rigged_part(ranger_prefix+"Body_Belt_1",armor)
    _set_rigged_part(ranger_prefix+"Body_Belt_2",false)
    _set_rigged_part(ranger_prefix+"Head_Hood",false)

    for suffix in ["Arms","Body","Feet","Legs"]:
        var part := outfit_model.find_child(peasant_prefix+suffix,true,false)
        if part is MeshInstance3D:
            (part as MeshInstance3D).visible = (
                (suffix == "Arms" and shirt)
                or (suffix == "Legs" and trousers)
            )

    # Small per-piece shell margin prevents skin z-fighting without inflating
    # the complete character or collar/head.
    _scale_wearable_part(ranger_model,ranger_prefix+"Body",Vector3(1.025,1.01,1.025))
    _scale_wearable_part(ranger_model,ranger_prefix+("Feet" if is_female else "Feet_Boots"),Vector3(1.035,1.02,1.035))
    _scale_wearable_part(ranger_model,ranger_prefix+"Arms_Bracer",Vector3(1.04,1.02,1.04))
    _scale_wearable_part(outfit_model,peasant_prefix+"Arms",Vector3(1.03,1.01,1.03))
    _scale_wearable_part(outfit_model,peasant_prefix+"Legs",Vector3(1.025,1.01,1.025))

    # Face copies on clothing rigs are unnecessary now: the segmented body head
    # stays visible whenever the base body shell is occluded.
    for skel in [ranger_skeleton,outfit_skeleton]:
        if skel == null:
            continue
        for extra in ["HeadMesh","Eyes","Eyebrows","SurvivorHair"]:
            var duplicate: Node = skel.get_node_or_null(extra)
            if duplicate is Node3D:
                (duplicate as Node3D).visible = false
    if backpack_root != null:
        backpack_root.visible = not String(equipped["back"]).is_empty()
'''
s=s[:sync_a]+new_sync+s[sync_b:]

# Generic fantasy-part hiding helper.
hide_a=s.find("func _hide_ranger_fantasy_parts() -> void:\n")
hide_b=s.find("\nfunc ",hide_a+6)
if hide_a>=0 and hide_b>hide_a:
    new_hide=r'''func _hide_ranger_fantasy_parts() -> void:
    if ranger_model == null:
        return
    var prefix := "Female_Ranger_" if body_type == "female" else "Male_Ranger_"
    var names := [
        prefix+"Head_Hood",
        prefix+("Acc_Pauldrons" if body_type == "female" else "Acc_Pauldron"),
        prefix+"Arms_Bracer",
        prefix+"Body_Belt_2",
    ]
    for node_name in names:
        var part := ranger_model.find_child(node_name,true,false)
        if part is Node3D:
            (part as Node3D).visible = false
'''
    s=s[:hide_a]+new_hide+s[hide_b:]

visual.write_text(s,encoding="utf-8")

# ---------- Temporary male/female template test control ----------
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.20  |  TACTICAL GRIP"' not in h:
    raise SystemExit("D3D.21 build stamp anchor missing")
h=h.replace('marker.text = "D3D.20  |  TACTICAL GRIP"','marker.text = "D3D.21  |  MALE/FEMALE TEMPLATES"',1)
stamp_end='''    add_child(marker)
'''
idx=h.find(stamp_end,h.find("func _add_d3d16_build_stamp"))
if idx<0:
    raise SystemExit("D3D.21 stamp add_child anchor missing")
idx2=idx+len(stamp_end)
h=h[:idx2]+'    call_deferred("_add_body_template_toggle")\n'+h[idx2:]
toggle=r'''
func _add_body_template_toggle() -> void:
    if has_node("BodyTemplateToggle"):
        return
    var button := Button.new()
    button.name = "BodyTemplateToggle"
    button.text = "BODY: MALE"
    button.position = Vector2(maxf(12.0,get_viewport().get_visible_rect().size.x * 0.204),108.0)
    button.size = Vector2(150,38)
    button.add_theme_font_size_override("font_size",14)
    button.pressed.connect(_toggle_body_template)
    add_child(button)

func _toggle_body_template() -> void:
    var player := get_parent().get_node_or_null("Player")
    var button := get_node_or_null("BodyTemplateToggle") as Button
    if player == null or not player.has_method("set_body_type"):
        return
    var current := String(player.get("body_type"))
    var next := "female" if current != "female" else "male"
    player.call("set_body_type",next)
    if button != null:
        button.text = "BODY: FEMALE" if next == "female" else "BODY: MALE"

'''
build_anchor="func _build_ui() -> void:\n"
if build_anchor not in h:
    raise SystemExit("D3D.21 HUD function anchor missing")
h=h.replace(build_anchor,toggle+build_anchor,1)
hud.write_text(h,encoding="utf-8")

# ---------- Larger trees ----------
world=root/"scripts/world/world_chunk.gd"
w=world.read_text(encoding="utf-8")
for old,new in [
    ('var canopy_center := p + Vector2(0, -37)','var canopy_center := p + Vector2(0, -49)'),
    ('var canopy_center: Vector2 = p + Vector2(0, -37)','var canopy_center: Vector2 = p + Vector2(0, -49)'),
    (' / 38.0',' / 50.0'),
    (' / 43.0',' / 57.0'),
    ('Rect2(p - Vector2(40, 7), Vector2(80, 40))','Rect2(p - Vector2(53, 20), Vector2(106, 53))'),
]:
    if old not in w:
        raise SystemExit("D3D.21 tree world anchor missing "+old)
    w=w.replace(old,new)
world.write_text(w,encoding="utf-8")

overlay=root/"scripts/world/tree_canopy_overlay.gd"
o=overlay.read_text(encoding="utf-8")
old='draw_texture_rect_region(PROPS_ATLAS, Rect2(p - Vector2(40, 79), Vector2(80, 84)), source)'
new='draw_texture_rect_region(PROPS_ATLAS, Rect2(p - Vector2(53, 106), Vector2(106, 111)), source)'
if old not in o:
    raise SystemExit("D3D.21 canopy overlay anchor missing")
overlay.write_text(o.replace(old,new,1),encoding="utf-8")

natural=root/"scripts/ecology/natural_resource.gd"
n=natural.read_text(encoding="utf-8")
old='''    if _tree_trunk_sprite == null or not is_instance_valid(_tree_trunk_sprite):
        _tree_trunk_sprite = _make_tree_part(Rect2(0, 72, 80, 40), Vector2(0, 13), 0)
    if _tree_canopy_sprite == null or not is_instance_valid(_tree_canopy_sprite):
        _tree_canopy_sprite = _make_tree_part(Rect2(0, 0, 80, 84), Vector2(0, -37), 30)
'''
new='''    if _tree_trunk_sprite == null or not is_instance_valid(_tree_trunk_sprite):
        _tree_trunk_sprite = _make_tree_part(Rect2(0,72,80,40),Vector2(0,6),0)
        _tree_trunk_sprite.scale = Vector2(1.325,1.325)
    if _tree_canopy_sprite == null or not is_instance_valid(_tree_canopy_sprite):
        _tree_canopy_sprite = _make_tree_part(Rect2(0,0,80,84),Vector2(0,-49),30)
        _tree_canopy_sprite.scale = Vector2(1.325,1.325)
'''
if old not in n:
    raise SystemExit("D3D.21 resource tree anchor missing")
natural.write_text(n.replace(old,new,1),encoding="utf-8")

# ---------- Version ----------
preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=50',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.21"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.21 version anchors missing")
preset.write_text(p,encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.21"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.21: female reference template, per-slot segmented skin occlusion, template toggle, and ~32% larger trees.")
