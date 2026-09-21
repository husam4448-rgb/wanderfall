#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
visual_path = root / "scripts/art/production_survivor_visual.gd"
if not visual_path.is_file():
    raise SystemExit(f"Missing D2B.18 target: {visual_path}")
s = visual_path.read_text(encoding="utf-8")

def replace_func(src: str, name: str, body: str) -> str:
    start_token = f"func {name}("
    start = src.find(start_token)
    if start < 0:
        raise SystemExit(f"D2B.18 function not found: {name}")
    nxt = src.find("\nfunc ", start + len(start_token))
    if nxt < 0:
        nxt = len(src)
    return src[:start] + body.rstrip() + "\n\n" + src[nxt+1 if nxt < len(src) else nxt:]

draw_func = r'''func _draw() -> void:
    if _pose.is_empty():
        return

    var aim: Vector2 = _pose["aim"]
    var side: float = _pose["side"]
    var backness: float = _pose["backness"]
    var p_x: float = _pose["perspective_x"]

    var l_hip: Vector2 = _pose["l_hip"]
    var r_hip: Vector2 = _pose["r_hip"]
    var l_knee: Vector2 = _pose["l_knee"]
    var r_knee: Vector2 = _pose["r_knee"]
    var l_ankle: Vector2 = _pose["l_ankle"]
    var r_ankle: Vector2 = _pose["r_ankle"]
    var ls: Vector2 = _pose["ls"]
    var rs: Vector2 = _pose["rs"]
    var le: Vector2 = _pose["le"]
    var re: Vector2 = _pose["re"]
    var lw: Vector2 = _pose["lw"]
    var rw: Vector2 = _pose["rw"]
    var torso_center: Vector2 = _pose["torso_center"]
    var head_center: Vector2 = _pose["head_center"]

    # Direction visibility rules requested for D2B.18:
    # pure up     -> both arms underneath torso/head
    # pure side   -> only near arm visible
    # diagonals/down -> both arms visible
    var pure_up := aim.y < -0.86 and absf(aim.x) < 0.34
    var pure_side := absf(aim.x) > 0.86 and absf(aim.y) < 0.34

    # Side-view leg order follows torso depth instead of a front-facing gait order.
    if absf(side) > 0.70:
        if side > 0.0:
            _draw_leg(l_hip, l_knee, l_ankle, false)
            _draw_leg(r_hip, r_knee, r_ankle, true)
        else:
            _draw_leg(r_hip, r_knee, r_ankle, false)
            _draw_leg(l_hip, l_knee, l_ankle, true)
    elif sin(gait_phase) >= 0.0:
        _draw_leg(r_hip, r_knee, r_ankle, false)
        _draw_leg(l_hip, l_knee, l_ankle, true)
    else:
        _draw_leg(l_hip, l_knee, l_ankle, false)
        _draw_leg(r_hip, r_knee, r_ankle, true)

    # Back-layer arms are painted before torso/head.
    if pure_up:
        _draw_shoulder_bridge(torso_center, ls, -1.0, p_x, false)
        _draw_upper_arm(ls, le, false)
        _draw_forearm_hand(le, lw, false)
        _draw_shoulder_bridge(torso_center, rs, 1.0, p_x, false)
        _draw_upper_arm(rs, re, false)
        _draw_forearm_hand(re, rw, false)
    elif pure_side:
        # Hide the far arm completely beneath the body; only the near arm is
        # brought forward later.
        if side > 0.0:
            _draw_shoulder_bridge(torso_center, ls, -1.0, p_x, false)
            _draw_upper_arm(ls, le, false)
            _draw_forearm_hand(le, lw, false)
        else:
            _draw_shoulder_bridge(torso_center, rs, 1.0, p_x, false)
            _draw_upper_arm(rs, re, false)
            _draw_forearm_hand(re, rw, false)
    else:
        # Diagonal/down: establish shoulder roots behind torso so the visible
        # arms still feel physically attached when redrawn in front.
        _draw_shoulder_bridge(torso_center, ls, -1.0, p_x, false)
        _draw_shoulder_bridge(torso_center, rs, 1.0, p_x, false)

    _draw_backpack(torso_center, p_x, side, backness)
    _draw_neck(head_center, torso_center, side, backness, p_x)
    _draw_torso(torso_center, p_x, side, backness)
    _draw_head(head_center, side, backness)

    # Foreground arm pass obeys direction-specific visibility.
    if pure_up:
        # Nothing: torso/head deliberately occlude both arms.
        pass
    elif pure_side:
        if side > 0.0:
            _draw_shoulder_bridge(torso_center, rs, 1.0, p_x, true)
            _draw_upper_arm(rs, re, true)
            _draw_forearm_hand(re, rw, true)
        else:
            _draw_shoulder_bridge(torso_center, ls, -1.0, p_x, true)
            _draw_upper_arm(ls, le, true)
            _draw_forearm_hand(le, lw, true)
    else:
        _draw_shoulder_bridge(torso_center, ls, -1.0, p_x, true)
        _draw_upper_arm(ls, le, true)
        _draw_forearm_hand(le, lw, true)
        _draw_shoulder_bridge(torso_center, rs, 1.0, p_x, true)
        _draw_upper_arm(rs, re, true)
        _draw_forearm_hand(re, rw, true)
'''

