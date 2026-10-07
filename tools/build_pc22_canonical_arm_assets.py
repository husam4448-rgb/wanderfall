#!/usr/bin/env python3
"""Build PlayerCharacters_v22 canonical articulated arm assets and deterministic QA."""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops, ImageOps
import base64, hashlib, json, math, re, sys

repo=Path(sys.argv[1] if len(sys.argv)>1 else ".")
game=Path(sys.argv[2]) if len(sys.argv)>2 else None
runtime=(game/"scripts/art/d2d29_minimal_token_runtime.gd") if game else None
runtime_text=runtime.read_text(encoding="utf-8") if runtime and runtime.is_file() else ""
canonical_path=repo/"assets/authored2d/unified_character/canonical_pc22.json"
if not canonical_path.is_file():
    raise SystemExit("canonical_pc22.json missing")
canonical=json.loads(canonical_path.read_text(encoding="utf-8"))
if canonical.get("standard_id")!="PlayerCharacters_v22":
    raise SystemExit("Wrong canonical standard")

src_dir=repo/"art_source/characters"
upper_src_path=src_dir/"hybrid_male_upper_arm.b64"
fore_src_path=src_dir/"hybrid_male_forearm_hand.b64"
male_torso_src_path=src_dir/"hybrid_male_torso.b64"
female_torso_src_path=repo/"assets/authored2d/unified_character/core/female/torso_base.png"
gear_torso_src_path=repo/"assets/authored2d/unified_character/generic/torso.png"
glove_src_path=repo/"art_source/gear/d2d40/glove.webp"
rifle_src_path=repo/"assets/authored2d/gear/rifle.png"
for required in (upper_src_path,fore_src_path,male_torso_src_path,female_torso_src_path,gear_torso_src_path,glove_src_path,rifle_src_path):
    if not required.is_file():
        raise SystemExit(f"Authored arm/torso/hand/weapon source missing: {required}")

root=repo/"assets/authored2d/unified_character/arms"
qa=root/"qa"
meta=root/"metadata"
v3_root=root/"hybrid_v3"
for d in (root/"male",root/"female",root/"weapons",v3_root/"male",v3_root/"female",v3_root/"weapons",qa,meta,
          repo/"assets/authored2d/unified_character/core/male",
          repo/"assets/authored2d/unified_character/core/female"):
    d.mkdir(parents=True,exist_ok=True)

def load_b64_png(p):
    raw=base64.b64decode(p.read_text(encoding="utf-8").strip())
    return Image.open(BytesIO(raw)).convert("RGBA")

def embedded_runtime_image(name):
    if not runtime_text:
        return None
    m=re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"',runtime_text)
    if not m:
        return None
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")

def trim(img):
    bb=img.getchannel("A").getbbox()
    if bb is None:
        raise SystemExit("Empty source image")
    return img.crop(bb)

def recolor(img, base_rgb, grain=2):
    img=img.convert("RGBA")
    out=Image.new("RGBA",img.size,(0,0,0,0))
    src=img.load(); dst=out.load()
    for y in range(img.height):
        for x in range(img.width):
            r,g,b,a=src[x,y]
            if a<4: continue
            lum=(r+g+b)/3.0
            delta=int(max(-58,min(58,(lum-112.0)*0.42)))
            gnoise=((x*17+y*11)%5)-2 if grain else 0
            dst[x,y]=(max(0,min(255,base_rgb[0]+delta+gnoise)),
                      max(0,min(255,base_rgb[1]+delta+gnoise)),
                      max(0,min(255,base_rgb[2]+delta+gnoise)),a)
    return out

def fabric_grade(img, base_rgb, contrast=1.42):
    """Preserve authored folds/high-frequency shading while retinting to PC22 cloth.

    The previous flat recolor compressed most sleeve values into a narrow olive
    range, which made runtime arms look like soft blobs beside the detailed torso.
    This maps the original luminance through a wide cloth palette instead.
    """
    src=img.convert("RGBA")
    alpha=src.getchannel("A")
    gray=ImageOps.grayscale(src)
    gray=ImageEnhance.Contrast(gray).enhance(contrast)
    dark=tuple(max(0,int(c*0.34)) for c in base_rgb)
    light=tuple(min(255,int(c*1.62+10)) for c in base_rgb)
    graded=ImageOps.colorize(gray,dark,light).convert("RGBA")
    graded.putalpha(alpha)

    # Re-introduce a small amount of source chroma/texture so seam/fold detail
    # survives aggressive runtime down-scaling without changing the cloth hue.
    out=Image.blend(graded,src,0.10)
    out.putalpha(alpha)
    return out

