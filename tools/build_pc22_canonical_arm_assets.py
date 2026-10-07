#!/usr/bin/env python3
"""Build PlayerCharacters_v22 canonical articulated arm assets and deterministic QA."""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
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
glove_src_path=repo/"art_source/gear/d2d40/glove.webp"
rifle_src_path=repo/"assets/authored2d/gear/rifle.png"
if not upper_src_path.is_file() or not fore_src_path.is_file() or not glove_src_path.is_file() or not rifle_src_path.is_file():
    raise SystemExit("Authored modular arm/hand/weapon sources missing")

root=repo/"assets/authored2d/unified_character/arms"
qa=root/"qa"
meta=root/"metadata"
for d in (root/"male",root/"female",root/"weapons",qa,meta,
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
            delta=int(max(-24,min(24,(lum-112.0)*0.15)))
            gnoise=((x*17+y*11)%5)-2 if grain else 0
            dst[x,y]=(max(0,min(255,base_rgb[0]+delta+gnoise)),
                      max(0,min(255,base_rgb[1]+delta+gnoise)),
                      max(0,min(255,base_rgb[2]+delta+gnoise)),a)
    return out

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

def derive_bare_hand(glove_img, sex):
    # Convert the authored hand/glove silhouette into a compact weapon-grip hand.
    # The old candidate preserved long straight fingers and looked like a pointing
    # hand at the grip. Compress/fold the distal finger region toward the palm while
    # retaining authored pixel texture and skin shading.
    g=glove_img.convert("RGBA")
    bb=g.getchannel("A").getbbox()
    if bb is None:
        raise SystemExit("Empty glove source")
    g=g.crop(bb)
    x0=max(0,int(g.width*0.28))  # remove cuff
    g=g.crop((x0,0,g.width,g.height))
    base=(196,132,96) if sex=="male" else (202,140,105)
    g=recolor(g,base,1)
    g=trim(g)

    split=max(2,int(g.width*0.56))
    palm=g.crop((0,0,split,g.height))
    fingers=g.crop((split,0,g.width,g.height))
    fw=max(2,int(round(fingers.width*0.46)))
    fh=max(2,int(round(fingers.height*0.82)))
    fingers=fingers.resize((fw,fh),Image.Resampling.LANCZOS)

    folded=Image.new("RGBA",(split+fw+2,g.height),(0,0,0,0))
    folded.alpha_composite(palm,(0,0))
    # Fold the fingers slightly downward into the palm/grip instead of extending
    # straight along the barrel.
    fy=max(0,int(round((g.height-fh)*0.62)))
    folded.alpha_composite(fingers,(max(0,split-4),fy))
    folded=trim(folded)

    canvas=Image.new("RGBA",(96,96),(0,0,0,0))
    max_w=58 if sex=="male" else 54
    max_h=50 if sex=="male" else 47
    sc=min(max_w/folded.width,max_h/folded.height)
    rs=folded.resize((max(1,int(round(folded.width*sc))),max(1,int(round(folded.height*sc)))),Image.Resampling.LANCZOS)
    canvas.alpha_composite(rs,(9,(96-rs.height)//2))
    return canvas

def derive_support_hand(dominant, sex):
    # Same compact grip family, slightly smaller for the fore-end/handguard.
    d=trim(dominant)
    target=(52,46) if sex=="male" else (48,43)
    sc=min(target[0]/d.width,target[1]/d.height)
    rs=d.resize((max(1,int(round(d.width*sc))),max(1,int(round(d.height*sc)))),Image.Resampling.LANCZOS)
    out=Image.new("RGBA",(96,96),(0,0,0,0))
    out.alpha_composite(rs,(9,(96-rs.height)//2))
    return out

upper_src=load_b64_png(upper_src_path)
fore_src=load_b64_png(fore_src_path)
glove_src=Image.open(glove_src_path).convert("RGBA")
rifle_src=Image.open(rifle_src_path).convert("RGBA")

# Preserve the canonical rifle body/grip geometry, but move only the upper
# butt-stock pixels forward by 4 source pixels. In the original 44x14 asset,
# the stock protruded behind the shoulder socket and appeared as a brown
# triangular chest intrusion at magnified runtime QA. Grip/barrel pixels stay
# exactly where they are, so hand/socket geometry is unchanged.
rifle_arm=rifle_src.copy()
rp=rifle_arm.load()
moved=[]
for y in range(min(5,rifle_arm.height)):
    for x in range(rifle_arm.width):
        if rp[x,y][3] > 0:
            moved.append((x,y,rp[x,y]))
            rp[x,y]=(0,0,0,0)
for x,y,pix in moved:
    nx=min(rifle_arm.width-1,x+4)
    rp[nx,y]=pix
rifle_arm_path=root/"weapons"/"SP_PC22_Rifle_ArmCompatible.png"
rifle_arm.save(rifle_arm_path)

female_upper_runtime=embedded_runtime_image("FEMALE_UPPER_ARM_B64")
female_fore_runtime=embedded_runtime_image("FEMALE_FOREARM_B64")

# Canonical geometry: PC22 has no active shoulders by design (PC08 removed visible arms).
# Therefore shoulder sockets come from the last exact PC03 articulated implementation,
# while weapon/hand sockets and aim range come from the active PC22 runtime/manifest.
specs={
 "male":{
   "rig_id":"MALE_CANONICAL_ARM_SYSTEM",
   "shoulder_rear":[6.2,-8.5],
   "shoulder_front":[3.8,-5.3],
   "upper_arm_length":10.9,
   "forearm_length":10.7,
   "upper_arm_width":7.3,
   "forearm_width":6.5,
   "hand_size":canonical["male"]["hand_size"],
   "dominant_hand_size":[7.6,7.0],
   "support_hand_size":[6.6,5.8],
   "neutral_upper_angle_deg":82.0,
   "neutral_elbow_flex_deg":22.0,
   "source_tint":[78,88,72],
 },
 "female":{
   "rig_id":"FEMALE_CANONICAL_ARM_SYSTEM",
   "shoulder_rear":[5.3,-8.0],
   "shoulder_front":[3.0,-5.0],
   "upper_arm_length":10.6,
   "forearm_length":10.5,
   "upper_arm_width":6.2,
   "forearm_width":5.6,
   "hand_size":canonical["female"]["hand_size"],
   "dominant_hand_size":[7.0,6.5],
   "support_hand_size":[6.1,5.4],
   "neutral_upper_angle_deg":84.0,
   "neutral_elbow_flex_deg":24.0,
   "source_tint":[80,91,75],
 }
}
for sex,s in specs.items():
    s.update({
      "standard_id":"PlayerCharacters_v22",
      "shoulder_source":"PC03 exact articulated socket retained as candidate; active PC22 intentionally has no visible shoulder joint",
      "upper_forearm_length_source":"corrected from prior 9.4+10.5 solver to cover the complete active PC22 support-hand aim envelope without stretch",
      "weapon_socket":canonical["weapon_socket"]["pivot_from_base"],
      "dominant_hand_grip_socket":canonical["weapon_socket"]["dominant_hand_from_pivot"],
      "support_hand_grip_socket":canonical["weapon_socket"]["support_hand_from_pivot"],
      "support_hand_vertical_offset_right":1.8,
      "support_hand_vertical_offset_left":2.1,
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

    u=row_warp(source_upper,0.94 if female else 1.02,0.90 if female else 0.98,0.84 if female else 0.92)
    u=recolor(u,tuple(s["source_tint"]),2)
    u.putalpha(u.getchannel("A").filter(ImageFilter.GaussianBlur(0.20)))
    u=recanvas_vertical(u,(64,128),1,0.72 if female else 0.84)
    u=keep_largest_alpha_component(u)
    u=add_joint_caps(u,tuple(s["source_tint"]),0.56 if female else 0.60,0.44 if female else 0.48,11)

    f=row_warp(source_fore,0.94 if female else 0.98,0.90 if female else 0.94,0.82 if female else 0.88)
    # Convert the full authored forearm/hand source into a sleeve-to-wrist segment.
    # Distal rows are kept but recolored as a darker wrist cuff so the separate hand overlaps it.
    f=f.convert("RGBA"); fp=f.load()
    for y in range(f.height):
        t=y/max(1,f.height-1)
        for x in range(f.width):
            r,g,b,a=fp[x,y]
            if a<4: continue
            lum=(r+g+b)/3.0
            base=tuple(s["source_tint"]) if t<0.80 else (70,76,66)
            d=int(max(-18,min(18,(lum-110)*0.12)))
            fp[x,y]=(max(0,min(255,base[0]+d)),max(0,min(255,base[1]+d)),max(0,min(255,base[2]+d)),a)
    f.putalpha(f.getchannel("A").filter(ImageFilter.GaussianBlur(0.18)))
    f=recanvas_vertical(f,(64,128),1,0.66 if female else 0.82)
    f=keep_largest_alpha_component(f)
    f=add_joint_caps(f,tuple(s["source_tint"]),0.48 if female else 0.52,0.31 if female else 0.34,10)

    sex_dir=root/sex
    up_name=f"SP_PC22_{sex.title()}_UpperArm_Right.png"
    fo_name=f"SP_PC22_{sex.title()}_Forearm_Right.png"
    u.save(sex_dir/up_name)
    f.save(sex_dir/fo_name)

    # Prefer the already-generated PC22 unified hand base so arm and existing equipment remain compatible.
    hand=derive_bare_hand(glove_src,sex)
    support_hand=derive_support_hand(hand,sex)
    hand.save(sex_dir/f"SP_PC22_{sex.title()}_Hand_Dominant_Right.png")
    support_hand.save(sex_dir/f"SP_PC22_{sex.title()}_Hand_Support_Right.png")

    for seg,fn,img,parent,child,length in (
      ("upper_arm",up_name,u,"shoulder","elbow",s["upper_arm_length"]),
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

# Store exact machine-readable specs in requested core locations and arm metadata.
for sex,s in specs.items():
    core_spec=repo/f"assets/authored2d/unified_character/core/{sex}/arm_spec.json"
    core_spec.write_text(json.dumps(s,indent=2),encoding="utf-8")
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
        def score(p):
            continuity=length(sub(p,prev))
            upward_penalty=max(0.0,(shoulder[1]-p[1])-1.0)*3.0
            return continuity+upward_penalty
        elbow=min(candidates,key=score)
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
