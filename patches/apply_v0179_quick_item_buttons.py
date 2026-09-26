#!/usr/bin/env python3
"""Compatibility entry point for the current Android Quick-Use test build."""
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).resolve().parent
combined = patch_dir / "apply_v0179_quick_items_safe_spawn.py"
radial = patch_dir / "apply_v0180_radial_quick_menu.py"
polish = patch_dir / "apply_v0181_quick_radial_joystick.py"
static_scene = patch_dir / "apply_v0182_static_quick_scene.py"
ci_compat = patch_dir / "apply_v0182_ci_compat.py"
responsive_hud = patch_dir / "apply_v0183_responsive_hud.py"
uniform_inventory = patch_dir / "apply_v0184_uniform_hud_inventory_grid.py"
dual_stick = patch_dir / "apply_v0185_dual_stick_combat.py"
qol_world = patch_dir / "apply_v0186_qol_world_spacing.py"
vehicle_controls = patch_dir / "apply_v0187a_character_vehicle_controls.py"
vehicle_qol = patch_dir / "apply_v0187a2_vehicle_qol_fix.py"
vehicle_a3 = patch_dir / "apply_v0187a3_vehicle_sensitivity_quick_melee.py"
control_editor_a4 = patch_dir / "apply_v0187a4_control_editor_stability.py"
storage_b = patch_dir / "apply_v0187b_storage_windows.py"
storage_b2 = patch_dir / "apply_v0187b2_storage_grid_interaction.py"
universal_c = patch_dir / "apply_v0187c_universal_windows.py"
universal_c2 = patch_dir / "apply_v0187c2_window_touch_scroll.py"
universal_c3 = patch_dir / "apply_v0187c3_inventory_gestures_hud_bounds.py"
art_foundation = patch_dir / "apply_v0190a_survival_paradise_art_foundation.py"
terrain_props = patch_dir / "apply_v0190b_terrain_props.py"
grass_density = patch_dir / "apply_v0190b1_grass_density.py"
structures_interiors = patch_dir / "apply_v0190c_structures_interiors.py"
structures_parser_fix = patch_dir / "apply_v0190c_parser_fix.py"
world_coherence_c1 = patch_dir / "apply_v0190c1_world_coherence.py"
hud_natural_water_c2 = patch_dir / "apply_v0190c2_hud_natural_water.py"
world_density_c3 = patch_dir / "apply_v0190c3_world_density.py"
visual_fixes_c4 = patch_dir / "apply_v0190c4_layering_lake_fill.py"
world_layering_c5 = patch_dir / "apply_v0190c5_world_layering.py"
world_layering_c5_parser_fix = patch_dir / "apply_v0190c5_parser_fix.py"
aim_occlusion_c6 = patch_dir / "apply_v0190c6_aim_occlusion.py"
storage_use_icon_d1a = patch_dir / "apply_v0190d1a_storage_use_icon_size.py"
bandit_loot_d1b = patch_dir / "apply_v0190d1b_bandit_loot.py"
interior_utilities_d1c = patch_dir / "apply_v0190d1c_interior_utilities.py"
visual_slots_d2a1 = patch_dir / "apply_v0190d2a1_slots_lootall.py"
layered_visuals_d2a2 = patch_dir / "apply_v0190d2a2_layered_visuals.py"
visual_d2a_parser_fix = patch_dir / "apply_v0190d2a_parser_fix.py"
weapon_visuals_d2b1 = patch_dir / "apply_v0190d2b1_weapon_visuals.py"
npc_weapon_state_d2b2 = patch_dir / "apply_v0190d2b2_npc_weapon_state.py"
exact_weapon_icons_d2b3 = patch_dir / "apply_v0190d2b3_exact_weapon_icons.py"
character_visual_repair_d2b1 = patch_dir / "apply_v0190d2b1_character_visual_repair.py"
articulated_actor_d2b2a = patch_dir / "apply_v0190d2b2a_articulated_actor_core.py"
articulated_gear_d2b2b = patch_dir / "apply_v0190d2b2b_articulated_gear.py"
animation_integration_d2b2c = patch_dir / "apply_v0190d2b2c_animation_integration.py"
weapon_pose_fix_d2b2d = patch_dir / "apply_v0190d2b2d_weapon_pose_fix.py"
slim_weapon_art_d2b2e = patch_dir / "apply_v0190d2b2e_slim_weapon_art.py"
direction_pose_d2b3a = patch_dir / "apply_v0190d2b3a_directional_pose_engine.py"
direction_body_d2b3b = patch_dir / "apply_v0190d2b3b_directional_body_perspective.py"
direction_head_arms_d2b3c = patch_dir / "apply_v0190d2b3c_directional_head_arms.py"
direction_gear_d2b3d = patch_dir / "apply_v0190d2b3d_directional_gear.py"
production_survivor_d2b4 = patch_dir / "apply_v0190d2b4_production_survivor_art.py"
production_survivor_d2b4_parser_fix = patch_dir / "apply_v0190d2b4_parser_fix.py"
player_male_female_d2b5 = patch_dir / "apply_v0190d2b5_player_male_female_visual.py"
direct_sprite_d2b6 = patch_dir / "apply_v0190d2b6_direct_sprite_actor.py"
hybrid_sprite_d2b7 = patch_dir / "apply_v0190d2b7_hybrid_sprite_skeleton.py"
directional_hybrid_idle_d2b8 = patch_dir / "apply_v0190d2b8_directional_hybrid_idle.py"
aiming_fix_d2b9 = patch_dir / "apply_v0190d2b9_aiming_fix.py"
pure_sprite_skeleton_d2b10 = patch_dir / "apply_v0190d2b10_pure_sprite_skeleton.py"
mesh_head_upgrade_d2b11 = patch_dir / "apply_v0190d2b11_mesh_head_upgrade.py"
thickness_only_d2b12 = patch_dir / "apply_v0190d2b12_thickness_only.py"
opaque_procedural_d2b13 = patch_dir / "apply_v0190d2b13_opaque_procedural_skeleton.py"
definition_pass_d2b14 = patch_dir / "apply_v0190d2b14_definition_pass.py"
humanized_body_d2b15 = patch_dir / "apply_v0190d2b15_humanized_body.py"
connected_face_zoom_updates_d2b16 = patch_dir / "apply_v0190d2b16_connected_face_zoom_updates.py"
directional_anatomy_weapon_d2b17 = patch_dir / "apply_v0190d2b17_directional_anatomy_weapon.py"
arm_layers_leg_rotation_boots_d2b18 = patch_dir / "apply_v0190d2b18_arm_layers_leg_rotation_boots.py"
subviewport_character_d3d1 = patch_dir / "apply_v0200d3d1_subviewport_character.py"
rigged_survivor_d3d2 = patch_dir / "apply_v0200d3d2_rigged_survivor_fix.py"
rotation_scale_clothing_gait_d3d3 = patch_dir / "apply_v0200d3d3_rotation_scale_clothing_gait.py"
aim_pose_performance_zoom_d3d4 = patch_dir / "apply_v0200d3d4_aim_pose_performance_zoom.py"
head_grip_idle_zoom_d3d5 = patch_dir / "apply_v0200d3d5_head_grip_idle_zoom.py"
character_bag_fixes_d3d6 = patch_dir / "apply_v0200d3d6_character_bag_fixes.py"
render_apparel_quality_d3d7 = patch_dir / "apply_v0200d3d7_render_apparel_quality.py"
human_idle_head_bag_d3d8 = patch_dir / "apply_v0200d3d8_human_idle_head_bag.py"
hands_modern_unequip_d3d9 = patch_dir / "apply_v0200d3d9_hands_modern_unequip.py"
relaxed_arms_large_sticks_bagfix_d3d10 = patch_dir / "apply_v0200d3d10_relaxed_arms_large_sticks_bagfix.py"
volumetric_slots_tactical_d3d11 = patch_dir / "apply_v0200d3d11_volumetric_slots_tactical.py"
rigged_gear_pistol_socket_d3d12 = patch_dir / "apply_v0200d3d12_rigged_gear_pistol_socket.py"
joystick_edge_latch_d3d13a = patch_dir / "apply_v0200d3d13a_joystick_edge_latch.py"
palm_fit_breath_d3d13b = patch_dir / "apply_v0200d3d13b_palm_fit_breath.py"
actor_fit_tactical_crouch_d3d14 = patch_dir / "apply_v0200d3d14_actor_fit_tactical_crouch.py"
player_world_scale_d3d15 = patch_dir / "apply_v0200d3d15_player_world_scale.py"
visible_player_scale_d3d16 = patch_dir / "apply_v0200d3d16_visible_player_scale.py"
planted_stance_knife_d3d17 = patch_dir / "apply_v0200d3d17_planted_stance_knife.py"
reference_stance_fit_grip_d3d18 = patch_dir / "apply_v0200d3d18_reference_stance_fit_grip.py"
normal_stance_hand_grip_d3d19 = patch_dir / "apply_v0200d3d19_normal_stance_hand_grip.py"
tactical_grip_crouch_head_d3d20 = patch_dir / "apply_v0200d3d20_tactical_grip_crouch_head.py"
female_slots_trees_d3d21 = patch_dir / "apply_v0200d3d21_female_slots_trees.py"
female_hair_crouch_pivot_d3d22 = patch_dir / "apply_v0200d3d22_female_hair_crouch_pivot.py"
independent_gear_hair_crouch_gun_d3d23 = patch_dir / "apply_v0200d3d23_independent_gear_hair_crouch_gun.py"
gear_gun_crouch_render_d3d24 = patch_dir / "apply_v0200d3d24_gear_gun_crouch_render_fix.py"
slot_gear_crouch_gait_d3d25 = patch_dir / "apply_v0200d3d25_slot_gear_crouch_gait.py"
grounded_locomotion_neck_barrel_d3d26 = patch_dir / "apply_v0200d3d26_grounded_locomotion_neck_barrel.py"
character_render_performance_d3d27 = patch_dir / "apply_v0200d3d27_character_render_performance.py"
world_performance_d3d28 = patch_dir / "apply_v0200d3d28_world_performance.py"
pixel_character_performance_d3d29 = patch_dir / "apply_v0200d3d29_pixel_character_performance.py"
idle_render_chunk_cull_d3d30 = patch_dir / "apply_v0200d3d30_idle_render_chunk_cull.py"
mobile_chunk_scale_fix_d3d31 = patch_dir / "apply_v0200d3d31_mobile_chunk_scale_fix.py"
combat_proving_ground_d3d32 = patch_dir / "apply_v0200d3d32_combat_proving_ground.py"
combat_occlusion_fix_d3d322 = patch_dir / "apply_v0200d3d32_2_combat_occlusion_fix.py"
production_bandit_d3d323 = patch_dir / "apply_v0200d3d32_3_production_bandit.py"
pure_2d_runtime_d2d1 = patch_dir / "apply_v0210d2d1_pure_2d_runtime.py"
baked_reference_d2d2 = patch_dir / "apply_v0210d2d2_baked_reference_runtime.py"
true2d_gear_d2d3 = patch_dir / "apply_v0210d2d3_true2d_gear_style.py"
authored2d_d2d4 = patch_dir / "apply_v0210d2d4_authored2d_runtime.py"
atlas_fix_d2d41 = patch_dir / "apply_v0210d2d41_atlas_fix.py"
verified_atlas_d2d42 = patch_dir / "apply_v0210d2d42_verified_atlas.py"
webp_fix_d2d43 = patch_dir / "apply_v0210d2d43_webp_import_fix.py"
player_visibility_d2d44 = patch_dir / "apply_v0210d2d44_player_visibility.py"
armed_visibility_d2d45 = patch_dir / "apply_v0210d2d45_armed_visibility.py"
opaque_direction_d2d46 = patch_dir / "apply_v0210d2d46_opaque_direction_fix.py"
modular_rig_d2d5 = patch_dir / "apply_v0210d2d5_modular_rig.py"
south_gear_d2d51 = patch_dir / "apply_v0210d2d51_south_gear.py"
restore_old_skeleton_d2d6 = patch_dir / "apply_v0210d2d6_restore_old_skeleton.py"
drawn_skeleton_d2d7 = patch_dir / "apply_v0210d2d7_drawn_skeleton.py"
oriented_procedural_d2d8 = patch_dir / "apply_v0210d2d8_oriented_procedural.py"
aim_arms_d2d81 = patch_dir / "apply_v0210d2d81_aim_arms_fix.py"
grip_stance_d2d82 = patch_dir / "apply_v0210d2d82_grip_stance_zoom.py"
pose_oracle_d2d9 = patch_dir / "apply_v0210d2d9_pose_oracle_3d.py"

