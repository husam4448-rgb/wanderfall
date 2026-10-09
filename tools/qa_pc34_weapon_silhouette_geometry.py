#!/usr/bin/env python3
"""PC34: evaluate painted rifle silhouette vs measured head + two-hand IK.

Unlike PC33's stock-to-grip *line* proxy, this samples every opaque source
weapon region and transforms it via the PC30 calibrated weapon render matrix.
Searches body-relative low/forward candidate stances without changing the
approved source art or the tested runtime. Explicitly identifies aim angles
that cannot be staged with fixed shoulders and a still head.

This is diagnostic research, not a claim of finished gameplay poses.
"""
import math,json,csv
from pathlib import Path
from PIL import Image,ImageDraw
base=Path(__file__).resolve().parents[1]
profiles=json.loads((base/'assets/authored2d/unified_character/rig/humanoid_rig_profiles.json').read_text())['profiles']
weapons=json.loads((base/'assets/authored2d/unified_character/rig/weapon_rig_contracts.json').read_text())['weapons']
meta=json.loads((base/'assets/authored2d/unified_character/arms/metadata/hybrid_v3_weapon_assets.json').read_text())['rifle']
w=weapons['rifle']
png=Image.open(base/meta['filename']).convert('RGBA')
samples=[(x,y) for y in range(png.height) for x in range(png.width) if png.getpixel((x,y))[3]>90]
if len(samples)<100:raise SystemExit('PC34 missing actual rifle sprite pixels')
# Source silhouette sampling is deterministic, including tips and rear stock.
pixels=samples[::max(1,len(samples)//110)]
for extreme in [min(samples),max(samples)]:
    if extreme not in pixels:pixels.append(extreme)
pivot=meta['dominant_grip_px']
source_sup=(meta['support_grip_px'][0]-pivot[0],meta['support_grip_px'][1]-pivot[1])
source_muz=(meta['muzzle_px'][0]-pivot[0],meta['muzzle_px'][1]-pivot[1])
world_sup=w['support_grip_relative_to_dominant']
world_muz=w['muzzle_relative_to_dominant']
cant=math.atan2(world_sup[1],world_sup[0])
sx=math.hypot(*world_sup)/source_sup[0]
sy=(source_muz[0]*sx*math.sin(cant)-world_muz[1])/(-source_muz[1]*math.cos(cant))
assert 0.2<sx<0.6 and 0.15<sy<0.6
def rotate(v,a):
    return (v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a))
out=base/'pc34-silhouette-evidence'
out.mkdir(exist_ok=True)
rows=[]
unreachable={}
for sex in ('male','female'):
    pro=profiles[sex];rig=pro['runtime'];reg=rig.get('reference_registration',pro.get('reference_registration'))['rifle']
    ref=pro['reference_measurements_px']
    world_scale=reg['world_per_reference_px']
    head_top=reg['runtime_foot_offset_y']+(reg['head_top_y']-reg['feet_y'])*world_scale if 'runtime_foot_offset_y' in reg else rig.get('reference_registration',pro.get('reference_registration'))['runtime_foot_offset_y']+(reg['head_top_y']-reg['feet_y'])*world_scale
    head_radius=max(6.4,ref['south_head_width_estimate']*world_scale/2)
    # Approximate side head ellipse inferred from approved top & head width,
    # enlarged for hair and rifle clearance; exact head alpha remains for PC35.
    head_cy=head_top+head_radius
    head_cx=(ref['east_anatomical_shoulder'][0]-reg['torso_center_x'])*world_scale+2.0
    hx=head_radius+1.5;hy=head_radius+1.7
    shoulder=(ref['east_anatomical_shoulder'][0]-reg['torso_center_x'])*world_scale
    maxlen=rig['upper_arm_length']+rig['forearm_length']-.25
    minlen=abs(rig['upper_arm_length']-rig['forearm_length'])+.05
    for facing in (-1,1):
        failures=0
        for degrees in range(-90,91,6):
            angle=math.radians(degrees)
            painted=[rotate(((x-pivot[0])*sx,(y-pivot[1])*sy),angle+cant) for x,y in pixels]
            sup=rotate(w['support_grip_relative_to_dominant'],angle)
            owD=rotate(rig['dominant_wrist_to_grip_local'],angle+math.radians(w['dominant_palm_rotation_offset_deg']))
            owS=rotate(rig['support_wrist_to_grip_local'],angle+math.radians(w['support_palm_rotation_offset_deg']))
            grip=w['dominant_grip_body_anchor']
            chosen=None
            for dx in [k*.75 for k in range(0,21)]:
                for dy in [k*.75 for k in range(0,23)]:
                    minclear=999.0
                    for vx,vy in painted:
                        x=facing*(grip[0]+dx+vx)
                        y=grip[1]+dy+vy
                        minclear=min(minclear,math.hypot((x-facing*head_cx)/hx,(y-head_cy)/hy))
                    if minclear<1.08:continue
                    wrists=((grip[0]+dx-owD[0],grip[1]+dy-owD[1]),
                            (grip[0]+dx+sup[0]-owS[0],grip[1]+dy+sup[1]-owS[1]))
                    valid=True
                    for wrist,shoulder_y in zip(wrists,(-9.8 if sex=='male' else -9.6,-9.3 if sex=='male' else -9.1)):
                        length=math.hypot(wrist[0]-shoulder,wrist[1]-shoulder_y)
                        if not minlen<length<maxlen:valid=False
                    if not valid:continue
                    cost=dx*dx*.85+dy*dy
                    if chosen is None or cost<chosen['cost']:
                        chosen={'forward':round(dx,4),'down':round(dy,4),'cost':round(cost,4),
                                'min_head_clearance_normalized':round(minclear,4)}
            if chosen is None:failures+=1
            rows.append({'sex':sex,'facing':'right' if facing>0 else 'left',
                         'angle_deg':degrees,'pose_feasible_fixed_torso':chosen is not None,
                         'forward':chosen['forward'] if chosen else None,
                         'down':chosen['down'] if chosen else None,
                         'pixel_samples':len(pixels)})
        unreachable[f'{sex}_{"right" if facing>0 else "left"}']=failures
        print(f'PC34_FULL_ALPHA_RIFLE_FEASIBILITY {sex} dir={facing}: {failures}/31 angles cannot satisfy head clearance + IK with static torso')
with (out/'pc34-weapon-feasibility.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
report={'tested_source':'actual committed alpha rifle PNG + PC30 transform',
        'purpose':'plan anatomically achievable full-body aim states; NOT a final pose solver',
        'head_envelope':'reference measured size plus 1.5 world-unit safety margin',
        'angles_tested_per_sex_direction':31,'unreachable_fixed_torso':unreachable,
        'outcome':'diagnostic only — do not approve APK based on this'}
(out/'pc34-silhouette-feasibility.json').write_text(json.dumps(report,indent=2)+'\n')
# Compact visual map uses calculated geometric feasibility, not synthesized sprites.
canvas=Image.new('RGB',(1060,380),'#151a20')
d=ImageDraw.Draw(canvas)
d.text((18,12),'PC34 ACTUAL PAINTED RIFLE ALPHA / FIXED-BODY AIM FEASIBILITY',fill='white')
for row,group in enumerate(['male_right','male_left','female_right','female_left']):
    sex,direction=group.split('_')
    d.text((12,56+row*72),group,fill='#eeeeee')
    points=[a for a in rows if a['sex']==sex and a['facing']==direction]
    for i,a in enumerate(points):
        x=120+i*29
        y=55+row*72
        good=a['pose_feasible_fixed_torso']
        d.rectangle([x,y,x+23,y+40],fill='#4b8c74' if good else '#a04446')
    d.text((1022,56+row*72),str(unreachable[group]),fill='#eeeeee')
d.text((120,353),'Aim left/up  -90 degrees',fill='#cccccc')
d.text((580,353),'Aim right/down  +90 degrees',fill='#cccccc')
canvas.save(out/'pc34-full-weapon-feasibility.png')
print('PC34_DIAGNOSTIC_COMPLETE — decide torso/head pose rig states before another APK')
