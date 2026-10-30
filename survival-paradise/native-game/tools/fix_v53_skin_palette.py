#!/usr/bin/env python3
"""V53 skin synchronization, color-only, with original V31/V40 idle untouched.

Player idle is always body.png. NPC idle is the original planted silhouette.
The V44-derived walk and the role variants must share their exact skin RGB with
those respective idle atlases. We never change a frame's alpha or coordinates.
"""
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image
from build_v51_assets import ROLES, SEXES, role_palette

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'app/src/main/assets'

def read(name):
    return np.array(Image.open(ASSETS/name).convert('RGBA'),dtype=np.uint8)

def store(name,pixels):
    Image.fromarray(pixels,'RGBA').save(ASSETS/name,optimize=True)

def skin_like(c):
    r,g,b,a=map(int,c)
    return a==255 and r>=120 and g>=85 and b>=55 and r>=g+17 and g>=b+10

def skin_colors(frame):
    # Take actual canonical face swatches, never shirt, pants or outlines.
    sample=frame[25:92,65:111,:].reshape(-1,4)
    counts=Counter(tuple(int(v) for v in p) for p in sample if skin_like(p))
    assert counts,'Approved face must contain a recognizable skin palette'
    # Keep all skin shades, ranked by their observed area.
    return {rgb for rgb,n in counts.items() if n>=4}

def mask_from_colors(pixels,colors):
    mask=np.zeros(pixels.shape[:2],dtype=bool)
    for rgba in colors:
        mask|=np.all(pixels==np.array(rgba,dtype=np.uint8),axis=-1)
    return mask

def common_color(pixels,region=None):
    colors=skin_colors(region if region is not None else pixels)
    counts=Counter(tuple(int(v) for v in p) for p in
                   (region if region is not None else pixels).reshape(-1,4))
    return max(colors,key=lambda c:counts[c])

def main():
    original=read('body.png')
    walk=read('stable_v51_body.png')
    npc_walk=read('npc_roles_v51.png')
    npc_idle=read('npc_idle_v52.png')
    assert original.shape==(160,1040,4) and walk.shape==(160,1040,4)
    assert npc_walk.shape==(1920,1040,4) and npc_idle.shape==(1920,260,4)
    approved=original[:,520:780,:]
    original_skin=skin_colors(approved)
    walk_skin=skin_colors(walk[:,520:780,:])
    player_color=common_color(approved)
    walk_mask=mask_from_colors(walk,walk_skin)
    idle_mask=mask_from_colors(approved,original_skin)
    original_walk_alpha=walk[:,:,3].copy()
    original_roles_alpha=npc_walk[:,:,3].copy()
    original_role_idle_alpha=npc_idle[:,:,3].copy()
    assert int(walk_mask.sum())>=40 and int(idle_mask.sum())>=40,'Skin mask unexpectedly small'
    # Color-only: canonical original idle has priority over every walking pose.
    walk[walk_mask]=player_color
    for role_idx,role in enumerate(ROLES):
        for sex_idx,sex in enumerate(SEXES):
            i=role_idx*2+sex_idx
            role_color=role_palette(role,sex)['skin']
            row_walk=npc_walk[i*160:(i+1)*160]
            row_idle=npc_idle[i*160:(i+1)*160]
            # The role walk frame geometry exactly matches the player walk.
            row_walk[walk_mask]=role_color
            # Restore the approved role complexion on original planted geometry.
            row_idle[idle_mask]=role_color
    assert np.array_equal(walk[:,:,3],original_walk_alpha)
    assert np.array_equal(npc_walk[:,:,3],original_roles_alpha)
    assert np.array_equal(npc_idle[:,:,3],original_role_idle_alpha)
    # Assert identity of actual complexion in every pose, independent of sprite shape.
    assert all(tuple(p)==tuple(player_color) for p in walk[walk_mask])
    for role_idx,role in enumerate(ROLES):
        for sex_idx,sex in enumerate(SEXES):
            i=role_idx*2+sex_idx
            color=tuple(role_palette(role,sex)['skin'])
            assert np.all(np.all(npc_walk[i*160:(i+1)*160][walk_mask]==color,axis=1))
            assert np.all(np.all(npc_idle[i*160:(i+1)*160][idle_mask]==color,axis=1))
    store('stable_v51_body.png',walk)
    store('npc_roles_v51.png',npc_walk)
    store('npc_idle_v52.png',npc_idle)
    print('V53 PASS: original player idle unchanged, all walking and NPC idle/walk skin RGB consistent')

if __name__=='__main__':
    main()
