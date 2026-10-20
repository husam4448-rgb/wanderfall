#!/usr/bin/env python3
"""Assemble deterministic visual region previews and environmental prop prototypes.
Region PNGs are illustrations for composition/scale QA, NOT collision-ready playable maps.
"""
from pathlib import Path
import os,io,random,zipfile,math,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from build_world import ROOT,OUT,T,BIOMES,DECALS,MANIFEST,store,rgb,SEED

BIOME_NAMES=list(BIOMES)
REGION=12
REGION_PX=REGION*T
P=ROOT/'Previews';P.mkdir(exist_ok=True)
COLLIDING_CELLS=set()

# Construct front-visible walls and shallow oblique roofs, not interactable or enterable.
def structure(biome,v):
 r=random.Random(SEED+v*37+len(biome)*421)
 wall={'Desert':'#aa9073','Grassland':'#857662','Swamp':'#6f705f','Coastal':'#ada38d','RockyHighlands':'#88847b','AridScrubland':'#a6957a','Forest':'#817869','City':'#777774','Industrial':'#656766'}[biome]
 roof={'Desert':'#736552','Grassland':'#625949','Swamp':'#39473f','Coastal':'#6b7880','RockyHighlands':'#4d4d4d','AridScrubland':'#676058','Forest':'#4d4f4c','City':'#4b5558','Industrial':'#444c50'}[biome]
 im=Image.new('RGBA',(176,152));d=ImageDraw.Draw(im)
 sh=(0,0,0,65);d.ellipse((29,112,150,133),fill=sh)
 if v%2==0:
  # rectangular industrial / flat-roof rural structure with shaded right wall
  d.polygon([(35,57),(127,57),(141,69),(141,121),(35,121)],fill=rgb(wall)+(255,))
  d.polygon([(126,55),(141,69),(141,120),(126,111)],fill=(44,42,39,235))
  d.polygon([(20,52),(108,32),(142,53),(55,76)],fill=rgb(roof)+(255,))
  d.line([(20,52),(55,76),(142,53)],fill=(23,25,24,255),width=4)
 else:
  d.rectangle((31,61,139,121),fill=rgb(wall)+(255,))
  d.polygon([(28,61),(84,21),(143,61)],fill=rgb(roof)+(255,))
  d.polygon([(84,21),(143,61),(134,68),(81,36)],fill=(41,39,36,165))
  d.line((28,61,84,21,143,61),fill=(31,32,31,255),width=4)
 # doors visually closed, no stairs
 d.rectangle((82,89,102,121),fill=(32,34,31,255));d.rectangle((84,89,86,119),fill=(65,58,52,255))
 d.rectangle((43,88,62,100),fill=(22,31,32,255));d.line((43,88,62,88),fill=(138,142,138,245),width=2)
 for _ in range(60):
  x=r.randint(37,135);y=r.randint(63,117)
  if x in range(82,104) and y>89:continue
  d.point((x,y),fill=(35,38,37,r.randint(80,190)))
 for _ in range(20):
  x=r.randint(42,129);y=r.randint(42,61)
  d.line((x,y,x+r.randint(-6,7),y+r.randint(0,7)),fill=(150,78,55,95),width=1)
 # tiny sign / beam, no text
 if v%3==0:d.rectangle((48,72,73,76),fill=(78,77,65,255))
 return im

