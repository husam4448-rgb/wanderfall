#!/usr/bin/env python3
"""V56: ONLY the approved immutable V44 four-frame walking art and V31 planted idle.

Do NOT derive characters from stable_v51_body.png or recolor a guessed skin mask.
NPC role tint uses the same explicit approved-palette substitution in walking
and idle. This script never edits either canonical source, geometry or alpha.
"""
from pathlib import Path
import hashlib
import numpy as np
from PIL import Image
from build_v51_assets import ROLES, SEXES, role_palette, recolor

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'app/src/main/assets'
WALK=ASSETS/'approved_v44_walk_palette.png'
IDLE=ASSETS/'body.png'
OUT_WALK=ASSETS/'npc_walk_v56.png'
OUT_IDLE=ASSETS/'npc_idle_v56.png'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    before=(sha(WALK),sha(IDLE))
    walk=Image.open(WALK).convert('RGBA')
    body=Image.open(IDLE).convert('RGBA')
    assert walk.size==(1040,160) and body.size==(1040,160)
    walk_pixels=np.asarray(walk)
    planted=np.asarray(body.crop((520,0,780,160)))
    # Source V44 follows the user-approved gait AND preserves V31 face and upper
    # silhouette pixels in corresponding source frames; do not reconstruct it.
    base=walk_pixels[:,520:780,:]
    assert np.array_equal(base[:110],np.asarray(body)[:110,520:780]), (
        'Approved V44 frame 2 face does not match the original idle face')
    canonical_skin=(242,198,158,255)
    assert int(np.all(planted==canonical_skin,axis=2).sum())>=8, (
        'Canonical V31 skin swatch missing: do not guess or generate a replacement')
    roles_walk=Image.new('RGBA',(1040,12*160),(0,0,0,0))
    roles_idle=Image.new('RGBA',(260,12*160),(0,0,0,0))
    skinmask=np.all(planted==canonical_skin,axis=2)
    for i,role in enumerate(ROLES):
        for j,sex in enumerate(SEXES):
            index=2*i+j
            palette=role_palette(role,sex)
            w=np.asarray(recolor(walk,palette),dtype=np.uint8)
            idle=np.asarray(recolor(Image.fromarray(planted,'RGBA'),palette),
                            dtype=np.uint8)
            assert np.array_equal(w[:,:,3],walk_pixels[:,:,3]), (
                'NPC walking silhouette changed')
            assert np.array_equal(idle[:,:,3],planted[:,:,3]), (
                'NPC idle silhouette changed')
            assert np.all(idle[skinmask]==palette['skin']), (
                'Role face skin not identical to approved role mapping')
            # The entire frame-2 upper region is identical for idle and walk,
            # including all skin shades, hair, outlines and eyes.
            assert np.array_equal(w[:110,520:780],idle[:110]), (
                f'Idle / walk identity mismatch in {role} {sex}')
            roles_walk.alpha_composite(Image.fromarray(w,'RGBA'),(0,index*160))
            roles_idle.alpha_composite(Image.fromarray(idle,'RGBA'),(0,index*160))
    roles_walk.save(OUT_WALK,optimize=True)
    roles_idle.save(OUT_IDLE,optimize=True)
    assert (sha(WALK),sha(IDLE))==before,'Immutable approved art was modified'
    print('V56 PASS: approved V44 walking PNG untouched, canonical V31 planted idle')
    print('V56 PASS: 12 NPC roles share exact face and silhouette across idle/walk')
    print('V56 canonical input SHA256:',before,'NPC outputs:',sha(OUT_WALK),sha(OUT_IDLE))

if __name__=='__main__':main()
