#!/usr/bin/env python3
"""v0.20.0D3D.10: relaxed true two-hand pistol pose, larger sticks, BAG interaction repair."""
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# ---------------------------------------------------------------------------
# 1) Pistol rig: compact low-ready, support hand physically converges onto grip.
# ---------------------------------------------------------------------------
visual=root/"scripts/art/production_survivor_visual.gd"
v=visual.read_text(encoding="utf-8")

start=v.find('func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n')
end=v.find('\nfunc _rebuild_backpack_shape() -> void:\n',start)
if start<0 or end<0:
    raise SystemExit("D3D.10 pose function bounds missing")

pose=r'''func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:
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
        # D3D.10: compact low-ready. At zero aim the pistol sits close to the
        # torso with visibly bent elbows. Right-stick travel extends BOTH arms
        # gradually, but never into a locked straight-arm posture.
        var ext := clampf(_aim_extension, 0.0, 1.0)
        var breathe := sin(idle_phase) * 0.020 if not moving else 0.0
        var r_upper_low := Vector3(-0.42, -0.73 + breathe, 0.53)
        var l_upper_low := Vector3(0.42, -0.73 + breathe, 0.53)
        var r_upper_aim := Vector3(-0.30, -0.47, 0.83)
        var l_upper_aim := Vector3(0.30, -0.47, 0.83)
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
        var hand_breathe := sin(idle_phase + 0.35) * 0.018 if not moving else 0.0

        # Primary hand: tucked low-ready -> controlled aimed stance.
        var r_fore_low := Vector3(0.28, -0.61 + hand_breathe, 0.74)
        var r_fore_aim := Vector3(0.18, -0.28, 0.94)
        _point_bone_fast(skel, "lowerarm_r", "hand_r", r_fore_low.lerp(r_fore_aim, ext).normalized())
        skel.force_update_all_bone_transforms()

        # True support-hand chain. First steer the left elbow toward a bent
        # support position, then converge the left hand directly onto the right
        # hand/grip. This removes the visible floating secondary hand.
        var right_hand_idx := skel.find_bone("hand_r")
        var left_upper_idx := skel.find_bone("upperarm_l")
        if right_hand_idx >= 0:
            var right_hand_pos := skel.get_bone_global_pose(right_hand_idx).origin
            if left_upper_idx >= 0:
                var left_shoulder := skel.get_bone_global_pose(left_upper_idx).origin
                var elbow_bias := Vector3(0.12, -0.13, -0.035).lerp(Vector3(0.085, -0.07, 0.015), ext)
                var support_elbow_target := left_shoulder.lerp(right_hand_pos, 0.48) + elbow_bias
                _point_bone_to_target(skel, "upperarm_l", "lowerarm_l", support_elbow_target)
                skel.force_update_all_bone_transforms()

            var support_offset := Vector3(-0.015, -0.008, 0.004).lerp(Vector3(-0.020, -0.010, 0.009), ext)
            var grip_target := right_hand_pos + support_offset
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
v=v[:start]+pose+v[end:]

# Make the initial right-stick region relaxed. Significant stick travel is now
# required before the hands begin approaching the aimed extension.
old='    _aim_extension = clampf((raw_aim - 0.18) / 0.82, 0.0, 1.0) if armed else 0.0\n'
new='    _aim_extension = clampf((raw_aim - 0.28) / 0.72, 0.0, 1.0) if armed else 0.0\n'
if old not in v:
    raise SystemExit("D3D.10 aim extension anchor missing")
v=v.replace(old,new,1)
visual.write_text(v,encoding="utf-8")

# ---------------------------------------------------------------------------
# 2) Mobile HUD: larger default left/right sticks + repair BAG UI hierarchy.
# ---------------------------------------------------------------------------
mobile=root/"scripts/mobile_hud.gd"
m=mobile.read_text(encoding="utf-8")

# D3D.9's overlay UNEQUIP was parented directly to the panel and overlapped the
# item grid. Remove that overlay installation/function, then put UNEQUIP into the
# normal inventory content flow.
m=m.replace('    _install_inventory_unequip_button()\n','')

a=m.find('func _install_inventory_unequip_button() -> void:\n')
b=m.find('\nfunc _refresh_inventory() -> void:\n',a)
if a>=0 and b>=0:
    # Preserve only the actual unequip callback; replace the whole overlay block
    # with a clean callback and let the button be built inside inventory_root.
    callback=r'''func _unequip_selected_inventory_item() -> void:
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
    if String(player.equipment.get_equipped(slot)) == item_id:
        player.equipment.unequip_wearable(slot)
        changed = true

    # Clear a cosmetic override only when the selected inventory item is itself
    # the currently visible transmog item.
    if String(player.equipment.get_visual_item(slot)) == item_id and String(player.equipment.get_equipped(slot)) != item_id:
        player.equipment.set_transmog(slot, "", player.inventory)
        changed = true

    if changed:
        _show_message("Unequipped %s." % ItemDatabase.get_display_name(item_id))
        player.queue_redraw()
    else:
        _show_message("%s is not currently equipped." % ItemDatabase.get_display_name(item_id))
    _refresh_inventory()

