#!/usr/bin/env python3
"""Bake true single-sprite, full-body walk/run/idle frames from approved 64x96 art.

This is not the old static torso + animated leg overlay: the ENTIRE actor,
including head, shirt, backpack, pelvis, both pants and boots, is rasterized
into ONE transparent RGBA image for every animation frame. Runtime uses just
one Sprite2D; no separate leg nodes, procedural strokes or skeletons.
"""
from pathlib import Path
from PIL import Image
import hashlib, json, math
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"melee-six-prototype/assets/approved_clean_torso_right.png"
BANDIT=ROOT/"assets/sp_npc_simple/sp_simple_bandit_male_01.png"
DEST=ROOT/"assets/sp_unified_character"
W,H=64,96
orig=Image.open(BASE).convert("RGBA")
bandit_upper=Image.open(BANDIT).convert("RGBA")
assert orig.size==(W,H)==bandit_upper.size
assert orig.getchannel("A").getbbox()
# Combined source is SAME approved player alpha at rest. None of the existing
# actor's silhouette is enlarged or replaced by an unrelated avatar.
def make_source(name):
    if name=="player":return orig.copy()
    assert name=="bandit01"
    v=orig.copy()
    # Replace corresponding source pixels, do NOT alpha-composite the same
    # semi-transparent antialiased silhouette twice (that increases opacity).
    for yy in range(78):
        for xx in range(W):
            v.putpixel((xx,yy),bandit_upper.getpixel((xx,yy)))
    assert v.getchannel("A").tobytes()==orig.getchannel("A").tobytes()
    return v

def bounded(v,lo,hi):
    return min(hi,max(lo,v))
def bake(src,phase,mode):
    if mode=="idle" and phase==0:return src.copy()
    # Micro-movement at 64x96. The whole upper body and bag sway with each step.
    phase=float(phase)
    amplitude={"idle":0.0,"walk":3.0,"run":5.0}[mode]
    s=math.sin(phase)
    c=math.cos(phase)
    # Head, backpack and torso are never left behind at original coordinates.
    torso_sway=(int(round(1.0*s)) if mode!="idle" else 0)
    bob=(int(round(1.0*(1.0-c*c))) if mode!="idle" else 0)
    # Running uses more upper-body momentum but stays within original 64px scale.
    shoulder_shift=int(round((0.7 if mode=="walk" else 1.0)*math.sin(phase+0.5))) if mode!="idle" else 0
    # Resting breathing: entire torso/head gently moves a pixel every other
    # phase; no static second skeleton or leg overlay is rendered.
    idle_breath=(-1 if math.sin(phase)>0.70 else 0) if mode=="idle" else 0
    canvas=Image.new("RGBA",(W,H),(0,0,0,0))
    sp=src.load()
    # Split is exclusively OFFLINE pixel remapping to produce a SINGLE frame.
    # At runtime no leg, upper or pelvis child is ever instantiated.
    for layer in ("far_leg","near_leg","upper"):
        for y in range(H):
            for x in range(W):
                if (layer=="upper") != (y<=77):continue
                if layer=="far_leg" and x<37:continue
                if layer=="near_leg" and x>=37:continue
                color=sp[x,y]
                if color[3]==0:continue
                if layer=="upper":
                    # All upper parts move coherently: head, shirt, backpack and hips.
                    fraction=bounded((76.0-y)/65.0,0,1)
                    dx=torso_sway+int(round(shoulder_shift*fraction))
                    dy=idle_breath if mode=="idle" else -bob
                else:
                    stride_fraction=bounded((y-77.0)/18.0,0,1)
                    gait=s if layer=="near_leg" else -s
                    dx=torso_sway+int(round(amplitude*gait*stride_fraction))
                    lift=(max(0.0,gait) * (1.1 if mode=="walk" else 2.1)) if mode!="idle" else 0
                    dy=(idle_breath if mode=="idle" else -bob) - int(round(lift*stride_fraction))
                nx,ny=x+dx,y+dy
                if 0<=nx<W and 0<=ny<H:
                    canvas.putpixel((nx,ny),color)
    # Occlusion fix: copy only original opaque pelvis clothing at the
    # shared y75–79 waist seam, aligned with the moving full character.
    # This prevents exposed transparent hip gaps on opposite leg swings.
    seam_x=torso_sway
    seam_y=idle_breath if mode=="idle" else -bob
    for y in range(73,79):
        for x in range(23,55):
            col=sp[x,y]
            if col[3]==0:continue
            xx,yy=x+seam_x,y+seam_y
            if 0<=xx<W and 0<=yy<H:
                canvas.putpixel((xx,yy),col)
    return canvas

def png(im,path):
    assert im.mode=="RGBA" and im.size==(W,H),path
    assert im.getchannel("A").getbbox() is not None,path
    path.parent.mkdir(parents=True,exist_ok=True)
    im.save(path,optimize=True)
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest={"schema":"SP_UNIFIED_FULLBODY_V1",
   "target_canvas":[W,H],
   "source":"approved_clean_torso_right.png",
   "rendering":"exactly ONE Sprite2D full character for each frame",
   "no_static_torso_layer":True,"no_procedural_or_skeletal_legs":True,
   "no_parallel_character_skeleton":True,
   "left_direction":"mirror same full-body frames",
   "approval":"EXPERIMENTAL_NATIVE_GODOT_VISUAL_REVIEW_REQUIRED",
   "integrated_into_playable_game":False,"characters":{}}
for character in ("player","bandit01"):
    source=make_source(character)
    source_alpha=source.getchannel("A")
    pathroot=DEST/character
    record={}
    for mode,count in (("idle",8),("walk",16),("run",16)):
        images=[]
        hashes=[]
        for k in range(count):
            image=bake(source,2*math.pi*k/count,mode)
            images.append(image)
            hashes.append(png(image,pathroot/mode/("%02d.png"%k)))
        if mode=="idle":
            assert images[0].tobytes()==source.tobytes(),"first idle frame must EXACTLY reproduce approved player"
        unique=len(set(im.tobytes() for im in images))
        assert unique>=(2 if mode=="idle" else 4),(character,mode,unique)
        record[mode]={"count":count,"sha256":hashes,"unique_frames":unique}
    manifest["characters"][character]=record
    # zero-frame physical dimensions and alpha exactly match original
    zero=Image.open(pathroot/"idle/00.png").convert("RGBA")
    assert zero.getchannel("A").tobytes()==source_alpha.tobytes()

(DEST/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
print("SP_UNIFIED_FULLBODY_80_FRAMES_PASS")
print("SP_UNIFIED_ONE_SPRITE_NO_LEG_OVERLAY_PASS")
print("SP_UNIFIED_IDLE_SOURCE_BYTE_IDENTICAL_PASS")
