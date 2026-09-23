#!/usr/bin/env python3
"""v0.20.0D3D.9: natural two-hand pistol rig, modern outfit, hair/backpack, UNEQUIP UI."""
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

# ---------------------------------------------------------------------------
# Production 3D survivor
# ---------------------------------------------------------------------------
visual = root / "scripts/art/production_survivor_visual.gd"
v = visual.read_text(encoding="utf-8")

# Compatible hair asset fetched by CI.
if 'const HAIR_SCENE:' not in v:
    v = v.replace(
        'const RANGER_SCENE: PackedScene = preload("res://assets/models/superhero_male/Male_Ranger.gltf")\n',
        'const RANGER_SCENE: PackedScene = preload("res://assets/models/superhero_male/Male_Ranger.gltf")\n'
        'const HAIR_SCENE: PackedScene = preload("res://assets/models/superhero_male/Hair_SimpleParted.gltf")\n',
        1,
    )

# Continuous aim-extension state.
v = v.replace(
    'var _active_aiming := false\n',
    'var _active_aiming := false\nvar _aim_extension := 0.0\n',
    1,
)

# Hair helpers before apparel sync.
hair_helper = r'''
func _install_hair_on_skeleton(target_skeleton: Skeleton3D) -> void:
    if target_skeleton == null or target_skeleton.get_node_or_null("SurvivorHair") != null:
        return
    var source_root := HAIR_SCENE.instantiate() as Node3D
    if source_root == null:
        return
    var source_hair := source_root.find_child("Hair_SimpleParted", true, false) as MeshInstance3D
    if source_hair != null:
        var hair := source_hair.duplicate() as MeshInstance3D
        hair.name = "SurvivorHair"
        hair.skeleton = NodePath("..")
        target_skeleton.add_child(hair)
    source_root.free()

func _hide_ranger_fantasy_parts() -> void:
    if ranger_model == null:
        return
    for node_name in [
        "Male_Ranger_Head_Hood",
        "Male_Ranger_Acc_Pauldron",
        "Male_Ranger_Arms_Bracer",
        "Male_Ranger_Body_Belt_2",
    ]:
        var part := ranger_model.find_child(node_name, true, false)
        if part is Node3D:
            (part as Node3D).visible = false

'''
anchor='func _sync_apparel_visuals() -> void:\n'
if anchor not in v:
    raise SystemExit("D3D.9 apparel anchor missing")
if 'func _install_hair_on_skeleton' not in v:
    v=v.replace(anchor,hair_helper+anchor,1)

# Install hair after face transfer.
needle='    _install_face_on_outfit(outfit_skeleton)\n    _install_face_on_outfit(ranger_skeleton)\n    _sync_apparel_visuals()\n'
replacement='    _install_face_on_outfit(outfit_skeleton)\n    _install_face_on_outfit(ranger_skeleton)\n    _install_hair_on_skeleton(body_skeleton)\n    _install_hair_on_skeleton(outfit_skeleton)\n    _install_hair_on_skeleton(ranger_skeleton)\n    _hide_ranger_fantasy_parts()\n    _sync_apparel_visuals()\n'
if needle not in v:
    raise SystemExit("D3D.9 face/hair install anchor missing")
v=v.replace(needle,replacement,1)

# Modern player clothing: never use the Peasant silhouette. Ranger base is used
# for clothing, with fantasy hood/pauldron/bracers hidden.
start=v.find('func _sync_apparel_visuals() -> void:\n')
end=v.find('\nfunc _weapon_category() -> String:\n',start)
if start<0 or end<0:
    raise SystemExit("D3D.9 apparel function bounds missing")
apparel='''func _sync_apparel_visuals() -> void:
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

    var has_clothes := (
        not torso.is_empty()
        or not armor.is_empty()
        or not legs.is_empty()
        or not hands.is_empty()
        or not feet.is_empty()
    )
    body_model.visible = not has_clothes
    outfit_model.visible = false
    if ranger_model != null:
        ranger_model.visible = has_clothes
    if backpack_root != null:
        backpack_root.visible = not back.is_empty()

'''
v=v[:start]+apparel+v[end:]

# Replace the arm/hand section of the pose function, retaining leg logic.
pose_start=v.find('func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n')
pose_end=v.find('\nfunc _rebuild_backpack_shape() -> void:\n',pose_start)
if pose_start<0 or pose_end<0:
    raise SystemExit("D3D.9 pose function bounds missing")

