#!/usr/bin/env python3
"""Pack existing original world PNGs into a deterministic V166 sprite atlas.

The input sprites are authored repository assets; no character/head sources are
opened or modified. Every atlas cell has a transparent edge and a fixed anchor.
"""
from pathlib import Path
from PIL import Image
import json

GAME=Path(__file__).resolve().parents[1]
ROOT=GAME.parents[1]
OUT=GAME/"app/src/main/assets"
WORLD="assets/world/"
# Order is a runtime contract shared with WorldArtSelectionV166.
FAMILIES=[
 ("forest","Forest/Nature/Trees/",[
  "SP_Tree_Green_02.png","SP_Tree_Tall_01.png","SP_Tree_Wide_01.png"]),
 ("autumn","Forest/Nature/Trees/",[
  "SP_Tree_Autumn_01.png","SP_Tree_Weeping_01.png"]),
 ("acacia","Desert/Nature/Tree/",["SP_Desert_Tree_Acacia_02.png"]),
 ("dead","Desert/Nature/Tree/",["SP_Desert_Tree_DeadTree_01.png"]),
 ("rock","Forest/Nature/Rocks/",[
  "SP_Rock_Cluster_01.png","SP_Rock_Cluster_02.png",
  "SP_Rock_Medium_01.png","SP_Rock_MossCluster_01.png",
  "SP_Rock_JaggedCluster_01.png","SP_Rock_Small_01.png"]),
 ("wood","Forest/Nature/Wood/",[
  "SP_Log_Fallen_01.png","SP_Log_Fallen_02.png",
  "SP_Log_CutPile_01.png","SP_Stump_Chopped_01.png"]),
 ("sparse","Forest/Nature/Trees/",[
  "SP_Tree_Sparse_01.png","SP_Tree_Damaged_01.png",
  "SP_Tree_BurntSnag_01.png"]),
 ("bush","Forest/Nature/Trees/",[
  "SP_Tree_Green_02.png","SP_Tree_Autumn_01.png",
  "SP_Tree_Weeping_01.png"]),
]
CELL=128
count=sum(len(sprites) for _,_,sprites in FAMILIES)
assert count==23,count
atlas=Image.new("RGBA",(CELL*count,CELL),(0,0,0,0))
entries=[]
i=0
for family,directory,sprites in FAMILIES:
    for name in sprites:
        rel=WORLD+directory+name
        with Image.open(ROOT/rel) as im:
            original=im.convert("RGBA")
        alpha=original.getchannel("A")
        bounds=alpha.getbbox()
        if bounds is None or alpha.getextrema()[0]==255:
            raise ValueError("Sprite missing alpha or opaque background: "+rel)
        crop=original.crop(bounds)
        if family=="bush":
            # Use the authored foliage from the upper crown, not a procedural
            # polygon masquerading as a shrub. Preserve its native alpha.
            crown_height=max(1,round(crop.height*.57))
            crop=crop.crop((0,0,crop.width,crown_height))
            new_bounds=crop.getchannel("A").getbbox()
            if not new_bounds:raise ValueError("Empty shrub crown "+rel)
            crop=crop.crop(new_bounds)
        scale=min(110/crop.width,113/crop.height)
        w=max(1,round(crop.width*scale))
        h=max(1,round(crop.height*scale))
        sprite=crop.resize((w,h),Image.Resampling.LANCZOS)
        x=i*CELL+(CELL-w)//2
        y=CELL-h-8
        atlas.alpha_composite(sprite,(x,y))
        entries.append(dict(id=f"{family}_{i}",family=family,source=rel,
                            atlas_cell=i,source_bounds=bounds,
                            alpha_pixel_size=[w,h]))
        i+=1
assert i==23
OUT.mkdir(parents=True,exist_ok=True)
atlas.save(OUT/"world_props_v166.png",optimize=True)
(OUT/"world_props_v166_manifest.json").write_text(json.dumps({
 "version":166,"status":"REQUIRES_ACTUAL_EMULATOR_VISUAL_APPROVAL",
 "cell":CELL,"size":atlas.size,"entries":entries
},indent=2)+"\n")
for index in range(count):
    cell=atlas.crop((index*CELL,0,(index+1)*CELL,CELL))
    a=cell.getchannel("A")
    if a.getbbox() is None or a.getextrema()[0]!=0:
        raise AssertionError("Invalid transparent atlas cell "+str(index))
print("PASS V166: packed",count,"authored source sprites from",len(FAMILIES),"families")
