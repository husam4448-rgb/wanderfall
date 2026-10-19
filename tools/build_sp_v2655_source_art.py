#!/usr/bin/env python3
"""Survival Paradise v265.5 ART-FIRST source recovery.

No algorithmic animal outline is manufactured: source still-life silhouettes
were isolated from newly authored pixel-art scene, manually masked, then
lossily compressed at mobile-native resolution. Those independent source art
bytes are stored in source_art/v2655/source_raster_b64.json in GitHub.

Movement is limited procedural deformation (not motion capture or independently
painted bone animation); document this clearly, don't claim polished gait.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
from io import BytesIO
import base64,json,math,sys
root=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parents[1]
art=json.loads((repo/"source_art/v2655/source_raster_b64.json").read_text())
assert set(art)=={"deer","boar","chicken","rat","workbench","crate","barrel"}
out=root/"assets/biomes/v2653"
out.mkdir(parents=True,exist_ok=True)
print("SP_V2655_ART_SOURCE_BLOB_CHECK",len(art))

def decode(name):
    data=base64.b64decode(art[name],validate=True)
    assert data[:4]==b"RIFF" and data[8:12]==b"WEBP",name
    im=Image.open(BytesIO(data)).convert("RGBA")
    assert 20<=im.width<=130 and 20<=im.height<=96,name
    assert im.getbbox(),name
    return im

for name in art:
    image=decode(name)
    image.save(out/("v2655_SOURCE_%s.png" % name),optimize=True)

def animal_frame(species,direction,frame):
    original=decode(species)
    # Deer and chicken in the authored source face right; boar and rat left.
    right_faces=("deer","chicken")
    if (species in right_faces)!=(direction=="right"):
        original=ImageOps.mirror(original)
    original.thumbnail((59,48),Image.Resampling.LANCZOS)
    w,h=original.size
    phase=math.tau*float(frame)/8
    bounce=round(1.1*(1.0-math.cos(phase*2.0)))
    # Keep original head and torso in the provided authored pixels. Shift the
    # lower silhouette by up to 2 px in opposite gait phase for each limb-pair.
    out=Image.new("RGBA",(64,72))
    px=original.load()
    x0=(64-w)//2
    y0=31-h//2 - bounce
    for y in range(h):
        for x in range(w):
            rgba=px[x,y]
            if rgba[3]<30: continue
            xshift=0
            if y>h*.62 and species in ("deer","boar","rat"):
                step=math.sin(phase+(math.pi if x<w*.46 else 0))
                xshift=round(2.4*step*((y/h-.62)/.38))
            # Head/neck bob offset, all sprite pixels remain tied to the body.
            head_move=round(math.sin(phase)*.8) if (
                y<h*.42 and x>w*.70 and species!="boar") else 0
            dx=x0+x+xshift
            dy=y0+y+head_move
            if 0<=dx<64 and 0<=dy<72:
                out.putpixel((dx,dy),rgba)
    if species=="chicken":
        # Reference art has no sufficiently readable foot pixels. Hand-draw
        # two narrow orange-shaded shanks behind its rounded breast silhouette.
        dr=ImageDraw.Draw(out,"RGBA")
        foot_center=32
        fy=y0+h-2
        for leg,offset in ((-1,0),(1,math.pi)):
            dx=round(3.3*math.sin(phase+offset))
            base_x=foot_center+leg*7
            dr.line([(base_x,fy-2),(base_x+dx,fy+6)],
                fill=(117,78,36,255),width=2)
            dr.line([(base_x+dx,fy+6),(base_x+dx-3,fy+8),
                (base_x+dx+4,fy+8)],fill=(180,117,45,236),width=1)
    return out

for species in ("deer","boar","chicken","rat"):
    for side in ("left","right"):
        images=[]
        for i in range(8):
            im=animal_frame(species,side,i)
            im.save(out/f"v2654_animal_{species}_{side}_{i}.png",optimize=True)
            images.append(im)
        assert any(images[i].tobytes()!=images[0].tobytes() for i in range(1,8)),species
# Old scavenged table now has recognizable hand-painted wood plane and objects.
# Keep exact v2654 source asset dimensions to avoid remapping structure collision.
for prop in ("table","workbench"):
    for variant in range(2):
        p=out/f"v2654_{prop}_{variant}.png"
        if not p.exists():continue
        base=Image.open(p).convert("RGBA")
        src=decode("workbench")
        # Keep authored legs/understructure, replace its simplistic top with
        # properly textured source while respecting target 112x96 canvas.
        src.thumbnail((int(base.width*.80),int(base.height*.43)),
                      Image.Resampling.LANCZOS)
        bx=(base.width-src.width)//2
        by=max(0,int(base.height*.19))
        base.alpha_composite(src,(bx,by))
        base.save(p,optimize=True)
# Show exactly the raster sources and a four-frame motion sequence, at
# gameplay-equivalent small sizes beside a zoomed inspectable view.
panel=Image.new("RGB",(1024,420),(43,47,43))
paint=ImageDraw.Draw(panel)
for idx,species in enumerate(("deer","boar","chicken","rat")):
    paint.text((18+idx*251,9),species.upper()+" source and frame sequence",
              fill=(233,226,206))
    specimen=decode(species)
    specimen.thumbnail((120,100),Image.Resampling.LANCZOS)
    panel.paste(specimen,(18+idx*251,35),specimen)
    for k,frame in enumerate((0,2,4,6)):
        im=Image.open(out/f"v2654_animal_{species}_right_{frame}.png").convert("RGBA")
        im=im.resize((80,90),Image.Resampling.NEAREST)
        dx=10+idx*251+(k%2)*112
        dy=144+(k//2)*118
        panel.paste(im,(dx,dy),im)
paint.text((18,393),"SOURCE-PAINTED ANATOMY; GAIT IS STILL A LIMITED ART-DEFORMATION PROTOTYPE",
           fill=(209,195,157))
panel.save(root/"SP_v2655_SOURCE_ART_QA.png")
print("SP_V2655_SOURCE_ART_PASS 7 traced original-image assets and 64 bidirectional motion frames")
