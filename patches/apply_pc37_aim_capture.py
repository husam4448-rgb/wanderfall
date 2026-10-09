#!/usr/bin/env python3
"""PC37 25-frame per side, per sex actual Godot aim transition harness.

Captures 100 real engine frames covering a continuous requested 0..85 degree
down aim. Names preserve gender/facing/time progression and can be assembled
into GIFs. Current safe rifle gate blocks and holds before unreachable pitch.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=p.read_text(encoding="utf8")
old='''    if OS.get_environment("PC26_GAIT_CAPTURE") == "1":
        var phase_names := PackedStringArray()'''
new='''    if OS.get_environment("PC37_AIM_CAPTURE") == "1":
        var transition_names := PackedStringArray()
        for sex_name in ["male","female"]:
            for facing_name in ["right","left"]:
                for frame in range(25):
                    transition_names.append("%s_%s_%02d" % [sex_name,facing_name,frame])
        pc22_arm_capture_names = transition_names
        print("PC37_AIM_CAPTURE_PREPARED:",pc22_arm_capture_names.size())
    if OS.get_environment("PC26_GAIT_CAPTURE") == "1":
        var phase_names := PackedStringArray()'''
if s.count(old)!=1:raise SystemExit("PC37 aim harness capture preparation anchor mismatch")
s=s.replace(old,new,1)
old='''func _pc22_apply_arm_capture_state(idx: int) -> void:
    if OS.get_environment("PC26_GAIT_CAPTURE") == "1":'''
new='''func _pc22_apply_arm_capture_state(idx: int) -> void:
    if OS.get_environment("PC37_AIM_CAPTURE") == "1":
        var per_sex: int = 50
        var sex_id: int = int(idx/per_sex)
        var facing_id: int = int((idx%per_sex)/25)
        var frame: int = idx%25
        female_mode = sex_id == 1
        pc22_role = ""
        actor_pos = Vector2(640,360)
        visual_zoom = 5.5
        step_phase = 0.0
        move_vec = Vector2.ZERO
        running = false
        weapon_visible = true
        weapon_two_handed = true
        gear_head = false
        gear_torso = true
        gear_back = true
        gear_legs = true
        gear_boots = true
        gear_gloves = true
        shot_flash = 0.0
        shot_recoil = 0.0
        var ang: float = deg_to_rad(85.0*float(frame)/24.0)
        var side: float = -1.0 if facing_id == 1 else 1.0
        aim_pos = actor_pos+Vector2(side*250.0*cos(ang),250.0*sin(ang))
        pc22_prev_arm_valid = false
        _refresh_gear_buttons()
        _apply_visual_zoom()
        queue_redraw()
        return
    if OS.get_environment("PC26_GAIT_CAPTURE") == "1":'''
if s.count(old)!=1:raise SystemExit("PC37 aim capture branch mismatch")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf8")
print("PC37 100 actual Godot male/female mirrored aim transition frames enabled")
