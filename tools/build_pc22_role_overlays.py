#!/usr/bin/env python3
"""Generate role clothing overlays that inherit PC22 canonical arm geometry."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,sys

repo=Path(sys.argv[1] if len(sys.argv)>1 else ".")
base=repo/"assets/authored2d/unified_character"
arms=base/"arms"
roles_root=base/"roles"
qa=arms/"qa"
meta=arms/"metadata"
qa.mkdir(parents=True,exist_ok=True); meta.mkdir(parents=True,exist_ok=True)

# Deterministic rebuild: failed/older candidate layouts must never accumulate.
import shutil
for stale in (arms/"sleeves", arms/"gloves", roles_root):
    if stale.exists():
        shutil.rmtree(stale)

roles={
 "trader":{"cloth":(61,63,70),"accent":(119,84,58),"glove":(53,49,46)},
 "medic":{"cloth":(184,190,184),"accent":(67,111,121),"glove":(79,91,91)},
 "mechanic":{"cloth":(63,76,80),"accent":(139,91,47),"glove":(62,57,51)},
 "guard":{"cloth":(72,82,61),"accent":(45,53,42),"glove":(49,52,45)},
 "bandit":{"cloth":(66,56,52),"accent":(116,58,49),"glove":(50,43,40)},
 "civilian":{"cloth":(86,91,96),"accent":(62,84,105),"glove":(67,67,68)},
}

def colorize(src,base_rgb,accent_rgb=None,accent_zone=None):
    src=src.convert("RGBA")
    out=Image.new("RGBA",src.size,(0,0,0,0))
    sp=src.load(); op=out.load(); w,h=src.size
    for y in range(h):
        for x in range(w):
            r,g,b,a=sp[x,y]
            if a==0: continue
            lum=(r+g+b)/3.0
            d=max(-34,min(34,int((lum-112.0)*0.22)))
            rgb=base_rgb
            if accent_rgb and accent_zone and accent_zone(x,y,w,h):
                rgb=accent_rgb
            grain=((x*13+y*17)%7)-3
            op[x,y]=(max(0,min(255,rgb[0]+d+grain)),
                     max(0,min(255,rgb[1]+d+grain)),
                     max(0,min(255,rgb[2]+d+grain)),a)
    return out

def sleeve_asset(src,role,segment):
    p=roles[role]
    if segment=="upper":
        zone=lambda x,y,w,h: y>h*0.72 and ((x+y)//4)%2==0
    else:
        zone=lambda x,y,w,h: y>h*0.80
    return colorize(src,p["cloth"],p["accent"],zone)

def glove_asset(src,role):
    p=roles[role]
    return colorize(src,p["glove"],p["accent"],lambda x,y,w,h: x<w*0.26)

def torso_asset(src,role):
    p=roles[role]
    return colorize(src,p["cloth"],p["accent"],lambda x,y,w,h: (y>h*0.72) or (role=="medic" and x>w*0.58 and y<h*0.60))

records=[]
for role in roles:
    for sex in ("male","female"):
        sex_arm=arms/sex
        upper=Image.open(sex_arm/f"SP_PC22_{sex.title()}_UpperArm_Right.png").convert("RGBA")
        fore=Image.open(sex_arm/f"SP_PC22_{sex.title()}_Forearm_Right.png").convert("RGBA")
        hand_dom=Image.open(sex_arm/f"SP_PC22_{sex.title()}_Hand_Dominant_Right.png").convert("RGBA")
        hand_sup=Image.open(sex_arm/f"SP_PC22_{sex.title()}_Hand_Support_Right.png").convert("RGBA")
        torso=Image.open(base/f"core/{sex}/torso_base.png").convert("RGBA")

        outdir=arms/"sleeves"/role/sex; outdir.mkdir(parents=True,exist_ok=True)
        gdir=arms/"gloves"/role/sex; gdir.mkdir(parents=True,exist_ok=True)
        tdir=roles_root/role/sex; tdir.mkdir(parents=True,exist_ok=True)

        su=sleeve_asset(upper,role,"upper")
        sf=sleeve_asset(fore,role,"fore")
        sg_dom=glove_asset(hand_dom,role)
        sg_sup=glove_asset(hand_sup,role)
        st=torso_asset(torso,role)

        files={
          "upper_arm":outdir/"upper_arm.png",
          "forearm":outdir/"forearm.png",
          "glove_dominant":gdir/"glove_dominant.png",
          "glove_support":gdir/"glove_support.png",
          "torso":tdir/"torso.png",
        }
        for k,img in (("upper_arm",su),("forearm",sf),("glove_dominant",sg_dom),("glove_support",sg_sup),("torso",st)):
            img.save(files[k])

        spec=json.loads((base/f"core/{sex}/arm_spec.json").read_text(encoding="utf-8"))
        for k,img,parent,child in (
          ("upper_arm",su,"shoulder","elbow"),
          ("forearm",sf,"elbow","wrist"),
          ("glove_dominant",sg_dom,"wrist","dominant_hand"),
          ("glove_support",sg_sup,"wrist","support_hand"),
          ("torso",st,"body","shoulder_interface"),
        ):
            src_ref={"upper_arm":upper,"forearm":fore,"glove_dominant":hand_dom,"glove_support":hand_sup,"torso":torso}[k]
            if img.size!=src_ref.size:
                raise SystemExit(f"{role}/{sex}/{k}: canvas mismatch")
            if img.getchannel("A").tobytes()!=src_ref.getchannel("A").tobytes():
                raise SystemExit(f"{role}/{sex}/{k}: alpha/pivot envelope changed")
            records.append({
              "role":role,"sex":sex,"asset":k,
              "filename":str(files[k].relative_to(repo)),
              "canvas_size":list(img.size),
              "alpha_bbox":list(img.getchannel("A").getbbox() or (0,0,0,0)),
              "joint_parent":parent,"joint_child":child,
              "compatible_rig":spec["rig_id"],
              "geometry_override":False,
              "mirroring_supported":True,
              "approval_state":"candidate",
              "sha256":hashlib.sha256(files[k].read_bytes()).hexdigest(),
            })

# Hard-count the requested 24 sleeve segments.
sleeves=[r for r in records if r["asset"] in ("upper_arm","forearm")]
if len(sleeves)!=24:
    raise SystemExit(f"Expected 24 sleeve assets, got {len(sleeves)}")

(meta/"role_overlays.json").write_text(json.dumps({
  "standard_id":"PlayerCharacters_v22",
  "skeleton_policy":"roles cannot override canonical arm geometry",
  "sleeve_asset_count":len(sleeves),
  "role_glove_count":len([r for r in records if r["asset"] in ("glove_dominant","glove_support")]),
  "role_torso_count":len([r for r in records if r["asset"]=="torso"]),
  "assets":records
},indent=2),encoding="utf-8")

# Large deterministic QA sheet: role torso, upper sleeve, fore sleeve, glove for both sexes.
cellw,cellh=300,360
sheet=Image.new("RGBA",(6*cellw,2*cellh),(18,22,23,255))
for row,sex in enumerate(("male","female")):
    for col,role in enumerate(roles):
        canvas=Image.new("RGBA",(cellw,cellh),(20,25,26,255))
        d=ImageDraw.Draw(canvas)
        t=Image.open(roles_root/role/sex/"torso.png").convert("RGBA")
        u=Image.open(arms/"sleeves"/role/sex/"upper_arm.png").convert("RGBA")
        f=Image.open(arms/"sleeves"/role/sex/"forearm.png").convert("RGBA")
        g=Image.open(arms/"gloves"/role/sex/"glove_dominant.png").convert("RGBA")
        def fit(im,maxw,maxh):
            bb=im.getchannel("A").getbbox()
            if bb: im=im.crop(bb)
            sc=min(maxw/im.width,maxh/im.height)
            return im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.Resampling.LANCZOS)
        tt=fit(t,120,180); uu=fit(u,70,145); ff=fit(f,70,145); gg=fit(g,80,70)
        canvas.alpha_composite(tt,(20,95))
        canvas.alpha_composite(uu,(155,78))
        canvas.alpha_composite(ff,(215,78))
        canvas.alpha_composite(gg,(175,240))
        d.text((12,12),f"{role.upper()} — {sex.upper()}",fill=(235,235,228,255))
        d.text((12,330),"torso | upper | fore | glove",fill=(210,210,204,255))
        sheet.alpha_composite(canvas,(col*cellw,row*cellh))
sheet.convert("RGB").save(qa/"role_overlays_contact_sheet.jpg",quality=95,subsampling=0)

print("PC22_ROLE_OVERLAYS_OK")
print(json.dumps({"sleeves":24,"gloves":24,"torsos":12},sort_keys=True))
