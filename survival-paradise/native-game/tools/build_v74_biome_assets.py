#!/usr/bin/env python3
"""Make one pixel-sharp transparent atlas from existing original world PNGs."""
from pathlib import Path
import json
from PIL import Image

GAME=Path(__file__).resolve().parents[1]
ROOT=GAME.parents[1]
OUT=GAME/"app/src/main/assets"
SOURCES=[
("forest_green","assets/world/Forest/Nature/Trees/SP_Tree_Green_02.png"),
("forest_autumn","assets/world/Forest/Nature/Trees/SP_Tree_Autumn_01.png"),
("desert_acacia","assets/world/Desert/Nature/Tree/SP_Desert_Tree_Acacia_02.png"),
("desert_dead","assets/world/Desert/Nature/Tree/SP_Desert_Tree_DeadTree_01.png"),
("rock","assets/world/Forest/Nature/Rocks/SP_Rock_Cluster_01.png"),
("log","assets/world/Forest/Nature/Wood/SP_Log_Fallen_01.png"),
("sparse_tree","assets/world/Forest/Nature/Trees/SP_Tree_Sparse_01.png")]
S=128
atlas=Image.new("RGBA",(S*len(SOURCES),S),(0,0,0,0))
entries=[]
for i,(name,relative) in enumerate(SOURCES):
    with Image.open(ROOT/relative) as im:
        orig=im.convert("RGBA")
    bbox=orig.getchannel("A").getbbox()
    if bbox is None or orig.getchannel("A").getextrema()[0]==255:
        raise ValueError("Not a transparent sprite: "+relative)
    crop=orig.crop(bbox)
    factor=min(108/crop.width,112/crop.height)
    w=max(1,round(crop.width*factor))
    h=max(1,round(crop.height*factor))
    img=crop.resize((w,h),Image.Resampling.NEAREST)
    x=i*S+(S-w)//2;y=S-h-8
    atlas.alpha_composite(img,(x,y))
    entries.append({"index":i,"id":name,"source":relative,
                    "dimensions":[orig.width,orig.height],"alpha_bounds":list(bbox),
                    "packed_rect":[x,y,w,h]})
OUT.mkdir(parents=True,exist_ok=True)
atlas.save(OUT/"world_props_v74.png",optimize=True)
(OUT/"world_props_v74_manifest.json").write_text(json.dumps({
    "version":"V74","visual_status":"EXPERIMENTAL_PENDING_REVIEW",
    "atlas_cell":S,"entries":entries},indent=2)+"\n")
assert atlas.size==(896,128)
print("V74 atlas: 7 existing transparent source sprites")
