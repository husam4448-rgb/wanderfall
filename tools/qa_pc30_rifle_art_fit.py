#!/usr/bin/env python3
"""Compare original vs contract-calibrated RIFLE rendered by actual Godot.

Source art source-pixel contacts define fit; no subjective image-difference
test can substitute for the human visual review of hands, stock and geometry.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
import math,json
root=Path('.')
meta=json.loads((root/"assets/authored2d/unified_character/arms/metadata/hybrid_v3_weapon_assets.json").read_text())['rifle']
w=json.loads((root/"assets/authored2d/unified_character/rig/weapon_rig_contracts.json").read_text())['weapons']['rifle']
p0=meta['dominant_grip_px']; sp=meta['support_grip_px']; mu=meta['muzzle_px']
sup=(sp[0]-p0[0],sp[1]-p0[1])
muzzle=(mu[0]-p0[0],mu[1]-p0[1])
desired=w['support_grip_relative_to_dominant']
desired_muzzle=w['muzzle_relative_to_dominant']
theta=math.atan2(desired[1],desired[0])
sx=math.hypot(*desired)/sup[0]
sy=(muzzle[0]*sx*math.sin(theta)-desired_muzzle[1])/(-muzzle[1]*math.cos(theta))
def transformed(v):
    return (v[0]*sx*math.cos(theta)-v[1]*sy*math.sin(theta),
            v[0]*sx*math.sin(theta)+v[1]*sy*math.cos(theta))
ms=transformed(sup);mm=transformed(muzzle)
su_err=math.dist(ms,desired)
mu_err=math.dist(mm,desired_muzzle)
if su_err>0.01 or mu_err>0.60:
    raise RuntimeError(f'PC30 painted handguard/muzzle mismatch {su_err:.3f}/{mu_err:.3f}')
old=Path('pc30-rifle-legacy-art-captures')
new=Path('pc24-reference-outfit-captures')
output=Path('pc30-rifle-visual-evidence')
output.mkdir(exist_ok=True)
scores={}
for sex in ('male','female'):
    for pose in ('rifle_horizontal','rifle_max_up','rifle_max_down','rifle_left','full_gear_rifle'):
        fname=f'{sex}_{pose}.png'
        a=Image.open(old/fname).convert('RGB').crop((430,115,865,595))
        b=Image.open(new/fname).convert('RGB').crop((430,115,865,595))
        if a.size!=b.size:raise RuntimeError('PC30 A2 image sizes mismatch '+fname)
        delta=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
        if delta<0.03:raise RuntimeError(f'PC30 A2 rifle artwork unchanged {fname} diff={delta:.4f}')
        canvas=Image.new('RGB',(870,512),(16,20,23))
        canvas.paste(a,(0,30))
        canvas.paste(b,(435,30))
        d=ImageDraw.Draw(canvas)
        d.text((9,9),f'{sex} {pose}: original visual scale',fill='white')
        d.text((445,9),'Rifle fitted to actual grip/handguard',fill='white')
        canvas.save(output/f'{sex}_{pose}_old_vs_fitted.jpg',quality=94)
        scores[fname]=round(delta,6)
        print(f'PC30_RIFLE_ART_CAPTURE_DIFFERENCE_OK {fname} {delta:.5f}')
results={'contract':{'source_dominant_px':p0,'source_support_px':sp,'source_muzzle_px':mu,
   'uniform_x_scale':sx,'uniform_y_scale':sy,'visual_cant_deg':math.degrees(theta),
   'support_socket_error_world':su_err,'muzzle_socket_error_world':mu_err},
   'actual_Godot_image_differences':scores,'visual_approval':'PENDING'}
(output/'pc30-rifle-qa.json').write_text(json.dumps(results,indent=2)+'\n')
print(f'PC30_RIFLE_PAINTED_GRIP_SOCKET_MATCH support_error={su_err:.5f} muzzle_error={mu_err:.5f}')
