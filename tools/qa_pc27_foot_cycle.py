#!/usr/bin/env python3
"""PC27 deterministic A/B evidence for real full-cycle gait corrections.

Reports leg-pixel symmetry/temporal change; human visual review is required.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat,ImageOps,ImageDraw
import json
base=Path('pc27-legacy-gait-captures')
new=Path('pc26-gait-captures')
out=Path('pc27-gait-comparison')
out.mkdir(exist_ok=True)
result={}
for sex in ('male','female'):
    for gait in ('walk','run'):
        key=f'{sex}_{gait}'
        original=[]
        candidate=[]
        for i in range(8):
            n=f'{key}_{i:02d}.png'
            a=Image.open(base/n).convert('RGB')
            b=Image.open(new/n).convert('RGB')
            if a.size!=b.size or a.width<950 or a.height<570:
                raise SystemExit(f'PC27_BAD_CAPTURE {n} {a.size}/{b.size}')
            original.append(a)
            candidate.append(b)
        roi=(535,300,755,563)
        def score(seq):
            a=seq[1].crop(roi)
            b=ImageOps.mirror(seq[5].crop(roi))
            return round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,5)
        before_sym=score(original)
        after_sym=score(candidate)
        phase_change=sum(ImageStat.Stat(ImageChops.difference(original[1].crop(roi),candidate[1].crop(roi))).mean)/3
        if phase_change<0.10:
            raise SystemExit(f'PC27_GAIT_PATCH_NOT_VISIBLE {key} {phase_change}')
        result[key]={'legacy_phase_1_vs_mirrored_5_difference':before_sym,
                     'pc27_phase_1_vs_mirrored_5_difference':after_sym,
                     'baseline_vs_candidate_difference':round(phase_change,5),
                     'note':'Raw image symmetry is diagnostic, not automatic quality acceptance'}
        canvas=Image.new('RGB',(4*350,2*400),(16,19,22))
        d=ImageDraw.Draw(canvas)
        for row,seq in enumerate((original,candidate)):
            for column,frame_i in enumerate((0,1,3,5)):
                view=seq[frame_i].crop((485,158,815,518)).resize((330,360),Image.Resampling.LANCZOS)
                x=column*350;y=row*400
                canvas.paste(view,(x,y+24))
                d.text((x+8,y+7),f'{"OLD" if row==0 else "PC27"} {key} phase {frame_i}',fill=(238,238,226))
        canvas.save(out/f'{key}_gait_old_vs_pc27.jpg',quality=93,subsampling=0)
        print(f'PC27_GAIT_EVIDENCE {key} baseline_sym={before_sym} new_sym={after_sym} change={phase_change:.4f}')
(out/'pc27_gait_qa.json').write_text(json.dumps(result,indent=2)+'\n')
print('PC27 phase A/B generated; final gait acceptance requires watching genuine 8-frame GIFs')
