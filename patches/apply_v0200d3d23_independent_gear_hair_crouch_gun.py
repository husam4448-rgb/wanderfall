#!/usr/bin/env python3
"""D3D.23: scalp-anchored female hair wind, independent garment coverage, crouch gait cleanup, fitted pistol."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

# ------------------------------------------------------------------
# 1) Female long hair: keep the scalp/root fixed and deform only the
# lower part of the mesh in the vertex shader. This removes the old
# whole-hair orbit/hover while retaining subtle wind at the tips.
# ------------------------------------------------------------------
old_material='''        if body_type == "female" and hair.mesh != null and hair.mesh.get_surface_count() > 0:
            var base_mat := hair.mesh.surface_get_material(0)
            if base_mat is BaseMaterial3D:
                var mat := (base_mat as BaseMaterial3D).duplicate() as BaseMaterial3D
                mat.albedo_color = Color(0.24,0.11,0.055,1.0)
                mat.metallic = 0.0
                mat.roughness = 0.88
                hair.set_surface_override_material(0,mat)
'''
new_material='''        if body_type == "female" and hair.mesh != null and hair.mesh.get_surface_count() > 0:
            var base_mat := hair.mesh.surface_get_material(0)
            if base_mat is BaseMaterial3D:
                var source_mat := base_mat as BaseMaterial3D
                var shader := Shader.new()
                shader.code = """
