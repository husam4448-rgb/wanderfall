#!/usr/bin/env python3
"""SP v262: preserve D2D.14 world/HUD/combat, tint each actor exactly once.

Order: apply v257, v258, v259, v260, v261 then this script.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import math, shutil, sys
root=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
protected=(
    "scripts/mobile_hud.gd","scripts/virtual_joystick.gd",
    "scripts/world/world_chunk.gd","scripts/world/world_manager.gd",
    "scripts/combat/zombie.gd","scripts/combat/bandit.gd",
    "scripts/ecology/wildlife_actor.gd","scripts/art/layered_actor_visual.gd")
base={p:(root/p).read_bytes() for p in protected}
overlay=repo/"occlusion/v261_overlay.gd"
output=root/"scripts/world/occlusion_silhouette_overlay.gd"
assert overlay.exists()
shutil.copy2(overlay,output)
art=root/"assets/sp_melee"
art.mkdir(parents=True,exist_ok=True)

# WildlifeActor._draw source anatomy, pixels drawn into ONE solid alpha mask.
# Body+head+ears/limbs/tails/beaks are merged once, with no UI bars or shadow.
W,H=64,72
OX,OY=W//2,H//2
white=(255,255,255,255)
def init():
    im=Image.new("RGBA",(W,H),(0,0,0,0))
    return im,ImageDraw.Draw(im)
def at(x,y):
    return (float(x+OX),float(y+OY))
def poly(d,points):
    d.polygon([at(x,y) for x,y in points],fill=white)
def oval(d,cx,cy,rx,ry):
    pts=[(cx+math.cos(math.tau*i/18)*rx,cy+math.sin(math.tau*i/18)*ry)
         for i in range(18)]
    poly(d,pts)
def circle(d,x,y,r):
    d.ellipse((x+OX-r,y+OY-r,x+OX+r,y+OY+r),fill=white)
def line(d,x1,y1,x2,y2,w):
    d.line((at(x1,y1),at(x2,y2)),fill=white,width=w)
def save(name,im):
    target=art/f"v262_animal_{name}.png"
    im.save(target)
    assert im.getpixel((0,0))[3]==0
    assert im.getpixel((OX,OY))[3]==255
    print(f"SP_V262_SPECIES_MASK {name}: {target.name} alpha pixels={sum(a>0 for a in im.getchannel('A').getdata())}")

im,d=init()
oval(d,0,0,15,9)
circle(d,15,-5,6)
line(d,17,-10,21,-17,2)
line(d,14,-10,10,-17,2)
for x in [-8,7]:
    line(d,x,6,x,16,3)
save("deer",im)

im,d=init()
oval(d,0,0,16,10)
circle(d,15,1,6)
line(d,19,3,24,1,2)
save("boar",im)

im,d=init()
circle(d,0,0,9)
circle(d,8,-7,5)
poly(d,[(13,-7),(20,-4),(13,-2)])
save("chicken",im)

im,d=init()
oval(d,0,0,9,5)
circle(d,8,-1,3.5)
line(d,-8,1,-18,6,2)
save("rat",im)

im,d=init()
oval(d,0,0,18,8)
line(d,-10,0,12,5,3)
save("dead",im)

text=output.read_text(encoding="utf-8")
assert "OneFlatOpacityAlphaComposite" in text
assert 'for group_name in ["player_actor","hostile_actor","friendly_npc","wildlife_actor","huntable_actor"]' in text
assert "func _wildlife_state" in text
assert 'state["material"]' in text
assert "func _inside_actor_silhouette" not in text
assert "func _draw_sprite_mask" not in text
for p,b in base.items():
    if (root/p).read_bytes()!=b:
        raise SystemExit("SP_V262_PROTECTED_WORLD_HUD_ACTOR_CHANGED: "+p)
print("SP_V262_SOURCE_QA_PASS same historical world/HUD; player composite tint once; zombies, bandits, NPCs and four wildlife species + carcasses use one final shader")
