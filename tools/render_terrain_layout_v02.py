#!/usr/bin/env python3
"""Deterministic, NON-PLAYABLE biome composition QA (v02).

Uses original verified 281-PNG source archive. This changes preview composition,
not approved art or gameplay. Forest/Desert source previews remain unchanged.
"""
import argparse, hashlib, io, json, random, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

BIOMES = ('Forest','Desert','Grassland','Swamp','Coastal','RockyHighlands','AridScrubland','City','Industrial')
SURFACES = dict(Forest='Dirt',Desert='Gravel',Grassland='Dirt',Swamp='Dirt',Coastal='Asphalt',RockyHighlands='Gravel',AridScrubland='Gravel',City='Asphalt',Industrial='Concrete')
T=256; G=12; SZ=T*G; SEED=20261020

def segments(nodes):
    result=[]
    for (x1,y1),(x2,y2) in zip(nodes,nodes[1:]):
        assert 0 <= x1 < G and 0 <= x2 < G and 0 <= y1 < G and 0 <= y2 < G
        assert x1 == x2 or y1 == y2, (x1,y1,x2,y2)
        dx=(x2>x1)-(x2<x1);dy=(y2>y1)-(y2<y1)
        while (x1,y1)!=(x2,y2):
            result.append((x1,y1)); x1+=dx;y1+=dy
    result.append(nodes[-1]);return result

def network(biome):
    # Non-grid spine with staggered bends, four exits, optional disconnected-free spurs.
    vertical=[(5,0),(5,3),(6,3),(6,8),(7,8),(7,11)]
    horizontal=[(0,6),(2,6),(2,7),(6,7),(6,8),(10,8),(10,9),(11,9)]
    if biome=='Coastal':
        horizontal=[(0,6),(2,6),(2,7),(6,7),(6,8),(8,8)]
        vertical=[(5,0),(5,3),(6,3),(6,8),(7,8),(7,11)]
    spine=set(segments(vertical)+segments(horizontal))
    if biome in ('City','Industrial'): # Short connected service lanes, not a city-spanning grid.
        spine.update(segments([(6,5),(8,5)]));spine.update(segments([(10,9),(10,11)]))
    if biome=='Grassland':spine.update(segments([(7,8),(9,8)]))
    if biome=='RockyHighlands':spine.update(segments([(2,7),(2,9)]))
    if biome=='Swamp':spine.update(segments([(2,7),(2,9)]))
    assert all(0 <= x < G and 0 <= y < G for x,y in spine)
    assert not any({(x,y),(x+1,y),(x,y+1),(x+1,y+1)} <= spine for x in range(G-1) for y in range(G-1)), 'Unsafe 2x2 road square'
    return spine

def get(z,n):return Image.open(io.BytesIO(z.read(n))).convert('RGBA')