def anatomical_sleeve(img, base_rgb, sex, segment, fabric_ref=None):
    """Impose a smooth anatomical silhouette while retaining authored cloth folds.

    Real-device V3 screenshots exposed jagged/pointed alpha from the tiny legacy
    source art after rotation.  The texture is preserved, but the visible sleeve
    edge is rebuilt as a continuous shoulder/elbow/wrist profile.
    """
    img=img.convert("RGBA")
    w,h=img.size
    female=(sex=="female")
    if segment=="upper":
        # broad hidden shoulder root -> biceps -> compact elbow
        profile=(0.38,0.50,0.35) if female else (0.42,0.56,0.39)
    else:
        # elbow mass -> tapered forearm -> narrow wrist/cuff
        profile=(0.40,0.43,0.20) if female else (0.44,0.48,0.22)

    mask=Image.new("L",(w,h),0)
    mp=mask.load()
    # Build the silhouette row-by-row with smooth interpolation.
    for y in range(h):
        t=y/max(1,h-1)
        if t<0.52:
            q=t/0.52
            frac=profile[0]+(profile[1]-profile[0])*(q*q*(3.0-2.0*q))
        else:
            q=(t-0.52)/0.48
            frac=profile[1]+(profile[2]-profile[1])*(q*q*(3.0-2.0*q))
        half=max(2.0,(w*frac)*0.5)
        curve=(2.25 if not female else 1.75)*math.sin(math.pi*t)
        if segment=="forearm":
            curve*=0.76
        cx=(w-1)*0.5+curve
        x0=max(0,int(round(cx-half)))
        x1=min(w-1,int(round(cx+half)))
        for x in range(x0,x1+1):
            mp[x,y]=255
    # Soften only one pixel-class at the edge; do not create a blurred blob.
    mask=mask.filter(ImageFilter.GaussianBlur(0.38))

    # Fill the silhouette with cloth-toned edge shading first so any transparent
    # holes in the legacy source cannot become visible black gaps at runtime.
    base=Image.new("RGBA",(w,h),(0,0,0,0))
    bp=base.load(); ma=mask.load()
    for y in range(h):
        for x in range(w):
            a=ma[x,y]
            if a<4: continue
            center=(w-1)*0.5
            edge=min(1.0,abs(x-center)/max(1.0,w*0.36))
            light=1.03-0.25*edge
            # tiny deterministic fabric variation avoids a flat vector tube
            grain=(((x*13+y*7)%9)-4)*0.010
            bp[x,y]=(max(0,min(255,int(base_rgb[0]*(light+grain)))),
                     max(0,min(255,int(base_rgb[1]*(light+grain)))),
                     max(0,min(255,int(base_rgb[2]*(light+grain)))),a)

    # Preserve broad authored limb luminance without reintroducing jagged legacy
    # alpha. Then borrow fold structure from the real torso art so the sleeve and
    # body share the same painted visual language.
    broad=ImageOps.grayscale(img).filter(ImageFilter.GaussianBlur(1.05))
    low=tuple(max(0,int(c*0.72)) for c in base_rgb)
    high=tuple(min(255,int(c*1.30+5)) for c in base_rgb)
    tonal=ImageOps.colorize(broad,low,high).convert("RGBA")
    tonal.putalpha(mask)
    base=Image.blend(base,tonal,0.20)
    base.putalpha(mask)

    if fabric_ref is not None:
        ref=trim(fabric_ref).convert("RGBA")
        # Use luminance only: this transfers folds/weave, not torso silhouette.
        refgray=ImageOps.grayscale(ref).filter(ImageFilter.GaussianBlur(0.55))
        refgray=ImageEnhance.Contrast(refgray).enhance(1.38)
        refgray=refgray.resize((w,h),Image.Resampling.LANCZOS)
        ref_dark=tuple(max(0,int(c*0.56)) for c in base_rgb)
        ref_light=tuple(min(255,int(c*1.50+8)) for c in base_rgb)
        reftex=ImageOps.colorize(refgray,ref_dark,ref_light).convert("RGBA")
        reftex.putalpha(mask)
        base=Image.blend(base,reftex,0.50 if sex=="female" else 0.38)
        base.putalpha(mask)

    # Sparse cloth creases give readable fabric structure without jagged source
    # silhouettes. They rotate with the limb and remain subtle at gameplay scale.
    d=ImageDraw.Draw(base)
    crease_dark=tuple(max(0,int(c*0.62)) for c in base_rgb)+(95,)
    crease_light=tuple(min(255,int(c*1.34+5)) for c in base_rgb)+(70,)
    crease_rows=(0.34,0.61,0.82) if segment=="upper" else (0.28,0.55,0.78)
    for idx,yf in enumerate(crease_rows):
        y=int(round(h*yf))
        t=y/max(1,h-1)
        if t<0.52:
            q=t/0.52
            frac=profile[0]+(profile[1]-profile[0])*(q*q*(3.0-2.0*q))
        else:
            q=(t-0.52)/0.48
            frac=profile[1]+(profile[2]-profile[1])*(q*q*(3.0-2.0*q))
        half=max(2.0,(w*frac)*0.5)
        cx=(w-1)*0.5
        x0=int(round(cx-half*0.62))
        x1=int(round(cx+half*0.58))
        d.line((x0,y,x1,y+(1 if idx%2==0 else -1)),fill=crease_dark,width=1)
        if y+2<h:
            d.line((x0+2,y+2,x1-2,y+2),fill=crease_light,width=1)

    # Avoid a long straight stitch that makes the limb read as a rigid strap.
    # Short diagonal cloth breaks reinforce fabric without exposing the segment axis.
    for yf,sgn in ((0.43,1),(0.69,-1)):
        y=int(round(h*yf))
        cx=int(round(w*0.50))
        span=max(3,int(round(w*0.13)))
        d.line((cx-span,y,cx+span,y+sgn),fill=crease_dark,width=1)
        if y+2<h:
            d.line((cx-span+2,y+2,cx+span-2,y+2+sgn),fill=crease_light,width=1)

    # Distal cuff shadow defines the wrist without a rectangular joint.
    if segment=="forearm":
        y=int(round(h*0.90))
        d.line((int(w*0.40),y,int(w*0.60),y),fill=crease_dark,width=1)

    # Dark inner edge gives the same pixel-art contour weight as torso/head.
    inner=mask.filter(ImageFilter.MinFilter(3))
    edge=ImageChops.subtract(mask,inner)
    outline=Image.new("RGBA",(w,h),(0,0,0,0))
    op=outline.load(); ep=edge.load()
    edge_rgb=tuple(max(0,int(c*0.40)) for c in base_rgb)
    for yy in range(h):
        for xx in range(w):
            ea=ep[xx,yy]
            if ea>0:
                op[xx,yy]=(edge_rgb[0],edge_rgb[1],edge_rgb[2],min(150,ea))
    base.alpha_composite(outline)
    base.putalpha(mask)
    return base

