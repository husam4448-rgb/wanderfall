#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];A=P/'app/src/main/assets';OUT=P/'previews';OUT.mkdir(exist_ok=True)
player=Image.open(A/'stable_v51_body.png').convert('RGBA');npc=Image.open(A/'npc_roles_v51.png').convert('RGBA')
# Game source is 1040x160; crop visual 116x150 preserving source y/mirror.
for name,image,row,frames,dur in [('SP_V51_Walking_Face_Stable.gif',player,0,4,230),('SP_V51_Idle_Face_Stable.gif',player,0,2,600)]:
    pages=[]
    for f in range(frames):
        if name.startswith('SP_V51_Idle'):
            base=Image.new('RGBA',(136,152))
            pose=player.crop((520+3,0,520+139,152))
            # Planted feet/torso drawn first, then head-only inhale/exhale.
            base.alpha_composite(pose.crop((0,92,136,152)),(0,92))
            base.alpha_composite(pose.crop((0,0,136,101)),(0,-4 if f==1 else 0))
        else:
            base=image.crop((f*260+3,0,f*260+139,152))
        scale=3
        surface=Image.new('RGBA',(430,485),(43,62,56,255))
        surface.alpha_composite(base.resize((408,456),Image.Resampling.NEAREST),(10,16))
        draw=ImageDraw.Draw(surface)
        pages.append(surface.convert('RGB'))
    pages[0].save(OUT/name,save_all=True,append_images=pages[1:],duration=dur,loop=0,optimize=True)
# Role identities with the SAME body geometry and canonical face.
labels=['BANDIT ♂','BANDIT ♀','GUARD ♂','GUARD ♀','MEDIC ♂','MEDIC ♀','MECHANIC ♂','MECHANIC ♀','TRADER ♂','TRADER ♀','CIVILIAN ♂','CIVILIAN ♀']
page=Image.new('RGBA',(6*148,2*217),(38,57,54,255));draw=ImageDraw.Draw(page)
for i,label in enumerate(labels):
    col=i%6;row=i//6
    spr=npc.crop((520+10,i*160,520+120,i*160+150)).resize((110,150),Image.Resampling.NEAREST)
    page.alpha_composite(spr,(col*148+19,row*217+16)); draw.text((col*148+6,row*217+182),label,fill=(226,228,210))
page.convert('RGB').save(OUT/'SP_V51_Approved_NPC_Roles.png',optimize=True)
print('V51 preview files:',[(x.name,x.stat().st_size) for x in OUT.iterdir()])