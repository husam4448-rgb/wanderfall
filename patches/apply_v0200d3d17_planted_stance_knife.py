#!/usr/bin/env python3
"""D3D.17: planted separated stance, flexed knees, distinct knife guard, genuine crouch."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
path=root/"scripts/art/production_survivor_visual.gd"
s=path.read_text(encoding="utf-8")
pose_a=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_a)
if pose_a<0 or pose_b<0:
    raise SystemExit("D3D.17 missing pose bounds")
pose=s[pose_a:pose_b]
def change(before,after,label):
    global pose
    n=pose.count(before)
    if n!=1:
        raise SystemExit("D3D.17 "+label+" anchor count "+str(n))
    pose=pose.replace(before,after,1)

# A pelvis-wide planted base is more reliable than merely changing shin pitch.
# These small local translations separate the upper legs at the actual hip
# joints, so the feet no longer overlap from front or back.
change(
    '''    var wave := sin(gait_phase)
    var stride := (0.44 if sprinting else (0.22 if crouching else 0.34)) * wave
''',
    '''    var wave := sin(gait_phase)
    var stride := (0.44 if sprinting else (0.22 if crouching else 0.34)) * wave
    var knife_ready := _weapon_category() in ["melee", "knife"]
    var thigh_gap := 0.079 if crouching else (0.060 if armed else 0.052)
    for side in ["l","r"]:
        var thigh_bone := skel.find_bone("thigh_"+side)
        if thigh_bone >= 0:
            var thigh_pose := skel.get_bone_pose_position(thigh_bone)
            thigh_pose.x += thigh_gap if side == "l" else -thigh_gap
            skel.set_bone_pose_position(thigh_bone,thigh_pose)
    skel.force_update_all_bone_transforms()
''',"hip separation"
)
change(
    '''var pelvis_offset := Vector3(0.0,-0.145,0.035) if crouching else Vector3.ZERO''',
    '''var pelvis_offset := Vector3(0.0,-0.255,0.095) if crouching else Vector3.ZERO''',
    "deep crouch pelvis"
)
change(
    '''Vector3(-0.12,-0.74,0.48+crouch_step)''',
    '''Vector3(-0.32,-0.72,0.54+crouch_step)''',
    "left crouch thigh"
)
change(
    '''Vector3(0.12,-0.74,0.48-crouch_step)''',
    '''Vector3(0.32,-0.72,0.54-crouch_step)''',
    "right crouch thigh"
)
change(
    '''Vector3(-0.09,-0.88,0.14+stride)''',
    '''Vector3(-0.20,-0.87,0.14+stride)''',
    "left walk leg"
)
change(
    '''Vector3(0.09,-0.88,0.14-stride)''',
    '''Vector3(0.20,-0.87,0.14-stride)''',
    "right walk leg"
)
change(
    '''var ready_forward := 0.17 if armed else 0.10
        _point_bone_fast(skel,"thigh_l","calf_l",Vector3(-0.13,-0.95,ready_forward))
        _point_bone_fast(skel,"thigh_r","calf_r",Vector3(0.13,-0.95,ready_forward))''',
    '''var ready_forward := 0.25 if armed else (0.19 if knife_ready else 0.12)
        _point_bone_fast(skel,"thigh_l","calf_l",Vector3(-0.29,-0.88,ready_forward))
        _point_bone_fast(skel,"thigh_r","calf_r",Vector3(0.29,-0.88,ready_forward))''',
    "stable staggered standing legs"
)
change(
    '''    else:
        var arm_swing := stride * 0.72 if moving else 0.0''',
    '''    elif knife_ready:
        # Knife: bent dominant elbow carried in front of the ribs, independent
        # guard hand higher and open. Do NOT force the two-hand pistol grip.
        _point_bone_fast(skel,"upperarm_r","lowerarm_r",Vector3(-0.23,-0.69,0.64))
        _point_bone_fast(skel,"upperarm_l","lowerarm_l",Vector3(0.30,-0.79,0.43))
    else:
        var arm_swing := stride * 0.72 if moving else 0.0''',
    "knife upper arm"
)
change(
    '''var crouch_knee := 0.54 + (0.10 * absf(wave) if moving else 0.0)
        _point_bone_fast(skel,"calf_l","foot_l",Vector3(0.0,-0.73,-crouch_knee))
        _point_bone_fast(skel,"calf_r","foot_r",Vector3(0.0,-0.73,-crouch_knee))''',
    '''var crouch_knee := 0.72 + (0.08 * absf(wave) if moving else 0.0)
        _point_bone_fast(skel,"calf_l","foot_l",Vector3(-0.10,-0.70,-crouch_knee))
        _point_bone_fast(skel,"calf_r","foot_r",Vector3(0.10,-0.70,-crouch_knee))''',
    "grounded crouch shins"
)
change(
    '''var ready_bend := 0.24 if armed else 0.14
        ready_bend += _aim_extension*0.13 if armed else 0.0
        _point_bone_fast(skel,"calf_l","foot_l",Vector3(-0.02,-0.96,-ready_bend))
        _point_bone_fast(skel,"calf_r","foot_r",Vector3(0.02,-0.96,-ready_bend))''',
    '''var ready_bend := 0.36 if armed else (0.28 if knife_ready else 0.24)
        ready_bend += _aim_extension*0.15 if armed else 0.0
        _point_bone_fast(skel,"calf_l","foot_l",Vector3(-0.11,-0.90,-ready_bend))
        _point_bone_fast(skel,"calf_r","foot_r",Vector3(0.11,-0.90,-ready_bend))''',
    "persistent standing knee flex"
)
change(
    '''    else:
        var fore_swing := stride * 0.22 if moving else 0.0''',
    '''    elif knife_ready:
        _point_bone_fast(skel,"lowerarm_r","hand_r",Vector3(0.16,-0.30,0.92))
        _point_bone_fast(skel,"lowerarm_l","hand_l",Vector3(-0.19,-0.52,0.75))
        _curl_pistol_hand(skel,"r")
    else:
        var fore_swing := stride * 0.22 if moving else 0.0''',
    "knife dominant hand and offhand guard"
)
s=s[:pose_a]+pose+s[pose_b:]

# A switch from bare hands to knife must refresh the on-demand SubViewport
# even though neither state is a firearm.
proc_a=s.find("func _process(delta: float) -> void:\n")
if proc_a<0:
    proc_a=s.find("func _process(delta: double) -> void:\n")
proc_b=s.find("\nfunc ",proc_a+6) if proc_a>=0 else -1
if proc_a<0:raise SystemExit("D3D.17 process function not found")
if proc_b<0:proc_b=len(s)
proc=s[proc_a:proc_b]
needle='    var armed := _weapon_category() == "firearm"\n'
if proc.count(needle)!=1:raise SystemExit("D3D.17 armed state process anchor missing")
proc=proc.replace(needle,needle+'''    var visual_weapon_kind := _weapon_category()
    if visual_weapon_kind != _last_visual_weapon_kind:
        _pose_dirty = true
        _last_visual_weapon_kind = visual_weapon_kind
''',1)
s=s[:proc_a]+proc+s[proc_b:]
first='var _last_armed := false\n'
if s.count(first)!=1:
    raise SystemExit("D3D.17 class state anchor missing")
s=s.replace(first,first+'var _last_visual_weapon_kind := ""\n',1)

# Keep the D3D.16 world scale, changing only rig posing. Stamp identifies the
# actually running APK so screenshots cannot be confused with old installs.
if "PLAYER_WORLD_SPRITE_SCALE := 0.266" not in s:
    raise SystemExit("D3D.17 must preserve D3D.16 player scale")
path.write_text(s,encoding="utf-8")
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.16  |  PLAYER 1.55x"' not in h:
    raise SystemExit("D3D.17 build stamp anchor missing")
h=h.replace('marker.text = "D3D.16  |  PLAYER 1.55x"',
            'marker.text = "D3D.17  |  PLANTED STANCE"',1)
hud.write_text(h,encoding="utf-8")
preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=46',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.17"',p,count=1)
if n1!=1 or n2!=1:raise SystemExit("D3D.17 Android version anchors missing")
preset.write_text(p,encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.17"',t,count=1)
    save.write_text(t,encoding="utf-8")
print("Applied D3D.17: hip-separated planted legs, knee flex, deeper crouch, distinct knife guard, refreshed weapon-state rendering; world scale unchanged.")