def row_warp(img, top_scale, mid_scale, bottom_scale):
    img=img.convert("RGBA"); w,h=img.size
    out=Image.new("RGBA",(w,h),(0,0,0,0))
    for y in range(h):
        t=y/max(1,h-1)
        if t<0.5:
            sc=top_scale+(mid_scale-top_scale)*(t/0.5)
        else:
            sc=mid_scale+(bottom_scale-mid_scale)*((t-0.5)/0.5)
        nw=max(1,int(round(w*sc)))
        row=img.crop((0,y,w,y+1)).resize((nw,1),Image.Resampling.LANCZOS)
        out.alpha_composite(row,((w-nw)//2,y))
    return out

def recanvas_vertical(img, canvas=(64,128), margin_y=5, width_fraction=0.48):
    img=trim(img)
    target_h=canvas[1]-2*margin_y
    ratio=target_h/img.height
    natural_w=max(1,int(round(img.width*ratio)))
    max_w=max(1,int(round(canvas[0]*width_fraction)))
    # Production draw helpers scale the full canvas. Fill the intended width
    # instead of preserving a narrow source canvas that visually collapses to a bar.
    target_w=max_w
    resized=img.resize((target_w,target_h),Image.Resampling.LANCZOS)
    out=Image.new("RGBA",canvas,(0,0,0,0))
    out.alpha_composite(resized,((canvas[0]-target_w)//2,margin_y))
    return out

def tactical_sleeve(img, sex, segment):
    """Detailed tactical cloth variant used when vest/body armor is equipped."""
    src=img.convert("RGBA")
    alpha=src.getchannel("A")
    gray=ImageOps.grayscale(src)
    gray=ImageEnhance.Contrast(gray).enhance(1.28)
    if sex=="female":
        dark=(55,55,44); light=(126,118,86)
    else:
        dark=(52,51,41); light=(119,109,80)
    out=ImageOps.colorize(gray,dark,light).convert("RGBA")
    out.putalpha(alpha)
    # Transfer only shading/detail from the actual tactical torso/vest art.
    gref=trim(gear_torso_ref).convert("RGBA")
    glum=ImageOps.grayscale(gref).filter(ImageFilter.GaussianBlur(0.45))
    glum=ImageEnhance.Contrast(glum).enhance(1.45).resize(out.size,Image.Resampling.LANCZOS)
    gdark=tuple(max(0,int(c*0.52)) for c in light)
    glight=tuple(min(255,int(c*1.35+6)) for c in light)
    gtex=ImageOps.colorize(glum,gdark,glight).convert("RGBA")
    gtex.putalpha(alpha)
    out=Image.blend(out,gtex,0.50)
    out.putalpha(alpha)
    d=ImageDraw.Draw(out)
    w,h=out.size
    stitch=(174,157,112,58)
    shadow=(29,31,27,78)
    # subdued panel seam and two fabric folds
    d.line((int(w*0.36),int(h*0.10),int(w*0.37),int(h*0.88)),fill=stitch,width=1)
    for yf in ((0.46,0.67) if segment=="upper" else (0.37,0.72)):
        y=int(h*yf)
        d.line((int(w*0.32),y,int(w*0.67),y+1),fill=shadow,width=1)
    out.putalpha(alpha)
    return out

def derive_hand_fallback(fore, sex):
    f=trim(fore)
    h=f.height
    crop=f.crop((0,int(h*0.70),f.width,h))
    base=(190,126,94) if sex=="male" else (195,132,101)
    crop=recolor(crop,base,1)
    crop=trim(crop)
    canvas=Image.new("RGBA",(96,96),(0,0,0,0))
    max_w,max_h=(70,48)
    sc=min(max_w/crop.width,max_h/crop.height)
    rs=crop.resize((max(1,int(crop.width*sc)),max(1,int(crop.height*sc))),Image.Resampling.LANCZOS)
    canvas.alpha_composite(rs,((96-rs.width)//2,(96-rs.height)//2))
    return canvas

def keep_largest_alpha_component(img, threshold=12):
    img=img.convert("RGBA")
    a=img.getchannel("A")
    pix=a.load(); w,h=img.size
    seen=set(); comps=[]
    for y in range(h):
        for x in range(w):
            if (x,y) in seen or pix[x,y] <= threshold:
                continue
            stack=[(x,y)]; seen.add((x,y)); comp=[]
            while stack:
                qx,qy=stack.pop(); comp.append((qx,qy))
                for nx,ny in ((qx-1,qy),(qx+1,qy),(qx,qy-1),(qx,qy+1)):
                    if 0<=nx<w and 0<=ny<h and (nx,ny) not in seen and pix[nx,ny] > threshold:
                        seen.add((nx,ny)); stack.append((nx,ny))
            comps.append(comp)
    if not comps:
        return img
    keep=set(max(comps,key=len))
    out=Image.new("RGBA",img.size,(0,0,0,0)); src=img.load(); dst=out.load()
    for x,y in keep:
        dst[x,y]=src[x,y]
    return out

def add_joint_caps(img, rgb, top_frac, bottom_frac, depth=11):
    # Small rounded overlap zones at parent/child ends. They sit behind the
    # authored texture and prevent transparent gaps during rotation.
    img=img.convert("RGBA")
    layer=Image.new("RGBA",img.size,(0,0,0,0))
    d=ImageDraw.Draw(layer)
    w,h=img.size
    tw=max(3,int(w*top_frac)); bw=max(3,int(w*bottom_frac))
    col=(max(0,rgb[0]-4),max(0,rgb[1]-4),max(0,rgb[2]-4),255)
    d.ellipse(((w-tw)//2,-depth//2,(w+tw)//2,depth),fill=col)
    d.ellipse(((w-bw)//2,h-depth,(w+bw)//2,h+depth//2),fill=col)
    layer.alpha_composite(img)
    return layer


def make_v3_pivoted_segment(vertical_img):
    """Turn the authored vertical limb into a tightly cropped +X segment.

    The source's proximal/top end becomes the left/parent end.  Pivots are
    deliberately inside the visible overlap zones rather than at the canvas
    edge so shoulder/elbow seams remain covered without stretching artwork.
    """
    seg=trim(vertical_img).rotate(90,expand=True,resample=Image.Resampling.BICUBIC)
    seg=trim(seg)
    w,h=seg.size
    parent_x=max(2,min(6,int(round(w*0.035))))
    child_x=max(parent_x+2,w-1-max(2,min(6,int(round(w*0.035)))))
    pivot_y=h/2.0
    return seg, [float(parent_x),float(pivot_y)], [float(child_x),float(pivot_y)]


def make_v3_pivoted_hand(hand_img):
    """Tightly crop a hand while keeping its wrist as the local left-side pivot."""
    hand=trim(hand_img)
    w,h=hand.size
    wrist_x=max(1,min(4,int(round(w*0.06))))
    return hand,[float(wrist_x),float(h/2.0)]


def make_v3_shoulder_cap(upper_x, sex):
    """Build an asymmetric torso-rooted deltoid from proximal V3 arm texture.

    The former ellipse-plus-rounded-rectangle mask still read as a separate
    shoulder pad in Godot.  This mask deliberately has a broad shallow torso
    root, a single outer-deltoid apex, and a narrow arm-side taper.  Male and
    female proportions differ while canonical shoulder/IK geometry stays fixed.
    """
    src=trim(upper_x).convert("RGBA")
    sw,sh=src.size
    if sex=="female":
        cap_w=max(10,min(sw,max(int(round(sh*1.42)),int(round(sw*0.36)))))
        root_top,root_bottom=0.20,0.80
        apex_top,apex_bottom=0.08,0.92
        taper_top,taper_bottom=0.36,0.64
    else:
        cap_w=max(10,min(sw,max(int(round(sh*1.58)),int(round(sw*0.40)))))
        root_top,root_bottom=0.14,0.86
        apex_top,apex_bottom=0.04,0.96
        taper_top,taper_bottom=0.32,0.68

    cap=src.crop((0,0,cap_w,sh)).copy()
    w,h=cap.size
    mask=Image.new("L",(w,h),0)
    d=ImageDraw.Draw(mask)

    # Broad torso root -> rounded deltoid apex -> narrow upper-arm handoff.
    pts=[
        (0,int(round(h*root_top))),
        (int(round(w*0.24)),int(round(h*apex_top))),
        (int(round(w*0.50)),int(round(h*0.12 if sex=="female" else h*0.08))),
        (w-1,int(round(h*taper_top))),
        (w-1,int(round(h*taper_bottom))),
        (int(round(w*0.50)),int(round(h*0.88 if sex=="female" else h*0.92))),
        (int(round(w*0.24)),int(round(h*apex_bottom))),
        (0,int(round(h*root_bottom))),
    ]
    d.polygon(pts,fill=255)

    # Round only the outer deltoid apex; keep root/taper directional.
    apex_r=max(2,int(round(h*(0.24 if sex=="female" else 0.28))))
    apex_c=(int(round(w*0.31)),int(round(h*0.50)))
    d.ellipse((apex_c[0]-apex_r,apex_c[1]-apex_r,
               apex_c[0]+apex_r,apex_c[1]+apex_r),fill=255)

    alpha=ImageChops.multiply(cap.getchannel("A"),mask)
    cap.putalpha(alpha)
    cap=trim(cap)
    w,h=cap.size

    # Keep runtime-compatible proximal pivot ratio; do not move skeleton.
    pivot=[float(max(1,int(round(w*0.18)))),float(h/2.0)]
    return cap,pivot

def _aa_grip_hand(sex, support=False):
    """Weapon-wrap hand: palm/wrist plus visible thumb/fingers around a clear gun channel."""
    S=4
    im=Image.new("RGBA",(80*S,96*S),(0,0,0,0))
    d=ImageDraw.Draw(im)
    skin=(190,126,92,255) if sex=="male" else (204,139,103,255)
    light=(226,160,120,255) if sex=="male" else (232,172,132,255)
    mid=(145,88,67,255) if sex=="male" else (160,98,75,255)
    deep=(58,39,33,255)
    def sc(box): return tuple(int(v*S) for v in box)
    def rr(box,r,fill):
        d.rounded_rectangle(sc(box),radius=r*S,fill=fill,outline=deep,width=2*S)

    # Wrist enters from the forearm; keep it distinctly narrower than the palm.
    rr((13,39,29,57),5,mid)

    if support:
        # Handguard runs horizontally through the middle of this C-shape.
        rr((24,28,48,62),8,skin)
        rr((39,24,53,36),4,light)  # thumb over rail
        rr((38,52,50,66),4,skin)
        rr((33,57,45,71),4,skin)
        rr((28,59,40,72),4,skin)
        # Cut a horizontal weapon channel so rail remains visibly inside the hand.
        d.rounded_rectangle(sc((31,41,58,50)),radius=3*S,fill=(0,0,0,0))
        d.line([(28*S,37*S),(47*S,37*S)],fill=light,width=S)
        d.line([(29*S,56*S),(45*S,60*S)],fill=deep,width=S)
    else:
        # Pistol/rifle grip falls vertically through the palm.
        rr((23,27,48,64),8,skin)
        rr((38,23,53,36),4,light)  # thumb web over backstrap
        rr((34,52,47,67),4,skin)
        rr((31,58,43,72),4,skin)
        rr((27,60,39,73),4,skin)
        # Vertical grip channel: weapon remains visible between thumb and fingers.
        d.rounded_rectangle(sc((36,41,44,70)),radius=3*S,fill=(0,0,0,0))
        d.arc(sc((25,31,48,58)),280,85,fill=mid,width=2*S)
        d.line([(27*S,48*S),(35*S,49*S)],fill=deep,width=S)

    d.ellipse(sc((29,31,34,36)),fill=light)
    return im.resize((80,96),Image.Resampling.LANCZOS)

def _detailed_skin_hand(glove_img, sex, support=False):
    """Derive a compact articulated-looking bare hand from the authored glove.

    The glove source contains real finger/palm shading. Recoloring and compacting
    that source preserves far more readable anatomy than the old block/mitten hand.
    """
    src=trim(glove_img).convert("RGBA")
    # Remove most of the bulky equipment cuff, retain a short wrist bridge.
    w,h=src.size
    crop_x=max(0,int(round(w*0.10)))
    src=src.crop((crop_x,0,w,h))
    # Keep the authored finger silhouette, but suppress glove fabric/color so
    # bare hands read as skin rather than brown tactical gloves.
    gray=ImageOps.grayscale(src).filter(ImageFilter.GaussianBlur(0.42))
    gray=ImageEnhance.Contrast(gray).enhance(1.22)
    dark=(104,64,49) if sex=="male" else (116,70,53)
    light=(236,166,126) if sex=="male" else (242,176,136)
    recol=ImageOps.colorize(gray,dark,light).convert("RGBA")
    recol.putalpha(src.getchannel("A"))
    src=recol
    src=trim(src)

    # Compact the open authored fingers toward a gripping silhouette.
    xscale=0.62 if not support else 0.68
    src=src.resize((max(2,int(round(src.width*xscale))),src.height),Image.Resampling.LANCZOS)
    src=trim(src)

    canvas=Image.new("RGBA",(96,96),(0,0,0,0))
    maxw,maxh=(70,58) if not support else (74,56)
    sc=min(maxw/max(1,src.width),maxh/max(1,src.height))
    rs=src.resize((max(2,int(round(src.width*sc))),max(2,int(round(src.height*sc)))),Image.Resampling.LANCZOS)
    ox=10
    oy=(96-rs.height)//2
    canvas.alpha_composite(rs,(ox,oy))

    # Cut a narrow weapon channel through the palm. The weapon remains visible
    # inside the hand, so fingers read as wrapping around it instead of sitting
    # as an orange block on top of the gun.
    a=canvas.getchannel("A")
    ad=ImageDraw.Draw(a)
    if support:
        cy=oy+int(round(rs.height*0.54))
        ad.rounded_rectangle((ox+int(rs.width*0.38),cy-3,ox+int(rs.width*0.92),cy+3),radius=2,fill=0)
    else:
        cx=ox+int(round(rs.width*0.58))
        ad.rounded_rectangle((cx-3,oy+int(rs.height*0.37),cx+3,oy+int(rs.height*0.90)),radius=2,fill=0)
    canvas.putalpha(a)
    return canvas

def derive_bare_hand(glove_img, sex):
    return _detailed_skin_hand(glove_img,sex,False)

def derive_support_hand(dominant, sex):
    # Use the same high-detail authored glove source, not the already-cut dominant.
    return _detailed_skin_hand(glove_src,sex,True)

def derive_tactical_glove(glove_img, sex, support=False):
    """Compact the authored tactical glove into the same weapon-wrap silhouette."""
    src=trim(glove_img).convert("RGBA")
    w,h=src.size
    src=src.crop((max(0,int(w*0.10)),0,w,h))
    # Keep genuine glove texture/material; only compact the open source fingers.
    xscale=0.64 if not support else 0.70
    src=src.resize((max(2,int(round(src.width*xscale))),src.height),Image.Resampling.LANCZOS)
    src=trim(src)
    canvas=Image.new("RGBA",(96,96),(0,0,0,0))
    maxw,maxh=((72,60) if sex=="male" else (68,56))
    sc=min(maxw/max(1,src.width),maxh/max(1,src.height))
    rs=src.resize((max(2,int(round(src.width*sc))),max(2,int(round(src.height*sc)))),Image.Resampling.LANCZOS)
    ox=10; oy=(96-rs.height)//2
    canvas.alpha_composite(rs,(ox,oy))
    a=canvas.getchannel("A"); ad=ImageDraw.Draw(a)
    if support:
        cy=oy+int(round(rs.height*0.54))
        ad.rounded_rectangle((ox+int(rs.width*0.38),cy-3,ox+int(rs.width*0.92),cy+3),radius=2,fill=0)
    else:
        cx=ox+int(round(rs.width*0.58))
        ad.rounded_rectangle((cx-3,oy+int(rs.height*0.37),cx+3,oy+int(rs.height*0.90)),radius=2,fill=0)
    canvas.putalpha(a)
    return canvas


upper_src=load_b64_png(upper_src_path)
fore_src=load_b64_png(fore_src_path)
male_torso_ref=load_b64_png(male_torso_src_path)
female_torso_ref=Image.open(female_torso_src_path).convert("RGBA")
gear_torso_ref=Image.open(gear_torso_src_path).convert("RGBA")
glove_src=Image.open(glove_src_path).convert("RGBA")

def build_reference_rifle():
    """Detailed side-view service rifle matched to approved reference proportions."""
    S=3
    im=Image.new("RGBA",(96*S,30*S),(0,0,0,0))
    d=ImageDraw.Draw(im)
    def poly(points,fill,outline=None):
        pts=[(int(x*S),int(y*S)) for x,y in points]
        d.polygon(pts,fill=fill)
        if outline: d.line(pts+[pts[0]],fill=outline,width=S)
    def rect(box,fill,outline=None,w=1):
        b=tuple(int(v*S) for v in box); d.rectangle(b,fill=fill,outline=outline,width=w*S)
    dark=(25,29,30,255); edge=(17,20,21,255); mid=(48,54,54,255)
    mid2=(61,68,67,255); hi=(101,108,103,255)
    stock=(54,49,42,255); stock_hi=(88,72,55,255)

    # Buttstock and butt pad: tapered, shouldered silhouette rather than a bar.
    poly([(2,13),(7,9),(22,9),(29,12),(29,18),(20,18),(10,22),(3,21)],stock,edge)
    rect((1,13,5,21),(38,38,35,255),edge)
    d.line([(8*S,11*S),(22*S,11*S),(27*S,14*S)],fill=stock_hi,width=S)
    d.line([(8*S,19*S),(19*S,16*S)],fill=(72,60,48,255),width=S)

    # Buffer tube + receiver body.
    rect((25,12,32,15),dark,edge)
    poly([(29,8),(53,8),(57,11),(55,18),(31,18),(28,15)],mid,edge)
    rect((31,7,54,9),dark,edge)
    d.line([(33*S,9*S),(51*S,9*S)],fill=hi,width=S)
    # Ejection/controls.
    rect((43,11,52,15),(33,37,38,255),edge)
    rect((34,11,39,13),mid2,edge)
    d.ellipse((39*S,12*S,41*S,14*S),fill=hi)

    # Low optic / rear sight to give a readable upper silhouette.
    rect((35,4,47,7),dark,edge)
    rect((38,2,45,4),mid2,edge)
    rect((36,7,49,8),(22,26,27,255),edge)

    # Pistol grip and curved magazine.
    poly([(32,17),(40,17),(42,27),(36,29),(31,23)],(48,43,39,255),edge)
    d.line([(35*S,19*S),(39*S,26*S)],fill=stock_hi,width=S)
    poly([(45,18),(54,18),(57,28),(50,29),(46,24)],(31,35,36,255),edge)
    d.line([(48*S,20*S),(54*S,26*S)],fill=mid2,width=S)

    # Handguard: visibly distinct from receiver, ribbed and slimmer.
    poly([(55,10),(79,10),(83,12),(81,17),(55,17)],(43,49,49,255),edge)
    rect((56,9,79,11),mid2,edge)
    for x in (59,64,69,74):
        rect((x,12,x+2,15),(22,26,27,255))
        d.line([(x*S,16*S),((x+2)*S,16*S)],fill=hi,width=S)

    # Gas block/front sight, barrel and muzzle device.
    poly([(78,10),(80,5),(82,10)],dark,edge)
    rect((80,12,92,14),(31,35,36,255),edge)
    rect((90,11,95,15),(20,23,24,255),edge)
    d.line([(82*S,12*S),(91*S,12*S)],fill=hi,width=S)
    return im.resize((96,30),Image.Resampling.LANCZOS)

def build_reference_pistol():
    """Detailed side-view pistol with readable slide, frame, trigger guard and grip."""
    S=4
    im=Image.new("RGBA",(48*S,28*S),(0,0,0,0))
    d=ImageDraw.Draw(im)
    def poly(points,fill,outline=None):
        pts=[(int(x*S),int(y*S)) for x,y in points]; d.polygon(pts,fill=fill)
        if outline: d.line(pts+[pts[0]],fill=outline,width=S)
    def rect(box,fill,outline=None,w=1):
        d.rectangle(tuple(int(v*S) for v in box),fill=fill,outline=outline,width=w*S)
    edge=(18,21,22,255); dark=(31,35,36,255); mid=(55,61,61,255); hi=(108,114,110,255)
    # Slide/barrel.
    poly([(5,5),(40,5),(45,8),(44,12),(6,12),(3,9)],mid,edge)
    d.line([(7*S,6*S),(38*S,6*S)],fill=hi,width=S)
    rect((41,7,47,11),dark,edge)
    rect((8,12,34,16),(42,47,47,255),edge)
    # rear/front sights
    rect((8,2,11,5),dark,edge); rect((38,3,40,5),dark,edge)
    # trigger guard and trigger
    d.ellipse((23*S,14*S,35*S,22*S),outline=(79,85,82,255),width=S)
    d.arc((26*S,15*S,32*S,22*S),260,70,fill=edge,width=S)
    # angled grip
    poly([(10,15),(22,15),(21,27),(12,27),(8,21)],(51,45,40,255),edge)
    for y in (18,21,24):
        d.line([(12*S,y*S),(19*S,(y+1)*S)],fill=(88,69,52,255),width=S)
    return im.resize((48,28),Image.Resampling.LANCZOS)

rifle_arm=build_reference_rifle()
pistol_arm=build_reference_pistol()
rifle_arm_path=root/"weapons"/"SP_PC22_Rifle_ArmCompatible.png"
pistol_arm_path=root/"weapons"/"SP_PC22_Pistol_ArmCompatible.png"
rifle_arm.save(rifle_arm_path)
pistol_arm.save(pistol_arm_path)

# Depth split: stock/buffer behind torso; receiver, grip, handguard, barrel in front.
rifle_stock=Image.new("RGBA",rifle_arm.size,(0,0,0,0))
rifle_front=rifle_arm.copy()
srcp=rifle_arm.load(); sp=rifle_stock.load(); fp=rifle_front.load()
for y in range(rifle_arm.height):
    for x in range(rifle_arm.width):
        if x <= 24 and srcp[x,y][3] > 0:
            sp[x,y]=srcp[x,y]
            fp[x,y]=(0,0,0,0)
rifle_stock_path=root/"weapons"/"SP_PC22_Rifle_Stock_Rear.png"
rifle_front_path=root/"weapons"/"SP_PC22_Rifle_Front.png"
rifle_stock.save(rifle_stock_path)
rifle_front.save(rifle_front_path)

female_upper_runtime=embedded_runtime_image("FEMALE_UPPER_ARM_B64")
female_fore_runtime=embedded_runtime_image("FEMALE_FOREARM_B64")

# Canonical geometry: PC22 has no active shoulders by design (PC08 removed visible arms).
# Therefore shoulder sockets come from the last exact PC03 articulated implementation,
# while weapon/hand sockets and aim range come from the active PC22 runtime/manifest.
specs={
 "male":{
   "rig_id":"MALE_CANONICAL_ARM_SYSTEM",
   "shoulder_rear":[10.0,-9.5],
   "shoulder_front":[9.8,-9.0],
   "upper_arm_length":10.9,
   "forearm_length":10.7,
   "upper_arm_width":6.2,
   "forearm_width":5.1,
   "hand_size":canonical["male"]["hand_size"],
   "dominant_hand_size":[5.6,5.2],
   "support_hand_size":[5.2,4.8],
   "neutral_upper_angle_deg":82.0,
   "neutral_elbow_flex_deg":22.0,
   "source_tint":[78,88,72],
 },
 "female":{
   "rig_id":"FEMALE_CANONICAL_ARM_SYSTEM",
   "shoulder_rear":[9.6,-9.3],
   "shoulder_front":[9.4,-8.9],
   "upper_arm_length":10.6,
   "forearm_length":10.5,
   "upper_arm_width":5.8,
   "forearm_width":4.8,
   "hand_size":canonical["female"]["hand_size"],
   "dominant_hand_size":[5.2,4.9],
   "support_hand_size":[4.9,4.6],
   "neutral_upper_angle_deg":84.0,
   "neutral_elbow_flex_deg":24.0,
   "source_tint":[80,91,75],
 }
}
for sex,s in specs.items():
    s.update({
      "standard_id":"PlayerCharacters_v22",
      "shoulder_source":"Visual-fix-v2: moved to visible PC22 deltoid/outer-torso attachment using approved reference sheets",
      "upper_forearm_length_source":"corrected from prior 9.4+10.5 solver to cover the complete active PC22 support-hand aim envelope without stretch",
      "weapon_socket":[10.5,-6.0],
      "dominant_hand_grip_socket":[9.8,0.8],
      "support_hand_grip_socket":[17.0,-1.0],
      "support_hand_vertical_offset_right":0.0,
      "support_hand_vertical_offset_left":0.0,
      "elbow_bend_constraints_deg":{"min_flex":12.0,"max_flex":155.0},
      "wrist_neutral_position":"derived from neutral upper angle + elbow flex; fixed-length FK",
      "torso_overlap_depth":1.15,
      "joint_overlap_each_end":1.10,
      "arm_sprite_canvas":[64,128],
      "maximum_upward_aim_angle_rad":canonical["shared_motion"]["aim_angle_clamp_rad"],
      "maximum_downward_aim_angle_rad":-canonical["shared_motion"]["aim_angle_clamp_rad"],
      "left_right_mirror_behavior":"right-authored; left runtime mirror",
      "body_scale":"PlayerCharacters_v22 runtime units",
      "layering":{"rear_arm":"behind torso/weapon as appropriate","front_arm":"ahead of torso, behind hands","hands":"weapon-contact layer"},
    })

# Generate texture assets from existing authored modular art, never plain geometric bars.
asset_meta=[]
for sex,s in specs.items():
    female=sex=="female"
    source_upper=female_upper_runtime if female and female_upper_runtime is not None else upper_src
    source_fore=female_fore_runtime if female and female_fore_runtime is not None else fore_src
    source_upper=keep_largest_alpha_component(trim(source_upper))
    source_fore=keep_largest_alpha_component(trim(source_fore))
    # Remove the baked distal hand from the legacy forearm source. The canonical
    # chain owns the hand as a separate wrist child.
    cut=0.80 if female else 0.74
    source_fore=source_fore.crop((0,0,source_fore.width,max(2,int(source_fore.height*cut))))

    # Preserve authored fold/detail structure and stop force-stretching every
    # limb to almost the full 64px canvas width. Runtime screenshots showed that
    # the old 0.90-0.96 width fill produced swollen modular arms.
    u=row_warp(source_upper,1.04 if female else 1.08,0.98 if female else 1.00,0.80 if female else 0.84)
    u=fabric_grade(u,tuple(s["source_tint"]),1.50 if female else 1.46)
    u.putalpha(u.getchannel("A").filter(ImageFilter.GaussianBlur(0.08)))
    u=recanvas_vertical(u,(64,128),1,0.66 if female else 0.73)
    sleeve_ref=female_torso_ref if female else male_torso_ref
    u=anatomical_sleeve(u,tuple(s["source_tint"]),sex,"upper",sleeve_ref)
    u=keep_largest_alpha_component(u)
    u=add_joint_caps(u,tuple(s["source_tint"]),0.34 if female else 0.38,0.38 if female else 0.42,4)

    f=row_warp(source_fore,1.02 if female else 1.05,0.91 if female else 0.94,0.66 if female else 0.70)
    f=fabric_grade(f,tuple(s["source_tint"]),1.55 if female else 1.50)
    # Darken only the distal cuff while retaining the original fold/edge detail.
    f=f.convert("RGBA"); fp=f.load()
    for y in range(f.height):
        t=y/max(1,f.height-1)
        if t < 0.82:
            continue
        for x in range(f.width):
            r,g,b,a=fp[x,y]
            if a<4: continue
            fp[x,y]=(int(r*0.74),int(g*0.74),int(b*0.74),a)
    f.putalpha(f.getchannel("A").filter(ImageFilter.GaussianBlur(0.07)))
    f=recanvas_vertical(f,(64,128),1,0.55 if female else 0.62)
    f=anatomical_sleeve(f,tuple(s["source_tint"]),sex,"forearm",sleeve_ref)
    f=keep_largest_alpha_component(f)
    f=add_joint_caps(f,tuple(s["source_tint"]),0.42 if female else 0.46,0.21 if female else 0.24,4)

    sex_dir=root/sex
    up_name=f"SP_PC22_{sex.title()}_UpperArm_Right.png"
    fo_name=f"SP_PC22_{sex.title()}_Forearm_Right.png"
    u.save(sex_dir/up_name)
    f.save(sex_dir/fo_name)

    # Proximal deltoid bridge used in armed poses after torso draw. The main
    # upper arm remains depth-layered behind the torso, while this small
    # textured cap reconnects the visible limb to the anatomical shoulder.
    ub=trim(u)
    cap_h=max(4,int(round(ub.height*0.24)))
    cap_src=ub.crop((0,0,ub.width,cap_h))
    cap=Image.new("RGBA",(64,64),(0,0,0,0))
    cap_trim=trim(cap_src)
    sc=min(48/max(1,cap_trim.width),36/max(1,cap_trim.height))
    cap_rs=cap_trim.resize((max(1,int(round(cap_trim.width*sc))),max(1,int(round(cap_trim.height*sc)))),Image.Resampling.LANCZOS)
    cap.alpha_composite(cap_rs,((64-cap_rs.width)//2,(64-cap_rs.height)//2))
    cap_name=f"SP_PC22_{sex.title()}_ShoulderCap_Right.png"
    cap.save(sex_dir/cap_name)

    # Prefer the already-generated PC22 unified hand base so arm and existing equipment remain compatible.
    hand=derive_bare_hand(glove_src,sex)
    support_hand=derive_support_hand(hand,sex)
    glove_dom=derive_tactical_glove(glove_src,sex,False)
    glove_sup=derive_tactical_glove(glove_src,sex,True)
    hand.save(sex_dir/f"SP_PC22_{sex.title()}_Hand_Dominant_Right.png")
    support_hand.save(sex_dir/f"SP_PC22_{sex.title()}_Hand_Support_Right.png")

    # Hybrid renderer V3 assets: tight bounds + explicit local pivots.
    v3_sex=v3_root/sex
    v3_upper,v3_upper_parent,v3_upper_child=make_v3_pivoted_segment(u)
    v3_fore,v3_fore_parent,v3_fore_child=make_v3_pivoted_segment(f)
    v3_gear_upper=tactical_sleeve(v3_upper,sex,"upper")
    v3_gear_fore=tactical_sleeve(v3_fore,sex,"forearm")
    v3_dom,v3_dom_pivot=make_v3_pivoted_hand(hand)
    v3_sup,v3_sup_pivot=make_v3_pivoted_hand(support_hand)
    v3_glove_dom,v3_glove_dom_pivot=make_v3_pivoted_hand(glove_dom)
    v3_glove_sup,v3_glove_sup_pivot=make_v3_pivoted_hand(glove_sup)
    v3_cap,v3_cap_pivot=make_v3_shoulder_cap(v3_upper,sex)

    v3_names={
      "upper_arm":f"SP_PC22_{sex.title()}_UpperArm_V3.png",
      "forearm":f"SP_PC22_{sex.title()}_Forearm_V3.png",
      "gear_upper_arm":f"SP_PC22_{sex.title()}_UpperArm_Gear_V3.png",
      "gear_forearm":f"SP_PC22_{sex.title()}_Forearm_Gear_V3.png",
      "hand_dominant":f"SP_PC22_{sex.title()}_Hand_Dominant_V3.png",
      "hand_support":f"SP_PC22_{sex.title()}_Hand_Support_V3.png",
      "glove_dominant":f"SP_PC22_{sex.title()}_Glove_Dominant_V3.png",
      "glove_support":f"SP_PC22_{sex.title()}_Glove_Support_V3.png",
      "shoulder_cap":f"SP_PC22_{sex.title()}_ShoulderCap_V3.png",
    }
    for key,img in (
      ("upper_arm",v3_upper),("forearm",v3_fore),
      ("gear_upper_arm",v3_gear_upper),("gear_forearm",v3_gear_fore),
      ("hand_dominant",v3_dom),("hand_support",v3_sup),
      ("glove_dominant",v3_glove_dom),("glove_support",v3_glove_sup),
      ("shoulder_cap",v3_cap),
    ):
        img.save(v3_sex/v3_names[key])

    v3_meta={
      "sex":sex,
      "rig_id":s["rig_id"],
      "renderer":"hybrid_pivoted_sprite_v3",
      "upper_arm":{
        "filename":str((v3_sex/v3_names["upper_arm"]).relative_to(repo)),
        "canvas_size":list(v3_upper.size),"parent_pivot_px":v3_upper_parent,
        "child_pivot_px":v3_upper_child,"canonical_length":s["upper_arm_length"],
      },
      "forearm":{
        "filename":str((v3_sex/v3_names["forearm"]).relative_to(repo)),
        "canvas_size":list(v3_fore.size),"parent_pivot_px":v3_fore_parent,
        "child_pivot_px":v3_fore_child,"canonical_length":s["forearm_length"],
      },
      "hand_dominant":{
        "filename":str((v3_sex/v3_names["hand_dominant"]).relative_to(repo)),
        "canvas_size":list(v3_dom.size),"wrist_pivot_px":v3_dom_pivot,
      },
      "hand_support":{
        "filename":str((v3_sex/v3_names["hand_support"]).relative_to(repo)),
        "canvas_size":list(v3_sup.size),"wrist_pivot_px":v3_sup_pivot,
      },
      "shoulder_cap":{
        "filename":str((v3_sex/v3_names["shoulder_cap"]).relative_to(repo)),
        "canvas_size":list(v3_cap.size),"shoulder_pivot_px":v3_cap_pivot,
      },
      "policy":{
        "anisotropic_scaling":False,
        "segment_scale":"uniform_from_canonical_length_and_parent_child_pixel_distance",
        "left_behavior":"mirror_about_parent_pivot_then rotate",
      }
    }
    (meta/f"hybrid_v3_{sex}_assets.json").write_text(json.dumps(v3_meta,indent=2),encoding="utf-8")

    for seg,fn,img,parent,child,length in (
      ("upper_arm",up_name,u,"shoulder","elbow",s["upper_arm_length"]),
      ("shoulder_cap",cap_name,cap,"shoulder","upper_arm",0.0),
      ("forearm",fo_name,f,"elbow","wrist",s["forearm_length"]),
      ("hand_dominant",f"SP_PC22_{sex.title()}_Hand_Dominant_Right.png",hand,"wrist","dominant_grip",0.0),
      ("hand_support",f"SP_PC22_{sex.title()}_Hand_Support_Right.png",support_hand,"wrist","support_grip",0.0),
    ):
        bb=img.getchannel("A").getbbox()
        asset_meta.append({
          "filename":str((sex_dir/fn).relative_to(repo)),
          "sex":sex,"segment":seg,"canvas_size":list(img.size),
          "pivot":"segment parent joint / centered draw helper",
          "joint_parent":parent,"joint_child":child,
          "canonical_length":length,
          "visual_overlap_parent":s["joint_overlap_each_end"] if length else 1.0,
          "visual_overlap_child":s["joint_overlap_each_end"] if length else 1.0,
          "compatible_rig":s["rig_id"],
          "mirroring_supported":True,"approval_state":"candidate",
          "alpha_bbox":list(bb) if bb else None,
          "sha256":hashlib.sha256((sex_dir/fn).read_bytes()).hexdigest(),
        })

# Hybrid V3 keeps the detailed V2 weapon art but stores it separately so
# rendering/pivot changes remain isolated from the known-good V2 candidate.
v3_rifle_path=v3_root/"weapons"/"SP_PC22_Rifle_V3.png"
v3_pistol_path=v3_root/"weapons"/"SP_PC22_Pistol_V3.png"
v3_rifle_stock_path=v3_root/"weapons"/"SP_PC22_Rifle_Stock_V3.png"
v3_rifle_front_path=v3_root/"weapons"/"SP_PC22_Rifle_Front_V3.png"
rifle_arm.save(v3_rifle_path)
pistol_arm.save(v3_pistol_path)
rifle_stock.save(v3_rifle_stock_path)
rifle_front.save(v3_rifle_front_path)
v3_weapon_meta={
  "renderer":"hybrid_pivoted_sprite_v3",
  "rifle":{
    "filename":str(v3_rifle_path.relative_to(repo)),
    "stock_filename":str(v3_rifle_stock_path.relative_to(repo)),
    "front_filename":str(v3_rifle_front_path.relative_to(repo)),
    "canvas_size":list(rifle_arm.size),
    "weapon_origin_px":[29.0,13.0],
    "butt_contact_px":[4.0,16.0],
    "dominant_grip_px":[36.0,18.0],
    "support_grip_px":[58.0,13.0],
    "muzzle_px":[94.0,13.0]
  },
  "pistol":{
    "filename":str(v3_pistol_path.relative_to(repo)),
    "canvas_size":list(pistol_arm.size),
    "weapon_origin_px":[14.0,16.0],
    "dominant_grip_px":[15.0,18.0],
    "muzzle_px":[46.0,9.0]
  }
}
(meta/"hybrid_v3_weapon_assets.json").write_text(json.dumps(v3_weapon_meta,indent=2),encoding="utf-8")

# Store exact machine-readable specs in requested core locations and arm metadata.
for sex,s in specs.items():
    core_spec=repo/f"assets/authored2d/unified_character/core/{sex}/arm_spec.json"
    core_spec.write_text(json.dumps(s,indent=2),encoding="utf-8")
asset_meta.append({
  "filename":str(pistol_arm_path.relative_to(repo)),
  "sex":"shared","segment":"weapon_pistol_arm_compatible",
  "canvas_size":list(pistol_arm.size),
  "pivot":"dominant grip socket",
  "joint_parent":"dominant_grip","joint_child":"muzzle",
  "canonical_length":0.0,
  "visual_overlap_parent":0.0,"visual_overlap_child":0.0,
  "compatible_rig":"MALE_CANONICAL_ARM_SYSTEM,FEMALE_CANONICAL_ARM_SYSTEM",
  "mirroring_supported":True,"approval_state":"candidate_visual_fix_v2",
  "sha256":hashlib.sha256(pistol_arm_path.read_bytes()).hexdigest(),
  "note":"Reference-driven pistol with readable slide/frame/grip mass"
})
asset_meta.append({
  "filename":str(rifle_arm_path.relative_to(repo)),
  "sex":"shared","segment":"weapon_rifle_arm_compatible",
  "canvas_size":list(rifle_arm.size),
  "pivot":"unchanged canonical PC22 weapon pivot",
  "joint_parent":"dominant_grip","joint_child":"support_grip",
  "canonical_length":0.0,
  "visual_overlap_parent":0.0,"visual_overlap_child":0.0,
  "compatible_rig":"MALE_CANONICAL_ARM_SYSTEM,FEMALE_CANONICAL_ARM_SYSTEM",
  "mirroring_supported":True,"approval_state":"candidate",
  "sha256":hashlib.sha256(rifle_arm_path.read_bytes()).hexdigest(),
  "note":"Only upper butt-stock pixels shifted +4 source px; body/grip/barrel geometry unchanged"
})
for wp,seg,note in (
  (rifle_stock_path,"weapon_rifle_stock_rear","Upper butt-stock only; render behind torso"),
  (rifle_front_path,"weapon_rifle_front","Receiver/barrel/grip only; render in front"),
):
    asset_meta.append({
      "filename":str(wp.relative_to(repo)),
      "sex":"shared","segment":seg,"canvas_size":list(rifle_arm.size),
      "pivot":"same canonical PC22 rifle center/pivot",
      "joint_parent":"weapon","joint_child":"weapon",
      "canonical_length":0.0,
      "visual_overlap_parent":0.0,"visual_overlap_child":0.0,
      "compatible_rig":"MALE_CANONICAL_ARM_SYSTEM,FEMALE_CANONICAL_ARM_SYSTEM",
      "mirroring_supported":True,"approval_state":"candidate",
      "sha256":hashlib.sha256(wp.read_bytes()).hexdigest(),
      "note":note,
    })
(meta/"arm_assets.json").write_text(json.dumps({"assets":asset_meta},indent=2),encoding="utf-8")

roles=["player","trader","medic","mechanic","guard","bandit","civilian"]
inheritance={
  "standard_id":"PlayerCharacters_v22",
  "policy":{
    "npc_specific_skeletons":False,
    "role_specialization_changes_geometry":False,
    "left_is_runtime_mirror":True,
    "role_specialization":["sleeve_overlay","glove_overlay","armor_overlay","equipment","weapon","held_tool"]
  },
  "male":{"rig_id":"MALE_CANONICAL_ARM_SYSTEM","users":[f"{r}_male" for r in roles]},
  "female":{"rig_id":"FEMALE_CANONICAL_ARM_SYSTEM","users":[f"{r}_female" for r in roles]},
}
(meta/"rig_inheritance.json").write_text(json.dumps(inheritance,indent=2),encoding="utf-8")

# --------------------------- deterministic IK QA ---------------------------
def rot(v,a):
    x,y=v
    return (x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a))

def add(a,b): return (a[0]+b[0],a[1]+b[1])
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def mul(a,k): return (a[0]*k,a[1]*k)
def length(v): return math.hypot(v[0],v[1])

def mirror(v,sign): return (v[0]*sign,v[1])

def pose_point(v,a,sign):
    # Mirror authored right-space before rotation. Equivalent to current two-side intent.
    x,y=v
    x*=sign
    return rot((x,y),a*sign)

def solve_two_bone(shoulder,wrist,L1,L2,prev=None):
    dvec=sub(wrist,shoulder); d=length(dvec)
    lo=abs(L1-L2)+1e-6; hi=L1+L2-1e-6
    if d<lo or d>hi:
        return None,{"reachable":False,"distance":d,"range":[lo,hi]}
    ux,uy=dvec[0]/d,dvec[1]/d
    along=(L1*L1-L2*L2+d*d)/(2*d)
    h=math.sqrt(max(0,L1*L1-along*along))
    perp=(-uy,ux)
    c1=add(add(shoulder,mul((ux,uy),along)),mul(perp,h))
    c2=add(add(shoulder,mul((ux,uy),along)),mul(perp,-h))
    candidates=(c1,c2)
    # Initial anatomical preference: screen-down elbow. Continuity dominates after first frame.
    if prev is None:
        elbow=max(candidates,key=lambda p:(p[1],-abs(p[0]-shoulder[0])))
    else:
        # Preserve the previously selected IK branch. A visual "screen-down"
        # penalty can overpower continuity near vertical aim and flip the elbow
        # across the body, so after initialization continuity is authoritative.
        elbow=min(candidates,key=lambda p:length(sub(p,prev)))
    return elbow,{"reachable":True,"distance":d,"range":[lo,hi]}

def flex_deg(L1,L2,d):
    c=(L1*L1+L2*L2-d*d)/(2*L1*L2)
    c=max(-1,min(1,c))
    internal=math.degrees(math.acos(c))
    return 180.0-internal

samples=[]
failures=[]
for sex,s in specs.items():
    L1,L2=s["upper_arm_length"],s["forearm_length"]
    clamp=canonical["shared_motion"]["aim_angle_clamp_rad"]
    for facing in (1,-1):
        for chain in ("dominant","support"):
            prev=None
            angles=[-clamp+i*(2*clamp/120.0) for i in range(121)]
            # Continuous return sweep catches solution discontinuity.
            angles += list(reversed(angles[:-1]))
            for idx,a in enumerate(angles):
                shoulder=add((0,0),mirror(tuple(s["shoulder_rear" if chain=="dominant" else "shoulder_front"]),facing))
                pivot=add((0,0),mirror(tuple(s["weapon_socket"]),facing))
                grip=tuple(s["dominant_hand_grip_socket" if chain=="dominant" else "support_hand_grip_socket"])
                wrist=add(pivot,pose_point(grip,a,facing))
                if chain=="support":
                    off=s["support_hand_vertical_offset_right"] if facing==1 else s["support_hand_vertical_offset_left"]
                    wrist=add(wrist,pose_point((0,off),a,facing))
                elbow,diag=solve_two_bone(shoulder,wrist,L1,L2,prev)
                if elbow is None:
                    failures.append({"sex":sex,"facing":facing,"chain":chain,"angle":a,"reason":"unreachable","diag":diag})
                    continue
                ua=length(sub(elbow,shoulder)); fa=length(sub(wrist,elbow))
                flex=flex_deg(L1,L2,length(sub(wrist,shoulder)))
                disp=0.0 if prev is None else length(sub(elbow,prev))
                samples.append({"sex":sex,"facing":facing,"chain":chain,"angle":a,
                                "upper":ua,"fore":fa,"flex":flex,"elbow_displacement":disp})
                if abs(ua-L1)>1e-5 or abs(fa-L2)>1e-5:
                    failures.append({"sex":sex,"chain":chain,"reason":"length_drift","upper":ua,"fore":fa})
                if flex<s["elbow_bend_constraints_deg"]["min_flex"]-0.05 or flex>s["elbow_bend_constraints_deg"]["max_flex"]+0.05:
                    failures.append({"sex":sex,"chain":chain,"reason":"flex_constraint","flex":flex,"angle":a})
                # Frame spacing is ~1.47 degrees. Large jumps indicate IK branch flips.
                if disp>2.2:
                    failures.append({"sex":sex,"chain":chain,"reason":"ik_discontinuity","disp":disp,"angle":a})
                prev=elbow

summary={"pass":not failures,"failure_count":len(failures),"samples":len(samples)}
for sex in specs:
    ss=[x for x in samples if x["sex"]==sex]
    summary[sex]={
      "upper_length_range":[min(x["upper"] for x in ss),max(x["upper"] for x in ss)],
      "forearm_length_range":[min(x["fore"] for x in ss),max(x["fore"] for x in ss)],
      "flex_range_deg":[min(x["flex"] for x in ss),max(x["flex"] for x in ss)],
      "max_frame_elbow_displacement":max(x["elbow_displacement"] for x in ss),
    }
(qa/"numerical_qa.json").write_text(json.dumps({"summary":summary,"failures":failures[:100]},indent=2),encoding="utf-8")
if failures:
    raise SystemExit("Canonical arm numerical QA failed: "+json.dumps(summary))

print("PC22_CANONICAL_ARM_ASSETS_OK")
print(json.dumps(summary,sort_keys=True))
