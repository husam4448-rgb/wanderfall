#!/usr/bin/env python3
"""Publish the exact 8 poses from the user's approved 10x12 Style A sprite strip.
The 80x12 source image below comes from the user-approved prototype A: grey short hair, no arms, body-width feet.
No AI image approximation and no extra hands/feet.
"""
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image

SOURCE_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAFAAAAAMCAYAAAD1XTohAAAA/ElEQVR4nO2WvwrCMBCHfxHfQ1y7uDg7iWPp4lb3gs9gpX2HgoOjm4t0FFychfoAoiC6+BJxsU0uTf8gut23XfNdLzlKegIUacQCdtj70NGlOIpwzjKcswxxFNkS2TM8oUs6rusiTVOEyyV7NV5XX5w5LxVc1pg5QIgy7CmPNLA3GFvSk9IT9pRX3IGkyzWwRykaaO9yGfYo+m9b3rZzstifJqbDnuGRO3BxeKIN7ClIA+/XR6sXsqcoPtfRZCgB4Lg/5TE+sW06zwdJ4QeeBIDNave1p9Wu9Mz9+YGHBk/o9etqtvUazgoJOombcRW/8PS1Kq/t/v6571LOG493V/oya7HHAAAAAElFTkSuQmCC"
strip = Image.open(BytesIO(base64.b64decode(SOURCE_PNG_B64))).convert("RGBA")
assert strip.size == (80, 12)
out = Path("assets/sp_player_a_preview")
out.mkdir(parents=True, exist_ok=True)
strip.save(out / "SP_Player_A_10x12_Walk_Sprite_Strip.png")

def paint(frame, scale):
    resized = frame.resize((10*scale,12*scale), Image.Resampling.NEAREST)
    back = Image.new("RGB", resized.size, (244,244,242))
    back.paste(resized, mask=resized.getchannel("A"))
    return back

cells = [strip.crop((10*i,0,10*(i+1),12)) for i in range(8)]
sheet_frames = [paint(im,30) for im in cells]
sheet = Image.new("RGB",(2400,360),(244,244,242))
for i,im in enumerate(sheet_frames):
    sheet.paste(im,(i*300,0))
sheet.save(out / "SP_Player_A_10x12_Walk_8_Frames.png", optimize=True)

gif_frames = [paint(im,38) for im in cells]
gif_frames[0].save(out / "SP_Player_A_10x12_Walk_Animated.gif",
                   save_all=True,append_images=gif_frames[1:],
                   duration=130,loop=0,optimize=False,disposal=2)
with Image.open(out/"SP_Player_A_10x12_Walk_Animated.gif") as gif:
    assert gif.n_frames == 8 and gif.size == (380,456)
    for n,ref in enumerate(gif_frames):
        gif.seek(n)
        assert gif.convert("RGB").tobytes() == ref.tobytes()
assert cells[0].getpixel((3,0)) == (0,0,0,255) # A's flat black upper outline
assert cells[0].getpixel((3,3))[:3] == (223,171,107) # A's peach forehead shading
for f in cells:
    assert f.getbbox()[0] >= 1 and f.getbbox()[2] <= 9 # no forward-protruding feet
print("SP_PLAYER_A_BROWSER_GIF_8_FRAMES_VERIFIED")
print("SP_PLAYER_A_BROWSER_PNG_2400x360_VERIFIED")
