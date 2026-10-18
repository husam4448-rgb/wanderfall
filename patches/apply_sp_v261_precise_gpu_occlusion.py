#!/usr/bin/env python3
"""SP v261 overlay integration, after v260. Preserve exact D2D.14 world/HUD."""
from pathlib import Path
from PIL import Image, ImageDraw
import shutil, sys
game=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
protected=("scripts/mobile_hud.gd","scripts/virtual_joystick.gd",
           "scripts/world/world_chunk.gd","scripts/world/world_manager.gd",
           "scripts/combat/zombie.gd","scripts/art/layered_actor_visual.gd")
original={p:(game/p).read_bytes() for p in protected}
shutil.copy2(repo/"occlusion/v261_overlay.gd",
             game/"scripts/world/occlusion_silhouette_overlay.gd")
dst=game/"occlusion"
dst.mkdir(exist_ok=True)
for file in ["v261_mask.gdshader","v261_leg_mask.gd"]:
    shutil.copy2(repo/"occlusion"/file,dst/file)
# Generate exactly the same primitive silhouettes as Zombie._draw (excluding
# ground shadow and health bar). Opaque pixels alone become canopy tint.
width,height=64,72
offset_x,offset_y=32,36
im=Image.new("RGBA",(width,height),(0,0,0,0))
d=ImageDraw.Draw(im)
def rect(x0,y0,x1,y1):
    d.rectangle((x0+offset_x,y0+offset_y,x1+offset_x,y1+offset_y),fill=(255,255,255,255))
def circle(cx,cy,r):
    d.ellipse((cx-r+offset_x,cy-r+offset_y,cx+r+offset_x,cy+r+offset_y),fill=(255,255,255,255))
def line(ax,ay,bx,by,w):
    d.line((ax+offset_x,ay+offset_y,bx+offset_x,by+offset_y),fill=(255,255,255,255),width=w)
# Rect2(-9,-4,18,22) -> box ends x=9, y=18
rect(-9,-4,8,17)
circle(0,-12,8.5)
rect(-9,-20,8,-16)
line(-7,0,-13,10,4)
line(7,0,13,10,4)
line(-5,15,-7,25,5)
line(5,15,7,25,5)
out=game/"assets/sp_melee/v261_zombie_mask.png"
im.save(out)
assert im.getpixel((offset_x,offset_y-12))[3]==255
assert im.getpixel((0,0))[3]==0
# Old + new game logic remains unchanged, with only overlay renderer replaced.
for p,bytes_saved in original.items():
    if (game/p).read_bytes()!=bytes_saved:
        raise SystemExit("SP_V261_PROTECTED_SOURCE_MUTATED "+p)
script=(game/"scripts/world/occlusion_silhouette_overlay.gd").read_text()
assert "func _inside_actor_silhouette" not in script
assert "func _draw_sprite_mask" not in script
assert "canopy_centers" in (dst/"v261_mask.gdshader").read_text()
print("SP_V261_SOURCE_INTEGRATION_PASS world/HUD/actor behavior byte-identical, GPU ellipse clipping, no rectangular NPC fallback")
