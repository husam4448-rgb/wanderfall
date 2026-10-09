#!/usr/bin/env python3
"""PC31 reference-measured side-view shoulder/arm articulation QA.

A rifle stance changes BODY clavicle sockets (using registered reference
shoulder position). The rifle never supplies or moves shoulders; grips stay
owned by weapon contacts. Validate physical reach and elbow flex, then compare
actual Godot reference-outfit renders at matched poses.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageStat,ImageChops
from math import cos,sin,atan2,acos,hypot,pi
import json
root=Path('.')
profiles=json.loads((root/'assets/authored2d/unified_character/rig/humanoid_rig_profiles.json').read_text())['profiles']
rifle=json.loads((root/'assets/authored2d/unified_character/rig/weapon_rig_contracts.json').read_text())['weapons']['rifle']
old=Path('pc31-legacy-shoulder-captures')
new=Path('pc24-reference-outfit-captures')
out=Path('pc31-reference-shoulder-evidence')
out.mkdir(exist_ok=True)
result={}
for sex,profile in profiles.items():
    r=profile['runtime']
    reg=profile.get('reference_registration',r.get('reference_registration',{}))['rifle']
    registered_shoulder=(profile['reference_measurements_px']['east_anatomical_shoulder'][0]-reg['torso_center_x'])*reg['world_per_reference_px']
    lengths=r['upper_arm_length'],r['forearm_length']
    samples=[]
    for degree in range(-88,89,2):
        a=degree*pi/180
        dx,dy=rifle['dominant_grip_body_anchor']
        sx,sy=rifle['support_grip_relative_to_dominant']
        off=r['support_wrist_to_grip_local']
        palm=a+rifle['support_palm_rotation_offset_deg']*pi/180
        wrist=(dx+sx*cos(a)-sy*sin(a)-(off[0]*cos(palm)-off[1]*sin(palm)),
               dy+sx*sin(a)+sy*cos(a)-(off[0]*sin(palm)+off[1]*cos(palm)))
        reach=[]
        flex=[]
        for shoulder_x in (r['shoulder_front'][0],registered_shoulder):
            d=hypot(wrist[0]-shoulder_x,wrist[1]-r['shoulder_front'][1])
            if not abs(lengths[0]-lengths[1])+.05<d<sum(lengths)-.05:
                raise RuntimeError(f'PC31 {sex} wrist unreachable at aim={degree}, d={d}')
            interior=acos(max(-1,min(1,(lengths[0]**2+lengths[1]**2-d*d)/(2*lengths[0]*lengths[1]))))
            flex.append(180-interior*180/pi)
            reach.append(d)
        samples.append((degree,reach,flex))
    old_mid=next(v for v in samples if v[0]==0)[2][0]
    new_mid=next(v for v in samples if v[0]==0)[2][1]
    if new_mid<old_mid+5 or new_mid>150:
        raise RuntimeError(f'PC31 {sex} rifle elbow failed to gain controlled flex: {old_mid} -> {new_mid}')
    print(f'PC31_ARTWORK_REGISTERED_RIFLE_ELBOW_OK {sex}: shoulder_x={registered_shoulder:.4f}, neutral_bend {old_mid:.2f} -> {new_mid:.2f}')
    result[sex]={'shoulder_x_from_approved_rifle':registered_shoulder,'original_neutral_bend_deg':old_mid,
                 'aim_shoulder_neutral_bend_deg':new_mid,'all_aim_angles_reachable':True,'visual_approval':'PENDING'}
    for state in ('rifle_horizontal','rifle_max_up','rifle_max_down','rifle_left','full_gear_rifle'):
        fn=f'{sex}_{state}.png'
        a=Image.open(old/fn).convert('RGB').crop((430,115,865,595))
        b=Image.open(new/fn).convert('RGB').crop((430,115,865,595))
        d=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
        if d<.015:
            raise RuntimeError(f'PC31 no visible arm posture difference {fn} d={d}')
        sheet=Image.new('RGB',(870,510),(16,20,23))
        sheet.paste(a,(0,30))
        sheet.paste(b,(435,30))
        draw=ImageDraw.Draw(sheet)
        draw.text((9,10),f'{sex} {state}: previous extended arm',fill='white')
        draw.text((443,10),'Reference-registered shouldered posture',fill='white')
        sheet.save(out/f'{sex}_{state}_old_vs_PC31.jpg',quality=94)
        result[sex][state+'_pixel_change']=round(d,5)
        print(f'PC31_ACTUAL_GODOT_RIFLE_POSE_OK {fn} change={d:.4f}')
(out/'pc31-reference-shoulder-qa.json').write_text(json.dumps(result,indent=2)+'\n')
print('PC31 reference-measured shoulder elbow flex verified; human visual review required')