steps = (combined, radial, polish, static_scene, ci_compat, responsive_hud, uniform_inventory, dual_stick, qol_world, vehicle_controls, vehicle_qol, vehicle_a3, control_editor_a4, storage_b, storage_b2, universal_c, universal_c2, universal_c3, art_foundation, terrain_props, grass_density, structures_interiors, structures_parser_fix, world_coherence_c1, hud_natural_water_c2, world_density_c3, visual_fixes_c4, world_layering_c5, world_layering_c5_parser_fix, aim_occlusion_c6, storage_use_icon_d1a, bandit_loot_d1b, interior_utilities_d1c, visual_slots_d2a1, layered_visuals_d2a2, visual_d2a_parser_fix, weapon_visuals_d2b1, npc_weapon_state_d2b2, exact_weapon_icons_d2b3, character_visual_repair_d2b1, articulated_actor_d2b2a, articulated_gear_d2b2b, animation_integration_d2b2c, weapon_pose_fix_d2b2d, slim_weapon_art_d2b2e, direction_pose_d2b3a, direction_body_d2b3b, direction_head_arms_d2b3c, direction_gear_d2b3d, production_survivor_d2b4, production_survivor_d2b4_parser_fix, player_male_female_d2b5, direct_sprite_d2b6, hybrid_sprite_d2b7, directional_hybrid_idle_d2b8, aiming_fix_d2b9, pure_sprite_skeleton_d2b10, mesh_head_upgrade_d2b11, thickness_only_d2b12, opaque_procedural_d2b13, definition_pass_d2b14, humanized_body_d2b15, connected_face_zoom_updates_d2b16, directional_anatomy_weapon_d2b17, arm_layers_leg_rotation_boots_d2b18, subviewport_character_d3d1, rigged_survivor_d3d2, rotation_scale_clothing_gait_d3d3, aim_pose_performance_zoom_d3d4, head_grip_idle_zoom_d3d5, character_bag_fixes_d3d6, render_apparel_quality_d3d7, human_idle_head_bag_d3d8, hands_modern_unequip_d3d9, relaxed_arms_large_sticks_bagfix_d3d10, volumetric_slots_tactical_d3d11, rigged_gear_pistol_socket_d3d12, joystick_edge_latch_d3d13a, palm_fit_breath_d3d13b, actor_fit_tactical_crouch_d3d14, player_world_scale_d3d15, visible_player_scale_d3d16, planted_stance_knife_d3d17, reference_stance_fit_grip_d3d18, normal_stance_hand_grip_d3d19, tactical_grip_crouch_head_d3d20, female_slots_trees_d3d21, female_hair_crouch_pivot_d3d22, independent_gear_hair_crouch_gun_d3d23, gear_gun_crouch_render_d3d24, slot_gear_crouch_gait_d3d25, grounded_locomotion_neck_barrel_d3d26, character_render_performance_d3d27, world_performance_d3d28, pixel_character_performance_d3d29, idle_render_chunk_cull_d3d30, mobile_chunk_scale_fix_d3d31, combat_proving_ground_d3d32, combat_occlusion_fix_d3d322, production_bandit_d3d323, pure_2d_runtime_d2d1, baked_reference_d2d2, true2d_gear_d2d3, authored2d_d2d4, atlas_fix_d2d41, verified_atlas_d2d42, webp_fix_d2d43, player_visibility_d2d44, armed_visibility_d2d45, opaque_direction_d2d46, modular_rig_d2d5, south_gear_d2d51, restore_old_skeleton_d2d6, drawn_skeleton_d2d7, oriented_procedural_d2d8, aim_arms_d2d81, grip_stance_d2d82, pose_oracle_d2d9)
for step in steps:
    if not step.is_file():
        raise SystemExit(f"Missing Quick-Use applicator: {step}")

