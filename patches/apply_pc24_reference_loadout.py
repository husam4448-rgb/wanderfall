#!/usr/bin/env python3
"""PC24: detailed survival reference outfit; preserve PC23 skeletal geometry.

The reference sprites depict vest, backpack, detailed trousers, and boots
WITHOUT a helmet. Use available authored equipment layers as the initial
showcase loadout rather than judging an undressed silhouette against them.
All equipment toggles remain independent and functional. An env var retains
the original undressed start for regression comparisons.

This is deliberately a visual/preset pass, NOT final visual approval.
"""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.is_file():
    raise SystemExit("PC24 requires reconstructed PC23 runtime")
s=runtime.read_text(encoding="utf-8")

ready_anchor='    if OS.has_environment("ARM_CAPTURE_DIR"):\n'
if s.count(ready_anchor)!=1:
    raise SystemExit("PC24 unique ready/capture anchor missing")
ready_preset='''    # PC24: the approved male/female reference is a dressed survivor, not
    # the unequipped base body. Load existing authentic authored equipment
    # at startup as a coherent showcase outfit; UI can still remove each item.
    # The old unarmored/default state remains reproducible for regression.
    if not OS.has_environment("PC24_UNEQUIPPED_START"):
        gear_head = false
        gear_torso = true
        gear_back = true
        gear_legs = true
        gear_boots = true
        gear_gloves = true
    _refresh_gear_buttons()
'''
s=s.replace(ready_anchor,ready_preset+ready_anchor,1)

capture_anchor='''    pc22_prev_arm_valid = false
    _refresh_gear_buttons()
    _apply_visual_zoom()
    queue_redraw()
'''
if s.count(capture_anchor)!=1:
    raise SystemExit("PC24 unique capture finalization anchor missing")
capture_override='''    # Run a second capture against the dressed reference without altering
    # PC23 legacy baseline captures or NPC role inheritances.
    if OS.get_environment("PC24_REFERENCE_OUTFIT_CAPTURE") == "1" and pc22_role.is_empty():
        gear_head = false
        gear_torso = true
        gear_back = true
        gear_legs = true
        gear_boots = true
        gear_gloves = true
'''
s=s.replace(capture_anchor,capture_override+capture_anchor,1)

old_title='PC23 HUMANOID RIG CALIBRATION | REFERENCE OVERLAY + JOINTS:'
new_title='PC23 HUMANOID RIG CALIBRATION | PC24 REFERENCE OUTFIT:'
if s.count(old_title)!=1:
    raise SystemExit("PC24 title anchor missing")
s=s.replace(old_title,new_title,1)
runtime.write_text(s,encoding="utf-8")

ep=root/"export_presets.cfg"
txt=ep.read_text(encoding="utf-8")
txt,n=re.subn(r'(?m)^version/code=193$','version/code=194',txt,count=1)
if n!=1:
    raise SystemExit("PC24 version code anchor missing")
txt,n=re.subn(r'(?m)^version/name="0.22.0-PC23-RIG-CALIBRATION"$',
               'version/name="0.22.0-PC24-REFERENCE-LOADOUT"',txt,count=1)
if n!=1:
    raise SystemExit("PC24 version name anchor missing")
ep.write_text(txt,encoding="utf-8")
sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    s2=sm.read_text(encoding="utf-8")
    s2,n=re.subn(r'const GAME_VERSION := "0.22.0-PC23-RIG-CALIBRATION"',
                 'const GAME_VERSION := "0.22.0-PC24-REFERENCE-LOADOUT"',s2,count=1)
    if n!=1:
        raise SystemExit("PC24 save version anchor missing")
    sm.write_text(s2,encoding="utf-8")

verify=runtime.read_text(encoding="utf-8")
for token in ("PC24_UNEQUIPPED_START","PC24_REFERENCE_OUTFIT_CAPTURE",
              "pc23_humanoid_rig_system.gd","pc23_calibration_enabled"):
    if token not in verify:
        raise SystemExit("PC24 postpatch invariant failed: "+token)
print("PC24 reference survivor loadout: detailed authentic equipment on both sexes; helmet off")
print("Optional PC24_UNEQUIPPED_START restores original unarmored launch.")
print("Separate dressed-reference QA via PC24_REFERENCE_OUTFIT_CAPTURE=1.")
