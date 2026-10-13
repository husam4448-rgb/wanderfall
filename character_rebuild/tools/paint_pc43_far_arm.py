"""Experimental tapered source-textured arm surfaces. NOT visual approval."""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ARM_SEGMENTS = {
    "upper_far": ((91, 78), (133, 107), (20, 17, 15)),
    "forearm_far": ((133, 107), (172, 85), (17, 13, 11)),
}

def paint_source_textured_arm(original, name):
    if name not in ARM_SEGMENTS:
        raise ValueError(name)
    a, b, radii = ARM_SEGMENTS[name]
    source = Image.fromarray(original, "RGB")
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    width, height = int(math.ceil(length)) + 16, 35
    mid = height // 2
    texture = source.crop((79, 85, 101, 108)).resize(
        (width, height), Image.Resampling.BICUBIC)
    texture = ImageEnhance.Color(texture).enhance(0.78)
    mask = Image.new("L", (width, height))
    draw = ImageDraw.Draw(mask)
    first, last = 6, width - 6
    step = (last - first) / 4
    top, elbow, cuff = [v / 2 for v in radii]
    contour = [
        (first, mid - top), (first + step, mid - top - 0.5),
        (first + 2 * step, mid - elbow),
        (first + 3 * step, mid - elbow - 1), (last, mid - cuff),
        (last, mid + cuff), (first + 3 * step, mid + elbow + 1),
        (first + 2 * step, mid + elbow),
        (first + step, mid + top + 0.5), (first, mid + top),
    ]
    draw.polygon(contour, fill=255)
    draw.ellipse((first - top / 2, mid - top,
                  first + top / 2, mid + top), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.55))
    surface = Image.new("RGBA", (width, height))
    surface.paste(texture, (0, 0), mask)
    folds = Image.new("RGBA", (width, height))
    ink = ImageDraw.Draw(folds, "RGBA")
    ink.arc((last - 11, mid - cuff - 3, last + 2, mid + cuff + 3),
            -83, 91, fill=(26, 28, 24, 175), width=2)
    ink.arc((first + step, mid - elbow, first + 2 * step, mid + elbow),
            -60, 100, fill=(181, 163, 118, 65), width=1)
    ink.line((first + 7, mid - top + 3,
              first + 2 * step, mid - elbow + 2),
             fill=(193, 170, 121, 65), width=1)
    folds.putalpha(Image.composite(
        folds.getchannel("A"), Image.new("L", (width, height)), mask))
    surface.alpha_composite(folds)
    angle = -math.degrees(math.atan2(dy, dx))
    surface = surface.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    canvas = Image.new("RGBA", (original.shape[1], original.shape[0]))
    canvas.alpha_composite(surface, (
        round(cx - surface.width / 2), round(cy - surface.height / 2)))
    return canvas
