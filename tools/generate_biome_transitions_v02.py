#!/usr/bin/env python3
"""Generate 36 deterministic biome-edge transition tiles for *prototype QA only*.

Each cardinal transition is restricted to the middle of its 256px cell and
preserves exact adjacent biome edge pixels. Does not alter approved art.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
from PIL import Image

PAIRS = [
  ('Forest','Grassland'), ('Grassland','Swamp'), ('Grassland','Coastal'),
  ('Grassland','RockyHighlands'), ('Desert','AridScrubland'),
  ('AridScrubland','RockyHighlands'), ('City','Industrial'),
  ('Grassland','City'), ('Desert','Coastal'),
]
DIRECTIONS=('LR','RL','TB','BT')
T=256

def load(root,biome):
 p=root/biome/'Terrain'/f'SP_{biome}_Terrain_Base_01.png'
 if not p.is_file():raise FileNotFoundError(p)
 im=Image.open(p).convert('RGB')
 if im.size!=(T,T):raise ValueError(f'Expected 256x256 {p}')
 return np.asarray(im,dtype=np.uint8)

def weight(direction,phase):
 # Periodic perpendicular offsets keep stacked transition tiles consistent.
 y,x=np.mgrid[0:T,0:T].astype(np.float32)
 coord=x if direction in ('LR','RL') else y
 perpendicular=y if direction in ('LR','RL') else x
 phasewave=(np.sin((perpendicular/T)*2*np.pi+phase)*0.047
     +np.sin((perpendicular/T)*6*np.pi+phase*.7)*0.021)
 center=T*(.5+phasewave)
 t=np.clip((coord-center)/(T*.19)+.5,0,1)
 s=t*t*(3-2*t)
 if direction in ('RL','BT'):s=1-s
 return s[:,:,None]

def generate(a,b,direction,phase):
 w=weight(direction,phase)
 out=np.clip(np.rint(a.astype(np.float32)*(1-w)+b.astype(np.float32)*w),0,255).astype('uint8')
 # Strict border contract: Tiled left/right or top/bottom biome source pixels.
 if direction=='LR':out[:,0,:]=a[:,-1,:];out[:,-1,:]=b[:,0,:]
 elif direction=='RL':out[:,0,:]=b[:,-1,:];out[:,-1,:]=a[:,0,:]
 elif direction=='TB':out[0,:,:]=a[-1,:,:];out[-1,:,:]=b[0,:,:]
 elif direction=='BT':out[0,:,:]=b[-1,:,:];out[-1,:,:]=a[0,:,:]
 return Image.fromarray(out,'RGB')

def validate_tile(im,a,b,direction):
 pix=np.asarray(im)
 if direction=='LR':valid=np.array_equal(pix[:,0],a[:,-1]) and np.array_equal(pix[:,-1],b[:,0])
 elif direction=='RL':valid=np.array_equal(pix[:,0],b[:,-1]) and np.array_equal(pix[:,-1],a[:,0])
 elif direction=='TB':valid=np.array_equal(pix[0],a[-1]) and np.array_equal(pix[-1],b[0])
 else:valid=np.array_equal(pix[0],b[-1]) and np.array_equal(pix[-1],a[0])
 assert valid,('border mismatch',direction)
 return True

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('game_assets',type=Path)
 ap.add_argument('output',type=Path)
 args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for index,(b1,b2) in enumerate(PAIRS):
  a,b=load(args.game_assets,b1),load(args.game_assets,b2)
  for direction in DIRECTIONS:
   im=generate(a,b,direction,index*.67+1.3)
   validate_tile(im,a,b,direction)
   name=f'SP_Transition_{b1}_To_{b2}_{direction}.png'
   dest=args.output/name
   im.save(dest,compress_level=4)
   manifest.append({'file':name,'from':b1,'to':b2,'direction':direction,'status':'generated_unapproved','sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
 assert len(manifest)==36
 (args.output/'manifest.json').write_text(json.dumps({'version':'v02','count':36,'status':'generated_unapproved_not_playable','tiles':manifest},indent=2))
 print('SP_TERRAIN_TRANSITIONS_QA_PASS pairs=9 cardinal_variants=36 border_checks=36')

if __name__=='__main__':main()