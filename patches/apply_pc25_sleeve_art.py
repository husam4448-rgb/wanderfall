#!/usr/bin/env python3
"""PC25: actual authored arm artwork follows existing PC23 shoulder/elbow/wrist.

Purely a rendering change. The continuous anatomical ribbon stays behind each
authored sleeve piece, which is fitted to the same bone endpoints. The source
textures remain in the existing sprite atlas; no regenerated/AI images.
PC25_LEGACY_ARM_ART=1 disables the overlay for controlled runtime A/B.
Run AFTER apply_pc24_reference_loadout.py.
"""
from pathlib import Path
import sys

game=Path(sys.argv[1] if len(sys.argv)>1 else 'game')
runtime=game/'scripts/art/d2d29_minimal_token_runtime.gd'
if not runtime.is_file():
    raise SystemExit('PC25 requires reconstructed PC24 game runtime')
s=runtime.read_text(encoding='utf-8')
fn='func _pc22_draw_arm_material_detail(shoulder: Vector2, elbow: Vector2, wrist: Vector2, flip_x: bool, depth_scale: float = 1.0) -> void:\n'
if s.count(fn)!=1:
    raise SystemExit('PC25 requires one material renderer anchor')
helper='''func _pc25_draw_bone_art(tex: Texture2D, a: Vector2, b: Vector2, flip_x: bool, alpha: float) -> void:
    # The authored longitudinal sleeve art follows the exact same IK bone
    # endpoints as the backing anatomical ribbon, never a separate skeleton.
    if tex == null or OS.get_environment("PC25_LEGACY_ARM_ART") == "1":
        return
    var delta: Vector2 = b-a
    if delta.length_squared() < 0.01:
        return
    var tw: float = float(tex.get_width())
    var th: float = float(tex.get_height())
    var proximal: float = clampf(tw*0.065,4.0,9.0)
    var distal: float = tw-1.0-proximal
    var tex_len: float = maxf(1.0,distal-proximal)
    var scale_long: float = delta.length()/tex_len
    # This multiplies the authored sprite's original sleeve thickness only,
    # never moves a wrist, elbow, or shoulder.
    var scale_thickness: float = scale_long*0.79
    var rot: float = delta.angle() if not flip_x else delta.angle()-PI
    var sx: float = scale_long if not flip_x else -scale_long
    draw_set_transform(a,rot,Vector2(sx,scale_thickness))
    draw_texture(tex,-Vector2(proximal,th*0.5),Color(1,1,1,alpha))
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

'''
s=s.replace(fn,helper+fn,1)
old='''    _pc22_draw_textured_limb_detail(upper_tex,upper_start,upper_end,upper_a,upper_b,flip_x,opacity)
    _pc22_draw_textured_limb_detail(fore_tex,fore_start,wrist,fore_a,fore_b,flip_x,opacity)
'''
new='''    _pc22_draw_textured_limb_detail(upper_tex,upper_start,upper_end,upper_a,upper_b,flip_x,opacity)
    _pc22_draw_textured_limb_detail(fore_tex,fore_start,wrist,fore_a,fore_b,flip_x,opacity)
    # PC25: layer actual textured/silhouetted sprites on the SAME rig bones,
    # instead of a mostly flat-color procedural sleeve. The smooth base
    # prevents gaps at acute elbows; legacy can be toggled for proof.
    _pc25_draw_bone_art(upper_tex,shoulder,elbow,flip_x,0.73*depth_scale)
    _pc25_draw_bone_art(fore_tex,elbow,wrist,flip_x,0.76*depth_scale)
'''
if s.count(old)!=1:
    raise SystemExit('PC25 unique arm-detail callsite missing')
s=s.replace(old,new,1)
runtime.write_text(s,encoding='utf-8')
for needle in ('func _pc25_draw_bone_art','PC25_LEGACY_ARM_ART','pc23_humanoid_rig_system.gd'):
    if needle not in s:
        raise SystemExit('PC25 invariant failed: '+needle)
print('PC25 real authored sleeves follow canonical rig; PC25_LEGACY_ARM_ART=1 restores old rendering')