pose_func=r'''func _curl_pistol_hand(skel: Skeleton3D, side: String) -> void:
    var curls := {
        "01": -0.55,
        "02": -0.72,
        "03": -0.50,
    }
    for finger in ["index", "middle", "ring", "pinky"]:
        for joint in curls.keys():
            var idx := skel.find_bone("%s_%s_%s" % [finger, joint, side])
            if idx < 0:
                continue
            var base_q := skel.get_bone_pose_rotation(idx)
            var curl_q := Quaternion(Vector3.RIGHT, float(curls[joint]))
            skel.set_bone_pose_rotation(idx, base_q * curl_q)
    var thumb := skel.find_bone("thumb_02_%s" % side)
    if thumb >= 0:
        var tq := skel.get_bone_pose_rotation(thumb)
        skel.set_bone_pose_rotation(thumb, tq * Quaternion(Vector3.RIGHT, -0.34))

func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:
    skel.reset_bone_poses()
    skel.force_update_all_bone_transforms()

    var wave := sin(gait_phase)
    var stride := (0.44 if sprinting else (0.22 if crouching else 0.34)) * wave

    if moving:
        _point_bone_fast(skel, "thigh_l", "calf_l", Vector3(0.0, -0.90, stride))
        _point_bone_fast(skel, "thigh_r", "calf_r", Vector3(0.0, -0.90, -stride))
    elif crouching:
        _point_bone_fast(skel, "thigh_l", "calf_l", Vector3(0.0, -0.92, 0.26))
        _point_bone_fast(skel, "thigh_r", "calf_r", Vector3(0.0, -0.92, 0.26))

    if armed:
        # Low-ready -> aimed pose. Elbows stay slightly out from the ribs and
        # forearms converge inward, preventing backward elbow inversion.
        var ext := clampf(_aim_extension, 0.0, 1.0)
        var breath_sway := sin(idle_phase) * 0.022 if not moving else 0.0
        var r_upper_low := Vector3(-0.40, -0.58 + breath_sway, 0.70)
        var l_upper_low := Vector3(0.40, -0.58 + breath_sway, 0.70)
        var r_upper_aim := Vector3(-0.27, -0.38, 0.885)
        var l_upper_aim := Vector3(0.27, -0.38, 0.885)
        _point_bone_fast(skel, "upperarm_r", "lowerarm_r", r_upper_low.lerp(r_upper_aim, ext).normalized())
        _point_bone_fast(skel, "upperarm_l", "lowerarm_l", l_upper_low.lerp(l_upper_aim, ext).normalized())
    else:
        var arm_swing := stride * 0.72 if moving else 0.0
        var idle_arm := sin(idle_phase) * 0.025 if not moving else 0.0
        _point_bone_fast(skel, "upperarm_l", "lowerarm_l", Vector3(-0.07 + idle_arm, -0.99, -arm_swing))
        _point_bone_fast(skel, "upperarm_r", "lowerarm_r", Vector3(0.07 - idle_arm, -0.99, arm_swing))

    skel.force_update_all_bone_transforms()

    if moving:
        var l_knee := 0.20 + maxf(0.0, -wave) * 0.30
        var r_knee := 0.20 + maxf(0.0, wave) * 0.30
        _point_bone_fast(skel, "calf_l", "foot_l", Vector3(0.0, -0.96, -l_knee))
        _point_bone_fast(skel, "calf_r", "foot_r", Vector3(0.0, -0.96, -r_knee))
    elif crouching:
        _point_bone_fast(skel, "calf_l", "foot_l", Vector3(0.0, -0.95, -0.26))
        _point_bone_fast(skel, "calf_r", "foot_r", Vector3(0.0, -0.95, -0.26))

    if armed:
        var ext := clampf(_aim_extension, 0.0, 1.0)
        var hand_breath := sin(idle_phase + 0.35) * 0.025 if not moving else 0.0
        # Right forearm converges inward from the right elbow. It remains bent
        # even at full aim instead of locking straight.
        var r_fore_low := Vector3(0.24, -0.42 + hand_breath, 0.875)
        var r_fore_aim := Vector3(0.14, -0.16, 0.977)
        _point_bone_fast(skel, "lowerarm_r", "hand_r", r_fore_low.lerp(r_fore_aim, ext).normalized())
        skel.force_update_all_bone_transforms()

        # Support hand stays on the pistol throughout low-ready and aiming.
        var r_hand_idx := skel.find_bone("hand_r")
        if r_hand_idx >= 0:
            var support_offset := Vector3(-0.030, -0.018, 0.010).lerp(Vector3(-0.044, -0.018, 0.018), ext)
            var grip_target := skel.get_bone_global_pose(r_hand_idx).origin + support_offset
            _point_bone_to_target(skel, "lowerarm_l", "hand_l", grip_target)

        _curl_pistol_hand(skel, "r")
        _curl_pistol_hand(skel, "l")
    else:
        var fore_swing := stride * 0.22 if moving else 0.0
        var idle_sway := sin(idle_phase) * 0.040 if not moving else 0.0
        _point_bone_fast(skel, "lowerarm_l", "hand_l", Vector3(0.08, -0.99, -fore_swing + idle_sway))
        _point_bone_fast(skel, "lowerarm_r", "hand_r", Vector3(-0.08, -0.99, fore_swing - idle_sway))

    skel.force_update_all_bone_transforms()
'''
v=v[:pose_start]+pose_func+v[pose_end:]

