#!/usr/bin/env python3
"""D3D.24: independent gear fit, real pistol scaling, planted crouch feet, upright crouch body, Android white-key cleanup."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

# ------------------------------------------------------------------
# 1) Independent garments: occlude only the anatomical region an item
# actually owns, while keeping calves/arms available under partial meshes.
# ------------------------------------------------------------------
sync_a=s.find("func _sync_apparel_visuals() -> void:\n")
sync_b=s.find("\nfunc _weapon_category() -> String:\n",sync_a)
if sync_a<0 or sync_b<0:
    raise SystemExit("D3D.24 apparel bounds missing")
sync=s[sync_a:sync_b]

old_regions='''    if segmented:
        # All anatomical skin remains present under independent wearable shells.
        # This prevents jeans from deleting bare calves/feet and boots from
        # depending on trousers or the rest of the costume.
        for region_name in ["head","torso","hips","upperarms","forearms","hands","legs","feet"]:
            _set_skin_region(region_name,true)
'''
new_regions='''    if segmented:
        # Each item is independent. Hide only the body zone that the item fully
        # replaces; leave partially covered limbs available beneath their shell.
        _set_skin_region("head",true)
        _set_skin_region("torso",not shirt)
        _set_skin_region("hips",not trousers)
        _set_skin_region("upperarms",true)
        _set_skin_region("forearms",true)
        _set_skin_region("hands",not gloves)
        _set_skin_region("legs",true)
        _set_skin_region("feet",not boots)
'''
if old_regions not in sync:
    raise SystemExit("D3D.24 D3D.23 region anchor missing")
sync=sync.replace(old_regions,new_regions,1)

# Give each shell enough thickness to fully cover its matching body surface.
repls=[
('_scale_wearable_part(ranger_model,ranger_prefix+"Body",Vector3(1.035,1.015,1.035))',
 '_scale_wearable_part(ranger_model,ranger_prefix+"Body",Vector3(1.075,1.015,1.075))'),
('_scale_wearable_part(ranger_model,ranger_prefix+("Feet" if is_female else "Feet_Boots"),Vector3(1.040,1.022,1.040))',
 '_scale_wearable_part(ranger_model,ranger_prefix+("Feet" if is_female else "Feet_Boots"),Vector3(1.105,1.075,1.105))'),
('_scale_wearable_part(ranger_model,ranger_prefix+"Arms_Bracer",Vector3(1.045,1.022,1.045))',
 '_scale_wearable_part(ranger_model,ranger_prefix+"Arms_Bracer",Vector3(1.070,1.035,1.070))'),
('_scale_wearable_part(outfit_model,peasant_prefix+"Arms",Vector3(1.040,1.015,1.040))',
 '_scale_wearable_part(outfit_model,peasant_prefix+"Arms",Vector3(1.065,1.030,1.065))'),
('_scale_wearable_part(outfit_model,peasant_prefix+"Legs",Vector3(1.055,1.025,1.055))',
 '_scale_wearable_part(outfit_model,peasant_prefix+"Legs",Vector3(1.085,1.050,1.085))'),
]
for old,new in repls:
    if old not in sync:
        raise SystemExit("D3D.24 wearable scale anchor missing: "+old)
    sync=sync.replace(old,new,1)

# Commit the corrected independent wearable block.\ns=s[:sync_a]+sync+s[sync_b:]

# ------------------------------------------------------------------
# 2) Crouch: undo D3D.23 foot/ball reset that collapsed the feet.
# Keep authored foot/ball rotations, lower through knees/pelvis, and keep
# torso mostly vertical with only a small realistic forward hinge.
# ------------------------------------------------------------------
pose_a=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_a)
if pose_a<0 or pose_b<0:
    raise SystemExit("D3D.24 pose bounds missing")
pose=s[pose_a:pose_b]

bad_foot='''    if crouching:
        for foot_name in ["foot_l","foot_r","ball_l","ball_r"]:
            var foot_idx := skel.find_bone(foot_name)
            if foot_idx >= 0:
                skel.set_bone_pose_rotation(foot_idx,Quaternion.IDENTITY)
        skel.force_update_all_bone_transforms()

'''
if bad_foot not in pose:
    raise SystemExit("D3D.24 D3D.23 foot reset anchor missing")
pose=pose.replace(bad_foot,"",1)

for old,new in [
('deg_to_rad(6.0)','deg_to_rad(3.5)'),
('deg_to_rad(3.0)','deg_to_rad(2.0)'),
('deg_to_rad(-5.0)','deg_to_rad(-3.0)'),
('deg_to_rad(-4.0)','deg_to_rad(-2.0)'),
]:
    if old not in pose:
        raise SystemExit("D3D.24 crouch lean anchor missing "+old)
    pose=pose.replace(old,new,1)

# Slightly less forward knee target and a touch more vertical drop keeps the
# feet planted instead of making the character look like it is riding.
pose=pose.replace('Vector3(0.13,-0.80,0.31+(crouch_step*1.30 if moving else crouch_step))',
                  'Vector3(0.125,-0.83,0.24+(crouch_step*1.22 if moving else crouch_step))',1)
pose=pose.replace('Vector3(-0.13,-0.80,0.31-(crouch_step*1.30 if moving else crouch_step))',
                  'Vector3(-0.125,-0.83,0.24-(crouch_step*1.22 if moving else crouch_step))',1)
pose=pose.replace('Vector3(0.055,-0.83,-0.40)','Vector3(0.055,-0.86,-0.34)',1)
pose=pose.replace('Vector3(-0.055,-0.83,-0.40)','Vector3(-0.055,-0.86,-0.34)',1)
s=s[:pose_a]+pose+s[pose_b:]

# ------------------------------------------------------------------
# 3) Pistol: D3D.23 changed Node3D.scale, but the later global_transform
# assignment overwrote that scale every frame. Put the scale into the basis
# actually assigned to the weapon, so the size change is real and persistent.
# ------------------------------------------------------------------
equip_a=s.find("func _update_equipment_3d(armed: bool) -> void:\n")
equip_b=s.find("\nfunc ",equip_a+6)
if equip_a<0 or equip_b<0:
    raise SystemExit("D3D.24 equipment bounds missing")
equip=s[equip_a:equip_b]
old_basis='var gun_basis := actor_root.global_transform.basis.orthonormalized()'
new_basis='var gun_basis := actor_root.global_transform.basis.orthonormalized().scaled(Vector3(0.84,0.84,0.84))'
if old_basis not in equip:
    raise SystemExit("D3D.24 pistol basis anchor missing")
equip=equip.replace(old_basis,new_basis,1)
# Remove ineffective root scale to avoid double scaling if code path changes later.
equip=equip.replace('        gun_root.scale = Vector3(0.88,0.88,0.88)\n','',1)
s=s[:equip_a]+equip+s[equip_b:]

# ------------------------------------------------------------------
# 4) Android compatibility fallback for the stubborn white rectangle.
# The 3D viewport is already transparent; additionally key only essentially
# pure-white background texels on the 2D presentation sprite. Threshold is
# intentionally extreme so gray/white hair highlights remain intact.
# ------------------------------------------------------------------
stage_anchor='''    viewport_sprite.texture = viewport.get_texture()
'''
if stage_anchor not in s:
    raise SystemExit("D3D.24 viewport sprite anchor missing")
if "D3D24WhiteKey" not in s:
    stage_insert='''    var key_shader := Shader.new()
    key_shader.resource_name = "D3D24WhiteKey"
    key_shader.code = """
shader_type canvas_item;
void fragment() {
    vec4 c = texture(TEXTURE,UV);
    float pure_white = step(0.997,c.r) * step(0.997,c.g) * step(0.997,c.b);
    c.a *= (1.0 - pure_white);
    COLOR = c;
}
"""
    var key_material := ShaderMaterial.new()
    key_material.shader = key_shader
    viewport_sprite.material = key_material
'''
    s=s.replace(stage_anchor,stage_anchor+stage_insert,1)

visual.write_text(s,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.23  |  INDEPENDENT GEAR + HAIR"' not in h:
    raise SystemExit("D3D.24 HUD marker anchor missing")
h=h.replace('marker.text = "D3D.23  |  INDEPENDENT GEAR + HAIR"',
            'marker.text = "D3D.24  |  GEAR + GUN + CROUCH"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=53',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.24"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.24 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.24"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.24: independent gear fit/alignment, persistent smaller pistol, planted crouch feet, upright crouch body and white-key fallback.")
