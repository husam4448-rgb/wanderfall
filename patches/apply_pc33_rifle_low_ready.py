#!/usr/bin/env python3
"""PC33: collision-aware 2D shouldered-to-low-ready rifle transition.

PC32 rotates a rifle around a static trigger grip. On screen-down aiming its
stock swings upward through the survivor's reference-measured head region.
A rifle cannot remain shouldered under such a rotation without crossing
the neck/face. This solves the *whole weapon-and-both-hands* downward
translation needed for the stock-to-grip segment to clear a conservative
head ellipse. All weapon contacts, muzzle direction and arm IK remain owned
by one shared target transform. No arbitrary elbow/shoulder offsets.

Original PC32 gun posture: PC33_LEGACY_RIFLE_POSE=1.
Run AFTER apply_pc32_authored_arm_bones.py.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
rig=root/"scripts/art/pc23_humanoid_rig_system.gd"
source=rig.read_text(encoding="utf-8")
needle='func weapon_targets(base: Vector2, angle: float, dir_sign: float, recoil: float, weapon_id: String = "rifle") -> Dictionary:\n'
if source.count(needle)!=1:
    raise SystemExit("PC33 cannot locate single shared weapon target method")
function='''func pc33_stock_head_margin(grip_local: Vector2, aim_angle: float, facing: float, downward_shift: float) -> float:
    # x radius 8 and y radius 8.4 cover the approved side-profile head with
    # conservative optic/stock clearance. Only local body space is used:
    # the head silhouette and aim both remain mirrored correctly.
    var stock: Vector2 = grip_local+pose_point(Vector2(-13.0,-1.3),aim_angle,facing)
    var hand: Vector2 = grip_local
    var closest: float = 100000.0
    for i in range(17):
        var t: float = float(i)/16.0
        var p: Vector2 = stock.lerp(hand,t)+Vector2(0.0,downward_shift)
        var normalized: float = Vector2(p.x/8.0,(p.y+24.0)/8.4).length()
        closest = minf(closest,normalized)
    return closest

func pc33_rifle_low_ready_drop(grip_local: Vector2, angle: float, facing: float) -> float:
    if angle <= 0.0:
        return 0.0
    # Preserve the original horizontal and high-angle shouldered pose.
    # When the swept rifle stock enters the head clearance envelope, solve
    # the smallest *body-local vertical move of the complete rifle rig*.
    var required: float = 1.15
    if pc33_stock_head_margin(grip_local,angle,facing,0.0) >= required:
        return 0.0
    var upper: float = 14.0
    if pc33_stock_head_margin(grip_local,angle,facing,upper) < required:
        return upper
    var lower: float = 0.0
    for i in range(16):
        var middle: float = (lower+upper)*0.5
        if pc33_stock_head_margin(grip_local,angle,facing,middle) >= required:
            upper = middle
        else:
            lower = middle
    return upper

'''
source=source.replace(needle,function+needle,1)
anchor='''        support_grip = dominant_grip+pose_point(Vector2(9.000000,2.000000),angle,dir_sign)'''
if source.count(anchor)!=1:
    raise SystemExit("PC33 rifle-only grip derived anchor not found")
source=source.replace(anchor,'''        # PC33 transitions shouldered rifle into anatomically feasible
        # screen-down low-ready by moving the weapon and BOTH hands together.
        # Weapon-local muzzle axis stays at the requested aim angle.
        if OS.get_environment("PC33_LEGACY_RIFLE_POSE") != "1":
            var drop: float = pc33_rifle_low_ready_drop(dominant_grip-base,angle,dir_sign)
            dominant_grip += Vector2(0.0,drop)
'''+anchor,1)
rig.write_text(source,encoding="utf-8")
runtime=root/"scripts/art/d2d29_minimal_token_runtime.gd"
rs=runtime.read_text(encoding="utf-8")
# Keep muzzle and rendered rifle placed from the same returned dominant_grip.
for token in ('pc22_dom_grip','_pc30_draw_fitted_rifle_piece','pc22_support_grip'):
    if token not in rs:
        raise SystemExit("PC33 shared transform source absent: "+token)
# Avoid stale elbow continuity when switching sharply between rifle/pistol or
# other animation states; do not rewrite previous tested IK path.
ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
a='version/name="0.22.0-PC32-AUTHORED-ARM-BONES"'
if e.count("version/code=204")!=1 or e.count(a)!=1:
    raise SystemExit("PC33 requires verified PC32 version 204")
ep.write_text(e.replace("version/code=204","version/code=205",1).replace(a,
    'version/name="0.22.0-PC33-RIFLE-LOW-READY"',1),encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.exists():
    q=save.read_text(encoding="utf-8")
    a='const GAME_VERSION := "0.22.0-PC32-AUTHORED-ARM-BONES"'
    if q.count(a)!=1:
        raise SystemExit("PC33 save version mismatch")
    save.write_text(q.replace(a,
        'const GAME_VERSION := "0.22.0-PC33-RIFLE-LOW-READY"',1),encoding="utf-8")
print("PC33 rifle stock clears the head by solving contact-preserving low-ready translation; pistol and 2D aim untouched.")
