#!/usr/bin/env python3
"""PC28: independent thigh/shin texture regions driven by an anatomical knee.

Retains the existing authored front/rear trouser and boot art, hips and
footwear sockets. The old PC27 rendering is preserved for A/B via
PC28_LEGACY_KNEE=1. Runtime diagnostics opt-in PC28_SHOW_KNEES=1.
Run AFTER apply_pc27_balanced_gait.py.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=p.read_text(encoding="utf-8")
fn='func _draw_separate_leg(base: Vector2, side: float, stride: float, dir_sign: float) -> void:\n'
if s.count(fn)!=1:
    raise SystemExit("PC28 leg routine missing or ambiguous")
helper='''func _pc28_draw_articulated_leg(tex: Texture2D, hip: Vector2, knee: Vector2, ankle: Vector2, is_mirrored: bool, cloth_width: float) -> void:
    # Existing leg RGBA texture is divided by *source-region sampling*.
    # No synthesized limb silhouette; original fabric detail stays visible.
    # Hip->knee and knee->ankle use independent rotations about true joints.
    if tex == null:
        return
    var sw: float = float(tex.get_width())
    var sh: float = float(tex.get_height())
    if sw < 2.0 or sh < 4.0:
        return
    var flip: float = -1.0 if is_mirrored else 1.0
    var u: Vector2 = knee-hip
    var f: Vector2 = ankle-knee
    # Source strips overlap by 3% at the actual knee to hide hard seams.
    var upper_source := Rect2(0.0,0.0,sw,sh*0.565)
    var shin_source := Rect2(0.0,sh*0.535,sw,sh*0.465)
    draw_set_transform(hip,u.angle()-PI*0.5,Vector2(flip,1.0))
    draw_texture_rect_region(tex,Rect2(-cloth_width*0.5,-0.85,cloth_width,u.length()+1.65),upper_source)
    draw_set_transform(knee,f.angle()-PI*0.5,Vector2(flip,1.0))
    draw_texture_rect_region(tex,Rect2(-cloth_width*0.42,-0.95,cloth_width*0.84,f.length()+1.85),shin_source)
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

func _pc28_knee_target(hip: Vector2, ankle: Vector2, dir_sign: float, female: bool) -> Vector2:
    # Constant bone lengths throughout gait; solve the intersection of the
    # upper-leg and shin circles. Forward-bending branch stays consistent.
    var v: Vector2 = ankle-hip
    var d: float = maxf(0.001,v.length())
    var upper_len: float = 10.6 if female else 10.25
    var shin_len: float = 10.6 if female else 10.25
    var axis: Vector2 = v/d
    var projected: float = clampf((upper_len*upper_len-shin_len*shin_len+d*d)/(2.0*d),0.001,upper_len)
    var bend: float = sqrt(maxf(0.0,upper_len*upper_len-projected*projected))
    var lateral := Vector2(-axis.y,axis.x)
    return hip+axis*projected-lateral*bend*dir_sign

'''
s=s.replace(fn,helper+fn,1)
# The PC27 stride solver provides anatomically placed hip and ankle targets.
# Override only the middle joint and source art; never change those targets.
render_begin='''    var mid := (hip + ankle) * 0.5
    var leg_angle := (ankle - hip).angle() - PI * 0.5
'''
if s.count(render_begin)!=1:
    raise SystemExit("PC28 draw leg segment entry not unique")
s=s.replace(render_begin,'''    var pc28_segmented: bool = OS.get_environment("PC28_LEGACY_KNEE") != "1" and move_vec.length() > 0.05
    if pc28_segmented:
        var bone_length: float = 10.6 if female_mode else 10.25
        var to_ankle: Vector2 = ankle-hip
        # Preserve bone lengths even for extreme gait targets; any reach cap
        # only applies to the new articulated candidate, not PC27 baseline.
        if to_ankle.length()>bone_length*2.0-0.15:
            ankle = hip+to_ankle.normalized()*(bone_length*2.0-0.15)
        knee = _pc28_knee_target(hip,ankle,dir_sign,female_mode)
    var mid := (hip + ankle) * 0.5
    var leg_angle := (ankle - hip).angle() - PI * 0.5
''',1)
# Switch rendering in both sex / gear states while leaving the texture
# selection intact (no direct side/female changes to outfit logic).
calls=[
'_draw_equipment_texture(female_leg_tex, mid, Vector2(19.8,26.5), leg_flip, leg_angle)',
'_draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)'
]
for call in calls:
    if s.count(call)!=2:
        raise SystemExit("PC28 cloth art call must occur twice: "+call)
    width="19.8" if "female_leg_tex" in call else "16.5"
    substitution=("if pc28_segmented:\n"
                  "                _pc28_draw_articulated_leg("+("female_leg_tex" if width=="19.8" else "leg_tex")+",hip,knee,ankle,leg_flip,"+width+")\n"
                  "            else:\n"
                  "                "+call)
    s=s.replace(call,substitution)
# Optional diagnostic landmarks without altering production texture blending.
boots='''    # D2D.50: slightly forward and lower relative to ankle.
'''
if s.count(boots)!=1:
    raise SystemExit("PC28 boots anchor missing")
s=s.replace(boots,'''    if OS.get_environment("PC28_SHOW_KNEES") == "1" and pc28_segmented:
        draw_line(hip,knee,Color(0.2,0.85,0.95,0.9),0.25,false)
        draw_line(knee,ankle,Color(0.95,0.68,0.12,0.9),0.25,false)
        draw_circle(hip,0.65,Color(0.1,0.85,0.35))
        draw_circle(knee,0.90,Color(1.0,0.3,0.2))
        draw_circle(ankle,0.65,Color(0.3,0.5,1.0))
'''+boots,1)
p.write_text(s,encoding="utf-8")
for needle in ("_pc28_knee_target","_pc28_draw_articulated_leg","PC28_LEGACY_KNEE","PC28_SHOW_KNEES"):
    if needle not in s:
        raise SystemExit("PC28 postpatch invariant missing: "+needle)
ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
if e.count("version/code=197")!=1 or e.count('version/name="0.22.0-PC27-BALANCED-GAIT"')!=1:
    raise SystemExit("PC28 expected PC27 baseline identity")
ep.write_text(e.replace("version/code=197","version/code=198",1).replace(
    'version/name="0.22.0-PC27-BALANCED-GAIT"',
    'version/name="0.22.0-PC28-ARTICULATED-KNEES"',1),encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.exists():
    q=save.read_text(encoding="utf-8")
    a='const GAME_VERSION := "0.22.0-PC27-BALANCED-GAIT"'
    if q.count(a)!=1:
        raise SystemExit("PC28 expected save baseline")
    save.write_text(q.replace(a,'const GAME_VERSION := "0.22.0-PC28-ARTICULATED-KNEES"',1),encoding="utf-8")
print("PC28 genuine 2-bone upper/shin cutout: hip/knee/ankle joints, forward knee selection; APK 198")