# Replace D3D.8 backpack with a clearly readable field backpack: rectangular
# canvas body, top flap, front pouch and side pockets. Straps sit behind the bag.
bag_start=v.find('func _rebuild_backpack_shape() -> void:\n')
bag_end=v.find('\nfunc _update_equipment_3d(armed: bool) -> void:\n',bag_start)
if bag_start<0 or bag_end<0:
    raise SystemExit("D3D.9 backpack function bounds missing")
bag_func=r'''func _rebuild_backpack_shape() -> void:
    if backpack_root == null:
        return
    for child in backpack_root.get_children():
        if child is VisualInstance3D:
            child.visible = false

    var canvas := StandardMaterial3D.new()
    canvas.albedo_color = Color(0.20, 0.25, 0.18, 1.0)
    canvas.roughness = 0.94
    var trim := StandardMaterial3D.new()
    trim.albedo_color = Color(0.11, 0.13, 0.10, 1.0)
    trim.roughness = 0.90

    var body := MeshInstance3D.new()
    body.name = "BackpackBody"
    var body_mesh := BoxMesh.new()
    body_mesh.size = Vector3(0.34, 0.40, 0.16)
    body.mesh = body_mesh
    body.position = Vector3(0.0, -0.015, 0.0)
    body.material_override = canvas
    backpack_root.add_child(body)

    var flap := MeshInstance3D.new()
    flap.name = "BackpackTopFlap"
    var flap_mesh := BoxMesh.new()
    flap_mesh.size = Vector3(0.30, 0.10, 0.045)
    flap.mesh = flap_mesh
    flap.position = Vector3(0.0, 0.155, 0.095)
    flap.rotation_degrees.x = -10.0
    flap.material_override = trim
    backpack_root.add_child(flap)

    var pocket := MeshInstance3D.new()
    pocket.name = "BackpackFrontPocket"
    var pocket_mesh := BoxMesh.new()
    pocket_mesh.size = Vector3(0.24, 0.17, 0.075)
    pocket.mesh = pocket_mesh
    pocket.position = Vector3(0.0, -0.075, 0.115)
    pocket.material_override = canvas
    backpack_root.add_child(pocket)

    for x in [-0.205, 0.205]:
        var side_pocket := MeshInstance3D.new()
        var side_mesh := BoxMesh.new()
        side_mesh.size = Vector3(0.075, 0.18, 0.11)
        side_pocket.mesh = side_mesh
        side_pocket.position = Vector3(x, -0.055, 0.015)
        side_pocket.material_override = canvas
        backpack_root.add_child(side_pocket)

    # Shoulder straps stay close to the back so they read as straps, not bars.
    for x in [-0.105, 0.105]:
        var strap := MeshInstance3D.new()
        var strap_mesh := BoxMesh.new()
        strap_mesh.size = Vector3(0.035, 0.31, 0.018)
        strap.mesh = strap_mesh
        strap.position = Vector3(x, 0.005, -0.095)
        strap.rotation_degrees.z = 7.0 * signf(x)
        strap.material_override = trim
        backpack_root.add_child(strap)
'''
v=v[:bag_start]+bag_func+v[bag_end:]

# Aim-stick magnitude drives gradual extension, and an armed idle updates each
# frame so breathing propagates through shoulders/elbows/hands.
old='''    var armed := _weapon_category() == "firearm"
    var aiming := armed and InputState.mobile_aim_active and InputState.mobile_aim.length_squared() > 0.04
    _active_aiming = aiming
'''
new='''    var armed := _weapon_category() == "firearm"
    var raw_aim := InputState.mobile_aim.length() if InputState.mobile_aim_active else 0.0
    _aim_extension = clampf((raw_aim - 0.18) / 0.82, 0.0, 1.0) if armed else 0.0
    var aiming := armed and _aim_extension > 0.02
    _active_aiming = aiming
'''
if old not in v:
    raise SystemExit("D3D.9 aim-state block missing")
