#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/baked_actor_visual.gd"
s=p.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# D2D.10 tactical/isometric presentation pass.
# Goals:
# - tactical two-hand firearm stance while idle/walking/aiming
# - arms visibly extend IN FRONT of torso
# - directional head silhouette, not just moving eyes/nose
# - preserve torso/leg/foot mass in side views
# ---------------------------------------------------------------------------

# Preserve isometric body bulk instead of collapsing to paper-thin side profile.
repls={
    'var shoulder_w := lerpf(shoulder_w_base,3.2,profile) + chest_breath':
        'var shoulder_w := lerpf(shoulder_w_base,7.1,profile) + chest_breath',
    'var waist_w := lerpf(waist_w_base,3.7,profile)':
        'var waist_w := lerpf(waist_w_base,5.1,profile)',
    'var hip_w := lerpf(hip_w_base,3.5,profile)':
        'var hip_w := lerpf(hip_w_base,5.0,profile)',
    'var knee_half := lerpf(3.2,1.4,profile)':
        'var knee_half := lerpf(3.4,2.55,profile)',
    'var ankle_half := lerpf(3.8,1.25,profile)':
        'var ankle_half := lerpf(4.0,2.75,profile)',
    '_limb(hip,knee,shade,4.9,outline)':
        '_limb(hip,knee,shade,5.35,outline)',
    '_limb(knee,ankle,shade.darkened(0.02),4.45,outline)':
        '_limb(knee,ankle,shade.darkened(0.02),4.95,outline)',
}
for a,b in repls.items():
    if a not in s:
        raise SystemExit("D2D.10 body-bulk anchor missing: "+a)
    s=s.replace(a,b,1)

# Tactical armed stance: slight athletic knee bend and wider planted base when not moving.
anchor='''    if _weapon_category() == "firearm" and not moving and not crouching:
        var stance_knee_half := lerpf(3.0, 1.15, profile)
        var stance_ankle_half := lerpf(3.6, 1.05, profile)
        l_knee = _q(Vector2(-stance_knee_half,12.0+body_bob))
        r_knee = _q(Vector2( stance_knee_half,12.0+body_bob))
        l_ankle = _q(Vector2(-stance_ankle_half,21.0+body_bob))
        r_ankle = _q(Vector2( stance_ankle_half,21.0+body_bob))
        l_stride = 0.0
        r_stride = 0.0
'''
replacement='''    if _weapon_category() == "firearm" and not moving and not crouching:
        # Tactical ready stance: planted, slightly flexed knees, shoulder-width feet.
        var stance_knee_half := lerpf(3.8, 3.0, profile)
        var stance_ankle_half := lerpf(4.5, 3.4, profile)
        l_knee = _q(Vector2(-stance_knee_half,12.8+body_bob))
        r_knee = _q(Vector2( stance_knee_half,12.8+body_bob))
        l_ankle = _q(Vector2(-stance_ankle_half,20.8+body_bob))
        r_ankle = _q(Vector2( stance_ankle_half,20.8+body_bob))
        l_stride = 0.0
        r_stride = 0.0
'''
if anchor in s:
    s=s.replace(anchor,replacement,1)

# Replace armed arm solver with explicit tactical 8-direction presentation.
# The positions are still continuous using aim/perp, but enforce a minimum
# forward extension so wrists can never fold back onto the chest.
a=s.index("func _arm_pose(")
b=s.index("\nfunc _draw_head",a)
new_arm=r'''func _arm_pose(l_shoulder: Vector2, r_shoulder: Vector2, body_bob: float) -> Array:
    var category:=_weapon_category()
    var aim:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var perp:=Vector2(-aim.y,aim.x)
    var moving:=move_velocity.length()>2.0

    if melee_time > 0.0:
        var progress:=1.0-melee_time/MELEE_DURATION
        var swing:=lerpf(-0.95,0.95,sin(progress*PI*0.5))
        var attack_dir:=melee_direction.rotated(swing)
        var attack_perp:=Vector2(-attack_dir.y,attack_dir.x)
        var wrist:=_q(Vector2(0,-1+body_bob)+attack_dir*11.0)
        var elbow:=_q((r_shoulder+wrist)*0.5+attack_perp*4.0)
        var support_wrist:=_q(Vector2(0,1+body_bob)+attack_dir*5.5-attack_perp*3.0)
        var support_elbow:=_q((l_shoulder+support_wrist)*0.5-attack_perp*2.5)
        return [support_elbow,support_wrist,elbow,wrist]

    if category=="firearm":
        var wid:=_weapon_id().to_lower()
        var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)

        # Tactical isosceles-ish stance.
        # Hands are deliberately placed far in FRONT of chest along aim.
        var chest:=Vector2(0.0,-1.5+body_bob)
        var reach:=16.0 if rifle else 13.8
        if moving:
            # Walking remains weapon-ready but slightly compressed for stability.
            reach-=1.2

        var grip:=_q(chest + aim*reach)
        var support:=_q(grip - aim*(3.0 if rifle else 0.9) + perp*(-1.25))

        # Elbows remain apart and behind the hands; never cross the centerline.
        var l_elbow:=_q(l_shoulder.lerp(support,0.54) - perp*3.1)
        var r_elbow:=_q(r_shoulder.lerp(grip,0.54) + perp*3.1)

        # Preserve clear two-arm silhouette in near-front/back views.
        if absf(aim.x)<0.38:
            l_elbow.x-=3.0
            r_elbow.x+=3.0
            support.x-=1.25
            grip.x+=1.25

        return [l_elbow,support,r_elbow,grip]

    # Unarmed tactical-neutral posture: relaxed but ready, not rigid T-pose.
    var sway:=sin(gait_phase)*(2.7 if moving else 0.0)
    var l_elbow:=_q(Vector2(-7.6,0.5+body_bob+sway*0.30))
    var l_wrist:=_q(Vector2(-6.2,7.0+body_bob+sway))
    var r_elbow:=_q(Vector2(7.6,0.5+body_bob-sway*0.30))
    var r_wrist:=_q(Vector2(6.2,7.0+body_bob-sway))
    return [l_elbow,l_wrist,r_elbow,r_wrist]
'''
s=s[:a]+new_arm+s[b:]

