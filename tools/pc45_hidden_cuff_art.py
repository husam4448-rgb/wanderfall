#!/usr/bin/env python3
"""PC45 provisional concealed cuff overlap. Real RGBA asset, not QA approval."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"pc42-static-prototype"/"assets"
source=Image.open(ART/"approved_reference_panel.png").convert("RGB")
w,h=source.size
# Only the final hidden sleeve/cuff span approaching the source's foregrip.
# No generated exposed bare arm and no modification to accepted body image.
mask=Image.new("L",(w,h),0)
d=ImageDraw.Draw(mask)
# A narrow concealed sleeve bridge starts inside the existing rifle/chest
# overlap and tapers toward the cuff. Avoid a hanging polygon below the rifle.
d.polygon([(151,89),(155,85),(162,83),(167,81),(172,79),
           (173,84),(168,86),(161,88),(155,92),(151,93)],fill=205)
d.ellipse((166,79,174,86),fill=235)
mask=mask.filter(ImageFilter.GaussianBlur(0.7))
patch=source.crop((97,88,114,104))
fabric=ImageEnhance.Color(patch).enhance(0.65)
texture=fabric.resize((w,h),Image.Resampling.BILINEAR)
# Repeat original material instead of stretching one tiny sample across full canvas.
tex=Image.new("RGB",(w,h))
for y in range(0,h,patch.height):
    for x in range(0,w,patch.width):
        tex.paste(fabric,(x,y))
out=tex.convert("RGBA")
out.putalpha(mask)
decor=Image.new("RGBA",(w,h),(0,0,0,0))
ink=ImageDraw.Draw(decor)
ink.line([(157,87),(162,85),(169,82)], fill=(22,25,21,130),width=2)
ink.line([(155,90),(163,87),(172,84)], fill=(175,151,111,95),width=1)
decor.putalpha(Image.composite(decor.getchannel("A"),Image.new("L",(w,h)),mask))
out.alpha_composite(decor)
dest=ART/"pc45_hidden_support_cuff.png"
out.save(dest)
print("PC45_HIDDEN_CUFF_RGBA",str(dest),"size",w,h,"alpha_pixels",sum(v>32 for v in mask.getdata()))
