#!/usr/bin/env python3
"""PC30 Phase A: weapon hand and wrist use one anatomical contact transform.

The PC23 rig derives wrists from the *unrotated* aiming angle, while the
rendered gun-grip hand is rotated by palm_rotation_offset() (rifle -18 degrees).
This produces a real disconnect between wrist joint and wrist pixels.
Use the exact same angle for both and preserve all original bone lengths,
shoulder anchors and pistol/rifle grips. Legacy side-by-side captured with
PC30_LEGACY_PALM_IK=1. Run AFTER PC29 knee patch.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'game')
rig=root/"scripts/art/pc23_humanoid_rig_system.gd"
if not rig.is_file():
    raise SystemExit("PC30 requires reconstructed PC29 PC23 rig")
s=rig.read_text(encoding="utf-8")
old='''    return {
        "pivot":pivot,
        "dominant_grip":dominant_grip,
        "support_grip":support_grip,
        "dominant_wrist":wrist_from_grip(dominant_grip,angle,dir_sign,false),
        "support_wrist":wrist_from_grip(support_grip,angle,dir_sign,true)
    }
'''
new='''    # PC30 single-source wrist/palm transform. Palm artwork is rotated by
    # palm_rotation_offset() at render time. The true anatomical wrist MUST
    # use that same transform or the painted wrist separates from the bone.
    var use_legacy: bool = OS.get_environment("PC30_LEGACY_PALM_IK") == "1"
    var dominant_angle: float = angle if use_legacy else angle+palm_rotation_offset(weapon_id,false)
    var support_angle: float = angle if use_legacy else angle+palm_rotation_offset(weapon_id,true)
    return {
        "pivot":pivot,
        "dominant_grip":dominant_grip,
        "support_grip":support_grip,
        "dominant_wrist":wrist_from_grip(dominant_grip,dominant_angle,dir_sign,false),
        "support_wrist":wrist_from_grip(support_grip,support_angle,dir_sign,true)
    }
'''
if s.count(old)!=1:
    raise SystemExit("PC30 wrist contract source mismatch; refusing speculative rewrite")
rig.write_text(s.replace(old,new,1),encoding="utf-8")
# The existing runtime already renders the hand at aim+palm_rotation_offset.
runtime=root/"scripts/art/d2d29_minimal_token_runtime.gd"
rt=runtime.read_text(encoding="utf-8")
for text in ("pc23_dom_hand_angle: float = pc22_arm_angle + pc22_player_arm_rig.palm_rotation_offset",
             "pc23_support_hand_angle: float = pc22_arm_angle + pc22_player_arm_rig.palm_rotation_offset",
             "_pc22_v3_draw_rig_grip_hand"):
    if text not in rt:
        raise SystemExit("PC30 runtime does not derive artwork from palm contact: "+text)
# Prevent a misleading output whose source version is still PC29.
ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
old_version='version/name="0.22.0-PC29-KNEE-STANCE"'
if e.count("version/code=200")!=1 or e.count(old_version)!=1:
    raise SystemExit("PC30 expected last verified PC29 APK version 200")
e=e.replace("version/code=200","version/code=201",1).replace(old_version,
    'version/name="0.22.0-PC30-WRIST-GRIP-CONTRACT"',1)
ep.write_text(e,encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.exists():
    v=save.read_text(encoding="utf-8")
    previous='const GAME_VERSION := "0.22.0-PC29-KNEE-STANCE"'
    if v.count(previous)!=1:
        raise SystemExit("PC30 save baseline version mismatch")
    save.write_text(v.replace(previous,
        'const GAME_VERSION := "0.22.0-PC30-WRIST-GRIP-CONTRACT"',1),
        encoding="utf-8")
print("PC30 wrist/grip transform aligned to actual rendered palm for both sexes/facings.")
print("PC30_LEGACY_PALM_IK=1 enables old disconnected-wrist geometry for A/B review.")
