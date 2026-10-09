#!/usr/bin/env python3
"""PC32 use independently rigged approved artwork for visibly articulated arms.

The old armed renderer drew a large flat-colored procedural polygon, then
low-alpha textile details over it. That obliterated folds/texture and created
tubular limbs despite correct IK. PC32 lets original authored shoulder, upper
arm, forearm, elbow and glove sprite art define the visible silhouette.
Every visible segment is mapped to the *existing* shoulder/elbow/wrist chain;
no fake bones or new graphics are created. Legacy can be restored with
PC32_LEGACY_ARM_RENDERER=1 for A/B comparison.
Apply AFTER PC31.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=p.read_text(encoding="utf-8")
fn='func _pc22_draw_anatomical_arm_shape(shoulder: Vector2, elbow: Vector2, wrist: Vector2, depth_scale: float = 1.0) -> void:\n'
if s.count(fn)!=1:
    raise SystemExit("PC32 procedural arm shape anchor mismatch")
helper='''func _pc32_draw_authored_arm_bone(tex: Texture2D, a: Vector2, b: Vector2, flip_x: bool, thickness_world: float, alpha: float = 1.0) -> void:
    # One world-space IK bone, one full-resolution source-art sprite. Two
    # independent axes fit authored length and width to skeletal anatomy.
    if tex == null:
        return
    var delta := b-a
    if delta.length_squared() < 0.01:
        return
    var tw: float = float(tex.get_width())
    var th: float = float(tex.get_height())
    var parent_px: float = clampf(tw*0.065,4.0,9.0)
    var child_px: float = tw-1.0-parent_px
    var length_pixels: float = maxf(1.0,child_px-parent_px)
    var along_scale: float = delta.length()/length_pixels
    var across_scale: float = thickness_world/maxf(1.0,th)
    var rot: float = delta.angle() if not flip_x else delta.angle()-PI
    var flip_sx: float = -along_scale if flip_x else along_scale
    draw_set_transform(a,rot,Vector2(flip_sx,across_scale))
    draw_texture(tex,-Vector2(parent_px,th*0.5),Color(1.0,1.0,1.0,alpha))
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

'''
s=s.replace(fn,helper+fn+'''    if OS.get_environment("PC32_LEGACY_ARM_RENDERER") != "1":
        # Full source-art segments are composited in _pc22_draw_arm_material_detail.
        # A tiny backing at the mathematical elbow hides sub-pixel seam holes.
        draw_circle(elbow,1.20*depth_scale,_pc22_arm_body_color())
        return
''',1)
material='func _pc22_draw_arm_material_detail(shoulder: Vector2, elbow: Vector2, wrist: Vector2, flip_x: bool, depth_scale: float = 1.0) -> void:\n'
if s.count(material)!=1:
    raise SystemExit("PC32 sleeve renderer anchor missing")
s=s.replace(material,material+'''    if OS.get_environment("PC32_LEGACY_ARM_RENDERER") != "1":
        var upper_art: Texture2D = _pc22_upper_texture()
        var fore_art: Texture2D = _pc22_fore_texture()
        var upper_width: float = pc22_player_arm_rig.upper_width()*depth_scale
        var lower_width: float = pc22_player_arm_rig.forearm_width()*depth_scale
        _pc32_draw_authored_arm_bone(upper_art,shoulder,elbow,flip_x,upper_width)
        _pc32_draw_authored_arm_bone(fore_art,elbow,wrist,flip_x,lower_width)
        # The approved cloth elbow/gusset and shoulder cap occlude each
        # joint seam while preserving independently rotating bone artwork.
        _pc22_v3_draw_elbow_gusset(_pc22_elbow_texture(),shoulder,elbow,wrist,flip_x)
        _pc22_v3_draw_cap(_pc22_shoulder_cap_texture(),shoulder,elbow,-1.0 if flip_x else 1.0)
        return
''',1)
bridge='func _pc22_draw_rear_rifle_wrist_bridge(elbow: Vector2, wrist: Vector2, flip_x: bool) -> void:\n'
if s.count(bridge)!=1:
    raise SystemExit("PC32 rear arm bridge anchor missing")
s=s.replace(bridge,bridge+'''    if OS.get_environment("PC32_LEGACY_ARM_RENDERER") != "1":
        # Rifle firing elbow is normally occluded by torso/stock. Render a
        # distal segment of the *actual* forearm rather than a flat rectangle.
        _pc22_v3_draw_distal_segment(_pc22_fore_texture(),elbow,wrist,flip_x,0.56,1.0)
        return
''',1)
p.write_text(s,encoding="utf-8")
for word in ('func _pc32_draw_authored_arm_bone','PC32_LEGACY_ARM_RENDERER','_pc22_v3_draw_elbow_gusset'):
    if word not in s:raise SystemExit("PC32 source invariant missing "+word)
ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
a='version/name="0.22.0-PC31-REFERENCE-SHOULDERS"'
if e.count("version/code=203")!=1 or e.count(a)!=1:
    raise SystemExit("PC32 requires PC31 APK identity")
ep.write_text(e.replace("version/code=203","version/code=204",1).replace(a,
    'version/name="0.22.0-PC32-AUTHORED-ARM-BONES"',1),encoding="utf-8")
sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    old='const GAME_VERSION := "0.22.0-PC31-REFERENCE-SHOULDERS"'
    if q.count(old)!=1:raise SystemExit("PC32 save version mismatch")
    sm.write_text(q.replace(old,'const GAME_VERSION := "0.22.0-PC32-AUTHORED-ARM-BONES"',1),encoding="utf-8")
print("PC32 independent authored upper/fore arm textures along canonical IK; procedural arm renderer can be restored for A/B.")
