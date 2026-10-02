#!/usr/bin/env python3
from pathlib import Path
import base64, io, re, sys
from collections import deque
from PIL import Image, ImageFilter, ImageStat

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parents[1]
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
gear_dir = repo_root / "art_source" / "gear" / "d2d40"
vest_path = gear_dir / "vest.webp"
legs_path = gear_dir / "legs.webp"

if not script.exists() or not vest_path.exists() or not legs_path.exists():
    raise SystemExit("D2D.55 required runtime/source assets missing")

def save_webp(img: Image.Image, path: Path) -> None:
    img.save(path, "WEBP", lossless=True, quality=100, method=6)

def fill_enclosed_alpha_holes(img: Image.Image) -> Image.Image:
    """Fill transparent components not connected to image border using nearby cloth pixels."""
    im = img.convert("RGBA")
    w,h = im.size
    px = im.load()
    transparent = [[px[x,y][3] < 24 for x in range(w)] for y in range(h)]
    outside = [[False]*w for _ in range(h)]
    q = deque()
    for x in range(w):
        for y in (0,h-1):
            if transparent[y][x] and not outside[y][x]:
                outside[y][x]=True; q.append((x,y))
    for y in range(h):
        for x in (0,w-1):
            if transparent[y][x] and not outside[y][x]:
                outside[y][x]=True; q.append((x,y))
    while q:
        x,y=q.popleft()
        for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=nx<w and 0<=ny<h and transparent[ny][nx] and not outside[ny][nx]:
                outside[ny][nx]=True; q.append((nx,ny))

    holes=[(x,y) for y in range(h) for x in range(w) if transparent[y][x] and not outside[y][x]]
    if not holes:
        return im

    # nearest opaque propagation from all opaque pixels, preserving actual garment palette
    dist=[[-1]*w for _ in range(h)]
    src=[[None]*w for _ in range(h)]
    q=deque()
    for y in range(h):
        for x in range(w):
            if px[x,y][3] >= 24:
                dist[y][x]=0; src[y][x]=(x,y); q.append((x,y))
    while q:
        x,y=q.popleft()
        for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=nx<w and 0<=ny<h and dist[ny][nx] == -1:
                dist[ny][nx]=dist[y][x]+1
                src[ny][nx]=src[y][x]
                q.append((nx,ny))
    for x,y in holes:
        sx,sy=src[y][x]
        r,g,b,a=px[sx,sy]
        px[x,y]=(r,g,b,255)

    # very light texture continuity only inside the former hole
    blurred=im.filter(ImageFilter.GaussianBlur(radius=max(0.35,w/300)))
    bp=blurred.load()
    for x,y in holes:
        r,g,b,_=bp[x,y]
        # retain slight nearby contrast so it reads as sleeve/armor mesh, not a flat disc
        if ((x+y)&3)==0:
            r=max(0,r-7); g=max(0,g-6); b=max(0,b-5)
        px[x,y]=(r,g,b,255)
    return im

