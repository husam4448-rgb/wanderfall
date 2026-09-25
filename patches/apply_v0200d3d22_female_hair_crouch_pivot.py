#!/usr/bin/env python3
"""D3D.22: transparent character viewport, refined female proportions/hair, stable realistic crouch pivot."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

# 1) Female long hair asset.
anchor='const HAIR_SCENE: PackedScene = preload("res://assets/models/superhero_male/Hair_SimpleParted.gltf")\n'
if anchor not in s:
    raise SystemExit("D3D.22 hair constant anchor missing")
if "FEMALE_HAIR_SCENE" not in s:
    s=s.replace(anchor,anchor+'const FEMALE_HAIR_SCENE: PackedScene = preload("res://assets/models/superhero_male/Hair_Long.gltf")\n',1)

# Replace hair installer with sex-specific hairstyle and dark-brown female material.
ha=s.find("func _install_hair_on_skeleton(target_skeleton: Skeleton3D) -> void:\n")
hb=s.find("\nfunc _hide_ranger_fantasy_parts() -> void:\n",ha)
if ha<0 or hb<0:
    raise SystemExit("D3D.22 hair helper bounds missing")
hair_func=r'''func _install_hair_on_skeleton(target_skeleton: Skeleton3D) -> void:
    if target_skeleton == null or target_skeleton.get_node_or_null("SurvivorHair") != null:
        return
    var selected_scene: PackedScene = FEMALE_HAIR_SCENE if body_type == "female" else HAIR_SCENE
    var mesh_name := "Hair_Long" if body_type == "female" else "Hair_SimpleParted"
    var source_root := selected_scene.instantiate() as Node3D
    if source_root == null:
        return
    var source_hair := source_root.find_child(mesh_name,true,false) as MeshInstance3D
    if source_hair != null:
        var hair := source_hair.duplicate() as MeshInstance3D
        hair.name = "SurvivorHair"
        hair.skeleton = NodePath("..")
        if body_type == "female" and hair.mesh != null and hair.mesh.get_surface_count() > 0:
            var base_mat := hair.mesh.surface_get_material(0)
            if base_mat is BaseMaterial3D:
                var mat := (base_mat as BaseMaterial3D).duplicate() as BaseMaterial3D
                mat.albedo_color = Color(0.24,0.11,0.055,1.0)
                mat.metallic = 0.0
                mat.roughness = 0.88
                hair.set_surface_override_material(0,mat)
        target_skeleton.add_child(hair)
    source_root.free()

func _animate_survivor_hair() -> void:
    if body_type != "female":
        return
    var sway := sin(idle_phase * 0.72) * 0.012
    var flutter := sin(idle_phase * 1.31 + 0.65) * 0.006
    for skel in [body_skeleton,outfit_skeleton,ranger_skeleton]:
        if skel == null:
            continue
        var hair := skel.get_node_or_null("SurvivorHair") as Node3D
        if hair != null:
            # Extremely small whole-mesh motion gives a light-wind read without
            # making the hairstyle orbit around the character.
            hair.rotation.x = flutter
            hair.rotation.z = sway

'''
s=s[:ha]+hair_func+s[hb:]

# Call hair animation every frame after the idle phase advances.
proc_anchor='    idle_phase = fmod(idle_phase + delta * 2.0, TAU)\n'
if proc_anchor not in s:
    raise SystemExit("D3D.22 process idle anchor missing")
s=s.replace(proc_anchor,proc_anchor+'    _animate_survivor_hair()\n',1)

# 2) Make the character render target unequivocally transparent.
vp_anchor='''    viewport.transparent_bg = true
'''
if vp_anchor not in s:
    raise SystemExit("D3D.22 viewport transparency anchor missing")
s=s.replace(vp_anchor,'''    viewport.transparent_bg = true
    viewport.render_target_clear_mode = SubViewport.CLEAR_MODE_ALWAYS
''',1)

# Reinforce transparency in runtime in case Android recreates the render target.
runtime_anchor='func _process(delta: float) -> void:\n'
if runtime_anchor not in s:
    raise SystemExit("D3D.22 process function anchor missing")
s=s.replace(runtime_anchor,runtime_anchor+'    if viewport != null:\n        viewport.transparent_bg = true\n',1)

# 3) Female legs: retain length, reduce lower-body bulk modestly.
pose_a=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_a)
if pose_a<0 or pose_b<0:
    raise SystemExit("D3D.22 pose bounds missing")
pose=s[pose_a:pose_b]
reset_anchor='    skel.reset_bone_poses()\n'
if reset_anchor not in pose:
    raise SystemExit("D3D.22 pose reset anchor missing")
female_scale='''    if body_type == "female":
        for bone_name in ["thigh_l","thigh_r","calf_l","calf_r"]:
            var leg_idx := skel.find_bone(bone_name)
            if leg_idx >= 0:
                skel.set_bone_pose_scale(leg_idx,Vector3(0.92,0.985,0.92))
        for bone_name in ["foot_l","foot_r"]:
            var foot_idx := skel.find_bone(bone_name)
            if foot_idx >= 0:
                skel.set_bone_pose_scale(foot_idx,Vector3(0.95,0.99,0.95))
'''
pose=pose.replace(reset_anchor,reset_anchor+female_scale,1)

# 4) Stable crouch: lower vertically around the original body/head axis.
pelvis_lines=[line for line in pose.splitlines() if "var pelvis_offset :=" in line]
if len(pelvis_lines)!=1:
    raise SystemExit("D3D.22 expected one pelvis_offset line, found %d" % len(pelvis_lines))
pose=pose.replace(pelvis_lines[0],'        var pelvis_offset := Vector3(0.0,-0.115,0.0) if crouching else Vector3.ZERO',1)
# Crouch leg targets: narrower than the old motorcycle/squat pose; knees bend,
# feet stay beneath the body instead of sending the pelvis forward.
for old,new in [
    ('Vector3(0.14,-0.75,0.48+crouch_step)','Vector3(0.11,-0.80,0.31+crouch_step)'),
    ('Vector3(-0.14,-0.75,0.48-crouch_step)','Vector3(-0.11,-0.80,0.31-crouch_step)'),
    ('Vector3(0.075,-0.78,-crouch_knee)','Vector3(0.055,-0.83,-0.40)'),
    ('Vector3(-0.075,-0.78,-crouch_knee)','Vector3(-0.055,-0.83,-0.40)'),
]:
    if old not in pose:
        raise SystemExit("D3D.22 crouch leg anchor missing "+old)
    pose=pose.replace(old,new,1)

# Reduce crouch torso pitch substantially; head/neck counterpose keeps gaze level.
for old,new in [
    ('deg_to_rad(12.0)','deg_to_rad(6.0)'),
    ('deg_to_rad(7.0)','deg_to_rad(3.0)'),
    ('deg_to_rad(-12.0)','deg_to_rad(-5.0)'),
    ('deg_to_rad(-7.0)','deg_to_rad(-4.0)'),
]:
    if old not in pose:
        raise SystemExit("D3D.22 crouch lean anchor missing "+old)
    pose=pose.replace(old,new,1)

s=s[:pose_a]+pose+s[pose_b:]

# 5) Individual clothing shells: tiny coverage margin only, avoiding bulky full-set look.
sync_a=s.find("func _sync_apparel_visuals() -> void:\n")
sync_b=s.find("\nfunc _weapon_category() -> String:\n",sync_a)
if sync_a<0 or sync_b<0:
    raise SystemExit("D3D.22 apparel bounds missing")
sync=s[sync_a:sync_b]
for old,new in [
    ('Vector3(1.025,1.01,1.025)','Vector3(1.035,1.015,1.035)'),
    ('Vector3(1.035,1.02,1.035)','Vector3(1.040,1.022,1.040)'),
    ('Vector3(1.04,1.02,1.04)','Vector3(1.045,1.022,1.045)'),
    ('Vector3(1.03,1.01,1.03)','Vector3(1.040,1.015,1.040)'),
    ('Vector3(1.025,1.01,1.025)','Vector3(1.035,1.015,1.035)'),
]:
    if old in sync:
        sync=sync.replace(old,new,1)
s=s[:sync_a]+sync+s[sync_b:]

visual.write_text(s,encoding="utf-8")

# Build stamp.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.21  |  MALE/FEMALE TEMPLATES"' not in h:
    raise SystemExit("D3D.22 HUD marker anchor missing")
h=h.replace('marker.text = "D3D.21  |  MALE/FEMALE TEMPLATES"','marker.text = "D3D.22  |  FEMALE + CROUCH FIX"',1)
hud.write_text(h,encoding="utf-8")

# Version.
preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=51',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.22"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.22 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.22"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.22: transparent viewport, long dark female hair with subtle sway, slimmer female legs, centered stable crouch/pivot, improved individual gear coverage.")
