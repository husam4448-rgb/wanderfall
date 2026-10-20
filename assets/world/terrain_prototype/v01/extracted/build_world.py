#!/usr/bin/env python3
"""Survival Paradise procedural-world modular art prototype, deterministic and repeatable.
Generates 2D ground tiles, seam-safe overlay decals, road masks and biome region previews.
Not a Godot scene; integration requires terrain import, collisions and gameplay logic.
"""
import os, math, csv, json, random, zipfile, hashlib, io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import numpy as np
from scipy.ndimage import gaussian_filter

ROOT=Path(__file__).parent
OUT=ROOT/'GameAssets'
T=256
SEED=20261020
R=random.Random(SEED)
BIOMES={
 'Forest':('#434934','#22291e','#606940','#667751'),
 'Desert':('#b4a077','#796d54','#d0b78b','#a89564'),
 'Grassland':('#647450','#46583e','#94a174','#b2ad70'),
 'Swamp':('#424c3d','#242e2a','#666a4b','#3c5551'),
 'Coastal':('#c1af8b','#877b65','#dfca9d','#9aab9d'),
 'RockyHighlands':('#777267','#4a4a45','#9d9788','#a39c89'),
 'AridScrubland':('#95826a','#6a6555','#b3a188','#7c8b5f'),
 'City':('#60605f','#424548','#858682','#918476'),
 'Industrial':('#595a58','#393c3d','#777570','#8c6e52'),
}
DECALS=['PebbleScatter','WeatheredPatch','VegetationTufts','ScuffedSoil','DebrisScatter','CrackNetwork','DarkStain','DenseTexture']
ROAD_TYPES={
 'Asphalt':('#3e4345','#24292c','#c4a153'),
 'Concrete':('#74736c','#4d4b47','#d0ad59'),
 'Gravel':('#847665','#665e53','#b69b5a'),
 'Dirt':('#76614e','#584737','#a78b67'),
}
MANIFEST=[]
def rgb(hexstr):return tuple(bytes.fromhex(hexstr.lstrip('#')))
def blend(a,b,t):return np.asarray(a)*(1-t)+np.asarray(b)*t

