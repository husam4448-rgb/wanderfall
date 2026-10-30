#!/usr/bin/env python3
"""Build V51 approved-geometry body/NPC atlases deterministically.
Original V44 source art remains unmodified. Role palettes sampled exclusively from
project-approved role art in assets/authored2d; never use random synthetic colors.
"""
from pathlib import Path
from collections import Counter
from PIL import Image
import numpy as np
import sys
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent.parent
ASSETS=ROOT/'app/src/main/assets'
ROLE_SRC=REPO/'assets/authored2d'
ROLES=['bandit','guard','medic','mechanic','trader','civilian']
SEXES=['male','female']
BLACK=np.array([0,0,0,255], dtype=np.uint8)
# Source optical face right from canonical original frame 2: x101..109 must be black.
FACE_FRONT_X=(101,110)
FACE_Y=(29,92)

def stable_from_atlas(original:Image.Image):
    source=np.asarray(original.convert('RGBA'),dtype=np.uint8)
    assert source.shape==(160,1040,4)
    out=np.zeros_like(source)
    source_offsets=[8,4,0,4]   # align whole gait to the original planted frame-2/idle pivot
    canon=source[:101,2*260:3*260,:].copy()
    for f,offset in enumerate(source_offsets):
        part=source[:,f*260:(f+1)*260,:]
        shifted=np.zeros_like(part)
        shifted[:,offset:,:]=part[:,:260-offset,:]
        # fixed canonical head prevents any horizontal optical contour shift.
        shifted[:101,:,:]=canon
        # 9 pixel inward black contour at identical source coords in every pose;
        # exact original black outer silhouette stays in its original position.
        shifted[FACE_Y[0]:FACE_Y[1],FACE_FRONT_X[0]:FACE_FRONT_X[1],:]=BLACK
        out[:,f*260:(f+1)*260,:]=shifted
    return Image.fromarray(out,'RGBA')

def color_from_image(path, section):
    im=Image.open(path).convert('RGBA'); im.thumbnail((128,128))
    colors=Counter()
    for r,g,b,a in im.getdata():
        if a<210:continue
        if min(r,g,b)<15 and max(r,g,b)<48:continue
        if section=='skin':
            if not(r>g*1.05 and g>=b*.80 and r>92):continue
        elif section=='hair':
            if not (r<185 and g<160 and b<165):continue
        else:
            if max(r,g,b)-min(r,g,b)<8:continue
        colors[(r//16*16,g//16*16,b//16*16)]+=1
    if not colors:raise ValueError(f'No usable approved color in {path}')
    chosen=colors.most_common(1)[0][0]
    return np.array((*chosen,255), dtype=np.uint8)

def role_palette(role,sex):
    prefix=f'SP_NPC_{role.capitalize()}_{sex.capitalize()}_'
    specialized=ROLE_SRC/'npc_specializations'
    faces=ROLE_SRC/'npc_faces'
    return {
        'skin':color_from_image(faces/(prefix+'Face_Right.png'),'skin'),
        'hair':color_from_image(faces/(prefix+'Face_Right.png'),'hair'),
        'shirt':color_from_image(specialized/(prefix+'Torso_Right.png'),'cloth'),
        'pants':color_from_image(specialized/(prefix+'Pants_Right.png'),'cloth'),
        'boots':color_from_image(specialized/(prefix+'Boots_Right.png'),'cloth'),
    }

def recolor(atlas, pal):
    a=np.asarray(atlas,dtype=np.uint8).copy()
    mapping={
        (242,198,158,255):pal['skin'],
        (169,79,41,255):pal['hair'],
        (124,58,41,255):pal['hair'],
        (220,139,38,255):pal['shirt'],
        (167,84,32,255):pal['shirt'],
        (86,102,65,255):pal['pants'],
        (104,64,43,255):pal['boots']
    }
    for source,target in mapping.items():
        mask=np.all(a==np.array(source,dtype=np.uint8),axis=2)
        a[mask]=target
    # Never recolor outlines, eyes or alpha.
    return Image.fromarray(a,'RGBA')

def main():
    base=stable_from_atlas(Image.open(ASSETS/'approved_v44_walk_palette.png'))
    ASSETS.mkdir(parents=True,exist_ok=True)
    base.save(ASSETS/'stable_v51_body.png',optimize=True)
    # Role palettes are based on genuinely approved role-specific assets.
    atlas=Image.new('RGBA',(1040,160*12),(0,0,0,0))
    for i,role in enumerate(ROLES):
        for j,sex in enumerate(SEXES):
            pal=role_palette(role,sex)
            atlas.alpha_composite(recolor(base,pal),(0,160*(2*i+j)))
    atlas.save(ASSETS/'npc_roles_v51.png',optimize=True)
    print('V51: head same x in every pose, original gait and role sources used',base.size,atlas.size)
if __name__=='__main__':main()