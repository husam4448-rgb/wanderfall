#!/usr/bin/env python3
"""Survival Paradise Bandit 01 — PURE PALETTE SWAP of APPROVED Player A.

Uses the already approved 8-frame 10x12 Player A sprite strip (including
the verified rear heel / black-outline correction) as the only source.
No reshaping, no additional hands/arms, no new bones, no moving layers.
Only six nonblack palette entries change; all alpha, outline and pixels
outside the color palette remain byte-identical at every frame.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from collections import Counter
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
APPROVED=ROOT/"assets/sp_player_a_preview/SP_Player_A_10x12_Walk_Sprite_Strip.png"
OUT=ROOT/"assets/sp_npc_simple/SP_NPC_Bandit_Male_01_10x12"
OUT.mkdir(parents=True,exist_ok=True)
BASE=Image.open(APPROVED).convert("RGBA")
assert BASE.size==(80,12),BASE.size
BLACK=(0,0,0,255)
CLEAR=(0,0,0,0)

# Player -> Bandit: charcoal brown hair, warm weathered skin,
# muted red clothing, dark burgundy trousers. NO change to black outline.
PALETTE={
 (130,129,129,255):(73,48,43,255),   # dark hair
 (208,207,207,255):(131,91,75,255),  # hair highlight
 (223,171,107,255):(163,100,73,255), # warm shaded skin / shirt band
 (254,218,175,255):(211,166,125,255),# tan face
 (92,104,80,255):(111,57,53,255),    # red-brown clothing
 (62,70,52,255):(69,38,38,255),      # dark burgundy trousers
}
source_set=set(BASE.getdata())
assert source_set==set(PALETTE)|{BLACK,CLEAR},source_set
BANDIT=Image.new("RGBA",BASE.size,CLEAR)
BANDIT.putdata([PALETTE.get(pixel,pixel) for pixel in BASE.getdata()])

for i in range(8):
    x0=10*i
    player=BASE.crop((x0,0,x0+10,12))
    bandit=BANDIT.crop((x0,0,x0+10,12))
    assert player.getchannel("A").tobytes()==bandit.getchannel("A").tobytes(),i
    assert player.getbbox()==bandit.getbbox(),i
    assert all((p==BLACK)==(b==BLACK) for p,b in zip(player.getdata(),bandit.getdata())),i
    assert all((p==CLEAR)==(b==CLEAR) for p,b in zip(player.getdata(),bandit.getdata())),i
    assert sum(p!=b for p,b in zip(player.getdata(),bandit.getdata()))>25,i
    bandit.save(OUT/("walk_%02d.png"%i),optimize=True)

# Preserve pixel-exact source strip for animation and pixel-art game import.
BANDIT.save(OUT/"SP_Bandit_01_10x12_8Frames_Transparent_Strip.png",optimize=True)
def zoom(sprite:Image.Image,scale=36):
    background=Image.new("RGBA",sprite.size,(238,236,231,255))
    background.alpha_composite(sprite)
    return background.convert("RGB").resize((sprite.width*scale,sprite.height*scale),Image.Resampling.NEAREST)

frames=[zoom(BANDIT.crop((i*10,0,(i+1)*10,12))) for i in range(8)]
gif_path=OUT/"SP_Bandit_01_10x12_Walking.gif"
frames[0].save(gif_path,save_all=True,append_images=frames[1:],
               duration=145,loop=0,optimize=False,disposal=2)
with Image.open(gif_path) as gif:
    assert gif.n_frames==8 and gif.size==(360,432)
    for i,expected in enumerate(frames):
        gif.seek(i)
        assert gif.convert("RGB").tobytes()==expected.tobytes(),i

sheet=Image.new("RGB",(2880,432),(238,236,231))
for i,img in enumerate(frames):
    sheet.paste(img,(360*i,0))
sheet.save(OUT/"SP_Bandit_01_8Frame_Sheet.png",optimize=True)

comparison=Image.new("RGB",(780,484),(238,236,231))
comparison.paste(zoom(BASE.crop((0,0,10,12))),(0,0))
comparison.paste(frames[0],(420,0))
d=ImageDraw.Draw(comparison)
d.text((8,450),"PLAYER A",fill=(25,25,25))
d.text((430,450),"BANDIT 01",fill=(25,25,25))
comparison.save(OUT/"SP_PlayerA_vs_Bandit01_Comparison.png",optimize=True)

manifest={
 "character_id":"SP_NPC_Bandit_Male_01",
 "variant_of":"SP_Player_A",
 "sprite_resolution":[10,12],
 "walk_frame_count":8,
 "same_silhouette_and_outline":True,
 "identical_alpha_every_frame":True,
 "idle_pose":"walk_00.png (same shape as approved Player A)",
 "legs_and_feet":"exact pixel masks of approved player, including rear heel correction",
 "arms_hands":"none",
 "changes":"six interior color entries only",
 "palette_rgba":[{"player":list(a),"bandit":list(b)} for a,b in PALETTE.items()],
 "source_sha256":hashlib.sha256(APPROVED.read_bytes()).hexdigest(),
 "sprite_strip_sha256":hashlib.sha256((OUT/"SP_Bandit_01_10x12_8Frames_Transparent_Strip.png").read_bytes()).hexdigest(),
 "animation_validation":"PASS eight frames equal mask, geometry and outline",
 "game_integration":"NOT_YET_INTEGRATED"
}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("SP_BANDIT01_PALETTE_ONLY_PASS")
print("SP_BANDIT01_ALL_8_MASKS_AND_BLACK_OUTLINE_IDENTICAL_PASS")
print("SP_BANDIT01_BROWSER_GIF_AND_PNG_PASS")