def remove_thigh_pocket(img: Image.Image) -> Image.Image:
    """Create a pocketless front-leg variant by inpainting only the upper-thigh cargo area."""
    im=img.convert("RGBA")
    w,h=im.size
    # Pocket visible in authored leg: upper-middle cargo block.
    x0,x1=int(w*0.16),int(w*0.82)
    y0,y1=int(h*0.24),int(h*0.51)
    # build a softened fabric donor from immediately below/around the pocket
    crop=im.crop((x0,y0,x1,y1))
    smooth=crop.filter(ImageFilter.GaussianBlur(radius=max(1.0,w*0.035)))
    src=im.load(); sm=smooth.load()
    for y in range(y0,y1):
        for x in range(x0,x1):
            if src[x,y][3] < 24:
                continue
            lx,ly=x-x0,y-y0
            r,g,b,a=sm[lx,ly]
            # preserve alpha and add subtle vertical cloth/camo modulation
            delta = -8 if ((x//3 + y//7) & 1) else 5
            src[x,y]=(max(0,min(255,r+delta)),max(0,min(255,g+delta)),max(0,min(255,b+delta)),src[x,y][3])
    return im

# Edit source art itself in the build workspace.
vest_fixed=fill_enclosed_alpha_holes(Image.open(vest_path))
save_webp(vest_fixed, vest_path)

front_path=gear_dir/"legs_front.webp"
front_fixed=remove_thigh_pocket(Image.open(legs_path))
save_webp(front_fixed, front_path)

vest_b64=base64.b64encode(vest_path.read_bytes()).decode("ascii")
front_b64=base64.b64encode(front_path.read_bytes()).decode("ascii")

s=script.read_text(encoding="utf-8")
s=s.replace('title.text = "D2D.54 GEAR:"','title.text = "D2D.55 GEAR:"',1)

# Replace embedded vest with corrected root asset.
s,n = re.subn(r'const GEAR_VEST_B64 := "[^"]+"',
              'const GEAR_VEST_B64 := "'+vest_b64+'"',s,count=1)
if n != 1:
    raise SystemExit("D2D.55 GEAR_VEST_B64 anchor missing")

# Add pocketless front-leg asset at the root asset level.
anchor='const GEAR_LEGS_B64 := '
idx=s.find(anchor)
if idx<0:
    raise SystemExit("D2D.55 GEAR_LEGS_B64 anchor missing")
line_end=s.find("\n",idx)
s=s[:line_end+1] + 'const GEAR_LEGS_FRONT_B64 := "'+front_b64+'"\n' + s[line_end+1:]

var_anchor='var tex_gear_legs: Texture2D = null\n'
if var_anchor not in s:
    raise SystemExit("D2D.55 tex_gear_legs var anchor missing")
s=s.replace(var_anchor,var_anchor+'var tex_gear_legs_front: Texture2D = null\nvar tex_base_leg_front: Texture2D = null\n',1)

ready_anchor='    tex_gear_legs = _texture_from_embedded_webp(GEAR_LEGS_B64)\n'
if ready_anchor not in s:
    raise SystemExit("D2D.55 leg texture ready anchor missing")
s=s.replace(ready_anchor,ready_anchor+'    tex_gear_legs_front = _texture_from_embedded_webp(GEAR_LEGS_FRONT_B64)\n',1)

base_anchor='    tex_base_leg = _solid_texture_from_embedded_webp(GEAR_LEGS_B64, Color("394247"))\n'
if base_anchor not in s:
    raise SystemExit("D2D.55 base leg ready anchor missing")
s=s.replace(base_anchor,base_anchor+'    tex_base_leg_front = _solid_texture_from_embedded_webp(GEAR_LEGS_FRONT_B64, Color("394247"))\n',1)

# Remove ALL runtime shoulder overlays/underlays from D2D.54.
old_base='''    if not gear_torso:
        # D2D.54: sleeve material sits BEHIND the authored torso.
        # Only the transparent shoulder socket reveals it.
        var shoulder_fill := base + Vector2(-8.0 * dir_sign,-8.1)
        draw_circle(shoulder_fill,4.05,Color("4e594b"))
        draw_line(shoulder_fill + Vector2(-2.2 * dir_sign,-1.0),
                  shoulder_fill + Vector2(2.0 * dir_sign,1.1),
                  Color("596455"),1.0,true)
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
new_base='''    if not gear_torso:
        # D2D.55: corrected source asset contains its own sleeve mesh.
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if old_base not in s:
    raise SystemExit("D2D.55 base shoulder runtime block missing")
s=s.replace(old_base,new_base,1)

old_vest='''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    # D2D.54: matching armor/sleeve mesh under the transparent shoulder socket.
    # Vest is drawn over it so the fill cannot look like an external round patch.
    var shoulder_fill := base + Vector2(-8.0 * dir_sign,-8.1)
    draw_circle(shoulder_fill,4.05,Color("514d42"))
    draw_line(shoulder_fill + Vector2(-2.1 * dir_sign,-1.1),
              shoulder_fill + Vector2(2.0 * dir_sign,1.0),
              Color("6c6657"),1.0,true)
    draw_line(shoulder_fill + Vector2(-1.7 * dir_sign,1.2),
              shoulder_fill + Vector2(1.7 * dir_sign,-1.2),
              Color("403d35"),0.8,true)
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
new_vest='''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    # D2D.55: no runtime shoulder patch; source vest is corrected directly.
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if old_vest not in s:
    raise SystemExit("D2D.55 geared shoulder runtime block missing")
s=s.replace(old_vest,new_vest,1)

# Remove D2D.54 runtime pocket paint-over entirely.
start=s.find('    # D2D.54: remove the inner-thigh cargo pocket from the near/forward leg.\n')
if start<0:
    raise SystemExit("D2D.55 old pocket runtime block missing")
end=s.find('    # D2D.50: slightly forward and lower relative to ankle.\n',start)
if end<0:
    raise SystemExit("D2D.55 pocket runtime end missing")
s=s[:start]+s[end:]

# Use the corrected ROOT front-leg texture for the near/forward leg; rear leg keeps original.
old_leg='''    if gear_legs:
        _draw_equipment_texture(tex_gear_legs, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
    else:
        _draw_equipment_texture(tex_base_leg, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
'''
new_leg='''    var is_front_leg := side * dir_sign > 0.0
    if gear_legs:
        var leg_tex := tex_gear_legs_front if is_front_leg else tex_gear_legs
        _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
    else:
        var leg_tex := tex_base_leg_front if is_front_leg else tex_base_leg
        _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
'''
if old_leg not in s:
    raise SystemExit("D2D.55 leg draw block missing")
s=s.replace(old_leg,new_leg,1)

script.write_text(s,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=128',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.55"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.55 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.55"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.55: source-art shoulder repair and source-art pocketless forward leg; runtime paint-over removed.")
