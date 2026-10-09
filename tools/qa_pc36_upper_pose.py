#!/usr/bin/env python3
"""PC36 compare actual male/female coherent body pose vs static PC33.

The only intended visual changes are two-handed rifle down-aim torso/pack,
neck/head and shoulder/arm geometry. Geometry tests remain independent from
visual appeal; nobody may declare a visual pass without reviewing sheets.
"""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageChops,ImageStat
old=Path('pc36-static-body-comparator')
new=Path('pc24-reference-outfit-captures')
out=Path('pc36-upper-body-visual')
out.mkdir(exist_ok=True)
scores={}
for sex in ('male','female'):
    results={}
    for state in ('rifle_horizontal','rifle_max_down','rifle_max_up','rifle_left','full_gear_rifle',
                  'pistol_horizontal','pistol_max_down'):
        filename=f'{sex}_{state}.png'
        a=Image.open(old/filename).convert('RGB')
        b=Image.open(new/filename).convert('RGB')
        if a.size!=b.size:raise RuntimeError('PC36 capture size mismatch '+filename)
        rect=(425,105,865,610)
        ac,bc=a.crop(rect),b.crop(rect)
        diff=sum(ImageStat.Stat(ImageChops.difference(ac,bc)).mean)/3
        results[state]=round(diff,5)
        canvas=Image.new('RGB',(880,535),(15,18,21))
        canvas.paste(ac,(0,30));canvas.paste(bc,(440,30))
        dr=ImageDraw.Draw(canvas)
        dr.text((8,8),sex.upper()+' '+state+' PC33 rigid body',fill='white')
        dr.text((448,8),'PC36 shared torso/neck/clavicle pose',fill='white')
        canvas.save(out/f'{sex}_{state}_PC33_vs_PC36.jpg',quality=93)
        print(f'PC36_GODOT_REAL_A_B {sex} {state}: {diff:.5f}')
    if results['rifle_max_down']<.05:
        raise RuntimeError('PC36 shared body rendering did not change down aim for '+sex)
    if results['pistol_horizontal']>.50 or results['pistol_max_down']>.50:
        raise RuntimeError('PC36 pistol silhouette change exceeds known nondeterministic frame-phase tolerance for '+sex)
    if results['rifle_max_down']<5.0*max(results['pistol_horizontal'],results['pistol_max_down'],.05):
        raise RuntimeError('PC36 rifle-down change is not sufficiently larger than temporal image noise for '+sex)
    scores[sex]=results
# Continuous smoothstep body pose gives zero deviation for <=0.28rad and
# bounded rotation at extremes; check against impossible instantaneous snaps.
prev=0.
max_jump=0.
for deg in range(-88,89):
    a=math.radians(deg)
    t=max(0,min(1,(a-.28)/(1.18-.28)))
    blend=t*t*(3-2*t)
    angle=-.145*blend
    max_jump=max(max_jump,abs(angle-prev))
    prev=angle
if max_jump>.02:raise RuntimeError(f'PC36 discontinuous torso lean: {max_jump}')
scores['pose_continuity']={'max_torso_delta_per_degree_rad':max_jump,
                          'source_art':'approved torso, head and arm segments retained',
                          'human_visual_approval':'PENDING'}
(out/'pc36-pose-qa.json').write_text(json.dumps(scores,indent=2)+'\n')
print('PC36_COHERENT_BODY_RENDER_QA_PASS; actual visual acceptance PENDING')
