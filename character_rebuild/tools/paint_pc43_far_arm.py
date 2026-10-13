"""Source-textured provisional far-arm surfaces for PC43.
These surfaces are newly synthesized from approved fabric pixels, NOT recovered
hidden anatomy. Keep candidate status until native Godot 22-angle visual QA.
"""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ARM_SEGMENTS = {
    "upper_far": ((91,78),(133,107),22),
    "forearm_far": ((133,107),(172,85),18),
}

def paint_source_textured_arm(original, name):
    if name not in ARM_SEGMENTS:
        raise ValueError(name)
    source = Image.fromarray(original, "RGB")
    a,b,width = ARM_SEGMENTS[name]
    fabric = source.crop((91,74,117,98))
    if fabric.size != (26,24):
        raise ValueError("Unexpected approved jacket patch")
    dx,dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx,dy)
    W = int(length+16)
    H = width+12
    sleeve = ImageEnhance.Color(fabric.resize((W,H),Image.Resampling.BICUBIC)).enhance(0.7)
    coverage = Image.new("L",(W,H))
    d = ImageDraw.Draw(coverage)
    d.rounded_rectangle((4,5,W-5,H-6),radius=width//2,fill=255)
    coverage = coverage.filter(ImageFilter.GaussianBlur(0.45))
    part = Image.new("RGBA",(W,H))
    part.paste(sleeve,(0,0),coverage)
    ink = ImageDraw.Draw(part,"RGBA")
    ink.line((W-12,6,W-12,H-6),fill=(28,30,25,150),width=3)
    ink.arc((W-22,6,W-3,H-5),90,270,fill=(179,155,112,125),width=1)
    theta = -math.degrees(math.atan2(dy,dx))
    part = part.rotate(theta,Image.Resampling.BICUBIC,expand=True)
    # Place source joint at start cap (roughly 8 source pixels from shaft edge)
    center = ((a[0]+b[0])/2,(a[1]+b[1])/2)
    canvas = Image.new("RGBA",(original.shape[1], original.shape[0]))
    canvas.alpha_composite(part,(round(center[0]-part.width/2), round(center[1]-part.height/2)))
    return canvas
