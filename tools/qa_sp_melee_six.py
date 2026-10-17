#!/usr/bin/env python3
"""Verify six Godot-rendered attacks and build Android-friendly GIF evidence."""
from pathlib import Path
from PIL import Image
import json, math
NAMES=['forward_right','up_right','down_right','forward_left','up_left','down_left']
FRAMES=[0,2,4,6,8,11]
E=Path('melee-six-prototype/evidence')
E.mkdir(parents=True,exist_ok=True)
report={'godot_screenshots':0,'slash_white_pixels':{},'source_art':'approved_clean_torso_right.png','user_visual_approval':'PENDING','apk':'NOT BUILT'}
all_rows={}
for label in NAMES:
    parts=[]
    for f in FRAMES:
        p=E/f'{label}_f{f:02d}.png'
        assert p.exists() and p.stat().st_size>100, f'missing native Godot capture {p}'
        im=Image.open(p).convert('RGB')
        assert im.size==(900,520), f'wrong output resolution {p}: {im.size}'
        report['godot_screenshots']+=1
        if f in (4,6): # frame 8 is the end of active swing: trail should have vanished
            cx=420+(23 if label.endswith('right') else -23)
            cy=255+29
            count=0
            for y in range(max(0,cy-52),min(520,cy+53)):
                for x in range(max(0,cx-53),min(900,cx+54)):
                    distance=math.hypot(x-cx,y-cy)
                    if 43.0<=distance<=53.5:
                        r,g,b=im.getpixel((x,y))
                        if r>219 and g>225 and b>230:
                            count+=1
            assert count>=4, f'white slash must appear at mechanical hit radius: {label} {f}, count={count}'
            report['slash_white_pixels'][f'{label}_f{f:02d}']=count
        parts.append(im)
    out=E/f'{label}.gif'
    parts[0].save(out,save_all=True,append_images=parts[1:],duration=[110,90,85,85,90,150],loop=0,optimize=False)
    all_rows[label]=parts
# Composite overview from real Godot screenshots, not fake sprite generation
montage=[]
for frame_index in range(len(FRAMES)):
    panel=Image.new('RGB',(3*450,2*360),(30,32,33))
    for i,label in enumerate(NAMES):
        src=all_rows[label][frame_index].crop((205,60,655,420))
        panel.paste(src,((i%3)*450,(i//3)*360))
    montage.append(panel)
montage[0].save(E/'all_six_godot_preview.gif',save_all=True,append_images=montage[1:],duration=[110,90,85,85,90,150],loop=0,optimize=False)
(E/'qa_report.json').write_text(json.dumps(report,indent=2))
print('SP_MELEE_RENDER_QA_PASS '+json.dumps(report))