# Replace head silhouette with directional geometry.
h0=s.index("func _draw_head(")
h1=s.index("\nfunc _draw_hair",h0)
new_head=r'''func _draw_head(center: Vector2, female: bool, outline: Color) -> void:
    var d:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var side:=absf(d.x)
    var back:=d.y < -0.45
    var sx:=1.0 if d.x>=0.0 else -1.0

    # Isometric rotation: side heads narrow somewhat, but retain skull volume.
    var front_w:=5.25 if female else 5.7
    var side_w:=4.55 if female else 4.95
    var half_w:=lerpf(front_w,side_w,side)
    var jaw_w:=lerpf(3.9 if female else 4.35,3.55 if female else 3.9,side)

    var pts:=PackedVector2Array()
    if side>0.72:
        # True profile silhouette: forehead/nose/chin project toward facing side.
        pts=PackedVector2Array([
            _q(center+Vector2(-sx*half_w*0.72,-6.1)),
            _q(center+Vector2(sx*half_w*0.35,-6.4)),
            _q(center+Vector2(sx*half_w,-4.0)),
            _q(center+Vector2(sx*(half_w+1.3),-0.4)),
            _q(center+Vector2(sx*(half_w+2.0),1.1)),
            _q(center+Vector2(sx*(jaw_w+0.7),4.2)),
            _q(center+Vector2(sx*1.6,6.3)),
            _q(center+Vector2(-sx*2.2,5.8)),
            _q(center+Vector2(-sx*half_w,2.0)),
            _q(center+Vector2(-sx*half_w,-3.8))
        ])
    elif back:
        # Back of skull: broader crown, no facial projection.
        pts=PackedVector2Array([
            _q(center+Vector2(-half_w+0.7,-6.3)),
            _q(center+Vector2(half_w-0.7,-6.3)),
            _q(center+Vector2(half_w,-3.8)),
            _q(center+Vector2(half_w-0.2,2.4)),
            _q(center+Vector2(jaw_w,5.2)),
            _q(center+Vector2(1.6,6.4)),
            _q(center+Vector2(-1.6,6.4)),
            _q(center+Vector2(-jaw_w,5.2)),
            _q(center+Vector2(-half_w+0.2,2.4)),
            _q(center+Vector2(-half_w,-3.8))
        ])
    else:
        # Front/three-quarter silhouette with directional cheek/jaw bias.
        var bias:=d.x*1.0
        pts=PackedVector2Array([
            _q(center+Vector2(-half_w+1.0+bias*0.2,-6.2)),
            _q(center+Vector2(half_w-1.0+bias*0.2,-6.2)),
            _q(center+Vector2(half_w+bias*0.35,-3.8)),
            _q(center+Vector2(half_w-0.3+bias*0.65,2.0)),
            _q(center+Vector2(jaw_w+bias*0.85,5.0)),
            _q(center+Vector2(1.8+bias*0.75,6.4)),
            _q(center+Vector2(-1.8+bias*0.55,6.4)),
            _q(center+Vector2(-jaw_w+bias*0.35,5.0)),
            _q(center+Vector2(-half_w+0.4+bias*0.2,2.0)),
            _q(center+Vector2(-half_w+bias*0.15,-3.8))
        ])
    _polygon(pts,skin_color,outline,1.5)

    # Only the visible ear(s) for the selected direction.
    if side>0.60:
        draw_rect(Rect2(center+Vector2(-sx*half_w-0.6,-0.4),Vector2(1.4,3.0)),skin_color.darkened(0.10),true)
    elif not back:
        draw_rect(Rect2(center+Vector2(-half_w-0.8,-0.4),Vector2(1.3,2.8)),skin_color.darkened(0.10),true)
        draw_rect(Rect2(center+Vector2(half_w-0.5,-0.4),Vector2(1.3,2.8)),skin_color.darkened(0.10),true)
'''
s=s[:h0]+new_head+s[h1:]

