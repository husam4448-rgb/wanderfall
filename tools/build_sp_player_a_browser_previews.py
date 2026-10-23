#!/usr/bin/env python3
"""Publish the exact 8 poses from the user's approved 10x12 Style A sprite strip.
The 80x12 source image below came from the original 8-frame source PNG.
No AI image approximation and no extra hands/feet.
"""
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image

SOURCE_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAFAAAAAMCAYAAAD1XTohAAABw0lEQVR4nMWXMUvDQBiG3wtZnItCtXaw2USo7e5PEAQLLv0/buLUuXNd6iSEghQ0Sxtbi0uJQoK2UFChU53iYC7m7pL2CtfkW0JyT77n/ZKGpAT/5SO+CLcvy8mWam+q+UgUOq/VGOKm1eLlstxK8Ya8qefTKVSuVIVO5UoVA7vPyCQ4skLMMAq9meTT6AGjdCCARumAaSDJLRXzjEJvJvn06ILz+oaHqwsAwNR7R75YwNTbhVHvYx1umRgAvXvKvVnk0+MgAMgXC8x2XU52YNXetPNpdOHyTLwjtHG0ZDnZQVR7086nAeJPNgoZ9etwX5aTEW/Cm0W+8BF+1Apwxz/4mH1ibycXbLeFk2W4gd0HYgLGDaLSm0U+HcErezh+xnD8d9C8/+Z7h99ZEpwPAA3nCw3nDgAwmwhcyCr0ZpJPi8AAgHazA8u048LxHLFMG4vJHIvJnOdJu9kJWcoEfUmkD8PRskw7yjDcqnztZgdez4XXc5M4AiBkgn78jIQ7h84rXAv6CPtez8V+bitcjVwU+mHJcz4A8vTi8PODZwMm6a9UyFndEY4PDd7JcKcnR7jtjpLygcvkJ3B87iSOn1fw/gKc5h2JVPabcwAAAABJRU5ErkJggg=="
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
print("SP_PLAYER_A_BROWSER_GIF_8_FRAMES_VERIFIED")
print("SP_PLAYER_A_BROWSER_PNG_2400x360_VERIFIED")