v=v.replace(old,new,1)
v=v.replace(
    'var need_pose := _rig_ready and (moving or _pose_dirty or state_changed or melee_time > 0.0)',
    'var need_pose := _rig_ready and (moving or armed or _pose_dirty or state_changed or melee_time > 0.0)',
    1,
)

visual.write_text(v,encoding="utf-8")

# ---------------------------------------------------------------------------
# BAG UNEQUIP button
# ---------------------------------------------------------------------------
mobile=root/"scripts/mobile_hud.gd"
m=mobile.read_text(encoding="utf-8")

# Declare the button near existing inventory action vars if possible.
if 'var inventory_unequip_button: Button' not in m:
    decl_match=re.search(r'(?m)^var inventory_use_button: Button\s*$',m)
    if decl_match:
        insert=decl_match.end()
        m=m[:insert]+'\nvar inventory_unequip_button: Button'+m[insert:]
    else:
        # Stable class-level fallback.
        first_func=m.find('\nfunc _ready()')
        if first_func<0:
            raise SystemExit("D3D.9 mobile HUD declaration anchor missing")
        m=m[:first_func]+'\nvar inventory_unequip_button: Button\n'+m[first_func:]

# Install overlay action after UI creation; no dependency on the historical
# layout container structure.
m=m.replace(
    '    _build_ui()\n    _apply_text_scale(self)\n',
    '    _build_ui()\n    _install_inventory_unequip_button()\n    _apply_text_scale(self)\n',
    1,
)

bag_ui=r'''
func _install_inventory_unequip_button() -> void:
    if inventory_panel == null or inventory_unequip_button != null:
        return
    inventory_unequip_button = Button.new()
    inventory_unequip_button.text = "UNEQUIP"
    inventory_unequip_button.focus_mode = Control.FOCUS_NONE
    inventory_unequip_button.custom_minimum_size = Vector2(100, 38)
    inventory_unequip_button.anchor_left = 1.0
    inventory_unequip_button.anchor_top = 1.0
    inventory_unequip_button.anchor_right = 1.0
    inventory_unequip_button.anchor_bottom = 1.0
    inventory_unequip_button.offset_left = -116.0
    inventory_unequip_button.offset_top = -48.0
    inventory_unequip_button.offset_right = -10.0
    inventory_unequip_button.offset_bottom = -8.0
    inventory_unequip_button.z_index = 20
    UIManager.decorate_button(inventory_unequip_button, "UNEQUIP")
    inventory_unequip_button.pressed.connect(_unequip_selected_inventory_item)
    inventory_panel.add_child(inventory_unequip_button)

func _unequip_selected_inventory_item() -> void:
    var player := get_parent().get_node_or_null("Player")
    if player == null or player.inventory.stacks.is_empty():
        _show_message("No wearable item selected.")
        return
    _inventory_use_index = clampi(_inventory_use_index, 0, player.inventory.stacks.size() - 1)
    var item_id := String(player.inventory.stacks[_inventory_use_index].get("id", ""))
    var slot := ItemDatabase.get_equipment_slot(item_id)
    if slot.is_empty():
        _show_message("%s is not wearable." % ItemDatabase.get_display_name(item_id))
        return

    var changed := false
    if player.equipment.get_equipped(slot) == item_id:
        player.equipment.unequip_wearable(slot)
        changed = true

    # If this inventory item is currently supplying only the cosmetic override,
    # clear that look as well so the visual test is unambiguous.
    if player.equipment.get_visual_item(slot) == item_id and player.equipment.get_equipped(slot) != item_id:
        player.equipment.set_transmog(slot, "", player.inventory)
        changed = true

    if changed:
        _show_message("Unequipped %s." % ItemDatabase.get_display_name(item_id))
        player.queue_redraw()
    else:
        _show_message("%s is not currently equipped." % ItemDatabase.get_display_name(item_id))
    _refresh_inventory()

'''
ready_anchor='func _refresh_inventory() -> void:\n'
if ready_anchor not in m:
    raise SystemExit("D3D.9 inventory refresh anchor missing")
if 'func _install_inventory_unequip_button' not in m:
    m=m.replace(ready_anchor,bag_ui+ready_anchor,1)