'''
    m=m[:a]+callback+m[b+1:]

# Install UNEQUIP as a sibling of the existing USE button. This deliberately
# inherits the USE button's actual action-row/VBox parent instead of anchoring
# over the inventory panel/grid.
if '_install_inventory_unequip_button_safe()' not in m:
    ready_call='    _build_ui()\n'
    if ready_call not in m:
        raise SystemExit("D3D.10 BAG build anchor missing")
    m=m.replace(ready_call,ready_call+'    call_deferred("_install_inventory_unequip_button_safe")\n',1)

safe_installer=r'''func _install_inventory_unequip_button_safe() -> void:
    if inventory_unequip_button != null or inventory_use_button == null:
        return
    var action_parent := inventory_use_button.get_parent()
    if action_parent == null:
        return
    inventory_unequip_button = _make_small_button("UNEQUIP")
    inventory_unequip_button.focus_mode = Control.FOCUS_NONE
    inventory_unequip_button.pressed.connect(_unequip_selected_inventory_item)
    action_parent.add_child(inventory_unequip_button)
    _refresh_inventory()

'''
refresh_sig='func _refresh_inventory() -> void:\n'
if refresh_sig not in m:
    raise SystemExit("D3D.10 BAG refresh anchor missing")
if 'func _install_inventory_unequip_button_safe() -> void:' not in m:
    m=m.replace(refresh_sig,safe_installer+refresh_sig,1)

# Enlarge both virtual sticks in whichever responsive layout variant survived
# reconstruction. D3D.10 deliberately uses new layout IDs so old saved scaling
# cannot silently shrink the new defaults.
m=re.sub(
    r'var move_size := clampf\([^\n]+\)',
    'var move_size := clampf(short_side * 0.32 * clampf(ts, 0.85, 1.30), 200.0, 330.0)',
    m,count=1,
)
m=re.sub(
    r'var aim_size := clampf\([^\n]+\)',
    'var aim_size := clampf(move_size * 0.96, 195.0, 318.0)',
    m,count=1,
)
# Fallback for layouts that use a single stick_size variable.
m=re.sub(
    r'var stick_size := clampf\([^\n]+\)',
    'var stick_size := clampf(short_side * 0.32 * clampf(ts, 0.85, 1.30), 200.0, 330.0)',
    m,count=1,
)

m=m.replace('"joystick_v0185"','"joystick_v0200d3d10"')
m=m.replace('"aim_joystick_v0185"','"aim_joystick_v0200d3d10"')
m=m.replace('"joystick_v0184"','"joystick_v0200d3d10"')

# If later code still creates the aim stick at a small fixed size before layout,
# enlarge that initial footprint too.
m=m.replace('aim_joystick.size = Vector2(190, 190)','aim_joystick.size = Vector2(220, 220)')

mobile.write_text(m,encoding="utf-8")

# ---------------------------------------------------------------------------
# 3) Version.
# ---------------------------------------------------------------------------
preset=root/"export_presets.cfg"
ep=preset.read_text(encoding="utf-8")
ep,n1=re.subn(r'(?m)^version/code=\d+$','version/code=39',ep,count=1)
ep,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.10"',ep,count=1)
if not n1 or not n2:
    raise SystemExit("D3D.10 export identity fields missing")
preset.write_text(ep,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    s=save.read_text(encoding="utf-8")
    s,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.10"',s,count=1)
    save.write_text(s,encoding="utf-8")

# Guardrails.
checks={
    visual:["support_elbow_target","right_hand_pos","raw_aim - 0.28"],
    mobile:['func _install_inventory_unequip_button_safe() -> void:',"joystick_v0200d3d10"],
}
for p,needles in checks.items():
    s=p.read_text(encoding="utf-8")
    for n in needles:
        if n not in s:
            raise SystemExit(f"D3D.10 assertion missing in {p}: {n}")

print("Applied v0.20.0D3D.10: relaxed two-hand pistol chain, larger default dual sticks, repaired BAG interaction and UNEQUIP placement.")
