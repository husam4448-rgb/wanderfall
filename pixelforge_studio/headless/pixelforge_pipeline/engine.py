"""Offline headless renderer and asset-production engine for Pixel Forge project v4.

Reads/writes the SAME .pixelforge project JSON (embedded PNG layers) as Android
Pixel Forge v0.8. This is deterministic automation, NOT neural-network AI.
"""
from __future__ import annotations
import base64
import copy
import io
import json
import math
import re
from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw

MAX_DIM = 1024
MAX_LAYERS = 250
ANIMATIONS = ("idle", "walk", "run", "aim")
PARENTS = {
    "head": "torso", "hair": "head", "hat": "head", "helmet": "head",
    "torso": None, "pelvis": "torso", "belt": "pelvis", "backpack": "torso",
    "left_upper_arm": "torso", "left_forearm": "left_upper_arm", "left_hand": "left_forearm",
    "right_upper_arm": "torso", "right_forearm": "right_upper_arm", "right_hand": "right_forearm",
    "left_thigh": "pelvis", "left_shin": "left_thigh", "left_foot": "left_shin",
    "right_thigh": "pelvis", "right_shin": "right_thigh", "right_foot": "right_shin",
    "weapon": "right_hand", "mask": "head", "armor": "torso",
}
KINDS = {"legL": "left_thigh", "legR": "right_thigh", "armL": "left_upper_arm", "armR": "right_upper_arm",
         "pack": "backpack", "torsoGear": "armor", "headgear": "helmet", "weaponHand": "weapon"}


def blank_project(width=64, height=64):
    _check_dims(width, height)
    return {"version": 4, "name": "Survival Paradise Pixel Forge", "mode": "character", "selected": None,
            "face": "right", "animation": "idle", "documents": {
              "character": {"w": width, "h": height, "wholeCanvas": None, "layers": []},
              "weapon": {"w": 64, "h": 64, "wholeCanvas": None, "layers": []}}}


def _check_dims(w, h):
    if not (isinstance(w, int) and isinstance(h, int) and 1 <= w <= MAX_DIM and 1 <= h <= MAX_DIM):
        raise ValueError(f"Canvas/sprite dimensions must be 1..{MAX_DIM}")


def load(path):
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    validate(obj)
    return obj


def validate(project):
    if not isinstance(project, dict) or project.get("version") not in (1, 2, 3, 4):
        raise ValueError("Not a compatible Pixel Forge project")
    docs = project.get("documents")
    if not isinstance(docs, dict) or not all(k in docs for k in ("character", "weapon")):
        raise ValueError("Missing character/weapon documents")
    for doc in docs.values():
        _check_dims(doc.get("w"), doc.get("h"))
        ls = doc.get("layers")
        if not isinstance(ls, list) or len(ls) > MAX_LAYERS:
            raise ValueError("Too many or invalid layers")
        ids = set()
        for layer in ls:
            if layer.get("id") in ids:
                raise ValueError("Duplicate layer IDs")
            ids.add(layer.get("id"))
            im = image_of(layer)
            _check_dims(*im.size)
            if abs(float(layer.get("scale", 1))) > 100:
                raise ValueError("Unsafe layer scale")
    return True


def image_of(layer):
    s = layer.get("sprite", "")
    if isinstance(s, str) and s.startswith("data:image/png;base64,"):
        payload = base64.b64decode(s.partition(",")[2], validate=True)
        if len(payload) > 16*1024*1024:
            raise ValueError("Sprite is too large")
        return Image.open(io.BytesIO(payload)).convert("RGBA")
    raise ValueError("Layers require embedded PNG sprites (v0.8 project format)")


def put_image(layer, image):
    if image.mode != "RGBA": image = image.convert("RGBA")
    _check_dims(*image.size)
    b = io.BytesIO()
    image.save(b, format="PNG", optimize=True)
    layer["sprite"] = "data:image/png;base64," + base64.b64encode(b.getvalue()).decode("ascii")


def save(project, path):
    validate(project)
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")


def role_of(layer):
    role = (layer.get("rig") or {}).get("role")
    if role and role != "unassigned": return role
    kind = layer.get("kind", "")
    if kind in KINDS: return KINDS[kind]
    s = str(layer.get("name", "")).lower().replace("-", "_").replace(" ", "_")
    aliases = [("forearm", "forearm"), ("upper_arm", "upper_arm"), ("hand", "hand"),
               ("thigh", "thigh"), ("shin", "shin"), ("foot", "foot")]
    for side in ("left", "right"):
        for key, name in aliases:
            if side in s and key in s: return f"{side}_{name}"
    for key in ("helmet", "hat", "hair", "head", "torso", "pelvis", "belt", "backpack", "weapon", "mask", "armor"):
        if key in s: return key
    return "unassigned"


