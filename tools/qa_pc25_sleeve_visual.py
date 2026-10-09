#!/usr/bin/env python3
"""Evidence-only PC25 authored-sleeve comparison of actual Godot renders.

A pixel difference establishes that rendering changed, NOT that it improved.
Visual acceptance remains manual after side-by-side review.
"""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat

root=Path('.')
old=root/'pc25-legacy-art-captures'
new=root/'pc24-reference-outfit-captures'
out=root/'pc25-sleeve-review'
out.mkdir(exist_ok=True)
states=('pistol_horizontal','pistol_max_down','rifle_horizontal','rifle_max_up','rifle_left','run_rifle')
results={}
for sex in ('male','female'):
    results[sex]={}
    for pose in states:
        before=Image.open(old/f'{sex}_{pose}.png').convert('RGB')
        after=Image.open(new/f'{sex}_{pose}.png').convert('RGB')
        if before.size!=after.size or before.size!=(1280,720):
            raise RuntimeError(f'{sex}/{pose}: incompatible capture dimensions')
        # Fixed viewport crop is identical between runs, no resizing tricks.
        crop=(465,125,850,615)
        a=before.crop(crop)
        b=after.crop(crop)
        d=ImageChops.difference(a,b)
        diff=sum(ImageStat.Stat(d).mean)/3.0
        bbox=d.getbbox()
        results[sex][pose]={'mean_absolute_rgb_change':round(diff,5),'changed_bbox':list(bbox) if bbox else None}
        canvas=Image.new('RGB',(2*385,520),'#131a20')
        canvas.paste(a,(0,30))
        canvas.paste(b,(385,30))
        g=ImageDraw.Draw(canvas)
        g.text((10,10),f'{sex.upper()} {pose}: PC24 legacy arm',fill='white')
        g.text((395,10),'PC25 authored arm overlay',fill='white')
        canvas.save(out/f'{sex}_{pose}_before_after.jpg',quality=93,subsampling=0)
    if not results[sex]['rifle_horizontal']['changed_bbox']:
        raise RuntimeError(f'{sex}: authored sleeve overlay made no change in actual rifle render')
    print(f'PC25_SLEEVE_RENDER_CHANGE_OK {sex}: '+str(results[sex]['rifle_horizontal']))
(out/'pc25_qa_results.json').write_text(json.dumps(results,indent=2)+'\n')
print('PC25 comparison evidence generated. VISUAL APPROVAL NOT AUTOMATIC.')
