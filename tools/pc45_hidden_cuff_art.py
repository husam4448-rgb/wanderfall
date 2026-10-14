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
# Smooth tapered cloth edge stays tucked behind rifle and glove.
# Closed glove-side bridge: upper silhouette sits behind foregrip;
# lower boundary is convex and does not hang below hand skin pixels.
d.polygon([(154,88),(158,85),(163,83),(168,81),(171,80),
           (173,82),(171,84),(167,85),(163,87),(159,89),
           (155,90)],fill=194)
d.ellipse((168,80,173,85),fill=214)
mask=mask.filter(ImageFilter.GaussianBlur(0.65))
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
ink.line([(159,86),(164,84),(169,82)], fill=(22,25,21,130),width=2)
ink.line([(158,88),(163,86),(169,84)], fill=(175,151,111,95),width=1)
decor.putalpha(Image.composite(decor.getchannel("A"),Image.new("L",(w,h)),mask))
out.alpha_composite(decor)
dest=ART/"pc45_hidden_support_cuff.png"
out.save(dest)
print("PC45_HIDDEN_CUFF_RGBA",str(dest),"size",w,h,"alpha_pixels",sum(v>32 for v in mask.getdata()))