def pivot_for(role, width, height):
    x, y = width/2, height/2
    if role == "head": y = height*.83
    elif role in ("torso", "pelvis"): y = height*.3
    elif any(x in role for x in ("upper_arm", "thigh", "shin", "forearm")): y = height*.13
    elif any(x in role for x in ("hand", "foot")): y = height*.35
    elif role == "backpack": y = height*.2
    elif role in ("helmet", "hat"): y = height*.72
    return {"x": round(x), "y": round(y)}


def auto_rig(project, document="character"):
    """Add missing roles/pivots/parent links without overwriting manual rig settings."""
    layers = project["documents"][document]["layers"]
    byrole = {}
    for l in layers:
        role = role_of(l)
        if role != "unassigned":
            rig = l.setdefault("rig", {})
            rig.setdefault("role", role)
            rig.setdefault("pivot", pivot_for(role, *image_of(l).size))
            byrole.setdefault(role, l)
    for l in layers:
        rig = l.get("rig") or {}
        role = rig.get("role", "unassigned")
        parentrole = PARENTS.get(role)
        if parentrole and not rig.get("parentId") and parentrole in byrole:
            parent = byrole[parentrole]
            if parent["id"] != l["id"]:
                rig["parentId"] = parent["id"]
                rig.setdefault("linkMode", "rigid")
    return sum(1 for l in layers if l.get("rig", {}).get("role") not in (None, "unassigned"))


def motion(role, anim, frame, count=8, strength=.9):
    t=2*math.pi*frame/count
    sin, cos, bounce = math.sin(t), math.cos(t), (1-math.cos(2*t))*.5
    fast = anim == "run"
    amplitude=(20 if fast else 12)*strength
    travel=3 if fast else 2
    limb_leg = re.match(r"^(left|right)_(thigh|shin|foot)$", role or "")
    limb_arm = re.match(r"^(left|right)_(upper_arm|forearm|hand)$", role or "")
    sign = 1 if role.startswith("left") else -1
    x=y=rotation=0.0
    if anim in ("walk", "run"):
        if limb_leg:
            rotation=sign*sin*amplitude*(.6 if "shin" in role else 1)
            x=sign*cos*strength*.5
            y=-max(0,sign*sin)*strength*(1.3 if fast else .5)
        elif limb_arm:
            rotation=-sign*sin*amplitude*(.65 if "forearm" in role else .8)
            y=-bounce*strength*.6
        elif role in ("head", "torso", "pelvis", "backpack", "belt"):
            y=-round(bounce*travel*strength)
    elif anim == "idle":
        if role in ("head", "torso", "pelvis", "backpack", "belt"):
            y=-round(bounce*strength)
        elif limb_arm:
            rotation=sign*sin*1.3*strength
    elif anim == "aim":
        rotation={"right_upper_arm":-25, "right_forearm":-40,
                  "left_upper_arm":-13, "left_forearm":-22}.get(role,0)*strength
        if role == "weapon": y=-3*strength
    elif anim != "none": raise ValueError(f"Unknown animation: {anim}")
    return {"x":round(x,2), "y":round(y,2), "rotation":round(rotation,1), "scale":1}


def generate(project, anim="walk", frames=8, strength=.9, document="character"):
    """Create editable poses in native project. v0.8 UI shows the first eight frames."""
    if anim not in ANIMATIONS: raise ValueError("Animation must be idle/walk/run/aim")
    if not 1 <= frames <= 64: raise ValueError("Frame count must be 1..64")
    auto_rig(project, document)
    count=0
    for l in project["documents"][document]["layers"]:
        role = role_of(l)
        if role == "unassigned" or l.get("locked"): continue
        l.setdefault("rig", {})["skipDefaultMotion"] = True
        l.setdefault("poses", {})[anim]={str(f):motion(role,anim,f,frames,strength) for f in range(frames)}
        count += 1
    project["animation"] = anim
    project.setdefault("pipeline", {})["frameCount"] = frames
    project["documents"][document].setdefault("timelines", {})[anim] = {"count": frames}
    return count


def _local_pose(l, frame, anim):
    pose = (l.get("poses") or {}).get(anim, {}).get(str(frame), {})
    return {"x":float(l.get("x",0)) + float(pose.get("x",0)),
            "y":float(l.get("y",0)) + float(pose.get("y",0)),
            "rotation":float(l.get("rotation",0)) + float(pose.get("rotation",0)),
            "scale":float(l.get("scale",1)) * float(pose.get("scale",1))}


