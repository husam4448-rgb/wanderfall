#!/usr/bin/env python3
"""Produce actual world-ready transparent sprites from the approved Batch03 art.
Only static standalone props: no entrances, stairs, gates or interactive geometry.
Run in CI after checkout of published asset sheets. Deterministic for QA.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

source = Path(sys.argv[1])
destination = Path(sys.argv[2])
destination.mkdir(parents=True,exist_ok=True)
# family => (approved original, columns, rows, chosen slots or first-row-only).
packs = {
    "nature": ("nature_terrain_props_asset_grid.webp",6,5,None),
    "urban": ("post_apocalyptic_urban_clutter_asset_sheet.webp",6,4,None),
    "ruins": ("post_apocalyptic_ruins_asset_grid.webp",4,6,None),
    "camp": ("post_apocalyptic_survival_camp_asset_atlas.webp",6,4,[(r,c) for r in (0,2,3) for c in range(6)]),
    "wreck": ("post_apocalyptic_vehicle_asset_sheet.webp",4,5,[(r,c) for r in range(4) for c in range(4)]),
    "rock": ("top_down_realistic_rock_asset_sheet.webp",4,4,[(0,c) for c in range(4)]),
    "deadwood": ("top_down_dead_tree_asset_sheet.webp",4,3,[(0,c) for c in range(4)]),
}
counts = {}
preview_items=[]
for family,(filename,cols,rows,slots) in packs.items():
    filename_path=source/filename
    assert filename_path.is_file(), "SP267_SOURCE_MISSING: "+str(filename_path)
    raw=Image.open(filename_path).convert("RGBA")
    grid = slots if slots is not None else [(r,c) for r in range(rows) for c in range(cols)]
    family_dir=destination/family
    family_dir.mkdir(parents=True,exist_ok=True)
    count=0
    for r,c in grid:
        # First-row transparent sheets have unusually tall individual objects;
        # crop to their own row without risking mixing subsequent rows.
        if family=="rock":
            box=(round(c*raw.width/4),0,round((c+1)*raw.width/4),322)
        elif family=="deadwood":
            box=[(0,0,470,455),(465,0,828,455),(820,0,1088,450),(1070,0,1254,448)][c]
        else:
            box=(round(c*raw.width/cols),round(r*raw.height/rows),
                 round((c+1)*raw.width/cols),round((r+1)*raw.height/rows))
        cell=raw.crop(box)
        arr=np.asarray(cell).copy()
        existing=arr[:,:,3]
        if int(existing.min())>=235:
            # White/very pale studio backgrounds must not appear as boxes in-game.
            rgb=arr[:,:,:3].astype(np.int16)
            h,w=rgb.shape[:2]
            corners=np.concatenate([rgb[:min(h,12),:min(w,12)].reshape(-1,3),
                rgb[:min(h,12),-min(w,12):].reshape(-1,3),
                rgb[-min(h,12):,:min(w,12)].reshape(-1,3),
                rgb[-min(h,12):,-min(w,12):].reshape(-1,3)])
            bg=np.median(corners,axis=0)
            if bg.mean()<180:
                raise AssertionError("SP267_DARK_BACKGROUND_REQUIRES_MANUAL_ALPHA: "+filename)
            difference=np.abs(rgb-bg).max(axis=2).astype(np.float32)
            # Graduated alpha avoids white fringe halos.
            matte=np.clip((difference-17.0)/44.0*255.0,0,255).astype(np.uint8)
            arr[:,:,3]=np.minimum(existing,matte)
        else:
            arr[:,:,3]=existing
        image=Image.fromarray(arr,"RGBA")
        bbox=image.getchannel("A").point(lambda a:255 if a>24 else 0).getbbox()
        assert bbox is not None, "SP267_EMPTY_SOURCE_SLOT: "+family+":"+str((r,c))
        image=image.crop(bbox)
        assert image.width>=25 and image.height>=25, "SP267_TINY_SLOT:"+family
        # Optimize Android GPU texture memory; retain fine authored detail.
        image.thumbnail((240,240),Image.Resampling.LANCZOS)
        name=f"{family}_{count:02d}.png"
        image.save(family_dir/name,optimize=True)
        if count<12:
            preview_items.append((family,name,image.copy()))
        count+=1
    counts[family]=count
assert counts=={"nature":30,"urban":24,"ruins":24,"camp":18,
               "wreck":16,"rock":4,"deadwood":4},counts
manifest={"source":"Survival Paradise Batch03 approved sprite sheets",
          "counts":counts,"total":sum(counts.values()),
          "alpha_cropped":True,"visual_status":"Requires device-side approval",
          "collision":"Cosmetic decorations, no new blocking geometry"}
(destination/"sp267_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
# Transparent-background QA contact sheet; rendered from EXTRACTED sprites,
# not an artist's mock-up.
preview=Image.new("RGBA",(1000,((len(preview_items)+6)//7)*144),(72,78,72,255))
d=ImageDraw.Draw(preview)
for i,(family,name,sprite) in enumerate(preview_items):
    x=(i%7)*142+7
    y=(i//7)*144+3
    thumb=sprite.copy()
    thumb.thumbnail((128,111),Image.Resampling.LANCZOS)
    preview.alpha_composite(thumb,(x+(128-thumb.width)//2,y))
    d.text((x,y+114),name,fill=(240,240,240,255))
preview.convert("RGB").save(destination/"SP267_EXTRACTED_PREVIEW.jpg",quality=89)
print("SP267_AUTHORED_SPRITE_EXTRACTION_PASS",json.dumps(counts),"total",sum(counts.values()))