# Hair must also respect side/back direction so the whole head rotates.
hh0=s.index("func _draw_hair(")
hh1=s.index("\nfunc _draw_face_direction",hh0)
new_hair=r'''func _draw_hair(center: Vector2, female: bool, outline: Color) -> void:
    var d:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var side:=absf(d.x)
    var sx:=1.0 if d.x>=0.0 else -1.0
    var hair:=Color("3a302b") if role!="bandit" else Color("342925")
    var crown_shift:=d.x*0.8
    var hairline:=PackedVector2Array([
        center+Vector2(-5.0+crown_shift,-4.9),
        center+Vector2(-3.2+crown_shift,-6.9),
        center+Vector2(2.4+crown_shift,-6.9),
        center+Vector2(5.0+crown_shift,-4.6),
        center+Vector2(4.8+crown_shift,-2.1),
        center+Vector2(2.0+crown_shift*(1.0+side*0.3),-3.6),
        center+Vector2(-1.0+crown_shift,-2.9),
        center+Vector2(-4.4+crown_shift,-2.0)
    ])
    draw_colored_polygon(hairline,hair)
    if side>0.68:
        # Profile-side hair mass/nape.
        draw_line(center+Vector2(-sx*3.6,-2.8),center+Vector2(-sx*4.2,3.8),hair,2.3)
    if female:
        draw_line(center+Vector2(-4.8,-2.0),center+Vector2(-5.5,5.2),hair,2.4)
        draw_line(center+Vector2(4.8,-2.0),center+Vector2(5.5,5.2),hair,2.4)
'''
s=s[:hh0]+new_hair+s[hh1:]

# Make face details directional and sparse for side/back view.
f0=s.index("func _draw_face_direction(")
f1=s.index("\nfunc _limb",f0)
new_face=r'''func _draw_face_direction(center: Vector2, outline: Color) -> void:
    var d:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    if d.y < -0.45:
        return
    if absf(d.x)>0.60:
        var sx:=1.0 if d.x>0.0 else -1.0
        draw_rect(Rect2(center+Vector2(sx*2.6-0.5,-0.9),Vector2(1.2,1.2)),Color("252625"),true)
        # profile nose projects from silhouette
        draw_line(center+Vector2(sx*3.0,0.1),center+Vector2(sx*5.5,1.0),skin_color.darkened(0.18),1.0,true)
    else:
        var shift:=d.x*1.0
        draw_rect(Rect2(center+Vector2(-2.3+shift,-0.8),Vector2(1.1,1.1)),Color("252625"),true)
        draw_rect(Rect2(center+Vector2(1.2+shift,-0.8),Vector2(1.1,1.1)),Color("252625"),true)
        draw_rect(Rect2(center+Vector2(-0.5+shift*0.8,2.0),Vector2(1.0,1.0)),skin_color.darkened(0.20),true)
'''
s=s[:f0]+new_face+s[f1:]

# Draw firearm AFTER arms, but make it noticeably readable.
w=s.index("func _draw_skeleton_weapon(")
x=s.index("\nfunc get_weapon_anchor",w)
new_weapon=r'''func _draw_skeleton_weapon(lw: Vector2, rw: Vector2, outline: Color) -> void:
    if _weapon_category()!="firearm":
        return
    var aim:=facing.normalized() if facing.length_squared()>0.0001 else Vector2.DOWN
    var perp:=Vector2(-aim.y,aim.x)
    var wid:=_weapon_id().to_lower()
    var rifle:=("rifle" in wid or "shotgun" in wid or "smg" in wid or "carbine" in wid)

    # Dominant hand is the forward/right tactical grip.
    var grip:=rw
    var body_len:=13.0 if rifle else 8.7
    var muzzle:=grip+aim*body_len
    draw_line(grip,muzzle,outline,5.4 if rifle else 4.8,true)
    draw_line(grip,muzzle,Color("303536"),3.4 if rifle else 3.0,true)

    # Visible pistol/rifle grip attached exactly to the hand.
    var handle_end:=grip-aim*1.0+perp*3.9
    draw_line(grip,handle_end,outline,4.0,true)
    draw_line(grip,handle_end,Color("4a4038"),2.5,true)

    if rifle:
        var stock:=grip-aim*6.0
        draw_line(grip,stock,outline,4.8,true)
        draw_line(grip,stock,Color("4a4038"),3.0,true)
        draw_line(lw,grip+aim*4.1,Color("323638"),1.5,true)
'''
s=s[:w]+new_weapon+s[x:]

# Marker/version.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
h=re.sub(r'marker\.text = "D2D\.[^"]+"','marker.text = "D2D.10  |  TACTICAL ISOMETRIC"',h,count=1)
hud.write_text(h,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e=re.sub(r'(?m)^version/code=\d+$','version/code=83',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.10"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.10"',q,count=1)
    sm.write_text(q,encoding="utf-8")

p.write_text(s,encoding="utf-8")
print("Applied D2D.10 tactical isometric stance, extended firearm arms, directional head silhouette, and preserved side-view body volume.")