update_pose = r'''func _update_pose() -> void:
    var moving := move_velocity.length() > 2.0
    var move_dir := move_velocity.normalized() if moving else facing
    if move_dir.length_squared() <= 0.0001:
        move_dir = Vector2.DOWN

    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var side := clampf(aim.x, -1.0, 1.0)
    var profile := absf(side)
    var backness := clampf(-aim.y, 0.0, 1.0)

    var wave := sin(gait_phase) if moving else 0.0
    var lift_wave := absf(cos(gait_phase)) if moving else 0.0
    var breath := sin(idle_phase) * 0.30 if not moving else 0.0

    var stride := 6.8 if sprinting else (2.8 if crouching else 4.6)
    var body_bob := -(absf(sin(gait_phase)) * (1.55 if sprinting else 0.82)) if moving else breath
    if crouching:
        body_bob += 3.0

    var lean := move_dir * (1.25 if sprinting else 0.55) if moving else Vector2.ZERO
    if crouching:
        lean *= 0.45

    var perspective_x := lerpf(1.0, 0.62, profile)
    var shoulder_half := lerpf(8.2, 2.85, profile)
    var hip_half := lerpf(4.15, 1.75, profile)
    var hip_y := 6.0 + body_bob
    var shoulder_y := -8.3 + body_bob

    var l_phase := wave
    var r_phase := -wave
    var l_stride := l_phase * stride
    var r_stride := r_phase * stride
    var lateral := Vector2(-move_dir.y, move_dir.x)

    # Rotate the entire lower body into profile with the torso, not only the feet.
    # Side aim narrows X separation and introduces depth separation in Y.
    var leg_depth := side * profile * 1.75
    var knee_half := lerpf(3.8, 1.35, profile)
    var ankle_half := lerpf(4.15, 1.45, profile)

    var l_hip := Vector2(-hip_half, hip_y + leg_depth)
    var r_hip := Vector2(hip_half, hip_y - leg_depth)
    var l_knee := Vector2(-knee_half, 17.0 + body_bob + leg_depth * 0.72)
    var r_knee := Vector2(knee_half, 17.0 + body_bob - leg_depth * 0.72)
    var l_ankle := Vector2(-ankle_half, 31.0 + leg_depth * 0.42)
    var r_ankle := Vector2(ankle_half, 31.0 - leg_depth * 0.42)

    if moving:
        l_knee += move_dir * l_stride * 0.48 + lateral * l_stride * 0.10
        r_knee += move_dir * r_stride * 0.48 + lateral * r_stride * 0.10
        if l_phase < 0.0:
            l_knee.y += lift_wave * 1.9
        if r_phase < 0.0:
            r_knee.y += lift_wave * 1.9

        l_ankle += move_dir * l_stride
        r_ankle += move_dir * r_stride
        if l_phase < 0.0:
            l_ankle.y -= lift_wave * (2.0 if sprinting else 1.3)
        if r_phase < 0.0:
            r_ankle.y -= lift_wave * (2.0 if sprinting else 1.3)

    if crouching:
        l_knee.y += 2.4
        r_knee.y += 2.4
        l_ankle.y -= 1.0
        r_ankle.y -= 1.0

    var torso_center := Vector2(side * 0.68, -2.0 + body_bob) + lean * 0.30
    var head_center := Vector2(side * 0.95, -19.2 + body_bob * 0.55) + lean * 0.18

    var depth_offset := profile * 2.0
    var ls := Vector2(torso_center.x - shoulder_half, shoulder_y + side * depth_offset) + lean
    var rs := Vector2(torso_center.x + shoulder_half, shoulder_y - side * depth_offset) + lean

    var pts := _arm_points(ls, rs, body_bob)
    var le: Vector2 = pts[0]
    var lw: Vector2 = pts[1]
    var re: Vector2 = pts[2]
    var rw: Vector2 = pts[3]

    _last_lw = lw
    _last_rw = rw

    _pose = {
        "aim": aim,
        "side": side,
        "backness": backness,
        "perspective_x": perspective_x,
        "torso_center": torso_center,
        "head_center": head_center,
        "l_hip": l_hip,
        "r_hip": r_hip,
        "l_knee": l_knee,
        "r_knee": r_knee,
        "l_ankle": l_ankle,
        "r_ankle": r_ankle,
        "ls": ls,
        "rs": rs,
        "le": le,
        "re": re,
        "lw": lw,
        "rw": rw
    }
    queue_redraw()
'''

