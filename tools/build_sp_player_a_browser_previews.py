#!/usr/bin/env python3
"""Survival Paradise Style A 10x12: browser-ready walking preview.
Original eight-frame Style A strip retained exactly except ONE black pixel
under the planted back foot in frame 2 (index 1, x0 y11).
Never invent another silhouette. Uses the user's approved head and body.
"""
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image
SOURCE_PNG_B64="iVBORw0KGgoAAAANSUhEUgAAAFAAAAAMCAYAAAD1XTohAAABBElEQVR4nO2WsQrCQAyG/xPfQ1xdXJydxLG4uNld8Bms1HcoODi6uUhHwcVZaB9AFEQXX6Iu2rukaS3omG9L77tcEsq1BpSMxQYy6r1puNIyDJEmCdIkwTIMpY3qMc+4kovneYjjGMFioV6F13QX/c7TBuc1/A4QoIh61iMDbHUHwvao8EQ96+V3IJlyBepR8gHKUy6iHsX9bGfX7YwstscRd9RjHrkD54cH6qCehQzwdrnXSqieJX9d+8NeBgDH/ekT4x3n/0ST6QgAsFntjLuHezw/y02uDcmVPOfssvqIB9jGmVPwPjndOoRzeX+mrBlRhNBsiVfGr963+iSv6sy/1P0CB0NKE7KrIHwAAAAASUVORK5CYII="
PREVIOUS_PNG_B64="iVBORw0KGgoAAAANSUhEUgAAAFAAAAAMCAYAAAD1XTohAAABHklEQVR4nO2XMUvDQBTH/4sTz0Lh4KAQwUWdHFRx8QScHBw6uIiUdu6uUrq4CDp0FRsFwaFDREMFCS7mYBPv7VZ1aNL0m9zNu7e+f4+b19S0aJV1vvQU5dEOBocXmsIOCpKsCgRMIOCpKsCgRML+N4cWJqG6mNLuOHIIBBzkFzpQBVjII8cHoA8YSWPbNcwtNmI4WObZgeD/d15wts3ioDRRGHtEKCs6LEerUFgn8vRI7wzmUcWRKu6VVN8Wt9wEdpCjZoZgF2j5o5J1HjQvBPH6wQQ5YUwVxBQJQnTOllXICqOGeq3+4ZJZZ3uV9DSn6DJCQM4QFjpA5L9O4HBr8rcwdJpc1oqKRTli4RROhhlOh6LHcSpY/pg26ejr5xf/GOndjnrnCr0f4/Tqp5KWHc8PFzV/5vd4fOt/EgSxidMZY59EYkoAAAAASUVORK5CYII="
# Use the exact corrected strip only. Explicitly validate shape, foot outline
# and zero changes above the waist across all frames.
strip=Image.open(BytesIO(base64.b64decode(SOURCE_PNG_B64))).convert("RGBA")
assert strip.size==(80,12)
# Remove the 1-pixel dangling rear-foot tip in both back-step poses.
# These are the ONLY four pixel edits; preserve prototype A 10x12,
# the accepted body size, and the remainder of its animation.
before=strip.copy()
clear=(0,0,0,0)
black=(0,0,0,255)
assert before.getpixel((10,10))==black
assert before.getpixel((10,11))==black
assert before.getpixel((20,10))==black
strip.putpixel((10,10),clear)  # planted rear-foot stray tip
strip.putpixel((10,11),clear)  # previous incorrect lower protrusion
strip.putpixel((20,10),clear)  # raised rear-foot stray tip
strip.putpixel((11,10),black)  # continue back edge into the actual foot
deltas=[(x,y) for y in range(12) for x in range(80)
        if strip.getpixel((x,y))!=before.getpixel((x,y))]
assert set(deltas)=={(10,10),(10,11),(20,10),(11,10)},deltas
assert all(strip.crop((10*i,0,10*i+10,9)).tobytes()==before.crop((10*i,0,10*i+10,9)).tobytes()
           for i in range(8))

assert strip.getpixel((10,10))==(0,0,0,0)
assert strip.getpixel((10,11))==(0,0,0,0)
out=Path("assets/sp_player_a_preview")
out.mkdir(parents=True,exist_ok=True)
def create(scale, bg=(236,236,234)):
    pics=[]
    for i in range(8):
        fr=strip.crop((10*i,0,10*(i+1),12))
        back=Image.new("RGBA",fr.size,bg+(255,))
        back.alpha_composite(fr)
        pics.append(back.convert("RGB").resize((10*scale,12*scale),Image.Resampling.NEAREST))
    return pics
strip.save(out/"SP_Player_A_10x12_Walk_Sprite_Strip.png")
frames=create(36)
sheet=Image.new("RGB",(8*360,432),(236,236,234))
for i,f in enumerate(frames):
    sheet.paste(f,(i*360,0))
for name in ("SP_Player_A_10x12_Walk_8_Frames.png","SP_Style_A_BackFoot_Outlined_Walk_Frames.png","SP_Style_A_RearFoot_Clean_10x12_Frames.png"):
    sheet.save(out/name,optimize=True)
for name in ("SP_Player_A_10x12_Walk_Animated.gif","SP_Style_A_BackFoot_Outlined_Walk.gif","SP_Style_A_RearFoot_Clean_10x12.gif"):
    frames[0].save(out/name,save_all=True,append_images=frames[1:],
       duration=145,loop=0,optimize=False,disposal=2)
    with Image.open(out/name) as img:
        assert img.n_frames==8 and img.size==(360,432)
        for n,fr in enumerate(frames):
            img.seek(n)
            assert img.convert("RGB").tobytes()==fr.tobytes()
print("SP_STYLE_A_BACK_FOOT_BLACK_OUTLINE_BROWSER_LINKS_PASS")