shader_type spatial;
render_mode cull_back, depth_draw_opaque;
uniform sampler2D hair_tex : source_color;
uniform vec4 hair_tint : source_color = vec4(0.58,0.31,0.16,1.0);
void vertex() {
    // Hair_Long vertices run roughly Y=1.50..1.78. Keep the scalp
    // absolutely fixed and progressively move only the lower ends.
    float tip = 1.0 - smoothstep(1.57, 1.70, VERTEX.y);
    float gust = sin(TIME * 1.25 + VERTEX.y * 17.0 + VERTEX.z * 9.0);
    float flutter = cos(TIME * 1.73 + VERTEX.x * 21.0);
    VERTEX.x += gust * 0.0065 * tip;
    VERTEX.z += flutter * 0.0035 * tip;
}
void fragment() {
    vec4 tex = texture(hair_tex,UV);
    ALBEDO = tex.rgb * hair_tint.rgb;
    ALPHA = tex.a;
    ROUGHNESS = 0.88;
    METALLIC = 0.0;
}
"""
                var wind_mat := ShaderMaterial.new()
                wind_mat.shader = shader
                if source_mat.albedo_texture != null:
                    wind_mat.set_shader_parameter("hair_tex",source_mat.albedo_texture)
                hair.set_surface_override_material(0,wind_mat)
'''
if old_material not in s:
    raise SystemExit("D3D.23 female hair material anchor missing")
s=s.replace(old_material,new_material,1)

ha=s.find("func _animate_survivor_hair() -> void:\n")
hb=s.find("\nfunc _hide_ranger_fantasy_parts() -> void:\n",ha)
if ha<0 or hb<0:
    raise SystemExit("D3D.23 hair animation bounds missing")
s=s[:ha]+'''func _animate_survivor_hair() -> void:
    # Tip wind is handled in the hair vertex shader. Deliberately do not
    # rotate/translate the complete hairstyle: the scalp must stay attached.
    return

'''+s[hb:]

# ------------------------------------------------------------------
# 2) Independent equipment coverage.
# Keep the segmented skin beneath every garment. The slightly enlarged
# wearable shells occlude the covered zones naturally and no item can
# make unrelated bare body regions vanish.
# ------------------------------------------------------------------
sync_a=s.find("func _sync_apparel_visuals() -> void:\n")
sync_b=s.find("\nfunc _weapon_category() -> String:\n",sync_a)
if sync_a<0 or sync_b<0:
    raise SystemExit("D3D.23 apparel bounds missing")
sync=s[sync_a:sync_b]

old_regions='''    if segmented:
        _set_skin_region("head",true)
        _set_skin_region("torso",not shirt)
        _set_skin_region("hips",not (shirt or trousers))
        _set_skin_region("upperarms",not shirt)
        _set_skin_region("forearms",not shirt)
        _set_skin_region("hands",not gloves)
        _set_skin_region("legs",not trousers)
        _set_skin_region("feet",not boots)
'''
new_regions='''    if segmented:
        # All anatomical skin remains present under independent wearable shells.
        # This prevents jeans from deleting bare calves/feet and boots from
        # depending on trousers or the rest of the costume.
        for region_name in ["head","torso","hips","upperarms","forearms","hands","legs","feet"]:
            _set_skin_region(region_name,true)
'''
if old_regions not in sync:
    raise SystemExit("D3D.23 independent skin-region anchor missing")
sync=sync.replace(old_regions,new_regions,1)

# Slightly more shell margin on trousers/boots only, enough to cover the body
# without returning to the oversized full-costume appearance.
sync=sync.replace(
    '_scale_wearable_part(ranger_model,ranger_prefix+("Feet" if is_female else "Feet_Boots"),Vector3(1.045,1.022,1.045))',
    '_scale_wearable_part(ranger_model,ranger_prefix+("Feet" if is_female else "Feet_Boots"),Vector3(1.065,1.035,1.065))',
    1
)
sync=sync.replace(
    '_scale_wearable_part(outfit_model,peasant_prefix+"Legs",Vector3(1.035,1.015,1.035))',
    '_scale_wearable_part(outfit_model,peasant_prefix+"Legs",Vector3(1.055,1.025,1.055))',
    1
)
s=s[:sync_a]+sync+s[sync_b:]

# ------------------------------------------------------------------
# 3) Crouched movement: wider, readable steps while keeping the standing
# stance unchanged. Preserve a centered crouch pivot and planted body.
# ------------------------------------------------------------------
pose_a=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_a)
if pose_a<0 or pose_b<0:
    raise SystemExit("D3D.23 pose bounds missing")
pose=s[pose_a:pose_b]

if 'var stride := (0.44 if sprinting else (0.22 if crouching else 0.34)) * wave' in pose:
    pose=pose.replace(
        'var stride := (0.44 if sprinting else (0.22 if crouching else 0.34)) * wave',
        'var stride := (0.44 if sprinting else (0.31 if crouching else 0.34)) * wave',
        1
    )

# D3D.22 crouch targets: widen moving feet/thighs modestly but do not spread
# the idle crouch into a sumo pose.
pose=pose.replace(
    'Vector3(0.11,-0.80,0.31+crouch_step)',
    'Vector3(0.13,-0.80,0.31+(crouch_step*1.30 if moving else crouch_step))',
    1
)
pose=pose.replace(
    'Vector3(-0.11,-0.80,0.31-crouch_step)',
    'Vector3(-0.13,-0.80,0.31-(crouch_step*1.30 if moving else crouch_step))',
    1
)

# Keep feet in their authored neutral local orientation during crouch.
# Calf aiming still bends the knees, but the foot itself no longer pitches
# with the lower leg and appears to leave the ground.
insert='''    if crouching:
        for foot_name in ["foot_l","foot_r","ball_l","ball_r"]:
            var foot_idx := skel.find_bone(foot_name)
            if foot_idx >= 0:
                skel.set_bone_pose_rotation(foot_idx,Quaternion.IDENTITY)
        skel.force_update_all_bone_transforms()
'''
marker='''    var wave := sin(gait_phase)
'''
if marker not in pose:
    raise SystemExit("D3D.23 crouch foot insertion anchor missing")
pose=pose.replace(marker,insert+"\n"+marker,1)
s=s[:pose_a]+pose+s[pose_b:]

# ------------------------------------------------------------------
# 4) Pistol: reduce the complete weapon only modestly so the grip is
# contained by the dominant hand instead of protruding behind it.
# ------------------------------------------------------------------
equip_a=s.find("func _update_equipment_3d(armed: bool) -> void:\n")
equip_b=s.find("\nfunc ",equip_a+6)
if equip_a<0 or equip_b<0:
    raise SystemExit("D3D.23 equipment bounds missing")
equip=s[equip_a:equip_b]
vis='''    if gun_root != null:
        gun_root.visible = armed
'''
if vis not in equip:
    raise SystemExit("D3D.23 gun visibility anchor missing")
equip=equip.replace(vis,'''    if gun_root != null:
        gun_root.visible = armed
        gun_root.scale = Vector3(0.88,0.88,0.88)
''',1)
s=s[:equip_a]+equip+s[equip_b:]

visual.write_text(s,encoding="utf-8")

# Visible build marker.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.22  |  FEMALE + CROUCH FIX"' not in h:
    raise SystemExit("D3D.23 HUD marker anchor missing")
h=h.replace(
    'marker.text = "D3D.22  |  FEMALE + CROUCH FIX"',
    'marker.text = "D3D.23  |  INDEPENDENT GEAR + HAIR"',
    1
)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=52',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.23"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.23 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.23"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.23: scalp-fixed tip wind, independent skin/gear coverage, wider crouch gait, neutral crouch feet, fitted smaller pistol.")
