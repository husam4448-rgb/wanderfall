#!/usr/bin/env python3
"""PC37 Phase 1: one user-request / presented pose controller.

PC34 demonstrated discontinuity and female unreachable rifle angles. PC36
still draws the gun at impossible angles while head, torso and shot logic
solve separate aim requests. This guarded first reconstruction establishes a
SINGLE upper-body aim state which drives the rifle silhouette, both wrists,
head and body lean. Requests beyond the conservative verified region do not
pretend to be possible: muzzle stays at the safe pose and firing is blocked.
The safe envelope is provisional; this is not final visual acceptance.
PC37_LEGACY_AIM=1 restores PC36 visuals for A/B comparison.

Run AFTER the PC36 coordinated upper-body patch.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/d2d29_minimal_token_runtime.gd"
if not p.exists():raise SystemExit("Missing reconstructed PC36 runtime")
s=p.read_text(encoding="utf8")
def put(a,b,tag):
    global s
    n=s.count(a)
    if n!=1:raise SystemExit(f"PC37 {tag} expected one anchor, found {n}")
    s=s.replace(a,b,1)
pose=root/"scripts/art/pc37_aim_pose_2d.gd"
pose.write_text('''extends RefCounted
# PC37 provisional safety gate. PC34 full-alpha search identified female
# fixed-body unreachable sectors beginning at +36 degrees screen-down.
# Until a physically verified alternate pose is available, never display or
# fire at a fabricated steep-down shoulder pose.
const RIFLE_DOWN_LIMIT: float = 0.4886921905584123 # 28 degrees, conservative
const RIFLE_UP_LIMIT: float = 1.2217304763960306   # 70 degrees
const ORIGINAL_LIMIT: float = PI*0.49

static func resolve(request: Vector2, rifle: bool) -> Dictionary:
    var asked: float = clampf(atan2(request.y,maxf(absf(request.x),0.001)), -ORIGINAL_LIMIT, ORIGINAL_LIMIT)
    var shown: float = clampf(asked,-RIFLE_UP_LIMIT,RIFLE_DOWN_LIMIT) if rifle else asked
    var blocked: bool = rifle and absf(asked-shown)>0.0001
    var blend: float = smoothstep(0.08,RIFLE_DOWN_LIMIT,shown) if rifle else 0.0
    var state: String = "BLOCKED" if blocked else "LOW_READY" if shown>0.23 and rifle else "SHOULDERED" if rifle else "PISTOL"
    return {"requested_angle":asked,"angle":shown,"blocked":blocked,
            "body_blend":blend,"state":state}
''',encoding="utf8")
constline='const PC22CanonicalArmSystemScript = preload("res://scripts/art/pc23_humanoid_rig_system.gd")\n'
put(constline,constline+'const PC37AimPose2D = preload("res://scripts/art/pc37_aim_pose_2d.gd")\n','preload')
shot='''func _trigger_player_shot() -> void:
    shot_recoil = 1.0'''
put(shot,'''func _trigger_player_shot() -> void:
    # The same shared aim feasibility controller is used for rendering AND
    # gameplay. Never emit recoil/flash when the long gun cannot be posed.
    var resolved: Dictionary = PC37AimPose2D.resolve(aim_pos-actor_pos,weapon_visible and weapon_two_handed)
    if OS.get_environment("PC37_LEGACY_AIM") != "1" and bool(resolved["blocked"]):
        shot_recoil = 0.0
        shot_flash = 0.0
        queue_redraw()
        return
    shot_recoil = 1.0''','fire gate')
base='''    var base := actor_pos + Vector2(sway, -bob - breath * 0.28)
'''
put(base,base+'''    # Exactly one aim state is shared by shoulder-clavicle body, head,
    # dominant/support grips, rifle artwork and firing logic.
    var pc37_pose: Dictionary = PC37AimPose2D.resolve(aim_pos-base,weapon_visible and weapon_two_handed)
    if OS.get_environment("PC37_LEGACY_AIM") == "1":
        pc37_pose = {"angle":clampf(atan2(aim_pos.y-base.y,maxf(absf(aim_pos.x-base.x),0.001)),-PI*0.49,PI*0.49),
                     "blocked":false,"body_blend":smoothstep(0.28,1.18,clampf(atan2(aim_pos.y-base.y,maxf(absf(aim_pos.x-base.x),0.001)),-PI*0.49,PI*0.49)),"state":"LEGACY"}
''','aim pose owner')
old='''    var pc36_aim_angle: float = clampf(Vector2(absf(pc36_aim_vec.x),pc36_aim_vec.y).angle(),-PI*0.49,PI*0.49)'''
put(old,'''    var pc36_aim_angle: float = float(pc37_pose["angle"])''','torso follows same state')
old='''    var pc36_weight: float = smoothstep(0.28,1.18,pc36_aim_angle) if pc36_pose_enabled else 0.0'''
put(old,'''    var pc36_weight: float = float(pc37_pose["body_blend"]) if pc36_pose_enabled else 0.0''','lean follows state')
old='''    var pc22_arm_angle: float = clampf(pc22_local_aim.angle(),-PI*0.49,PI*0.49)'''
put(old,'''    var pc22_arm_angle: float = float(pc37_pose["angle"])''','hand IK shares angle')
old='''    var head_tilt := clampf(atan2(head_aim_vec.y, maxf(abs(head_aim_vec.x), 0.001)), -0.34, 0.34)'''
put(old,'''    var head_tilt := clampf(atan2(head_aim_vec.y,maxf(absf(head_aim_vec.x),0.001)),-0.34,0.34) if OS.get_environment("PC37_LEGACY_AIM") == "1" else clampf(float(pc37_pose["angle"]), -0.34, 0.34)''','neck aim shares angle')
old='''    var angle := clampf(local_aim.angle(), -PI * 0.49, PI * 0.49)'''
put(old,'''    var angle := float(pc37_pose["angle"])''','secondary aim layer')
old='''        if shot_flash > 0.02:'''
put(old,'''        if shot_flash > 0.02 and not bool(pc37_pose["blocked"]):''','shot visual consistency')
# An explicit blocked visual indicator avoids misleading player about aim.
marker='''    _pc23_draw_calibration_overlay(base,dir_sign,pc22_rear_shoulder,pc22_front_shoulder,pc22_rear_elbow,pc22_front_elbow,pc22_dom_wrist,pc22_front_wrist,pc22_dom_grip,pc22_support_grip,pc23_weapon_id)'''
put(marker,marker+'''
    if bool(pc37_pose["blocked"]):
        var denied_point: Vector2 = aim_pos
        draw_line(denied_point+Vector2(-4.0,-4.0),denied_point+Vector2(4.0,4.0),Color(0.96,0.27,0.22,0.9),1.5)
        draw_line(denied_point+Vector2(-4.0,4.0),denied_point+Vector2(4.0,-4.0),Color(0.96,0.27,0.22,0.9),1.5)
''','blocked target')
p.write_text(s,encoding="utf8")
# The shared state also blocks the PC33 solver from independently computing
# an impossible down-angle; PC33 sees the same safe presented angle.
assert "pc37_pose" in s and 'PC37AimPose2D.resolve' in s
print("PC37 shared aim pose and blocked fire/flash installed; documented conservative rifle down-angle gate (28 degrees)")
