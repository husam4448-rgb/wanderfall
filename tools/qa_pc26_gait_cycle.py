#!/usr/bin/env python3
"""PC26: actual Godot 8-phase walk/run playback, side-by-side evidence.

This checks that captured frames change, and reports motion scores. It does
NOT automatically prove an attractive full-cycle animation; inspect GIFs.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
import json
root=Path('pc26-gait-captures')
out=Path('pc26-animation-evidence')
out.mkdir(exist_ok=True)
results={}
for sex in ('male','female'):
    for gait in ('walk','run'):
        key=f'{sex}_{gait}'
        frames=[]
        for n in range(8):
            p=root/f'{key}_{n:02d}.png'
            if not p.is_file():
                raise SystemExit(f'PC26_GAIT_MISSING_FRAME {p}')
            im=Image.open(p).convert('RGB')
            if im.width<950 or im.height<570:
                raise SystemExit(f'PC26_GAIT_BAD_IMAGE_SIZE {p} {im.size}')
            frames.append(im.crop((400,82,870,568)))
        # Leg region is a fixed ROI inside the original character-centered
        # capture. No motion synthesis; pixels come from the real renderer.
        lower=[im.crop((158,215,380,482)) for im in frames]
        scores=[]
        for i in range(8):
            d=ImageChops.difference(lower[i],lower[(i+1)%8])
            scores.append(round(sum(ImageStat.Stat(d).mean)/3,4))
        distinct=sum(x>0.03 for x in scores)
        if distinct<4:
            raise SystemExit(f'PC26_GAIT_TOO_STATIC {key}: {scores}')
        results[key]={'frames':8,'distinct_transitions_over_0_03':distinct,
                      'consecutive_leg_region_rgb_diffs':scores,
                      'note':'Visual joint/foot cycle acceptance remains manual'}
        canvas=Image.new('RGB',(4*470,2*512),(18,20,23))
        painter=ImageDraw.Draw(canvas)
        for i,im in enumerate(frames):
            x=(i%4)*470;y=(i//4)*512
            canvas.paste(im,(x,y+24))
            painter.text((x+10,y+7),f'{sex.upper()} {gait.upper()}   phase {i}/8',fill=(240,240,230))
        canvas.save(out/f'{key}_8phase_contact_sheet.jpg',quality=94,subsampling=0)
        # Append phase 0 for explicitly visible closure of the full cycle.
        anim=[im.resize((376,389),Image.Resampling.NEAREST) for im in frames]
        anim.append(anim[0].copy())
        anim[0].save(out/f'{key}_full_cycle.gif',save_all=True,append_images=anim[1:],
                     duration=120 if gait=='walk' else 90,loop=0,optimize=False)
        print(f'PC26_GAIT_EVIDENCE {key} eight-phase leg transitions {scores}')
(out/'pc26_gait_qa.json').write_text(json.dumps(results,indent=2)+'\n')
print('PC26_GAIT_CAPTURE_PASS: 32 real frames and four full-cycle GIF previews; visual approval pending')
