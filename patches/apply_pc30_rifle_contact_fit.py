#!/usr/bin/env python3
"""PC30 Phase A2: source-asset/weapon-contact calibration, not sprite nudging.

The PC23 rifle handguard and muzzle socket came from the approved survivor
reference, but the PC22 generated rifle graphic used a fixed scale of 0.33
and different visual landmarks. The support grip therefore sat off the
actual lower handguard while the muzzle was shorter than the contract.
Compute a single rotated nonuniform transform from the weapon's source pixel
landmarks and approved weapon contract. Apply the SAME transform to front and
stock, then compute the flash location from the painted muzzle itself.

The authored PNG pixels are not regenerated. All shoulders, arms, IK targets
and boot sprites remain intact.
PC30_LEGACY_WEAPON_ART=1 restores old artwork transform for A/B evidence.
Apply AFTER PC30 wrist-grip consistency patch.
"""
from pathlib import Path
import math,json,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo=Path(__file__).resolve().parents[1]
runtime=root/"scripts/art/d2d29_minimal_token_runtime.gd"
if not runtime.is_file():
    raise SystemExit("PC30 A2 requires rebuilt PC30 game runtime")
s=runtime.read_text(encoding="utf-8")
asset=json.loads((repo/"assets/authored2d/unified_character/arms/metadata/hybrid_v3_weapon_assets.json").read_text())["rifle"]
contract=json.loads((repo/"assets/authored2d/unified_character/rig/weapon_rig_contracts.json").read_text())["weapons"]["rifle"]
dom=asset["dominant_grip_px"]
sup=asset["support_grip_px"]
muzzle=asset["muzzle_px"]
world_sup=contract["support_grip_relative_to_dominant"]
world_muz=contract["muzzle_relative_to_dominant"]
src_sup=[sup[0]-dom[0],sup[1]-dom[1]]
src_muz=[muzzle[0]-dom[0],muzzle[1]-dom[1]]
if abs(src_sup[1])>0.01 or src_sup[0]<1 or src_muz[1]>=-1:
    raise SystemExit("PC30 A2 expected source handguard and muzzle landmarks missing")
theta=math.atan2(world_sup[1],world_sup[0])
sx=math.hypot(*world_sup)/src_sup[0]
sy=(src_muz[0]*sx*math.sin(theta)-world_muz[1])/(-src_muz[1]*math.cos(theta))
if not 0.25<sx<0.50 or not 0.22<sy<0.45:
    raise SystemExit("PC30 A2 refuses implausible visual weapon scale")
actual_muzzle=[
    src_muz[0]*sx*math.cos(theta)-src_muz[1]*sy*math.sin(theta),
    src_muz[0]*sx*math.sin(theta)+src_muz[1]*sy*math.cos(theta)]
actual_support=[
    src_sup[0]*sx*math.cos(theta)-src_sup[1]*sy*math.sin(theta),
    src_sup[0]*sx*math.sin(theta)+src_sup[1]*sy*math.cos(theta)]
if math.dist(actual_support,world_sup)>0.01 or math.dist(actual_muzzle,world_muz)>0.6:
    raise SystemExit("PC30 A2 rifle asset fitting failed physical socket agreement")
helper='func _pc22_arm_lengths() -> Vector2:\n'
if s.count(helper)!=1:
    raise SystemExit("PC30 A2 arm helper anchor missing")
new_helper=f'''func _pc30_draw_fitted_rifle_piece(tex: Texture2D, grip_world: Vector2, aim_angle: float, dir_sign: float) -> void:
    if tex == null:
        return
    if OS.get_environment("PC30_LEGACY_WEAPON_ART") == "1":
        _pc22_v3_draw_weapon_piece(tex,grip_world,aim_angle,dir_sign,Vector2(36.0,18.0),0.33)
        return
    # Source weapon pivot, support grip and muzzle are measured in source PNG
    # pixels. Match real painted handguard with the rig's existing palm target.
    # Shape is only scaled/rotated; source pixels, shoulders and joints untouched.
    var visual_angle: float = aim_angle+{theta:.9f}
    var world_rot: float = visual_angle if dir_sign>0.0 else PI-visual_angle
    var flip_x: bool = dir_sign<0.0
    var draw_rot: float = world_rot if not flip_x else world_rot-PI
    var draw_sx: float = {-sx:.9f} if flip_x else {sx:.9f}
    draw_set_transform(grip_world,draw_rot,Vector2(draw_sx,{sy:.9f}))
    draw_texture(tex,-Vector2({dom[0]:.5f},{dom[1]:.5f}))
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

'''
s=s.replace(helper,new_helper+helper,1)
old_stock='_pc22_v3_draw_weapon_piece(tex_pc22_rifle_stock,pc22_dom_grip,pc22_arm_angle,dir_sign,Vector2(36.0,18.0),0.33)'
old_front='_pc22_v3_draw_weapon_piece(tex_pc22_rifle_front,pc22_dom_grip,pc22_arm_angle,dir_sign,Vector2(36.0,18.0),0.33)'
for name,old in [("stock",old_stock),("front",old_front)]:
    if s.count(old)!=1:
        raise SystemExit("PC30 A2 "+name+" visual artwork call not unique")
    s=s.replace(old,f'_pc30_draw_fitted_rifle_piece(tex_pc22_rifle_{name},pc22_dom_grip,pc22_arm_angle,dir_sign)',1)
old_muzzle='active_muzzle = pc22_dom_grip + _pose_point(Vector2(19.14,-1.65),pc22_arm_angle,dir_sign)'
new_muzzle=f'''if OS.get_environment("PC30_LEGACY_WEAPON_ART") == "1":
                active_muzzle = pc22_dom_grip + _pose_point(Vector2(19.14,-1.65),pc22_arm_angle,dir_sign)
            else:
                active_muzzle = pc22_dom_grip + _pose_point(Vector2({actual_muzzle[0]:.7f},{actual_muzzle[1]:.7f}),pc22_arm_angle,dir_sign)'''
if s.count(old_muzzle)!=1:
    raise SystemExit("PC30 A2 muzzle presentation anchor missing")
s=s.replace(old_muzzle,new_muzzle,1)
runtime.write_text(s,encoding="utf-8")

ex=root/"export_presets.cfg"
e=ex.read_text(encoding="utf-8")
if e.count("version/code=201")!=1 or e.count('version/name="0.22.0-PC30-WRIST-GRIP-CONTRACT"')!=1:
    raise SystemExit("PC30 A2 expected prior APK version 201")
e=e.replace("version/code=201","version/code=202",1).replace(
    'version/name="0.22.0-PC30-WRIST-GRIP-CONTRACT"',
    'version/name="0.22.0-PC30-RIFLE-CONTACT-FIT"',1)
ex.write_text(e,encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.exists():
    q=save.read_text(encoding="utf-8")
    a='const GAME_VERSION := "0.22.0-PC30-WRIST-GRIP-CONTRACT"'
    if q.count(a)!=1:
        raise SystemExit("PC30 A2 save version mismatch")
    save.write_text(q.replace(a,'const GAME_VERSION := "0.22.0-PC30-RIFLE-CONTACT-FIT"',1),encoding="utf-8")
print(f"PC30_RIFLE_PIXEL_CONTRACT scale_x={sx:.6f} scale_y={sy:.6f} cant_deg={math.degrees(theta):.4f} support_error={math.dist(actual_support,world_sup):.7f} muzzle_error={math.dist(actual_muzzle,world_muz):.6f}")
print("PC30_LEGACY_WEAPON_ART=1 preserves old source-image pose for visual comparison")
