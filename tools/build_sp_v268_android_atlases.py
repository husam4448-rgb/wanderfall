#!/usr/bin/env python3
"""v268: pack v267 independently alpha-cut, approved game objects into small
family atlases for older Android OpenGL drivers. Reduce bind/upload pressure.
Run AFTER v267 extraction+verification and before Godot import/export.
"""
from pathlib import Path
from PIL import Image
import json,sys,math
root=Path(sys.argv[1])
counts={"nature":30,"urban":24,"ruins":24,"camp":18,"wreck":16,"rock":4,"deadwood":4}
columns={"nature":6,"urban":6,"ruins":6,"camp":6,"wreck":4,"rock":2,"deadwood":2}
cell=128
manifest={"version":"268","cell":cell,"count":counts,"columns":columns,
          "source":"Approved v267 transparent single objects","atlases":{},
          "runtime_max_additional_props_per_chunk":6,
          "legacy_large_ground_tile_layer":False}
for family,count in counts.items():
    files=[root/family/(f"{family}_{i:02d}.png") for i in range(count)]
    assert all(f.exists() for f in files),(family,"missing approved cropped images")
    cols=columns[family];rows=math.ceil(count/cols)
    atlas=Image.new("RGBA",(cols*cell,rows*cell),(0,0,0,0))
    for i,p in enumerate(files):
        im=Image.open(p).convert("RGBA")
        im.thumbnail((cell-6,cell-6),Image.Resampling.LANCZOS)
        x=(i%cols)*cell+(cell-im.width)//2
        y=(i//cols)*cell+(cell-im.height)//2
        atlas.alpha_composite(im,(x,y))
    assert atlas.width<=1024 and atlas.height<=1024
    output=root/(family+"_atlas.png")
    atlas.save(output,optimize=True)
    manifest["atlases"][family]={"width":atlas.width,"height":atlas.height,"file":output.name}
    # Individual source sprites remain available in GitHub; not duplicated
    # into the Android PCK. Every live draw samples from just 7 GPU textures.
    for p in files:p.unlink()
    (root/family).rmdir()
(root/"sp268_atlases.json").write_text(json.dumps(manifest,indent=2)+"\n")
assert len(list(root.glob("*_atlas.png")))==7
assert not list(root.rglob("*_[0-9][0-9].png"))
print("SP268_GPU_ATLAS_PACK_PASS 120 authored sprites -> 7 compact textures; 128px cells, max 1024px atlas")