leg_func = r'''func _draw_leg(hip: Vector2, knee: Vector2, ankle: Vector2, front: bool) -> void:
    var thigh_w := 6.2
    var shin_w := 5.7
    var pants := C_PANTS_LITE if front else C_PANTS
    _draw_segment(hip, knee, thigh_w, pants, C_OUTLINE)
    _draw_segment(knee, ankle, shin_w, C_PANTS, C_OUTLINE)

    var kd := (ankle-hip).normalized()
    var kn := Vector2(-kd.y,kd.x)
    draw_line(knee-kn*2.0, knee+kn*2.0, C_STITCH, 0.60, false)
    draw_circle(knee, 1.3, C_PANTS_LITE, false)

    var shin_dir := (ankle-knee).normalized()
    if shin_dir.length_squared() < 0.001:
        shin_dir = Vector2.DOWN
    var shin_n := Vector2(-shin_dir.y, shin_dir.x)

    # Thick boot cuff / ankle mass prevents the foot from reading as a flat arrow.
    var cuff_top := ankle - shin_dir * 3.0
    var cuff_bottom := ankle + shin_dir * 0.7
    draw_line(cuff_top, cuff_bottom, C_OUTLINE, 8.0, true)
    draw_line(cuff_top, cuff_bottom, C_BOOT, 6.4, true)
    draw_circle(ankle, 3.15, C_BOOT, false)

    # Broad, truncated toe instead of a thin point.
    var face_dir := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var toe_dir := Vector2(face_dir.x*0.92, maxf(0.18, face_dir.y)).normalized()
    if face_dir.y < -0.35:
        toe_dir = Vector2(face_dir.x*0.82, -0.38).normalized()

    var foot_n := Vector2(-toe_dir.y, toe_dir.x)
    var heel := ankle - toe_dir * 1.6
    var toe_base := ankle + toe_dir * 4.25
    var toe_tip := ankle + toe_dir * 5.45

    var boot := PackedVector2Array([
        heel - foot_n*3.35,
        toe_base - foot_n*3.05,
        toe_tip - foot_n*2.15,
        toe_tip + foot_n*2.15,
        toe_base + foot_n*3.05,
        heel + foot_n*3.35
    ])
    draw_polygon(boot, PackedColorArray([C_BOOT]))
    draw_polyline(_closed(boot), C_OUTLINE, 1.05, false)

    # Sole and toe cap reinforce thickness.
    draw_line(heel + foot_n*2.75, toe_tip + foot_n*1.75, C_OUTLINE, 1.05, false)
    draw_line(toe_base - foot_n*2.45, toe_base + foot_n*2.45, C_STITCH, 0.65, false)
'''