def draw_topography(image,biome,rng):
    scale=8;small=SZ//scale
    layer=Image.new('RGBA',(small,small));d=ImageDraw.Draw(layer,'RGBA')
    palette={
        'Grassland':((93,115,68,22),(43,65,40,15)),
        'Swamp':((18,65,54,27),(85,96,63,22)),
        'Coastal':((174,149,101,31),(101,126,100,18)),
        'RockyHighlands':((30,33,31,19),(129,122,96,23)),
        'AridScrubland':((166,139,89,19),(67,82,57,22)),
        'City':((24,27,28,19),(102,90,73,18)),
        'Industrial':((26,31,31,25),(101,81,65,22)),
    }[biome]
    for _ in range(24):
        x=rng.randrange(-250,SZ);y=rng.randrange(-250,SZ)
        rad=rng.randrange(140,500)
        d.ellipse(((x-rad)//scale,(y-rad//2)//scale,(x+rad)//scale,(y+rad//2)//scale),fill=rng.choice(palette))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(10)).resize((SZ,SZ),Image.Resampling.BILINEAR))

def water(image,biome,rng):
    if biome not in ('Swamp','Coastal'):return
    layer=Image.new('RGBA',(SZ,SZ));d=ImageDraw.Draw(layer,'RGBA')
    if biome=='Coastal':
        # Shoreline entirely on far-east coast, distant from the western road spine.
        line=[(2300,0),(2330,250),(2290,480),(2380,730),(2280,980),(2330,1250),(2260,1500),(2320,1780),(2340,2020),(2270,2240),(2240,2490),(2310,2820),(2280,SZ)]
        d.polygon(line+[(SZ,SZ),(SZ,0)],fill=(33,82,91,237))
        d.line(line,fill=(175,169,133,124),width=22,joint='curve')
        for _ in range(280):
            x=rng.randrange(2440,SZ);y=rng.randrange(SZ)
            d.line([(x,y),(x+rng.randrange(5,30),y+rng.randrange(-3,4))],fill=(170,186,173,rng.randrange(25,90)),width=2)
    else:
        for cx,cy,rx,ry in [(500,380,270,170),(2550,300,180,320),(2450,1780,250,330),(520,2450,270,220)]:
            poly=[(cx+int(rx*__import__('math').cos(i*__import__('math').tau/14)*rng.uniform(.83,1.16)),cy+int(ry*__import__('math').sin(i*__import__('math').tau/14)*rng.uniform(.83,1.16))) for i in range(14)]
            d.polygon(poly,fill=(32,69,61,187));d.line(poly+[poly[0]],fill=(86,107,78,75),width=12,joint='curve')
    image.alpha_composite(layer)

def render(z,biome):
    rng=random.Random(SEED+BIOMES.index(biome)*11717)
    image=Image.new('RGBA',(SZ,SZ))
    tile=get(z,f'GameAssets/{biome}/Terrain/SP_{biome}_Terrain_Base_01.png')
    decals=[get(z,f'GameAssets/{biome}/TerrainDetails/SP_{biome}_Decal_{kind}_{v:02}.png') for kind in ('PebbleScatter','WeatheredPatch','VegetationTufts','ScuffedSoil','DebrisScatter','CrackNetwork','DarkStain','DenseTexture') for v in (1,2)]
    for y in range(G):
        for x in range(G):
            # Variation without scaling, keeping original repeated seamless source texture.
            variant=rng.randrange(4)
            img=tile.transpose((Image.Transpose.ROTATE_90,Image.Transpose.ROTATE_180,Image.Transpose.ROTATE_270,Image.Transpose.FLIP_LEFT_RIGHT)[variant]) if variant else tile
            image.paste(img,(x*T,y*T))
            if rng.random()<.8:image.alpha_composite(rng.choice(decals),(x*T,y*T))
            if rng.random()<.45:image.alpha_composite(rng.choice(decals),(x*T,y*T))
    draw_topography(image,biome,rng)
    water(image,biome,rng)
    spine=network(biome)
    typ=SURFACES[biome]
    roads={i:get(z,f'GameAssets/Shared/Roads/{typ}/SP_Road_{typ}_{i:02}.png') for i in range(16)}
    mask_counts={}
    for x,y in sorted(spine):
        mask=(1 if (x,y-1) in spine or y==0 else 0)|(2 if (x+1,y) in spine or x==G-1 else 0)|(4 if (x,y+1) in spine or y==G-1 else 0)|(8 if (x-1,y) in spine or x==0 else 0)
        assert mask != 0
        image.alpha_composite(roads[mask],(x*T,y*T))
        mask_counts[mask]=mask_counts.get(mask,0)+1
    # Settlement groups along roads; no 6 identical huts around square subdivisions.
    houses=[get(z,f'GameAssets/{biome}/Structures/SP_{biome}_Structure_ShelterFacade_{i:02}.png') for i in range(1,5)]
    zones=[(2,4),(8,3),(3,9),(9,10),(9,5)]
    if biome=='Coastal':zones=[(2,4),(8,3),(3,10)]
    if biome=='Swamp':zones=[(2,4),(8,3),(9,10)]
    clearings=set()
    for i,(x,y) in enumerate(zones):
        if (x,y) in spine:continue
        clearings.add((x,y))
        patch=Image.new('RGBA',(SZ,SZ));dd=ImageDraw.Draw(patch,'RGBA');cx=x*T+T//2;cy=y*T+T//2
        dd.ellipse((cx-110,cy-80,cx+110,cy+85),fill=(142,121,89,26))
        image.alpha_composite(patch.filter(ImageFilter.GaussianBlur(20)))
        prop=houses[(i+BIOMES.index(biome))%4];image.alpha_composite(prop,(x*T+35,y*T+40))
        if i==0: image.alpha_composite(houses[(i+1)%4],(x*T+118,y*T+96))
    # Vegetation or debris clumps; nonuniform density and preserved clear road corridors.
    props=[get(z,f'GameAssets/{biome}/Nature/SP_{biome}_Nature_Cluster_{i:02}.png') for i in range(1,5)]
    qty={'Grassland':215,'Swamp':230,'Coastal':120,'RockyHighlands':180,'AridScrubland':185,'City':95,'Industrial':125}[biome]
    count=0
    for _ in range(qty*5):
        if count>=qty:break
        x,y=rng.randrange(G),rng.randrange(G)
        if (x,y) in spine or (x,y) in clearings:continue
        if biome=='Coastal' and x>=9:continue
        if rng.random()<.5 and 3<=x<=8 and 3<=y<=8:continue
        prop=rng.choice(props)
        ox=x*T+rng.randrange(22,150);oy=y*T+rng.randrange(18,135)
        image.alpha_composite(prop,(ox,oy));count+=1
    assert len(spine)<60
    return image.convert('RGB'), {'biome':biome,'roads':len(spine),'road_masks':mask_counts,'structures':len(clearings),'props':count,'sha256':'','status':'composition_QA_only_not_playable_or_approved'}

def main():
    arg=argparse.ArgumentParser();arg.add_argument('terrain_zip',type=Path);arg.add_argument('original_previews_zip',type=Path);arg.add_argument('output',type=Path);cfg=arg.parse_args()
    cfg.output.mkdir(parents=True,exist_ok=True)
    result=[]
    with zipfile.ZipFile(cfg.terrain_zip) as z, zipfile.ZipFile(cfg.original_previews_zip) as old:
        for biome in BIOMES:
            out=cfg.output/f'SP_{biome}_RegionPreview_v02.png'
            if out.exists() and biome not in ('Forest','Desert'):out.unlink()
            if biome in ('Forest','Desert'):
                b=old.read(f'Previews/SP_{biome}_Procedural_RegionPreview_01.png')
                out.write_bytes(b)
                summary={'biome':biome,'status':'unchanged_v01_preview_preserves_approved_reference_sources','roads':None,'structures':None,'props':None}
            else:
                img,summary=render(z,biome);img.save(out,compress_level=2)
            summary['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();summary['size']=out.stat().st_size;result.append(summary)
            print(biome,summary['status'],summary.get('roads'),round(out.stat().st_size/1e6,2),flush=True)
    (cfg.output/'qa.json').write_text(json.dumps({'project':'Survival Paradise','version':'02','regions':result},indent=2))
    # Side-by-side tiles for full nine-biome production QA.
    contact=Image.new('RGB',(3*475,3*520),(24,27,28));dd=ImageDraw.Draw(contact)
    for i,biome in enumerate(BIOMES):
        im=Image.open(cfg.output/f'SP_{biome}_RegionPreview_v02.png');im.thumbnail((460,465),Image.Resampling.LANCZOS)
        x=(i%3)*475+7;y=(i//3)*520+6
        contact.paste(im,(x,y));dd.text((x,y+472),biome+(' (preserved)' if biome in ('Forest','Desert') else ' (v02 layout)'),fill='white')
    contact.save(cfg.output/'SP_9Biome_v02_QA.jpg',quality=88)

if __name__=='__main__':main()