def vegetation(biome,v):
 rng=random.Random(SEED+v*196+len(biome)*993)
 im=Image.new('RGBA',(144,144));d=ImageDraw.Draw(im)
 d.ellipse((28,113,116,130),fill=(0,0,0,45))
 if biome in ['Swamp','Grassland','Coastal']:
  base=(67,96,58) if biome=='Grassland' else ((81,99,59) if biome=='Swamp' else (100,113,76))
 elif biome in ['AridScrubland','RockyHighlands']:
  base=(113,113,76)
 else:base=(83,96,68)
 if biome=='Coastal' and v==4:
  # stylized driftwood with weathered highlight
  d.line((30,111,103,78),fill=(91,77,64,255),width=9);d.line((43,107,104,82),fill=(173,151,121,200),width=2)
  d.line((77,93,92,65),fill=(96,76,58,255),width=4)
  return im
 if biome in ['Industrial','City'] and v in [3,4]:
  d.polygon([(31,102),(53,86),(72,101),(99,89),(115,109),(64,121)],fill=(70,69,64,255))
  for _ in range(22):
   x=rng.randint(34,110);y=rng.randint(89,114)
   d.rectangle((x,y,x+rng.randint(2,9),y+rng.randint(2,5)),fill=rng.choice([(102,73,54,220),(125,117,98,245),(62,68,63,240)]))
  return im
 if biome=='RockyHighlands' and v in [1,2]:
  for _ in range(6):
   x=rng.randint(28,106);y=rng.randint(83,111);w=rng.randint(14,35);h=rng.randint(9,24)
   d.polygon([(x-w//2,y),(x,y-h),(x+w//2,y-h//3),(x+w//3,y+4)],fill=(104,101,97,255))
   d.line((x-w//2,y,x,y-h,x+w//2,y-h//3),fill=(178,170,154,180),width=2)
  return im
 count=35 if biome=='Swamp' else 22
 for i in range(count):
  x=rng.randint(30,109);y=rng.randint(103,120)
  t=rng.randint(9,35) if biome=='Swamp' else rng.randint(9,23)
  col=tuple(max(0,min(255,base[j]+rng.randint(-22,19))) for j in range(3))
  d.line((x,y,x+rng.randint(-9,9),y-t),fill=col+(255,),width=rng.choice([2,2,3]))
  if biome!='Swamp':
   d.ellipse((x-5,y-t-4,x+6,y-t+4),fill=col+(220,))
  elif i%6==0:
   d.ellipse((x-2,y-t-5,x+4,y-t+2),fill=(151,133,92,240))
 return im

def prop_library():
 # 9 x 4 authored silhouettes, each separate object; procedural prototypes, not replacements for approved art.
 for b in BIOME_NAMES:
  for i in range(1,5):
   st=structure(b,i)
   store(st,Path(b)/'Structures'/f'SP_{b}_Structure_ShelterFacade_{i:02d}.png','StructurePrototype',b,{'non_enterable_visual':True,'no_stairs':True})
  if b not in ['Forest','Desert']:
   for i in range(1,5):
    im=vegetation(b,i)
    store(im,Path(b)/'Nature'/f'SP_{b}_Nature_Cluster_{i:02d}.png','NaturePrototype',b)

ZIPS={}
def get_libraries():
 for biome,name in [('Forest','SurvivalParadise_Nature_Collection_v01.zip'),('Desert','SurvivalParadise_Desert_Nature_Collection_v01.zip')]:
  z=zipfile.ZipFile(Path('/mnt/data')/name)
  entries=[]
  for n in z.namelist():
   if not n.lower().endswith('.png'):continue
   if biome=='Desert' and ('Tree_DatePalm' in n or 'Tree_Acacia' in n):continue
   if biome=='Forest' and ('Tree' not in n and 'Bush' not in n and 'Rock' not in n):continue
   if biome=='Desert' and ('Shrub' not in n and 'Tree' not in n):continue
   im=Image.open(io.BytesIO(z.read(n))).convert('RGBA')
   # crop 10px transparent and scale to reasonable per-world cell size
   box=im.getchannel('A').getbbox()
   if box:im=im.crop(box)
   im.thumbnail((110,108) if biome=='Forest' else (115,115),Image.Resampling.LANCZOS)
   entries.append((n,im))
  ZIPS[biome]=entries

def draw_field(im, r, x,y,w,h):
 d=ImageDraw.Draw(im,'RGBA');d.rectangle((x,y,x+w,y+h),fill=(148,124,78,165))
 d.rectangle((x,y,x+w,y+h),outline=(80,71,51,235),width=4)
 for i in range(9,w-3,18):
  d.line((x+i,y+6,x+i,y+h-7),fill=(73,93,48,175),width=4)
  for j in range(8,h-3,25):
   if r.random()<.7:d.ellipse((x+i-4,y+j-3,x+i+4,y+j+5),fill=(83,115,48,210))

def paint_water(im, biome,r):
 if biome not in ['Coastal','Swamp']:return
 overlay=Image.new('RGBA',im.size);d=ImageDraw.Draw(overlay)
 if biome=='Coastal':
  # water occupies eastern quarter with bay and a small inland inlet
  poly=[(int(REGION_PX*.81),0),(REGION_PX,0),(REGION_PX,REGION_PX),(int(REGION_PX*.67),REGION_PX),(int(REGION_PX*.72),int(REGION_PX*.75)),(int(REGION_PX*.77),int(REGION_PX*.48)),(int(REGION_PX*.71),int(REGION_PX*.25))]
  d.polygon(poly,fill=(34,79,87,240))
  d.line(poly[:-1],fill=(200,197,163,150),width=17,joint='curve')
  for _ in range(230):
   x=r.randint(int(REGION_PX*.80),REGION_PX-12);y=r.randint(5,REGION_PX-5)
   d.line((x,y,x+r.randint(7,33),y+r.randint(-3,3)),fill=(131,168,166,r.randint(25,110)),width=2)
 else:
  for _ in range(30):
   x=r.randint(0,REGION_PX);y=r.randint(0,REGION_PX);rx=r.randint(100,330);ry=r.randint(75,240)
   d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(29,63,60,r.randint(130,225)))
   d.arc((x-rx+15,y-ry+15,x+rx-15,y+ry-15),10,130,fill=(135,151,104,100),width=5)
 im.alpha_composite(overlay)

def render_region(biome,idx):
 r=random.Random(SEED+idx*993)
 G=REGION;im=Image.new('RGBA',(G*T,G*T),(0,0,0,255))
 tile=Image.open(OUT/biome/'Terrain'/f'SP_{biome}_Terrain_Base_01.png')
 decals=[Image.open(OUT/biome/'TerrainDetails'/f'SP_{biome}_Decal_{kind}_{v:02d}.png') for kind in DECALS for v in (1,2)]
 for y in range(G):
  for x in range(G):
   X,Y=x*T,y*T
   im.paste(tile,(X,Y))
   if r.random()<.88:im.alpha_composite(r.choice(decals),(X,Y))
   if r.random()<.40:im.alpha_composite(r.choice(decals),(X,Y))
 # biome-specific geography before roads and POIs
 if biome=='Grassland':
  for x,y,w,h in [(8,1,2,2),(8,9,3,2),(1,8,2,2),(10,1,1,2)]:draw_field(im,r,x*T+22,y*T+26,w*T-50,h*T-50)
 elif biome=='Coastal':paint_water(im,biome,r)
 elif biome=='Swamp':paint_water(im,biome,r)
 elif biome=='Desert':
  # a minimal, smaller desert oasis, distant from most roads
  dd=ImageDraw.Draw(im,'RGBA')
  for q in range(9):
   cx=2050+r.randrange(-155,155);cy=500+r.randrange(-105,105)
   dd.ellipse((cx-45,cy-27,cx+45,cy+30),fill=(77,109,101,130))
 # consistent connected roads across map edges (N E S W) via cell occupancy, not top-down concept art.
 cells=set()
 for y in range(G):cells.add((5,y))
 for x in range(G):cells.add((x,6))
 for x in range(2,G-2):cells.add((x,2))
 for y in range(2,10):cells.add((9,y))
 for x in range(1,10):cells.add((x,10))
 for y in range(6,11):cells.add((1,y))
 typ={'Desert':'Gravel','Forest':'Dirt','Grassland':'Dirt','Swamp':'Dirt','Coastal':'Asphalt','RockyHighlands':'Gravel','AridScrubland':'Gravel','City':'Asphalt','Industrial':'Concrete'}[biome]
 for x,y in cells:
  bits=0
  if (x,y-1) in cells or y==0:bits|=1
  if (x+1,y) in cells or x==G-1:bits|=2
  if (x,y+1) in cells or y==G-1:bits|=4
  if (x-1,y) in cells or x==0:bits|=8
  road=Image.open(OUT/'Shared'/'Roads'/typ/f'SP_Road_{typ}_{bits:02d}.png')
  im.alpha_composite(road,(x*T,y*T))
 # clusters anchored to free cells: approved source props for Forest and Desert, unique local prototypes for other biomes.
 busy=set(cells)
 if biome in ZIPS:
  pool=ZIPS[biome]
  n=175 if biome=='Forest' else 75
  for _ in range(n):
   x,y=r.randrange(G),r.randrange(G)
   if (x,y) in busy or (biome=='Desert' and r.random()<.50):continue
   _,prop=r.choice(pool)
   cx=x*T+r.randrange(16,T-14);cy=y*T+r.randrange(17,T-21)
   im.alpha_composite(prop,(min(REGION_PX-prop.width,max(0,cx-prop.width//2)), min(REGION_PX-prop.height,max(0,cy-prop.height))))
 else:
  pool=[Image.open(OUT/biome/'Nature'/f'SP_{biome}_Nature_Cluster_{i:02d}.png') for i in range(1,5)]
  n={'Grassland':180,'Swamp':245,'Coastal':80,'RockyHighlands':100,'AridScrubland':115,'City':55,'Industrial':25}[biome]
  for _ in range(n):
   x,y=r.randrange(G),r.randrange(G)
   if (x,y) in busy or (biome=='Coastal' and x>=9):continue
   p=r.choice(pool)
   cx=x*T+r.randrange(12,T-12);cy=y*T+r.randrange(12,T-18)
   im.alpha_composite(p,(min(REGION_PX-p.width,max(0,cx-p.width//2)),min(REGION_PX-p.height,max(0,cy-p.height))))
 # settlements: grouped at positions away from road center, with no visual access steps.
 constructions=[(3,4),(7,3),(2,8),(8,9),(10,4),(3,11)]
 if biome=='Swamp':constructions=[(3,3),(7,3),(8,8)]
 if biome=='Coastal':constructions=[(2,3),(4,8),(7,9)]
 for k,(x,y) in enumerate(constructions):
  prop=Image.open(OUT/biome/'Structures'/f'SP_{biome}_Structure_ShelterFacade_{k%4+1:02d}.png')
  tx,ty=x*T+30,y*T+10
  im.alpha_composite(prop,(tx,ty))
  if k%2==0 and biome not in ['Swamp','Coastal']:
   im.alpha_composite(prop,(tx+115,ty+35))
 # higher-level pre-render reference: generated data and composition only
 dst=P/f'SP_{biome}_Procedural_RegionPreview_01.png'
 im.convert('RGB').save(dst,optimize=True,compress_level=6)
 # easy-to-preview JPEG rescale
 small=im.convert('RGB').resize((1536,1536),Image.Resampling.LANCZOS)
 small.save(P/f'SP_{biome}_Procedural_RegionPreview_01.jpg',quality=89,optimize=True)
 return {'biome':biome,'png':str(dst.name),'bytes':dst.stat().st_size,'width':REGION_PX,'height':REGION_PX,'road_type':typ,'connected_road_grid':REGION,'status':'composition_preview_only_not_playable','sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}

def main():
 prop_library();get_libraries();regions=[]
 for idx,b in enumerate(BIOME_NAMES):
  regions.append(render_region(b,idx))
  print('Region',b,regions[-1]['bytes']/1e6,'MB',flush=True)
 with (ROOT/'regional_previews_manifest.json').open('w') as f:json.dump({'project':'Survival Paradise','region_previews':regions},f,indent=2)
 with (ROOT/'props_manifest.json').open('w') as f:json.dump({'project':'Survival Paradise','status':'prototype_qa_pending','assets':MANIFEST},f,indent=2)
 print('New props',len(MANIFEST))
if __name__=='__main__':main()