# Enable/disable based on selected wearable state.
refresh_anchor='    if inventory_quickslot_button != null:\n'
if refresh_anchor in m and 'inventory_unequip_button.disabled' not in m:
    block='''    if inventory_unequip_button != null:
        var can_unequip := false
        if not player.inventory.stacks.is_empty():
            var selected_stack: Dictionary = player.inventory.stacks[_inventory_use_index]
            var selected_id := String(selected_stack.get("id", ""))
            var selected_slot := ItemDatabase.get_equipment_slot(selected_id)
            if not selected_slot.is_empty():
                can_unequip = (
                    player.equipment.get_equipped(selected_slot) == selected_id
                    or player.equipment.get_visual_item(selected_slot) == selected_id
                )
        inventory_unequip_button.disabled = not can_unequip
'''
    m=m.replace(refresh_anchor,block+refresh_anchor,1)

mobile.write_text(m,encoding="utf-8")

# ---------------------------------------------------------------------------
# GEAR/TRANSMOG UNEQUIP button
# ---------------------------------------------------------------------------
gear=root/"scripts/content/gear_hud.gd"
g=gear.read_text(encoding="utf-8")
if 'var unequip_button: Button' not in g:
    g=g.replace('var transmog_button: Button\n','var transmog_button: Button\nvar unequip_button: Button\n',1)

actions='''    transmog_button = _small("TRANSMOG")
    transmog_button.pressed.connect(_transmog_selected)
    actions.add_child(transmog_button)
    root.add_child(actions)
'''
actions_new='''    transmog_button = _small("TRANSMOG")
    transmog_button.pressed.connect(_transmog_selected)
    actions.add_child(transmog_button)
    unequip_button = _small("UNEQUIP")
    unequip_button.pressed.connect(_unequip_current_slot)
    actions.add_child(unequip_button)
    root.add_child(actions)
'''
if actions not in g:
    raise SystemExit("D3D.9 gear actions anchor missing")
g=g.replace(actions,actions_new,1)

unequip_func=r'''
func _unequip_current_slot() -> void:
    var player = _player()
    if player == null:
        return
    var slot := _slots[_slot_index]
    var item_id := player.equipment.get_equipped(slot)
    if item_id.is_empty():
        player.interaction_message.emit("Nothing equipped in %s." % slot)
    else:
        player.equipment.unequip_wearable(slot)
        player.interaction_message.emit("Unequipped %s." % ItemDatabase.get_display_name(item_id))
        player.queue_redraw()
    _refresh()

'''
clear_anchor='func _clear_transmog() -> void:\n'
if clear_anchor not in g:
    raise SystemExit("D3D.9 gear clear anchor missing")
if 'func _unequip_current_slot' not in g:
    g=g.replace(clear_anchor,unequip_func+clear_anchor,1)

# Reflect slot state in button.
refresh_button_anchor='    transmog_button.disabled = ItemDatabase.get_equipment_slot(item_id) != slot\n'
if refresh_button_anchor in g:
    g=g.replace(
        refresh_button_anchor,
        refresh_button_anchor+'    if unequip_button != null:\n        unequip_button.disabled = player.equipment.get_equipped(slot).is_empty()\n',
        1,
    )
# Also set UNEQUIP state when no wearables are in inventory; current _refresh returns early.
empty_anchor='''        equip_button.disabled = true
        transmog_button.disabled = true
        return
'''
if empty_anchor in g:
    g=g.replace(
        empty_anchor,
        '''        equip_button.disabled = true
        transmog_button.disabled = true
        if unequip_button != null:
            unequip_button.disabled = player.equipment.get_equipped(slot).is_empty()
        return
''',
        1,
    )

gear.write_text(g,encoding="utf-8")

# Version.
preset=root/"export_presets.cfg"
ep=preset.read_text(encoding="utf-8")
ep,n1=re.subn(r'(?m)^version/code=\d+$','version/code=38',ep,count=1)
ep,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.9"',ep,count=1)
if not n1 or not n2:
    raise SystemExit("D3D.9 export identity fields missing")
preset.write_text(ep,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    s=save.read_text(encoding="utf-8")
    s,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.9"',s,count=1)
    save.write_text(s,encoding="utf-8")

print("Applied v0.20.0D3D.9: natural elbow-safe two-hand pistol pose, gradual aim extension, curled grip hands, modern ranger clothing, hair, field backpack, BAG/GEAR UNEQUIP.")