def poses_for(layers, frame, anim):
    """Resolve connected world-space pivots and equipment sockets as in Pixel Forge v0.9."""
    ids={l["id"]:l for l in layers}
    memo={}
    _imagecache={}
    def image_of_cached(layer):
        key=layer["id"]
        if key not in _imagecache: _imagecache[key]=image_of(layer)
        return _imagecache[key]
    def pivot(layer):
        im=image_of_cached(layer)
        return (layer.get("rig") or {}).get("pivot") or {"x":im.width/2,"y":im.height/2}
    def calc(lid, seen):
        if lid in memo: return memo[lid]
        if lid in seen: raise ValueError("Joint parent cycle detected")
        l=ids[lid];pose=_local_pose(l,frame,anim)
        rig=l.get("rig") or {};parentid=rig.get("parentId")
        mode=rig.get("linkMode","none")
        if parentid in ids and parentid!=lid and mode!="none":
            par=ids[parentid];parent=calc(parentid,seen|{lid})
            pp=pivot(par);cp=pivot(l)
            parentrig=par.get("rig") or {}
            socket=next((x for x in parentrig.get("sockets",[]) if x.get("name")==rig.get("attachSocket")),None)
            if socket:
                dx=float(socket["x"])-float(pp["x"])+float(rig.get("offsetX",0))
                dy=float(socket["y"])-float(pp["y"])+float(rig.get("offsetY",0))
            else:
                dx=float(l.get("x",0))+float(cp["x"])-(float(par.get("x",0))+float(pp["x"]))
                dy=float(l.get("y",0))+float(cp["y"])-(float(par.get("y",0))+float(pp["y"]))
            weight={"rigid":1,"follow":.75,"loose":.35}.get(mode,0)
            a=math.radians((parent["rotation"]-float(par.get("rotation",0)))*weight)
            ps=float(par.get("scale",1)) or 1
            sx=parent["scale"]*float(parentrig.get("scaleX",1))/ps
            sy=parent["scale"]*float(parentrig.get("scaleY",1))/ps
            rx=parent["x"]+float(pp["x"])+dx*sx*math.cos(a)-dy*sy*math.sin(a)
            ry=parent["y"]+float(pp["y"])+dx*sx*math.sin(a)+dy*sy*math.cos(a)
            pose["x"]+=rx-(float(l.get("x",0))+float(cp["x"]))
            pose["y"]+=ry-(float(l.get("y",0))+float(cp["y"]))
            pose["rotation"]+=(parent["rotation"]-float(par.get("rotation",0)))*weight
        memo[lid]=pose
        return pose
    def check_parent(lid,seen):
        if lid in seen:raise ValueError("Joint parent cycle detected")
        parent=(ids[lid].get("rig") or {}).get("parentId")
        if parent in ids:check_parent(parent,seen|{lid})
    for lid in ids:check_parent(lid,set())
    for lid in ids:calc(lid,set())
    return memo,_imagecache


def render(project, anim="idle", frame=0, face="right", document="character", scale=1):
    if face not in ("left","right"): raise ValueError("Facing must be left or right")
    d=project["documents"][document];w,h=d["w"],d["h"]
    layers=d["layers"]
    pmap, images=poses_for(layers,frame,anim)
    output=Image.new("RGBA",(w,h))
    for l in layers:
        if not l.get("visible",True): continue
        sprite=images[l["id"]];p=pmap[l["id"]]
        pivot=(l.get("rig") or {}).get("pivot") or {"x":sprite.width/2,"y":sprite.height/2}
        px=float(pivot["x"]);py=float(pivot["y"])
        ang=math.radians(p["rotation"]);cs=math.cos(ang);sn=math.sin(ang)
        s=p["scale"]
        if abs(s)<.0001: continue
        rig=l.get("rig") or {}
        sx=s*float(rig.get("scaleX",1))*(-1 if l.get("flip") else 1);sy=s*float(rig.get("scaleY",1))
        A=cs*sx;B=-sn*sy;C=sn*sx;D=cs*sy
        det=A*D-B*C
        aa=D/det;bb=-B/det;dd=-C/det;ee=A/det
        qx=p["x"]+px;qy=p["y"]+py
        cc=px-aa*qx-bb*qy
        ff=py-dd*qx-ee*qy
        im=sprite.transform((w,h),Image.Transform.AFFINE,(aa,bb,cc,dd,ee,ff),resample=Image.Resampling.NEAREST)
        if float(l.get("opacity",1))<1:
            alpha=im.getchannel("A").point(lambda a: round(a*max(0,min(1,float(l["opacity"])))))
            im.putalpha(alpha)
        output=Image.alpha_composite(output,im)
    if face == "left": output=output.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if scale != 1:
        if not isinstance(scale,int) or scale<1 or scale>16:raise ValueError("Export scale 1..16")
        output=output.resize((w*scale,h*scale),Image.Resampling.NEAREST)
    return output


