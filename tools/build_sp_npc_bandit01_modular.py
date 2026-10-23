#!/usr/bin/env python3
"""SP_NPC_Bandit_Male_01 — real modular RGBA asset candidate from canonical sources.
No flattened portrait, no synthetic claims of approved animation, no source overwrite.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, math, sys

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"assets/authored2d/unified_character"
CAN=json.loads((SRC/"canonical_pc22.json").read_text())
assert CAN["standard_id"]=="PlayerCharacters_v22"
OUT=ROOT/"assets/npc_modular/SP_NPC_Bandit_Male_01"
PARTS=OUT/"parts"
GEAR=OUT/"equipment"
for d in (PARTS,GEAR,OUT/"qa",OUT/"rig",OUT/"animations"):
    d.mkdir(parents=True,exist_ok=True)

def rgba(p):
    assert p.is_file(), f"Missing canonical authored source {p}"
    im=Image.open(p).convert("RGBA")
    assert im.width>6 and im.height>6 and im.getchannel("A").getbbox(), str(p)
    return im

def bounds(im):
    return im.getchannel("A").getbbox()
def bbox_ratio(im):
    a,b,c,d=bounds(im)
    return a,b,c-a,d-b
def save(im,name,category="parts",origin="",pivots=None,notes=""):
    assert im.mode=="RGBA"
    bb=bounds(im)
    assert bb is not None and 0<=bb[0]<bb[2]<=im.width and 0<=bb[1]<bb[3]<=im.height
    dest=(PARTS if category=="parts" else GEAR)/f"{name}.png"
    im.save(dest, optimize=True)
    raw=dest.read_bytes()
    assert raw[:8]==b"\x89PNG\r\n\x1a\n"
    entries[name]={"path":str(dest.relative_to(ROOT)).replace("\\","/"),
       "canvas":list(im.size),"alpha_bounds":list(bb),
       "pivots":pivots or {}, "category":category, "sha256":hashlib.sha256(raw).hexdigest(),
       "source":origin,"notes":notes,
       "approval":"CANDIDATE_NOT_VISUALLY_APPROVED"}
    return im

def stroke(im, poly, color, width=2):
    d=ImageDraw.Draw(im,"RGBA");d.line(poly,fill=color,width=max(1,width),joint="curve")
def label_patch(im,quad,tint,outline=(24,22,20,255)):
    d=ImageDraw.Draw(im,"RGBA")
    d.polygon(quad,fill=tint)
    d.line(quad+[quad[0]],fill=outline,width=1)
def layer_source(name,source,category="parts",pivots=None):
    return save(rgba(source),name,category,str(source.relative_to(ROOT)),pivots)
def with_detail(source, name, effect):
    im=rgba(source)
    effect(im)
    return save(im,name,origin=str(source.relative_to(ROOT)),notes="additional authoring on existing canonical role artwork")

entries={}
role=SRC/"roles/bandit/male"
core=SRC/"core/male"
arms=SRC/"arms"
sleeves=arms/"sleeves/bandit/male"
hands=arms/"hybrid_v3/male"
p=CAN["male"]

def head_detail(im):
    x,y,w,h=bbox_ratio(im)
    # Scar, asymmetric fringe, soot near cheek; all tied to the head layer.
    stroke(im,[(x+int(w*.68),y+int(h*.35)),(x+int(w*.61),y+int(h*.53))],(115,56,46,230),max(1,w//38))
    stroke(im,[(x+int(w*.17),y+int(h*.11)),(x+int(w*.38),y+int(h*.03)),(x+int(w*.55),y+int(h*.10))],(38,29,26,245),max(2,w//13))
    ImageDraw.Draw(im,"RGBA").ellipse((x+int(w*.70),y+int(h*.58),x+int(w*.75),y+int(h*.65)),fill=(48,38,34,130))
with_detail(role/"head.png","head_neck",head_detail)

def torso_detail(im):
    x,y,w,h=bbox_ratio(im)
    # Rugged asymmetric chest strap and scuffed plates, not mere recolor.
    sw=max(2,w//10)
    stroke(im,[(x+int(w*.2),y+int(h*.12)),(x+int(w*.65),y+int(h*.82))],(49,35,30,245),sw+3)
    stroke(im,[(x+int(w*.2),y+int(h*.12)),(x+int(w*.65),y+int(h*.82))],(142,89,59,235),sw)
    d=ImageDraw.Draw(im,"RGBA")
    for i in range(3):
        px=x+int(w*(.31+.08*i)); py=y+int(h*(.33+.115*i))
        d.rounded_rectangle((px,py,px+max(2,w//12),py+max(3,h//11)),radius=1,
                            fill=(104,103,80,250),outline=(25,23,23,255))
    stroke(im,[(x+int(w*.08),y+int(h*.72)),(x+int(w*.47),y+int(h*.75))],(30,26,26,210),2)
with_detail(role/"torso.png","torso",torso_detail)

# The v22 body has a one-piece animated leg per side. We retain it as a
# reference and independently create knee-overlapping segments below.
def leg_segments(source,side):
    im=rgba(source)
    x,y,w,h=bbox_ratio(im)
    knee=y+int(h*.54)
    extension=max(3,int(h*.14))
    thigh=Image.new("RGBA",im.size,(0,0,0,0))
    shin=Image.new("RGBA",im.size,(0,0,0,0))
    a=im.getchannel("A")
    mask_hi=Image.new("L",im.size,0)
    mask_lo=Image.new("L",im.size,0)
    ImageDraw.Draw(mask_hi).rectangle((0,0,im.width,knee+extension),fill=255)
    ImageDraw.Draw(mask_lo).rectangle((0,knee-extension,im.width,im.height),fill=255)
    hi=Image.new("L",im.size);lo=Image.new("L",im.size)
    from PIL import ImageChops
    hi=ImageChops.multiply(a,mask_hi);lo=ImageChops.multiply(a,mask_lo)
    thigh.paste(im,(0,0));thigh.putalpha(hi)
    shin.paste(im,(0,0));shin.putalpha(lo)
    # Same source cloth pixels cover both sides of knee in rest pose.
    # This intentionally does NOT assert painted concealed knee surfaces.
    piv_hip=[x+int(w*.5),y+int(h*.10)]
    piv_knee=[x+int(w*.5),knee]
    piv_ankle=[x+int(w*.52),y+int(h*.94)]
    save(thigh,f"{side}_thigh",origin=str(source.relative_to(ROOT)),
         pivots={"hip":piv_hip,"knee":piv_knee},
         notes="original leg upper region with overlap; hidden bending surfaces REQUIRE visual review")
    save(shin,f"{side}_shin",origin=str(source.relative_to(ROOT)),
         pivots={"knee":piv_knee,"ankle":piv_ankle},
         notes="original leg lower region with overlap; not yet approved for independent knee rotation")
    return im
leg_segments(role/"pants_front.png","near")
leg_segments(role/"pants_rear.png","far")

# Belt/pelvis remain independent of animated trousers.
def pelvis_detail(im):
    x,y,w,h=bbox_ratio(im)
    d=ImageDraw.Draw(im,"RGBA")
    cy=y+int(h*.72)
    d.rounded_rectangle((x+int(w*.23),cy,x+int(w*.73),cy+max(4,h//8)),
       radius=max(1,w//22),fill=(72,52,37,245),outline=(31,24,22,255),width=2)
    d.rectangle((x+int(w*.43),cy+1,x+int(w*.54),cy+max(3,h//8)-1),
       fill=(162,127,78,235),outline=(43,35,28,255))
with_detail(role/"torso.png","pelvis_belt",pelvis_detail)

def upper_arm_detail(im):
    x,y,w,h=bbox_ratio(im)
    d=ImageDraw.Draw(im,"RGBA")
    # Worn segmented shoulder pad confined to original sleeve canvas.
    label_patch(im,[(x+int(w*.14),y+int(h*.19)),(x+int(w*.83),y+int(h*.23)),
                    (x+int(w*.75),y+int(h*.40)),(x+int(w*.20),y+int(h*.40))],
              (87,70,58,220))
    stroke(im,[(x+int(w*.33),y+int(h*.30)),(x+int(w*.65),y+int(h*.30))],
       (150,120,82,190),max(1,w//24))
for side in ("near","far"):
    with_detail(sleeves/"upper_arm.png",f"{side}_upper_arm",upper_arm_detail)
    layer_source(f"{side}_forearm",sleeves/"forearm.png")
    layer_source(f"{side}_hand",hands/("SP_PC22_Male_Hand_Dominant_V3.png" if side=="near"
                                      else "SP_PC22_Male_Hand_Support_V3.png"))

def boot_detail(im):
    x,y,w,h=bbox_ratio(im)
    stroke(im,[(x+int(w*.21),y+int(h*.45)),(x+int(w*.65),y+int(h*.48))],
           (131,112,85,170),max(1,h//24))
for side in ("near","far"):
    with_detail(core/"boot_base.png",f"{side}_boot",boot_detail)

# Role-specific carried gear is its own attached layer (not baked into torso).
layer_source("backpack",role/"backpack.png","equipment",
             {"attach":"back"},)
layer_source("utility",role/"utility.png","equipment",
             {"attach":"waist"},)
layer_source("glove",role/"glove.png","equipment",
             {"attach":"hands"},)

# Scarf and small side pouch are independent attachment layers, same transparent
# canvas as torso; no unapproved body shape is replaced with synthetic geometry.
tor=rgba(role/"torso.png")
x,y,w,h=bbox_ratio(tor)
scarf=Image.new("RGBA",tor.size,(0,0,0,0))
d=ImageDraw.Draw(scarf,"RGBA")
pts=[(x+int(w*.23),y+int(h*.08)),(x+int(w*.76),y+int(h*.08)),
     (x+int(w*.65),y+int(h*.28)),(x+int(w*.43),y+int(h*.37)),
     (x+int(w*.26),y+int(h*.25))]
d.polygon(pts,fill=(91,43,39,235))
d.line(pts+[pts[0]],fill=(40,25,25,255),width=max(1,w//30))
stroke(scarf,[(x+int(w*.31),y+int(h*.22)),(x+int(w*.51),y+int(h*.28))],(144,80,64,190),max(1,w//35))
save(scarf,"scarf","equipment",pivots={"neck":"torso_neck_socket"},notes="independent neck-worn equipment")
pouch=Image.new("RGBA",tor.size,(0,0,0,0))
d=ImageDraw.Draw(pouch,"RGBA")
px=x+int(w*.70);py=y+int(h*.70)
d.rounded_rectangle((px,py,px+max(5,w//5),py+max(7,h//4)),radius=2,
                   fill=(81,60,44,255),outline=(29,24,20,255),width=2)
d.line([(px+2,py+3),(px+max(3,w//5)-2,py+3)],fill=(148,118,84,250),width=2)
save(pouch,"waist_pouch","equipment",pivots={"attach":"pelvis_right"},notes="independent bag with belt socket")

# Preserve canonical source pivots as authoritative; leg pivots are provisional.
manifest={
 "schema":"SP_NPC_MODULAR_CANDIDATE_V1",
 "character_id":"SP_NPC_Bandit_Male_01",
 "rig_standard":"PlayerCharacters_v22",
 "source_branch":"sp-v286-npc-anatomy-visual-qa-20261023",
 "authored_facing":"RIGHT",
 "other_facing":"LEFT_MIRROR_UNVERIFIED",
 "gender":"male","role":"bandit",
 "visual_design":"scarred messy hair, scavenged shoulder plate, dusty bandolier and dark red scarf",
 "asset_parts":entries,
 "rig_contract":{"weapon_socket":CAN["weapon_socket"],
                 "male_proportions":p,
                 "arms":"canonical PlayerCharacters_v22 arms, direct part texture substitution",
                 "legs":"two segmented candidates cut with shared overlap from one-piece source; no independent knee animation approved"},
 "ready_for_game":False,
 "technical_qa":"PENDING",
 "visual_qa":"NOT_REVIEWED",
 "animation_qa":"NOT_TESTED",
 "known_blockers":["existing v286 NPC game renderer only replaces upper-body texture, not full modular part tree",
                   "new knee segments need actual concealed cloth artwork and Godot Bone2D bend tests",
                   "left direction, aiming and two-hand weapon contact not verified with new equipment"],
 "notes":"This is an actual collection of editable transparent individual PNGs, NOT a static whole-character sheet. Candidate only."
}
path=OUT/"manifest.json"
path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")

# Check all referenced files, geometry envelope, PNG mode and collision of hashes.
assert len(entries)>=18,len(entries)
for name,item in entries.items():
    ip=ROOT/item["path"]; im=rgba(ip)
    assert list(im.size)==item["canvas"] and list(bounds(im))==item["alpha_bounds"],name
    assert hashlib.sha256(ip.read_bytes()).hexdigest()==item["sha256"],name
assert {f"{side}_{part}" for side in ("near","far") for part in
  ("thigh","shin","upper_arm","forearm","hand","boot")}.issubset(entries)
manifest["technical_qa"]="PASS_RGBA_PARTS_AND_SOURCE_COMPATIBILITY_ONLY"
path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
print("SP_BANDIT01_PARTS_PASS",len(entries),str(OUT),manifest["technical_qa"])
print("SP_BANDIT01_VISUAL_PENDING",manifest["visual_qa"])
