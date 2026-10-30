#!/usr/bin/env python3
"""Restore ORIGINAL pixel-perfect planted idle for NPCs using V51 approved role palettes.
Uses previously approved original body.png and approved role-derived V51 atlas as
palette truth. Source images are never edited. Output contains the original
26x16(?) cell, 260x160, per NPC, vertically stacked.
"""
from PIL import Image
from collections import Counter
import numpy as np
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1] if 'native-game' in str(Path(__file__).resolve()) else None
if root is None or not (root/'app/src/main/assets').is_dir():
    # for development preview only
    root=Path('/mnt/data/v52_debug')
    base=Image.open(root/'V50_body.png').convert('RGBA')
    template=Image.open(root/'V51_stable_v51_body.png').convert('RGBA')
    roles=Image.open(root/'V51_npc_roles_v51.png').convert('RGBA')
    output=root/'npc_idle_v52.png'
else:
    base=Image.open(root/'app/src/main/assets/body.png').convert('RGBA')
    template=Image.open(root/'app/src/main/assets/stable_v51_body.png').convert('RGBA')
    roles=Image.open(root/'app/src/main/assets/npc_roles_v51.png').convert('RGBA')
    output=root/'app/src/main/assets/npc_idle_v52.png'
assert base.size==(1040,160) and template.size==(1040,160) and roles.size==(1040,1920)
source=np.array(base, dtype=np.uint8)
model=np.array(template, dtype=np.uint8)
role=np.array(roles, dtype=np.uint8)
orig=source[:,520:780,:].copy()  # source V40/V50 planted idle frame, never V51 reconstructed walk
pixel_source_colors=[tuple(x) for x in np.unique(model.reshape(-1,4),axis=0)]
output_array=np.zeros((160*12,260,4),dtype=np.uint8)
for idx in range(12):
    role_pixels=role[idx*160:(idx+1)*160]
    result=orig.copy()
    for color in pixel_source_colors:
        c=np.array(color,dtype=np.uint8)
        mask=np.all(model==c,axis=-1)
        if not np.any(mask):continue
        options,counts=np.unique(role_pixels[mask],axis=0,return_counts=True)
        mapped=options[np.argmax(counts)]
        recolor_mask=np.all(orig==c,axis=-1)
        result[recolor_mask]=mapped
    assert np.array_equal(result[:,:,3],orig[:,:,3]), 'Role idle alpha must exactly match original approved idle silhouette'
    output_array[idx*160:(idx+1)*160]=result
out=Image.fromarray(output_array,'RGBA')
output.parent.mkdir(parents=True,exist_ok=True)
out.save(output,optimize=True)
print('V52 NPC idle atlas:',output, out.size, output.stat().st_size,'bytes. Original idle geometry preserved exactly.')