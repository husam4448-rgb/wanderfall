#!/usr/bin/env python3
"""PC26: deterministic 8-phase complete gait capture from existing Godot rig.

Uses the actual _draw() and canonical skeleton for both sexes. Leaves player
movement, combat and equipment mechanics untouched in normal Android runtime.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'game')
p=root/'scripts/art/d2d29_minimal_token_runtime.gd'
if not p.is_file():
    raise SystemExit('PC26 requires PC25 reconstructed Godot runtime')
s=p.read_text(encoding='utf-8')
ready='    if OS.has_environment("ARM_CAPTURE_DIR"):\n'
if s.count(ready)!=1:
    raise SystemExit('PC26: arm capture setup anchor missing')
s=s.replace(ready,'''    if OS.get_environment("PC26_GAIT_CAPTURE") == "1":
        var phase_names := PackedStringArray()
        for sex_name in ["male","female"]:
            for gait_name in ["walk","run"]:
                for frame in range(8):
                    phase_names.append("%s_%s_%02d" % [sex_name,gait_name,frame])
        pc22_arm_capture_names = phase_names
        print("PC26_GAIT_CAPTURE_PREPARED:",pc22_arm_capture_names.size())
'''+ready,1)
anchor='func _pc22_apply_arm_capture_state(idx: int) -> void:\n'
if s.count(anchor)!=1:
    raise SystemExit('PC26: arm capture pose anchor missing')
extra='''func _pc26_apply_gait_capture_frame(idx: int) -> void:
    # 8 phases each for walking/running, male/female. Sequences have exactly
    # one period; frames 0 and 8 close the loop in exported GIF previews.
    var local_index: int = idx % 16
    female_mode = idx >= 16
    var gait_index: int = int(local_index / 8)
    var gait_frame: int = local_index % 8
    pc22_role = ""
    gear_head = false
    gear_torso = true
    gear_back = true
    gear_legs = true
    gear_boots = true
    gear_gloves = true
    actor_pos = Vector2(640,360)
    aim_pos = actor_pos+Vector2(250,0)
    visual_zoom = 5.5
    running = gait_index == 1
    move_vec = Vector2(1,0)
    step_phase = TAU*float(gait_frame)/8.0
    shot_recoil = 0.0
    shot_flash = 0.0
    weapon_visible = false
    weapon_two_handed = false
    pc22_prev_arm_valid = false
    _refresh_gear_buttons()
    _apply_visual_zoom()
    queue_redraw()

'''
s=s.replace(anchor,extra+anchor+'    if OS.get_environment("PC26_GAIT_CAPTURE") == "1":\n        _pc26_apply_gait_capture_frame(idx)\n        return\n',1)
p.write_text(s,encoding='utf-8')
if 'PC26_GAIT_CAPTURE_PREPARED:' not in s or 'func _pc26_apply_gait_capture_frame' not in s:
    raise SystemExit('PC26 runtime markers missing')
e=root/'export_presets.cfg'
txt=e.read_text(encoding='utf-8')
if txt.count('version/code=195')!=1 or txt.count('version/name="0.22.0-PC25-AUTHORED-SLEEVES"')!=1:
    raise SystemExit('PC26 baseline version anchors missing')
txt=txt.replace('version/code=195','version/code=196',1)
txt=txt.replace('version/name="0.22.0-PC25-AUTHORED-SLEEVES"',
                'version/name="0.22.0-PC26-GAIT-EVIDENCE"',1)
e.write_text(txt,encoding='utf-8')
sm=root/'scripts/save/save_manager.gd'
if sm.exists():
    x=sm.read_text(encoding='utf-8')
    if x.count('const GAME_VERSION := "0.22.0-PC25-AUTHORED-SLEEVES"')!=1:
        raise SystemExit('PC26 save version anchor missing')
    sm.write_text(x.replace('const GAME_VERSION := "0.22.0-PC25-AUTHORED-SLEEVES"',
                            'const GAME_VERSION := "0.22.0-PC26-GAIT-EVIDENCE"',1),encoding='utf-8')
print('PC26 32 deterministic live Godot gait frames enabled only for capture QA')