def add_layer(project, png, name, role, x, y, document="character", parent_id=None, pivot=None):
    d=project["documents"][document]
    if len(d["layers"])>=MAX_LAYERS:raise ValueError("Layer limit")
    im=Image.open(png).convert("RGBA")
    _check_dims(*im.size)
    index=1+max([int(m.group(1)) for l in d["layers"] if (m:=re.match(r"L(\d+)$",str(l.get("id",""))))] or [0])
    lid=f"L{index}"
    l={"id":lid,"name":str(name)[:80],"kind":"rigPart","x":x,"y":y,"rotation":0,
       "scale":1,"flip":False,"visible":True,"locked":False,"opacity":1,"poses":{},
       "rig":{"role":role,"pivot":pivot or pivot_for(role,im.width,im.height),"parentId":parent_id,"skipDefaultMotion":True}}
    put_image(l,im)
    d["layers"].append(l);project["selected"]=lid
    return lid


def export(project, output, animations=("idle","walk","run","aim"), faces=("left","right"),
           frames=8, scale=1, fps=8, gif=True):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    d=project["documents"]["character"]
    w,h=d["w"]*scale,d["h"]*scale
    manifest={"format":"survival-paradise-pixelforge-output","version":1,
              "canvas":{"width":d["w"],"height":d["h"]},"exportScale":scale,"fps":fps,
              "animations":{},"sourceProjectVersion":project["version"]}
    for anim in animations:
        manifest["animations"][anim]={}
        for face in faces:
            strip=Image.new("RGBA",(w*frames,h))
            imgs=[]
            for i in range(frames):
                im=render(project,anim,i,face,scale=scale)
                strip.alpha_composite(im,(i*w,0))
                imgs.append(im)
            title=f"SP_{anim}_{face}"
            strip.save(out/(title+".png"))
            if gif:
                imgs[0].save(out/(title+".gif"),save_all=True,append_images=imgs[1:],duration=max(20,round(1000/fps)),loop=0,disposal=2,optimize=False)
            manifest["animations"][anim][face]={"sheet":title+".png","gif":title+".gif" if gif else None,
                                                  "frameWidth":w,"frameHeight":h,"frames":frames}
    rig={"format":"survival-paradise-rig","version":2,"canvas":{"width":d["w"],"height":d["h"]},
         "timelines":d.get("timelines",{}),"poseLibrary":d.get("poseLibrary",{}),
         "layers":[{"id":l["id"],"name":l.get("name"),"role":role_of(l),
                    "parentId":(l.get("rig") or {}).get("parentId"),"pivot":(l.get("rig") or {}).get("pivot"),
                    "rect":{"x":l.get("x",0),"y":l.get("y",0),"w":image_of(l).width,"h":image_of(l).height},
                    "poses":l.get("poses",{}),"rig":l.get("rig",{})} for l in d["layers"]]}
    (out/"SP_Character_Rig.json").write_text(json.dumps(rig,indent=2),encoding="utf-8")
    (out/"SP_Asset_Manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return manifest


def demo_project():
    """Minimal entirely original placeholder to exercise the production pipeline."""
    p=blank_project(48,56)
    parts=[("torso","torso",17,17,14,17,"#6b8170"),
           ("pelvis","pelvis",18,32,12,7,"#354d44"),
           ("head","head",18,7,12,12,"#c5a17c"),
           ("left_upper_arm","left_upper_arm",12,19,5,13,"#556b58"),
           ("right_upper_arm","right_upper_arm",31,19,5,13,"#556b58"),
           ("left_forearm","left_forearm",11,30,5,10,"#ad9575"),
           ("right_forearm","right_forearm",32,30,5,10,"#ad9575"),
           ("left_thigh","left_thigh",18,39,5,8,"#41494b"),
           ("right_thigh","right_thigh",25,39,5,8,"#41494b"),
           ("left_shin","left_shin",17,46,6,8,"#454749"),
           ("right_shin","right_shin",25,46,6,8,"#454749"),
           ("backpack","backpack",27,20,7,12,"#7a5c3d"),
           ("helmet","helmet",17,5,14,6,"#506455"),
           ("belt","belt",17,30,14,3,"#99794d")]
    for role,name,x,y,w,h,color in parts:
        im=Image.new("RGBA",(w,h));dr=ImageDraw.Draw(im)
        dr.rectangle((0,0,w-1,h-1),fill=color)
        if w>3 and h>3:dr.rectangle((1,1,w-2,h-2),outline="#222a29")
        lid=f"L{len(p['documents']['character']['layers'])+1}"
        l={"id":lid,"name":name,"kind":"rigPart","x":x,"y":y,"rotation":0,"scale":1,
           "visible":True,"locked":False,"opacity":1,"flip":False,"poses":{}}
        put_image(l,im);p["documents"]["character"]["layers"].append(l)
    auto_rig(p)
    for anim in ANIMATIONS:generate(p,anim)
    return p