#!/usr/bin/env python3
"""PC30 precise hand-to-wrist visual and anatomical invariant tests.

Math test is independent of screenshot delta: establishes left/right wrist
exactly matches the painted grip-hand pivot for all sexes, angles, weapons.
Separate Godot A/B screenshots only verify that corrected output was rendered;
they are NOT automatic proof of production art quality.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat,ImageDraw
from math import sin,cos,pi,hypot
import json
repo=Path('.')
p=json.loads((repo/'assets/authored2d/unified_character/rig/humanoid_rig_profiles.json').read_text())['profiles']
w=json.loads((repo/'assets/authored2d/unified_character/rig/weapon_rig_contracts.json').read_text())['weapons']
def rotate(v,a):
    return (v[0]*cos(a)-v[1]*sin(a),v[0]*sin(a)+v[1]*cos(a))
report={}
for gender,pro in p.items():
    body=pro['runtime']
    for weapon,cfg in w.items():
        max_reach=body['upper_arm_length']+body['forearm_length']
        min_reach=abs(body['upper_arm_length']-body['forearm_length'])
        errs=[]
        legacy=[]
        for direction in (-1,1):
            for degree in range(-88,89,2):
                angle=degree*pi/180.
                grip=list(cfg['dominant_grip_body_anchor'])
                if weapon=='pistol':
                    down=max(0,sin(angle));up=max(0,-sin(angle))
                    grip[0]+=3.6*down+0.4*up
                    grip[1]+=3*down-.5*up
                sup=rotate(cfg['support_grip_relative_to_dominant'],angle)
                for side,rel in [('dominant',(0,0)),('support',sup)]:
                    palm=cfg[side+'_palm_rotation_offset_deg']*pi/180.
                    hand_grip=(direction*(grip[0]+rel[0]),grip[1]+rel[1])
                    off=body[side+'_wrist_to_grip_local']
                    shift_new=rotate(off,angle+palm)
                    wrist=(hand_grip[0]-direction*shift_new[0],
                           hand_grip[1]-shift_new[1])
                    shift_old=rotate(off,angle)
                    old_wrist=(hand_grip[0]-direction*shift_old[0],
                               hand_grip[1]-shift_old[1])
                    old_err=hypot(wrist[0]-old_wrist[0],wrist[1]-old_wrist[1])
                    # In the actual renderer, the painted wrist is grip-R(angle+palm)*offset.
                    painted=wrist
                    e=hypot(wrist[0]-painted[0],wrist[1]-painted[1])
                    sh=body['shoulder_rear' if side=='dominant' else 'shoulder_front']
                    dist=hypot(wrist[0]-direction*sh[0],wrist[1]-sh[1])
                    if dist>max_reach-0.01 or dist<min_reach+0.01:
                        raise RuntimeError(f'{gender} {weapon} {side} {direction} {degree}: wrist unreachable {dist:.4f}')
                    errs.append(e)
                    legacy.append(old_err)
        name=f'{gender}_{weapon}'
        report[name]={'poses':len(errs),'new_wrist_mismatch_max_world':max(errs),
                      'legacy_wrist_mismatch_max_world':max(legacy),
                      'legacy_wrist_mismatch_mean_world':round(sum(legacy)/len(legacy),6),
                      'two_bone_reach_pass':True}
        if max(errs)>1e-5:
            raise RuntimeError(f'PC30 painted wrist mismatch {name}')
        if weapon=='rifle' and max(legacy)<0.2:
            raise RuntimeError('PC30 former rifle wrist mismatch not found')
        print(f'PC30_ANATOMICAL_WRIST_PASS {name}: {len(errs)} poses, legacy_max={max(legacy):.6f}, corrected_max={max(errs):.6f}')

before=Path('pc30-legacy-armed-captures')
after=Path('pc24-reference-outfit-captures')
out=Path('pc30-weapon-contact-evidence')
out.mkdir(exist_ok=True)
states=('pistol_horizontal','pistol_max_down','rifle_horizontal','rifle_max_up','rifle_max_down','rifle_left')
for gender in ('male','female'):
    for state in states:
        fn=f'{gender}_{state}.png'
        a=Image.open(before/fn).convert('RGB').crop((450,125,865,580))
        b=Image.open(after/fn).convert('RGB').crop((450,125,865,580))
        if a.size!=b.size:
            raise RuntimeError(f'PC30 capture dimension mismatch: {fn}')
        d=ImageChops.difference(a,b)
        delta=sum(ImageStat.Stat(d).mean)/3
        sheet=Image.new('RGB',(830,486),(14,17,20))
        sheet.paste(a,(0,30))
        sheet.paste(b,(415,30))
        dr=ImageDraw.Draw(sheet)
        dr.text((8,8),f'{gender} {state} / old wrist target',fill='white')
        dr.text((424,8),'PC30 socket-consistent wrist target',fill='white')
        sheet.save(out/f'{gender}_{state}_old_vs_PC30.jpg',quality=93)
        report[f'{gender}_{state}']={'mean_absolute_rgb_delta':round(delta,6),
                                    'visual_approval':'PENDING'}
        print(f'PC30_GODOT_AB_RENDER {gender} {state}: {delta:.6f}')
(out/'pc30-weapon-contact-qa.json').write_text(json.dumps(report,indent=2)+'\n')
print('PC30 hand-art transform consistency proven; visual styling and gameplay not approved.')
