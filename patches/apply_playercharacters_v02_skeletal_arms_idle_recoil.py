#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC02 requires PC01 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V01 | TWO-SIDE BASELINE:"' not in s:
    raise SystemExit("PC02 PC01 title anchor missing")

# ---------------------------------------------------------------
# STATE: breathing + recoil
# ---------------------------------------------------------------
anchor='var weapon_two_handed := true\n'
if anchor not in s:
    raise SystemExit("PC02 weapon state anchor missing")
s=s.replace(anchor,anchor+'var idle_phase := 0.0\nvar shot_recoil := 0.0\nvar shot_flash := 0.0\n',1)

# Continuous subtle idle phase and critically damped recoil decay.
proc_anchor='''    running = mag > 0.72
    var speed := RUN_SPEED if running else WALK_SPEED
'''
proc_new='''    running = mag > 0.72
    idle_phase += delta * 1.65
    shot_recoil = move_toward(shot_recoil, 0.0, delta * 7.5)
    shot_flash = move_toward(shot_flash, 0.0, delta * 13.0)
    var speed := RUN_SPEED if running else WALK_SPEED
'''
if proc_anchor not in s:
    raise SystemExit("PC02 process anchor missing")
s=s.replace(proc_anchor,proc_new,1)

# One discrete shot impulse on a new right-side aim touch/click. This is a
# visual test-harness shot; aim dragging remains unchanged.
screen_anchor='''            elif right_touch == -1:
                right_touch = e.index
                aim_pos = wp
'''
screen_new='''            elif right_touch == -1:
                right_touch = e.index
                aim_pos = wp
                _trigger_player_shot()
'''
if screen_anchor not in s:
    raise SystemExit("PC02 screen shot anchor missing")
s=s.replace(screen_anchor,screen_new,1)

mouse_anchor='''                else:
                    aim_pos = wp
'''
mouse_new='''                else:
                    aim_pos = wp
                    _trigger_player_shot()
'''
if mouse_anchor not in s:
    raise SystemExit("PC02 mouse shot anchor missing")
s=s.replace(mouse_anchor,mouse_new,1)

draw_anchor='func _draw() -> void:\n'
helper='''func _trigger_player_shot() -> void:
    shot_recoil = 1.0
    shot_flash = 1.0
    queue_redraw()

'''
if draw_anchor not in s:
    raise SystemExit("PC02 draw anchor missing")
s=s.replace(draw_anchor,helper+draw_anchor,1)

# ---------------------------------------------------------------
# IDLE BREATHING: very small vertical chest/body motion.
# Keep feet stable by not touching leg stride; only the actor root gets a
# sub-pixel breathing lift at idle.
# ---------------------------------------------------------------
actor_anchor='''    var sway: float = sin(step_phase) * (1.8 if running else 1.0) if moving else 0.0

    var face_right := aim_pos.x >= actor_pos.x
    var dir_sign := 1.0 if face_right else -1.0
    var base := actor_pos + Vector2(sway, -bob)
'''
actor_new='''    var sway: float = sin(step_phase) * (1.8 if running else 1.0) if moving else 0.0
    var breath := sin(idle_phase) * 0.42 if not moving else 0.0

    var face_right := aim_pos.x >= actor_pos.x
    var dir_sign := 1.0 if face_right else -1.0
    var base := actor_pos + Vector2(sway, -bob - breath * 0.28)
'''
if actor_anchor not in s:
    raise SystemExit("PC02 actor breathing anchor missing")
s=s.replace(actor_anchor,actor_new,1)

# ---------------------------------------------------------------
# TWO-BONE AUTHORED ARMS FOR BOTH MALE AND FEMALE.
# The existing textured arm sprites are reused; male is wider/longer, female
# slimmer. The IK keeps elbow geometry valid and wrists terminate at the hands.
# ---------------------------------------------------------------
func_start=s.find('func _draw_female_authored_arm(')
func_end=s.find('\nfunc _draw_support_hand(',func_start)
if func_start<0 or func_end<0:
    raise SystemExit("PC02 authored-arm helper block missing")
new_helper='''func _draw_player_authored_arm(shoulder: Vector2, wrist: Vector2, bend_sign: float, dir_sign: float, back_arm: bool) -> void:
    var elbow := _female_elbow_for(shoulder,wrist,bend_sign)
    var flip := dir_sign < 0.0
    var upper_tex := tex_female_gear_upper_arm if gear_torso else tex_female_upper_arm
    var fore_tex := tex_female_gear_forearm if gear_torso else tex_female_forearm

    # Distinct anatomy: male limbs are broader; female limbs are slimmer while
    # sharing the same safe two-bone joint solver.
    var upper_w := (8.8 if back_arm else 9.4) if female_mode else (10.1 if back_arm else 10.8)
    var fore_w := (7.8 if back_arm else 8.4) if female_mode else (9.0 if back_arm else 9.6)
    _draw_female_arm_part(upper_tex,shoulder,elbow,upper_w,flip)
    _draw_female_arm_part(fore_tex,elbow,wrist,fore_w,flip)

'''
s=s[:func_start]+new_helper+s[func_end+1:]

