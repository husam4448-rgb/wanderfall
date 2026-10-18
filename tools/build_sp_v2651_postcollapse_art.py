#!/usr/bin/env python3
"""SP v265.1: actual v265 tree-alpha atlas + weathered post-collapse prop sprites.

Sprite bases are the project's existing authored site/prop PNGs, not primitive
polygon approximations. This baker changes pixel wear and clusters by biome.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import random,sys,math
game=Path(sys.argv[1])
out=game/"assets/biomes/v2651"
out.mkdir(parents=True,exist_ok=True)
source=game/"assets/biomes/v265"
assert source.is_dir(), "v265 original raster art absent"
alpha=Image.new("RGBA",(336,336))
for row,biome in enumerate(("forest","grassland","desert")):
    for col in range(3):
        im=Image.open(source/f"{biome}_foliage_{col}.png").convert("RGBA")
        assert im.size==(112,112), f"Unexpected {biome} canopy dimensions {im.size}"
        alpha.paste(im,(col*112,row*112))
alpha.save(out/"canopy_alpha_atlas.png",optimize=True)
site=Image.open(game/"assets/production/props/site_props_atlas.png").convert("RGBA")
props=Image.open(game/"assets/production/props/props_atlas.png").convert("RGBA")
regions=[
 ("barrel",site,(0,0,48,80)),
 ("tire",site,(48,0,112,80)),
 ("pallet",site,(112,0,184,80)),
 ("fence",site,(184,0,280,80)),
 ("sign",site,(280,0,320,88)),
 ("rubble",site,(320,0,384,80)),
 ("debris",props,(352,0,400,36)),
 ("trash",props,(432,0,480,36)),
 ("broken_log",props,(160,128,240,176)),
]
assert site.size[0]>=384 and site.size[1]>=88 and props.size[0]>=480, "source authored atlas mismatch"
# Surface grime palette is biome-specific; the source silhouette remains
# authoritative and its alpha is preserved, not replaced by simple primitives.
weather=[
 ((52,78,35),(102,107,56)), # temperate forest: moss + humus
 ((33,75,42),(81,90,58)),   # dense forest: fungus and rot
 ((131,117,56),(172,138,70)), # grassland: sun damage / straw
 ((50,83,66),(99,94,74)), # wetlands: algae / wet silt
 ((179,126,75),(202,171,112)), # desert: rust / sand
 ((110,105,94),(164,145,115)), # rocky highlands: stone dust
 ((174,190,191),(217,222,222)), # tundra: frost
 ((72,111,102),(138,140,107)), # lakes: algae and silt
 ((95,88,78),(137,116,101)), # urban: dirt and soot
]
for biome,(grime,dust) in enumerate(weather):
    for kind,(name,atlas,rect) in enumerate(regions):
        rng=random.Random(0x265100+biome*701+kind*127)
        cut=atlas.crop(rect)
        canvas=Image.new("RGBA",(112,112),(0,0,0,0))
        if cut.width>95 or cut.height>92:
            cut.thumbnail((94,84),Image.Resampling.NEAREST)
        # Distinct broken compositions: asymmetric wear, partial burial and
        # signature secondary debris made from the actual authored prop atlas.
        x=(112-cut.width)//2+rng.randint(-9,9)
        y=83-cut.height+rng.randint(-5,7)
        layer=cut.copy()
        px=layer.load()
        for py in range(layer.height):
            for xx in range(layer.width):
                r,g,b,a=px[xx,py]
                if a<24:continue
                s=rng.random()
                if s<0.11:   # paint/surface distress, not alpha erosion
                    mix=rng.uniform(.17,.52)
                    col=grime if rng.random()<.65 else dust
                    r=int(r*(1-mix)+col[0]*mix)
                    g=int(g*(1-mix)+col[1]*mix)
                    b=int(b*(1-mix)+col[2]*mix)
                if s>.996: a=int(a*.48) # chipped silhouette bits
                px[xx,py]=(r,g,b,a)
        canvas.alpha_composite(layer,(x,y))
        # Small companion relics give scraps a composition rather than repeated
        # isolated objects; these are sourced from the existing game's sprite art.
        if kind in (0,2,3,4,5,8):
            base=props.crop((352,0,400,36)).convert("RGBA")
            base.thumbnail((rng.randint(23,35),19),Image.Resampling.NEAREST)
            canvas.alpha_composite(base,(max(0,min(112-base.width,x+rng.randint(4,29))),
                                         min(112-base.height,rng.randint(79,91))))
        canvas.save(out/f"biome_{biome}_prop_{kind}.png",optimize=True)
expected=1+len(weather)*len(regions)
assert len(list(out.glob("*.png")))==expected
print("SP_V2651_PIXEL_ART_BAKE_PASS",expected,"transparent PNGs; true v265 canopy alpha atlas; 9x9 weathered authored-source clutter variants")