arm_points = r'''func _arm_points(ls: Vector2, rs: Vector2, body_y: float) -> Array:
    var category := _weapon_category()
    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var perp := Vector2(-aim.y, aim.x)

    if melee_time > 0.0:
        var progress := 1.0 - melee_time / MELEE_DURATION
        var attack := melee_direction.rotated(lerpf(-0.85, 0.92, sin(progress * PI * 0.5)))
        var ap := Vector2(-attack.y, attack.x)
        var rw := Vector2(0.0, -3.0 + body_y) + attack * 15.5
        var re := rs.lerp(rw, 0.56) - ap * 4.7
        var lw := Vector2(0.0, -2.5 + body_y) + attack * 8.4 + ap * 2.7
        var le := ls.lerp(lw, 0.53) + ap * 3.7
        return [le, lw, re, rw]

    if category == "firearm":
        # Slightly extend the gun-hand position so the enlarged pistol barrel
        # visibly clears the hands/body while retaining the two-hand grip.
        var hand_center := Vector2(0.0, -4.2 + body_y) + aim * 13.15
        var grip := hand_center - perp * 0.70
        var support := hand_center + aim * 1.10 + perp * 0.90

        var re := rs.lerp(grip, 0.52) - perp * 3.55 - aim * 1.10
        var le := ls.lerp(support, 0.52) + perp * 3.55 - aim * 1.10

        var profile := absf(aim.x)
        re += Vector2(0.0, -aim.x * profile * 0.9)
        le += Vector2(0.0, aim.x * profile * 0.9)
        return [le, support, re, grip]

    if category == "melee":
        var center := Vector2(0.0, -2.5 + body_y) + aim * 10.8
        var lw := center + perp * 2.5
        var rw := center - perp * 2.5
        return [
            ls.lerp(lw, 0.52) + perp * 3.7,
            lw,
            rs.lerp(rw, 0.52) - perp * 3.7,
            rw
        ]

    var moving := move_velocity.length() > 2.0
    var swing := sin(gait_phase) * (4.6 if sprinting else 3.4) if moving else 0.0
    return [
        Vector2(-8.1, 1.0 + body_y + swing * 0.35),
        Vector2(-6.9, 9.3 + body_y + swing),
        Vector2(8.1, 1.0 + body_y - swing * 0.35),
        Vector2(6.9, 9.3 + body_y - swing)
    ]
'''

s = replace_func(s, "_draw", draw_func)
s = replace_func(s, "_update_pose", update_pose)
s = replace_func(s, "_draw_leg", leg_func)
s = replace_func(s, "_arm_points", arm_points)
visual_path.write_text(s, encoding="utf-8")

# Make the pistol/weapon a little taller and more readable without changing
# the character scale. Non-uniform Y growth adds body to the pistol silhouette.
player_path = root / "scripts/player.gd"
if not player_path.is_file():
    raise SystemExit("D2B.18 player.gd missing")
player = player_path.read_text(encoding="utf-8")
if "_weapon_visual.scale = Vector2(0.56, 0.56)" in player:
    player = player.replace(
        "_weapon_visual.scale = Vector2(0.56, 0.56)",
        "_weapon_visual.scale = Vector2(0.60, 0.66)",
        1,
    )
elif "_weapon_visual.scale = Vector2(0.60, 0.66)" not in player:
    raise SystemExit("D2B.18 expected D2B.17 weapon scale anchor missing")
player_path.write_text(player, encoding="utf-8")

# Android update version; preserve package ID and persistent signing chain.
preset = root / "export_presets.cfg"
if not preset.is_file():
    raise SystemExit("D2B.18 export_presets.cfg missing")
ep = preset.read_text(encoding="utf-8")
ep, n_code = re.subn(r'(?m)^version/code=28$', 'version/code=29', ep, count=1)
ep, n_name = re.subn(r'(?m)^version/name="0\.19\.0D2B\.17"$', 'version/name="0.19.0D2B.18"', ep, count=1)
if not n_code:
    raise SystemExit("D2B.18 version/code 28 anchor missing")
if not n_name:
    raise SystemExit("D2B.18 version/name anchor missing")
if 'package/unique_name="org.wanderfall.game"' not in ep:
    raise SystemExit("D2B.18 package identity changed unexpectedly")
preset.write_text(ep, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.19.0D2B.17"', 'const GAME_VERSION := "0.19.0D2B.18"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.19.0D2B.18: directional arm occlusion, side single-arm pose, lower-body rotation, thick boots and taller firearm.")