arm_insert_anchor='''    var hand_rear := pivot + _pose_point(Vector2(3,4), angle, dir_sign)
    var hand_front := pivot + _pose_point(Vector2(16,2), angle, dir_sign)

    # D2D.78: REAL authored RGBA 2D arms. No Line2D/draw_line limb bars.
'''
arm_insert='''    var hand_rear := pivot + _pose_point(Vector2(3,4), angle, dir_sign)
    var hand_front := pivot + _pose_point(Vector2(16,2), angle, dir_sign)

    # PC02: real textured upper-arm + forearm chains for BOTH protagonists.
    # Shoulders are gender-specific; wrists stay locked to weapon hand sockets.
    var rear_shoulder := base + Vector2(((5.3 if female_mode else 6.2) * dir_sign), (-8.0 if female_mode else -8.5) - breath * 0.25)
    var front_shoulder := base + Vector2(((3.0 if female_mode else 3.8) * dir_sign), (-5.0 if female_mode else -5.3) - breath * 0.20)
    var support_target := hand_front + _pose_point(Vector2(0,1.4),angle,dir_sign)
    _draw_player_authored_arm(rear_shoulder,hand_rear,-dir_sign,dir_sign,true)
    _draw_player_authored_arm(front_shoulder,support_target,dir_sign,dir_sign,false)

    # D2D.78: REAL authored RGBA 2D arms. No Line2D/draw_line limb bars.
'''
if arm_insert_anchor not in s:
    raise SystemExit("PC02 hand/arm insertion anchor missing")
s=s.replace(arm_insert_anchor,arm_insert,1)

# ---------------------------------------------------------------
# RECOIL: weapon/hands/arms already share the same hand sockets.
# Move the complete pivot backward a small amount along the weapon axis.
# ---------------------------------------------------------------
pivot_old='''    var angle := clampf(local_aim.angle(), -PI * 0.49, PI * 0.49)
    var pivot := base + Vector2(6.0 * dir_sign, -2)
'''
pivot_new='''    var angle := clampf(local_aim.angle(), -PI * 0.49, PI * 0.49)
    var pivot := base + Vector2(6.0 * dir_sign, -2) + _pose_point(Vector2(-1.45 * shot_recoil,0),angle,dir_sign)
'''
if pivot_old not in s:
    raise SystemExit("PC02 recoil pivot anchor missing")
s=s.replace(pivot_old,pivot_new,1)

# Muzzle flash uses the already-computed muzzle point and decays immediately.
weapon_anchor='''    draw_line(pivot + _pose_point(Vector2(5,2),angle,dir_sign),
              pivot + _pose_point(Vector2(3,9),angle,dir_sign),
              Color("2e3132"), 4.0, true)

    # Dominant/trigger hand is always present.
'''
weapon_new='''    draw_line(pivot + _pose_point(Vector2(5,2),angle,dir_sign),
              pivot + _pose_point(Vector2(3,9),angle,dir_sign),
              Color("2e3132"), 4.0, true)

    if shot_flash > 0.02:
        var flash_len := 5.0 * shot_flash
        var flash_tip := muzzle + _pose_point(Vector2(flash_len,0),angle,dir_sign)
        draw_line(muzzle,flash_tip,Color(1.0,0.78,0.28,0.85*shot_flash),2.0,true)
        draw_circle(muzzle,1.6*shot_flash,Color(1.0,0.92,0.55,0.75*shot_flash))

    # Dominant/trigger hand is always present.
'''
if weapon_anchor not in s:
    raise SystemExit("PC02 muzzle-flash anchor missing")
s=s.replace(weapon_anchor,weapon_new,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V01 | TWO-SIDE BASELINE:"',
    'title.text = "PLAYER CHARACTERS V02 | ARMS + IDLE + RECOIL:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V02 | ARMS + IDLE + RECOIL:',
    'func _draw_player_authored_arm(',
    '_draw_player_authored_arm(rear_shoulder,hand_rear',
    'var breath := sin(idle_phase) * 0.42',
    'shot_recoil = 1.0',
    'var flash_tip := muzzle',
):
    if needle not in s2:
        raise SystemExit("PC02 verification missing: "+needle)

# Explicit two-side regression guard.
if 'var face_right := aim_pos.x >= actor_pos.x' not in s2:
    raise SystemExit("PC02 lost Left/Right facing lock")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=168',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC02"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC02 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC02"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC02 textured two-bone arms enabled for male and female")
print("PC02 subtle idle breathing enabled")
print("PC02 shot impulse/recoil and muzzle flash enabled")