def rel(name):return name.relative_to(OUT).as_posix()
def store(image,name,category,biome,meta=None):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 image.save(p,optimize=True,compress_level=9)
 stats=image.getchannel('A').getextrema() if image.mode=='RGBA' else (255,255)
 MANIFEST.append({'path':rel(p),'biome':biome,'category':category,'width':image.width,'height':image.height,'alpha_min':stats[0],'alpha_max':stats[1],'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'prototype_qa_pending',**(meta or {})})
 return p

def wrap_noise(seed,sigma):
 rng=np.random.default_rng(seed);a=rng.normal(size=(T,T)).astype('float32');a=gaussian_filter(a,sigma=sigma,mode='wrap');a-=a.mean();std=a.std();return a/(std if std else 1)

def make_ground(biome,colors,idx):
 base=np.array(rgb(colors[0]),dtype=np.float32);dark=np.array(rgb(colors[1]),dtype=np.float32)
 light=np.array(rgb(colors[2]),dtype=np.float32);accent=np.array(rgb(colors[3]),dtype=np.float32)
 n1=wrap_noise(idx+1000,24);n2=wrap_noise(idx+3000,6);n3=wrap_noise(idx+2000,1.4)
 n=n1*0.40+n2*0.32+n3*0.28
 arr=np.broadcast_to(base,(T,T,3)).copy()
 arr+=(n[:,:,None]*16)
 pos=np.clip(n1*0.5+n2*0.28,0,1)[:,:,None]
 neg=np.clip(-n1*0.3-n2*0.38,0,1)[:,:,None]
 arr+=pos*(light-base)*0.52+neg*(dark-base)*0.73
 # Unique biomes with their own surface ingredients.
 patch=wrap_noise(idx+9000,10)
 if biome=='Swamp':
  water=patch>1.33
  arr[water]=arr[water]*0.40+np.array([33,61,58])*0.60
 elif biome=='Desert':
  arr[:,:,0]+=np.clip(n2*4,0,7);arr[:,:,1]+=np.clip(n1*4,0,7)
 elif biome=='Industrial':
  oil=patch>1.55;arr[oil]=arr[oil]*.48+np.array([30,28,28])*.52
 elif biome=='Coastal':
  shell=patch>1.4;arr[shell]=arr[shell]*.65+np.array([224,218,193])*.35
 elif biome=='RockyHighlands':
  stone=patch>1.0;arr[stone]=arr[stone]*.7+np.array([110,112,107])*.3
 # Repeatable pixel clusters: paired dark/light grains.
 rng=np.random.default_rng(idx+20000)
 mask=rng.random((T,T))>.955
 arr[mask]=arr[mask]*.63+dark*.37
 mask=rng.random((T,T))>.969
 arr[mask]=arr[mask]*.62+accent*.38
 arr=np.clip(arr,0,255).astype('uint8')
 im=Image.fromarray(arr,'RGB').convert('RGBA')
 return im

def line(draw,coords,c,w=1):draw.line(coords,fill=c,width=w,joint='curve')
def make_decal(biome,kind,v):
 colors=BIOMES[biome];dark=rgb(colors[1]);accent=rgb(colors[3]);light=rgb(colors[2])
 rng=random.Random(SEED+v*141+len(kind)*37+len(biome)*191)
 im=Image.new('RGBA',(T,T));d=ImageDraw.Draw(im)
 # all decals must be transparent within 12px of all tile boundaries
 def pt():return rng.randint(16,T-17),rng.randint(16,T-17)
 center=(rng.randint(85,171),rng.randint(85,171))
 def radial(n,radius):
  for _ in range(n):
   q=rng.random()*2*math.pi;rad=radius*math.sqrt(rng.random());x=int(center[0]+math.cos(q)*rad);y=int(center[1]+math.sin(q)*rad)
   if 14<=x<T-14 and 14<=y<T-14: yield x,y
 if kind in ['PebbleScatter','DebrisScatter']:
  n=170 if kind=='PebbleScatter' else 65
  for x,y in radial(n,75):
   r=rng.randint(1,4 if kind=='PebbleScatter' else 7)
   shade=light if rng.random()>.48 else dark
   color=shade+(rng.randint(85,195),)
   d.ellipse((x-r,y-r//2,x+r,y+r//2+1),fill=color)
   if r>2:d.line((x-r+1,y-r//2,x+r-1,y-r//2),fill=(215,201,170,55),width=1)
 elif kind in ['WeatheredPatch','ScuffedSoil','DenseTexture','DarkStain']:
  alpha={'WeatheredPatch':48,'ScuffedSoil':67,'DenseTexture':85,'DarkStain':115}[kind]
  spread=70 if kind!='DarkStain' else 45
  for x,y in radial(750 if kind=='DenseTexture' else 310,spread):
   r=rng.randint(1,3 if kind!='DarkStain' else 7);col=dark if kind!='DenseTexture' else accent
   d.ellipse((x-r,y-r,x+r,y+r),fill=col+(rng.randint(25,alpha),))
 elif kind=='CrackNetwork':
  for _ in range(5):
   x,y=pt();x=min(max(x,55),200);y=min(max(y,55),200)
   pts=[(x,y)]
   for j in range(rng.randint(4,9)):
    x=min(max(x+rng.randint(-21,21),15),241);y=min(max(y+rng.randint(-19,19),15),241);pts.append((x,y))
   d.line(pts,fill=dark+(145,),width=rng.choice([1,1,2]))
   for x,y in pts[1:-1][::2]:d.line((x,y,x+rng.randrange(-16,17),y+rng.randrange(8,23)),fill=dark+(100,),width=1)
 elif kind=='VegetationTufts':
  wet=biome in ['Swamp','Forest','Grassland','Coastal']
  plant=(72,94,54) if wet else (113,116,74)
  if biome in ['Industrial','City']:plant=(89,105,75)
  for x,y in radial(42,76):
   height=rng.randrange(4,15);c=tuple(max(0,min(255,v+rng.randint(-17,15))) for v in plant)
   d.line((x,y,x-rng.randint(-3,4),y-height),fill=c+(rng.randint(130,220),),width=2)
   d.line((x+2,y,x+2+rng.randint(-5,5),y-height//2),fill=dark+(160,),width=1)
 # Guarantee seam-safe transparent 12-pixel perimeter for every decal.
 arr=np.asarray(im).copy();arr[:12,:,3]=0;arr[-12:,:,3]=0;arr[:,:12,3]=0;arr[:,-12:,3]=0
 return Image.fromarray(arr,'RGBA')

def road_tile(roadtype,bits):
 # N E S W bit mask 1 2 4 8. Transparent overlay, path must connect exactly at cardinal edges.
 road,shadow,mark=[rgb(x) for x in ROAD_TYPES[roadtype]]
 m=Image.new('L',(T,T),0);d=ImageDraw.Draw(m)
 W=78;c=T//2
 d.ellipse((c-W,c-W,c+W,c+W),fill=255)
 if bits&1:d.rectangle((c-W,0,c+W,c),fill=255)
 if bits&2:d.rectangle((c,c-W,T,c+W),fill=255)
 if bits&4:d.rectangle((c-W,c,c+W,T),fill=255)
 if bits&8:d.rectangle((0,c-W,c,c+W),fill=255)
 # no singleton circular island for 0; only decal texture at intersections
 if bits==0:d.rectangle((c-W,c-W,c+W,c+W),fill=255)
 arr=np.zeros((T,T,4),dtype=np.uint8)
 n=wrap_noise(70000+len(roadtype)*123,5)*.35+wrap_noise(70001+len(roadtype)*123,1.2)*.65
 base=np.array(road,dtype=np.float32)[None,None,:]
 arr[:,:,:3]=np.clip(base+n[:,:,None]*22,0,255).astype('uint8')
 arr[:,:,3]=np.asarray(m)
 im=Image.fromarray(arr,'RGBA')
 # rough surface + white/yellow dashes no misplaced stripes through junctions
 rng=random.Random(SEED+len(roadtype)*43+bits)
 details=Image.new('RGBA',(T,T));dd=ImageDraw.Draw(details)
 for _ in range(450):
  x,y=rng.randrange(T),rng.randrange(T)
  if not m.getpixel((x,y)):continue
  cc=shadow if rng.random()<.63 else tuple(min(255,v+28) for v in road)
  dd.point((x,y),fill=cc+(rng.randint(50,125),))
 # center line only when exactly opposite through passage, not at crossing/T
 if bits==5:
  for y in range(0,T,32):dd.rectangle((c-2,y+4,c+2,y+21),fill=mark+(180,))
 elif bits==10:
  for x in range(0,T,32):dd.rectangle((x+4,c-2,x+21,c+2),fill=mark+(180,))
 # soft bevel stone edge limited to mask perimeter, subtle relief from above
 e=m.filter(ImageFilter.MaxFilter(7));edge=np.clip(np.asarray(e).astype('int16')-np.asarray(m).astype('int16'),0,255).astype('uint8');edgeImg=Image.new('RGBA',(T,T),shadow+(0,));edgeImg.putalpha(Image.fromarray((edge*.65).astype('uint8'),'L'))
 canvas=Image.new('RGBA',(T,T));canvas.alpha_composite(edgeImg);canvas.alpha_composite(im);canvas.alpha_composite(details)
 return canvas

def generate():
 for idx,(biome,pal) in enumerate(BIOMES.items()):
  im=make_ground(biome,pal,idx*800+SEED)
  store(im,Path(biome)/'Terrain'/f'SP_{biome}_Terrain_Base_01.png','TerrainBase',biome,{'tile_seam_safe':True})
  for kind in DECALS:
   for v in [1,2]:
    de=make_decal(biome,kind,v)
    store(de,Path(biome)/'TerrainDetails'/f'SP_{biome}_Decal_{kind}_{v:02d}.png','TerrainDetail',biome,{'edge_transparent':True})
 for name in ROAD_TYPES:
  for b in range(16):
   im=road_tile(name,b)
   store(im,Path('Shared')/'Roads'/name/f'SP_Road_{name}_{b:02d}.png','RoadTile','Shared',{'connectors': ''.join(s for bit,s in [(1,'N'),(2,'E'),(4,'S'),(8,'W')] if b&bit),'mask':b,'edge_connectable':True})
 print('generated',len(MANIFEST),'PNG source files')

def main():
 generate()
 with (ROOT/'assets_manifest.json').open('w') as f:json.dump({'project':'Survival Paradise','build_type':'modular_2D_terrain_prototype','version':1,'seed':SEED,'terrain_tile_px':T,'biomes':list(BIOMES),'road_bitmask':'N=1 E=2 S=4 W=8','tile_semantics':'base tiles wrap-periodic; variation decals have transparent perimeter; road connector masks match boundaries','assets':MANIFEST},f,indent=2)
 print('Total MB',sum(m['bytes'] for m in MANIFEST)/1e6)
if __name__=='__main__':main()
