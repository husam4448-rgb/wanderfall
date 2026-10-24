#!/usr/bin/env python3
"""Survival Paradise Player A: 8 exact-silhouette equipment outfits.

Use *only* the accepted Style A 10x12 8-frame sprite source.
Gear is conveyed through internal-pixel recoloring; no added pixels,
body parts, hands, backpack protrusions, extra layers or runtime rig.
Every pixel with alpha=0 or pure black must be IDENTICAL to the original.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from collections import Counter
import json, hashlib, zipfile

HERE=Path(__file__).resolve().parents[1]
SRC=HERE/"assets/sp_player_a_preview/SP_Player_A_10x12_Walk_Sprite_Strip.png"
OUT=HERE/"assets/sp_player_a_equipment_skins"
ORIGINAL=Image.open(SRC).convert("RGBA")
assert ORIGINAL.size==(80,12)
CLEAR=(0,0,0,0); BLACK=(0,0,0,255)
HAIR=(130,129,129,255); HIGHLIGHT=(208,207,207,255)
NECK=(223,171,107,255); FACE=(254,218,175,255)
CLOTH=(92,104,80,255); PANTS=(62,70,52,255)
assert set(ORIGINAL.getdata())=={CLEAR,BLACK,HAIR,HIGHLIGHT,NECK,FACE,CLOTH,PANTS}
OUT.mkdir(parents=True,exist_ok=True)

# Pixel proportions and the original frame masks are a release contract.
# Helmet, armor plates, pocket, utility vest, scarf, respirator etc. MUST fit
# inside already opaque pixels and never alter the single black outer border.
# Each tuple is an opaque RGB color converted to RGBA in the renderer.
SKINS=[
 {"id":"leather_jacket","label":"Leather jacket","role":"rugged coat",
  "hair":"#635447","light":"#998273","neck":"#bd926d","face":"#ffdab2",
  "chest":"#684331","chest_light":"#aa6b4f","belt":"#3d2b25","pants":"#4e4c3d",
  "accent":"#b88a50","headgear":"none","gear":"crossbody strap"},
 {"id":"scavenger_vest","label":"Scavenger vest","role":"multi-pocket field vest",
  "hair":"#554938","light":"#9b8972","neck":"#c39a6c","face":"#ffdab2",
  "chest":"#756a43","chest_light":"#a29659","belt":"#48412a","pants":"#444e38",
  "accent":"#d0a85c","headgear":"none","gear":"side pouch and strap"},
 {"id":"guard_armor","label":"Guard armor","role":"steel-grey vest and helmet",
  "hair":"#4c5358","light":"#9aabb5","neck":"#cc9b72","face":"#ffdab2",
  "chest":"#414d5b","chest_light":"#9babb4","belt":"#27313a","pants":"#303b46",
  "accent":"#c8d3d7","headgear":"helmet","gear":"plated vest"},
 {"id":"medic_uniform","label":"Medic uniform","role":"medical tunic",
  "hair":"#514d4a","light":"#86827b","neck":"#d6a578","face":"#ffdab2",
  "chest":"#d9ddd8","chest_light":"#f0f2e9","belt":"#667c82","pants":"#607a84",
  "accent":"#cf4a49","headgear":"none","gear":"red medical insignia"},
 {"id":"mechanic_coverall","label":"Mechanic suit","role":"tool-pocket coveralls",
  "hair":"#544a43","light":"#958476","neck":"#ca986b","face":"#ffdab2",
  "chest":"#bb6d35","chest_light":"#e3a056","belt":"#3e3934","pants":"#515450",
  "accent":"#ccd0cc","headgear":"none","gear":"utility belt and buckle"},
 {"id":"hazmat_suit","label":"Hazmat suit","role":"sealed yellow protection",
  "hair":"#b39a31","light":"#f1d765","neck":"#d6b444","face":"#ffdab2",
  "chest":"#b99e35","chest_light":"#e4ce54","belt":"#76642a","pants":"#9a832e",
  "accent":"#385c62","headgear":"hood","gear":"face filter and sealed seam"},
 {"id":"winter_coat","label":"Winter coat","role":"blue padded cold-weather outfit",
  "hair":"#596578","light":"#a2b2c5","neck":"#b69b7e","face":"#ffdab2",
  "chest":"#4b667b","chest_light":"#8099a9","belt":"#2b4054","pants":"#344a5c",
  "accent":"#c8c0aa","headgear":"hood","gear":"fur collar and zipped coat"},
 {"id":"desert_ranger","label":"Desert ranger","role":"sand-colored desert uniform",
  "hair":"#ac976b","light":"#e2c997","neck":"#ce9e68","face":"#ffdab2",
  "chest":"#b8a175","chest_light":"#e0c38e","belt":"#645d40","pants":"#8b8062",
  "accent":"#4c6451","headgear":"helmet","gear":"bandolier and belt buckle"},
]

def rgba(h):
    h=h.lstrip("#")
    return tuple(int(h[i:i+2],16) for i in (0,2,4))+(255,)
def recolor(src,style):
    palette={
     HAIR:rgba(style["hair"]),
     HIGHLIGHT:rgba(style["light"]),
     NECK:rgba(style["neck"]),
     FACE:rgba(style["face"]),
     CLOTH:rgba(style["chest"]),
     PANTS:rgba(style["pants"]),
    }
    out=Image.new("RGBA",src.size,CLEAR)
    o=out.load(); s=src.load()
    for y in range(12):
      for x in range(80):
        p=s[x,y]
        if p==CLEAR or p==BLACK:
            o[x,y]=p
            continue
        xlocal=x%10
        q=palette[p]
        if y==7 and p==NECK and style["headgear"]=="hood" and xlocal in (3,6):
            q=rgba(style["chest_light"])  # hood/collar inside original silhouette
        if y==8 and p==CLOTH:
            # Top row of the actual 4-pixel-wide torso: reinforced panels.
            q=rgba(style["chest_light"] if xlocal in (4,5) else style["chest"])
        if y==9 and p==PANTS:
            q=rgba(style["belt"] if xlocal in (3,6) else style["chest"])
        if y>=10 and p in (PANTS,CLOTH):
            q=rgba(style["pants"])
        # Equipment cues at 1-pixel scale; masks never grow.
        if style["id"] in ("leather_jacket","desert_ranger"):
            if y==8 and xlocal==4 and p==CLOTH: q=rgba(style["accent"])
            if y==9 and xlocal==5 and p==PANTS: q=rgba(style["accent"])
        elif style["id"]=="scavenger_vest":
            if (y,xlocal) in ((8,3),(9,6)) and p in (CLOTH,PANTS):q=rgba(style["accent"])
        elif style["id"]=="guard_armor":
            if y==8 and xlocal in (4,5) and p==CLOTH:q=rgba(style["accent"])
        elif style["id"]=="medic_uniform":
            if (y,xlocal) in ((8,4),(9,4)) and p in (CLOTH,PANTS):q=rgba(style["accent"])
        elif style["id"]=="mechanic_coverall":
            if y==9 and xlocal==5 and p==PANTS:q=rgba(style["accent"])
        elif style["id"]=="hazmat_suit":
            if y==6 and xlocal in (5,6) and p==FACE:q=rgba(style["accent"])
            if y==8 and xlocal==4 and p==CLOTH:q=rgba(style["accent"])
        elif style["id"]=="winter_coat":
            if y==7 and xlocal in (4,5) and p==NECK:q=rgba(style["accent"])
            if y==8 and xlocal==5 and p==CLOTH:q=rgba(style["accent"])
        o[x,y]=q
    return out

def zoom(sprite,scale=27,bg=(237,235,231)):
    base=Image.new("RGBA",sprite.size,bg+(255,))
    base.alpha_composite(sprite)
    return base.convert("RGB").resize((sprite.width*scale,sprite.height*scale),Image.Resampling.NEAREST)
font_path=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
font=ImageFont.truetype(str(font_path),14) if font_path.exists() else ImageFont.load_default()
all_sets=[]
checks=[]
for style in SKINS:
    ident=style["id"]
    root=OUT/ident
    root.mkdir(parents=True,exist_ok=True)
    sheet=recolor(ORIGINAL,style)
    for frame in range(8):
        orig=ORIGINAL.crop((frame*10,0,(frame+1)*10,12))
        actual=sheet.crop((frame*10,0,(frame+1)*10,12))
        assert actual.getchannel("A").tobytes()==orig.getchannel("A").tobytes(),(ident,frame,"alpha")
        assert all((a==BLACK)==(b==BLACK) for a,b in zip(orig.getdata(),actual.getdata())),(ident,frame,"outline")
        assert all((a==CLEAR)==(b==CLEAR) for a,b in zip(orig.getdata(),actual.getdata())),(ident,frame,"silhouette")
        assert actual.getbbox()==orig.getbbox(),(ident,frame,"bbox")
        assert sum(1 for p in actual.getdata() if p[3])==sum(1 for p in orig.getdata() if p[3])
        actual.save(root/("walk_%02d.png"%frame),optimize=True)
    sheet.save(root/"8_frames_RGBA.png",optimize=True)
    gifs=[zoom(sheet.crop((i*10,0,(i+1)*10,12)),36) for i in range(8)]
    gifs[0].save(root/"walk.gif",save_all=True,append_images=gifs[1:],
                 duration=145,loop=0,optimize=False,disposal=2)
    with Image.open(root/"walk.gif") as gif:
        assert gif.n_frames==8 and gif.size==(360,432)
        for i,expect in enumerate(gifs):
            gif.seek(i)
            assert gif.convert("RGB").tobytes()==expect.tobytes()
    sha=hashlib.sha256((root/"8_frames_RGBA.png").read_bytes()).hexdigest()
    all_sets.append((style,sheet))
    checks.append({"id":ident,"label":style["label"],"category":style["role"],
       "headgear":style["headgear"],"visible_gear":style["gear"],
       "frames":8,"dimensions":[10,12],"colors":len(set(sheet.getdata())),
       "opaque_pixels_exact":True,"black_outline_exact":True,"alpha_exact":True,
       "sprite_sha256":sha})

# Nine panels: original player plus eight dressed equipment options.
selected=[({"id":"player_base","label":"Original player"},ORIGINAL)]+all_sets
grid=Image.new("RGB",(3*315,3*374),(237,235,231))
draw=ImageDraw.Draw(grid)
for i,(style,strip) in enumerate(selected):
    col=i%3; row=i//3
    xx=col*315;yy=row*374
    cell=zoom(strip.crop((0,0,10,12)),27)
    grid.paste(cell,(xx+22,yy+5))
    draw.text((xx+20,yy+336),style["label"],font=font,fill=(34,33,32))
grid.save(OUT/"SP_Equipment_Skins_8_Outfits_Preview.png",optimize=True)

# A single GIF displays all variants walking simultaneously with shared poses.
gif_frames=[]
for i in range(8):
    page=Image.new("RGB",(3*315,3*374),(237,235,231))
    d=ImageDraw.Draw(page)
    for ix,(style,strip) in enumerate(selected):
        col=ix%3; row=ix//3
        x0=col*315;y0=row*374
        block=zoom(strip.crop((i*10,0,(i+1)*10,12)),27)
        page.paste(block,(x0+22,y0+5))
        d.text((x0+20,y0+336),style["label"],font=font,fill=(34,33,32))
    gif_frames.append(page)
gif_frames[0].save(OUT/"SP_Equipment_Skins_8_Outfits_Walking.gif",
    save_all=True,append_images=gif_frames[1:],duration=145,loop=0,
    optimize=False,disposal=2)
with Image.open(OUT/"SP_Equipment_Skins_8_Outfits_Walking.gif") as gif:
    assert gif.n_frames==8 and gif.size==grid.size

manifest={
 "schema":"SP_PLAYER_A_EQUIPMENT_SKINS_V1",
 "source":"assets/sp_player_a_preview/SP_Player_A_10x12_Walk_Sprite_Strip.png",
 "source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
 "each_character_resolution":[10,12],
 "asset_role":"equipment-dependent palette texture swap",
 "outfits":checks,
 "same_pose_silhouette_as_player":True,
 "outline_unchanged":True,
 "no_extra_pixels":True,
 "no_added_hands":True,
 "note":"10x12 pixels permits recognizable palettes, helmets and 1-pixel uniform insignia, not detailed backpacks or complex equipment. Heavy gear would need a larger approved sprite.",
 "game_integration":"NOT_YET_INTEGRATED",
 "visual_approval":"PREVIEW_PENDING_USER_REVIEW"
}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
zipfile_path=OUT/"SP_Equipment_Skins_8_Outfits_RGBA_Pack.zip"
with zipfile.ZipFile(zipfile_path,"w",zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.rglob("*.png")):
        if p!=OUT/"SP_Equipment_Skins_8_Outfits_Preview.png":
            z.write(p,p.relative_to(OUT))
    z.write(OUT/"manifest.json","manifest.json")
print("SP_EQUIPMENT_SKINS_8_VARIANTS_MASK_AND_OUTLINE_EXACT_PASS")
print("SP_EQUIPMENT_SKINS_64_INDIVIDUAL_10x12_FRAMES_PASS")
print("SP_EQUIPMENT_SKINS_GIF_AND_PREVIEW_PASS")