result = subprocess.run([sys.executable, str(combined), str(root)])
if result.returncode != 0:
    raise SystemExit(result.returncode)

mobile_path = root / "scripts/mobile_hud.gd"
mobile = mobile_path.read_text(encoding="utf-8")
decl_anchor = "var inventory_use_button: Button\n"
if decl_anchor not in mobile:
    raise SystemExit("Inventory declaration anchor missing")
decls = ""
if "var inventory_quickslot_button: Button" not in mobile:
    decls += "var inventory_quickslot_button: Button\n"
if "var inventory_quickslot_clear_button: Button" not in mobile:
    decls += "var inventory_quickslot_clear_button: Button\n"
if "var _quickslot_assign_index :=" not in mobile:
    decls += "var _quickslot_assign_index := 0\n"
if decls:
    mobile = mobile.replace(decl_anchor, decl_anchor + decls, 1)

func_anchor = "func _toggle_inventory() -> void:\n"
if func_anchor not in mobile:
    raise SystemExit("Inventory toggle anchor missing")
missing = []
if "func _next_quickslot_assign() -> void:" not in mobile:
    missing.append("func _next_quickslot_assign() -> void:\n    pass\n\n")
if "func _assign_selected_to_quickbar() -> void:" not in mobile:
    missing.append("func _assign_selected_to_quickbar() -> void:\n    pass\n\n")
if "func _clear_quickslot_assign() -> void:" not in mobile:
    missing.append("func _clear_quickslot_assign() -> void:\n    pass\n\n")
if missing:
    mobile = mobile.replace(func_anchor, "".join(missing) + func_anchor, 1)
mobile_path.write_text(mobile, encoding="utf-8")

for step in steps[1:]:
    result = subprocess.run([sys.executable, str(step), str(root)])
    if result.returncode != 0:
        raise SystemExit(result.returncode)

print("Applied through v0.20.0D3D.14 Survival Paradise fitted character, matte pistol, bent stance and crouch toggle.")
