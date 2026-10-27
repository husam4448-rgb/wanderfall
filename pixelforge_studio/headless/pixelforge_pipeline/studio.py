"""Deterministic offline production tools for Pixel Forge 1.0.4 projects.

No UI, no hosted AI and no arbitrary third-party code execution. All methods
operate on the v4 .pixelforge document and produce editable sprites/metadata.
"""
from __future__ import annotations
import colorsys
import copy
import json
import math
import re
from pathlib import Path
from PIL import Image
from .engine import image_of, put_image, render, validate, pivot_for

BRUSH_SHAPES = ("square", "circle", "horizontal", "vertical", "slash", "backslash",
                "plus", "x", "diamond", "outline")
CANVAS_PRESETS = {"Obsidian": "#080b0e", "Charcoal": "#151b22",
                  "Graphite": "#272e36", "Slate": "#3b4550", "Neutral Gray": "#666e75",
                  "Soft Light": "#b8bec2", "White": "#eceff1"}
RIG_PARTS = ("head", "neck", "torso", "pelvis", "legs", "left_upper_arm",
             "right_upper_arm", "left_forearm", "right_forearm", "left_hand", "right_hand",
             "left_thigh", "right_thigh", "left_shin", "right_shin", "left_foot", "right_foot",
             "backpack", "belt", "helmet", "mask", "weapon", "armor", "other")


def _doc(project, document="character"):
    validate(project)
    if document not in project["documents"]:
        raise ValueError("Unknown document")
    return project["documents"][document]


def _layer(doc, layer_id):
    for layer in doc["layers"]:
        if layer["id"] == layer_id:
            return layer
    raise KeyError("Unknown layer: " + str(layer_id))


def _new_id(doc):
    existing = {str(l["id"]) for l in doc["layers"]}
    n = 1
    while f"L{n}" in existing:
        n += 1
    return f"L{n}"


def brush_mask(size: int, shape="square"):
    """Return exact logical-pixel offsets using the Android v1.0.4 mask rules."""
    if shape not in BRUSH_SHAPES:
        raise ValueError("Unknown brush shape")
    k = max(1, min(64, int(round(size))))
    c = (k - 1) / 2
    result = []
    for y in range(k):
        for x in range(k):
            dx, dy = x - c, y - c
            if shape == "square": hit = True
            elif shape == "circle": hit = dx*dx + dy*dy <= (k/2 - .15)**2
            elif shape == "horizontal": hit = abs(dy) <= .5
            elif shape == "vertical": hit = abs(dx) <= .5
            elif shape == "slash": hit = abs(x + y - (k-1)) < 1
            elif shape == "backslash": hit = abs(x - y) < 1
            elif shape == "plus": hit = abs(dx) <= .5 or abs(dy) <= .5
            elif shape == "x": hit = abs(x-y)<1 or abs(x+y-(k-1))<1
            elif shape == "diamond": hit = abs(dx) + abs(dy) <= k/2 - .1
            else: hit = x==0 or y==0 or x==k-1 or y==k-1
            if hit:
                result.append((x-int(math.floor(k/2)), y-int(math.floor(k/2))))
    return result or [(0,0)]


def set_workspace(project, *, preset="Charcoal", ui_dark=True,
                  checker_brightness=37, checker_contrast=13, grid_opacity=25,
                  grid_color="#718a96", grid_major=True, custom_color=None):
    """Store rendering/view preferences as project metadata (non-destructive)."""
    if preset != "Custom" and preset not in CANVAS_PRESETS:
        raise ValueError("Unknown canvas preset")
    bg = custom_color if preset == "Custom" else CANVAS_PRESETS[preset]
    bg = _hex(bg)
    _hex(grid_color)
    for v in (checker_brightness, checker_contrast, grid_opacity):
        if not 0 <= int(v) <= 100: raise ValueError("Workspace slider outside 0..100")
    settings = project.setdefault("studioSettings", {})
    settings["workspace"] = {"preset":preset,"outside":bg,"uiDark":bool(ui_dark),
        "checkerLight":int(checker_brightness),"checkerDiff":int(checker_contrast),
        "gridColor":grid_color,"gridOpacity":int(grid_opacity),"major":bool(grid_major)}
    return settings["workspace"]


def edit_whole_image(project, document="character"):
    """Switch to full-canvas painting while preserving all original part layers."""
    d = _doc(project, document)
    state = d.get("wholeCanvas")
    if state and state.get("layerId") in {l["id"] for l in d["layers"]}:
        target = _layer(d,state["layerId"])
        if not state.get("active"):
            state["originalVisibility"] = [{"id":l["id"],"visible":l.get("visible",True)} for l in d["layers"] if l is not target]
            for l in d["layers"]:
                if l is not target: l["visible"] = False
            target["visible"] = True
            state["active"] = True
        project["selected"] = target["id"]
        return target["id"]
    # Exact right-facing composition; do not merge the source layers permanently.
    flat = render(project, document=document, face="right", anim="idle", frame=0)
    original = [{"id":l["id"],"visible":l.get("visible",True)} for l in d["layers"]]
    for l in d["layers"]: l["visible"] = False
    lid = _new_id(d)
    layer = {"id":lid,"name":"FULL IMAGE — editable","kind":"paint", "x":0,"y":0,
             "rotation":0,"scale":1,"flip":False,"visible":True,"locked":False,
             "opacity":1,"poses":{}}
    put_image(layer, flat)
    d["layers"].append(layer)
    d["wholeCanvas"] = {"layerId":lid,"originalVisibility":original,
                          "selectedBefore":project.get("selected"),"active":True}
    project["selected"] = lid
    return lid


def edit_parts(project, document="character"):
    d = _doc(project,document)
    state = d.get("wholeCanvas")
    if not state: return False
    for l in d["layers"]:
        if l["id"] == state["layerId"]: l["visible"] = False
    orig = {x["id"]:x["visible"] for x in state.get("originalVisibility",[])}
    for l in d["layers"]:
        if l["id"] in orig: l["visible"] = orig[l["id"]]
    state["active"] = False
    project["selected"] = state.get("selectedBefore")
    return True


def stamp(project, x, y, color="#ffffff", *, size=1, shape="square", erase=False,
          document="character", layer_id=None, whole_default=True):
    """Apply an exact pixel brush; whole image is the default, part-only is opt-in."""
    d = _doc(project,document)
    if not layer_id:
        layer_id = edit_whole_image(project,document) if whole_default else project.get("selected")
    layer = _layer(d,layer_id)
    if layer.get("locked"): raise ValueError("Layer is locked")
    im = image_of(layer)
    p = im.load()
    rgba = (0,0,0,0) if erase else _rgb(color)+(255,)
    cx,cy = int(round(x)),int(round(y))
    if not whole_default:
        cx -= int(round(layer.get("x",0)))
        cy -= int(round(layer.get("y",0)))
    hits=0
    for dx,dy in brush_mask(size,shape):
        nx,ny=cx+dx,cy+dy
        if 0<=nx<im.width and 0<=ny<im.height:
            p[nx,ny]=rgba
            hits+=1
    put_image(layer,im)
    return hits


def copy_region(project, rect, *, document="character", layer_id=None, whole_default=True):
    d = _doc(project,document)
    lid = layer_id or (edit_whole_image(project,document) if whole_default else project.get("selected"))
    im = image_of(_layer(d,lid))
    x,y,w,h = [int(v) for v in rect]
    if w<=0 or h<=0 or x<0 or y<0 or x+w>im.width or y+h>im.height:
        raise ValueError("Selection exceeds editable sprite")
    return im.crop((x,y,x+w,y+h))


def cut_region(project, rect, *, document="character", layer_id=None, whole_default=True):
    d=_doc(project,document)
    lid=layer_id or (edit_whole_image(project,document) if whole_default else project.get("selected"))
    layer=_layer(d,lid)
    if layer.get("locked"):raise ValueError("Layer is locked")
    im=image_of(layer);selection=copy_region(project,rect,document=document,layer_id=lid)
    x,y,w,h=map(int,rect)
    im.paste((0,0,0,0),(x,y,x+w,y+h))
    put_image(layer,im)
    return selection


def paste_region(project, sprite, x, y, *, document="character", layer_id=None,whole_default=True):
    d=_doc(project,document)
    lid=layer_id or (edit_whole_image(project,document) if whole_default else project.get("selected"))
    layer=_layer(d,lid)
    if layer.get("locked"): raise ValueError("Layer locked")
    base=image_of(layer);sprite=sprite.convert("RGBA")
    base.alpha_composite(sprite,(int(round(x)),int(round(y))))
    put_image(layer,base)
    return lid


def rotate_region(project, rect, degrees, *, document="character", cut=True):
    """Nearest-neighbor selected pixel rotation around selection center."""
    if not -360<=float(degrees)<=360:raise ValueError("Rotation outside +/-360 degrees")
    d=_doc(project,document);lid=edit_whole_image(project,document)
    x,y,w,h=map(int,rect)
    sprite=cut_region(project,rect,document=document,layer_id=lid) if cut else copy_region(project,rect,document=document,layer_id=lid)
    rotated=sprite.rotate(-float(degrees),resample=Image.Resampling.NEAREST,expand=True)
    nx=round(x+w/2-rotated.width/2)
    ny=round(y+h/2-rotated.height/2)
    paste_region(project,rotated,nx,ny,document=document,layer_id=lid)
    return (nx,ny,rotated.width,rotated.height)


def extract_region(project, rect, name="Extracted part", role="other", *, document="character",cut=True):
    """Make selected pixels a separate, riggable layer."""
    d=_doc(project,document);lid=edit_whole_image(project,document)
    sprite=cut_region(project,rect,document=document,layer_id=lid) if cut else copy_region(project,rect,document=document,layer_id=lid)
    x,y,_,_=map(int,rect)
    new_id=_new_id(d)
    if role not in RIG_PARTS:raise ValueError("Invalid body-part role")
    layer={"id":new_id,"name":str(name)[:80],"kind":"rigPart","x":x,"y":y,
           "rotation":0,"scale":1,"flip":False,"visible":True,"locked":False,
           "opacity":1,"poses":{},"rig":{"role":role,"pivot":pivot_for(role,*sprite.size)}}
    put_image(layer,sprite)
    d["layers"].append(layer)
    # Original full canvas copy stays editable; extraction creates a visible rig part.
    return new_id


def recolor(project, color_from, color_to, *, tolerance=0, document="character", layer_id=None):
    """Replace similar RGB colors on selected layer or all visible layers."""
    d=_doc(project,document)
    target=_rgb(color_from);replacement=_rgb(color_to)
    if not 0<=tolerance<=255:raise ValueError("Tolerance 0..255")
    ls=[_layer(d,layer_id)] if layer_id else [l for l in d["layers"] if l.get("visible",True)]
    count=0
    for l in ls:
        if l.get("locked"):continue
        im=image_of(l)
        px=im.load()
        for y in range(im.height):
            for x in range(im.width):
                r,g,b,a=px[x,y]
                if a and max(abs(r-target[0]),abs(g-target[1]),abs(b-target[2]))<=tolerance:
                    px[x,y]=replacement+(a,)
                    count+=1
        put_image(l,im)
    return count


def palette_import(path, max_colors=256):
    """Read data-only palettes: GPL, PAL, TXT, HEX, JSON or an image."""
    p=Path(path)
    if p.suffix.lower() in (".png",".jpg",".jpeg",".webp"):
        im=Image.open(p).convert("RGBA")
        counts=im.getcolors(maxcolors=im.width*im.height)
        if counts is None: raise ValueError("Image too large for palette extraction")
        order=sorted(((n,rgb) for n,rgb in counts if rgb[3]),reverse=True)
        return [_hex('#%02x%02x%02x'%rgb[:3]) for _,rgb in order[:max_colors]]
    text=p.read_text(encoding="utf-8-sig")
    if p.suffix.lower()==".json":
        data=json.loads(text)
        if isinstance(data,dict):data=data.get("colors",data.get("palette",[]))
        if not isinstance(data,list): raise ValueError("Unsupported palette JSON")
        values=[str(v.get("color",v.get("hex",""))) if isinstance(v,dict) else str(v) for v in data]
    else:
        values=[]
        for line in text.splitlines():
            line=line.strip()
            if not line or line.startswith(("GIMP Palette","Name:","Columns:","JASC-PAL")):
                continue
            if line.startswith('#') and not re.fullmatch(r'#[0-9a-fA-F]{6}',line):continue
            m=re.match(r'^\s*(\d+)\s+(\d+)\s+(\d+)(?:\s|$)',line)
            if m and all(0<=int(m[i])<=255 for i in (1,2,3)):
                values.append('#%02x%02x%02x'%tuple(int(m[i]) for i in (1,2,3)))
            else:
                values+=re.findall(r'#[0-9a-fA-F]{6}(?![0-9a-fA-F])',line)
    result=[];seen=set()
    for val in values:
        try: color=_hex(val)
        except ValueError: continue
        if color not in seen:
            seen.add(color);result.append(color)
        if len(result)>=max_colors:break
    if not result:raise ValueError("No colors found")
    return result


def _hex(s):
    if not isinstance(s,str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',s):
        raise ValueError("Expected #RRGGBB color")
    return s.lower()


def _rgb(s):
    s=_hex(s)
    return tuple(int(s[i:i+2],16) for i in (1,3,5))


def shades_from_color(hex_color, steps=7, interval=7):
    r,g,b=[v/255 for v in _rgb(hex_color)]
    h,s,v=colorsys.rgb_to_hsv(r,g,b)
    result=[]
    for i in range(-steps,steps+1):
        value=max(.04,min(1,v + i*interval/100))
        rgb=colorsys.hsv_to_rgb(h,s,value)
        result.append('#'+''.join('%02x'%round(a*255) for a in rgb))
    return result


def sample_color(project,x,y,*,document="character", face="right"):
    im=render(project,document=document,face=face)
    x,y=int(x),int(y)
    if not (0<=x<im.width and 0<=y<im.height):raise ValueError("Sample outside canvas")
    r,g,b,a=im.getpixel((x,y))
    return None if a==0 else '#%02x%02x%02x'%(r,g,b)


def rig_layer(project, layer_id, role, *, pivot=None, parent_id=None,
              link_mode="rigid", document="character"):
    d=_doc(project,document)
    layer=_layer(d,layer_id)
    if role not in RIG_PARTS:raise ValueError("Unknown rig role")
    if link_mode not in ("none","rigid","follow","loose"):raise ValueError("Unknown joint mode")
    if parent_id == layer_id:raise ValueError("Cannot parent a layer to itself")
    if parent_id is not None:_layer(d,parent_id)
    rig=layer.setdefault("rig",{})
    rig["role"]=role;rig["linkMode"]=link_mode;rig["parentId"]=parent_id
    if pivot is not None:
        if len(pivot)!=2:raise ValueError("Pivot requires x,y")
        rig["pivot"]={"x":float(pivot[0]),"y":float(pivot[1])}
    else:rig.setdefault("pivot",pivot_for(role,*image_of(layer).size))
    # detect cyclic rig before writing to storage
    from .engine import poses_for
    poses_for(d["layers"],0,"idle")
    return rig


def socket(project, layer_id, name, x, y, *, document="character"):
    l=_layer(_doc(project,document),layer_id)
    rig=l.setdefault("rig",{})
    sockets=rig.setdefault("sockets",[])
    sockets[:]=[s for s in sockets if s.get("name")!=name]
    sockets.append({"name":str(name)[:64],"x":float(x),"y":float(y)})
    return sockets[-1]


def joint_limits(project, layer_id, minimum=-180, maximum=180, *, document="character"):
    if minimum>maximum or minimum< -360 or maximum>360: raise ValueError("Invalid joint limits")
    rig=_layer(_doc(project,document),layer_id).setdefault("rig",{})
    rig["minAngle"]=float(minimum);rig["maxAngle"]=float(maximum)
    return rig


def set_pose(project, layer_id, animation, frame, *, x=0, y=0,
             rotation=0, scale=1, document="character"):
    if not 0<=frame<64:raise ValueError("Frames 0..63")
    l=_layer(_doc(project,document),layer_id)
    rig=l.get("rig",{})
    rotation=max(float(rig.get("minAngle",-360)),min(float(rig.get("maxAngle",360)),float(rotation)))
    pose={"x":float(x),"y":float(y),"rotation":rotation,"scale":float(scale)}
    l.setdefault("poses",{}).setdefault(animation,{})[str(frame)]=pose
    return pose


def configure_timeline(project, animation="walk", frames=8, fps=8, *, document="character"):
    if not 1<=frames<=64 or not 1<=fps<=60:raise ValueError("frames 1..64, fps 1..60")
    d=_doc(project,document)
    d.setdefault("timelines",{})[animation]={"count":int(frames),"fps":int(fps)}
    return d["timelines"][animation]


def save_pose_template(project, name, animation, frame, *, document="character"):
    d=_doc(project,document)
    poses={l["id"]:copy.deepcopy(l.get("poses",{}).get(animation,{}).get(str(frame),{})) for l in d["layers"]}
    d.setdefault("poseLibrary",{})[name]={"animation":animation,"frame":frame,"poses":poses}
    return name


def apply_pose_template(project, name, animation, frame, *, document="character"):
    d=_doc(project,document); entry=d.get("poseLibrary",{}).get(name)
    if entry is None:raise KeyError("Unknown pose template")
    for l in d["layers"]:
        if l["id"] in entry["poses"]:
            l.setdefault("poses",{}).setdefault(animation,{})[str(frame)]=copy.deepcopy(entry["poses"][l["id"]])
    return len(entry["poses"])


def transform_layer(project, layer_id, *, rotation=None, scale_x=None,
                    scale_y=None, flip=None, x=None, y=None, document="character"):
    """Non-destructive arbitrary rotation, stretch, mirroring and repositioning."""
    l=_layer(_doc(project,document),layer_id)
    if l.get('locked'):raise ValueError('Layer is locked')
    if rotation is not None:l['rotation']=float(rotation)%360
    if flip is not None:l['flip']=bool(flip)
    rig=l.setdefault('rig',{})
    for attr,value in [('scaleX',scale_x),('scaleY',scale_y)]:
        if value is not None:
            if not .05<=float(value)<=32:raise ValueError('Scale must be .05..32')
            rig[attr]=float(value)
    if x is not None:l['x']=float(x)
    if y is not None:l['y']=float(y)
    return l


def resize_sprite(project, layer_id, width, height, *, document="character"):
    """Pixel-perfect physical sprite resizing (nearest-neighbor), unlike layer scale."""
    w,h=int(width),int(height)
    if not 1<=w<=1024 or not 1<=h<=1024:raise ValueError('Sprite dimensions 1..1024')
    l=_layer(_doc(project,document),layer_id)
    if l.get('locked'):raise ValueError('Layer is locked')
    old=image_of(l);sx=w/old.width;sy=h/old.height
    put_image(l,old.resize((w,h),Image.Resampling.NEAREST))
    if l.get('rig',{}).get('pivot'):
        p=l['rig']['pivot'];p['x']*=sx;p['y']*=sy
    for s in l.get('rig',{}).get('sockets',[]):s['x']*=sx;s['y']*=sy
    return (w,h)


def attach_socket(project, child_id, parent_id, socket_name, *, x_offset=0,
                  y_offset=0,document='character'):
    d=_doc(project,document);child=_layer(d,child_id);parent=_layer(d,parent_id)
    if child is parent:raise ValueError('Self attachment')
    if socket_name not in [s['name'] for s in parent.get('rig',{}).get('sockets',[])]:
        raise ValueError('Socket not found')
    rig=child.setdefault('rig',{})
    rig.update({'parentId':parent_id,'attachSocket':socket_name,'linkMode':'rigid',
                'offsetX':float(x_offset),'offsetY':float(y_offset)})
    from .engine import poses_for
    poses_for(d['layers'],0,'idle')
    return rig


def skeleton_preset(project, preset='minimal', *, document='character'):
    """Generate the same basic/bare/detailed named point graphs as the Android app."""
    specs={
        'minimal':[('head',.5,.22,'torso'),('torso',.5,.48,None),('legs',.5,.75,'torso')],
        'basic':[('head',.5,.17,'torso'),('torso',.5,.43,None),('left_arm',.33,.44,'torso'),
                 ('right_arm',.67,.44,'torso'),('legs',.5,.77,'torso'),('backpack',.39,.43,'torso')],
        'detailed':[('head',.5,.17,'neck'),('neck',.5,.29,'torso'),('torso',.5,.43,None),
                    ('pelvis',.5,.59,'torso'),('left_arm',.33,.44,'torso'),
                    ('right_arm',.67,.44,'torso'),('left_hand',.26,.58,'left_arm'),
                    ('right_hand',.74,.58,'right_arm'),('left_leg',.43,.81,'pelvis'),
                    ('right_leg',.57,.81,'pelvis'),('backpack',.36,.44,'torso'),
                    ('belt',.5,.59,'pelvis'),('helmet',.5,.105,'head'),('weapon',.78,.55,'right_hand')]}
    if preset not in specs:raise ValueError('Unknown skeleton preset')
    d=_doc(project,document)
    old={x['name']:x.get('layerId','') for x in d.get('skeleton',{}).get('points',[])}
    nodes=[{'id':f'P{i+1}','name':name,'x':round(x*d['w']),
            'y':round(y*d['h']),'parentId':'','layerId':old.get(name,''),'locked':False}
           for i,(name,x,y,parent) in enumerate(specs[preset])]
    byname={n['name']:n for n in nodes}
    for node,source in zip(nodes,specs[preset]):
        parent=source[3];node['parentId']=byname[parent]['id'] if parent else ''
    d['skeleton']={'points':nodes,'allowDetach':False}
    return nodes


def update_skeleton_point(project, name, *, x=None,y=None,layer_id=None,
                          parent_name=None,locked=None,document='character'):
    d=_doc(project,document)
    nodes=d.get('skeleton',{}).get('points',[])
    node=next((n for n in nodes if n['name']==name),None)
    if node is None:raise KeyError('Unknown rig point')
    if x is not None:node['x']=max(0,min(d['w'],float(x)))
    if y is not None:node['y']=max(0,min(d['h'],float(y)))
    if layer_id is not None:
        _layer(d,layer_id)
        node['layerId']=layer_id
    if parent_name is not None:
        parent=next((n for n in nodes if n['name']==parent_name),None)
        if parent is None:raise KeyError('Unknown skeleton parent')
        node['parentId']=parent['id']
    if locked is not None:node['locked']=bool(locked)
    return node


def solve_two_bone_ik(shoulder, length1, length2, target, bend=1):
    """Analytic 2D IK geometry for constructing editable arm/leg poses."""
    x,y=map(float,shoulder);tx,ty=map(float,target)
    a=float(length1);b=float(length2)
    if a<=0 or b<=0:raise ValueError('Limb lengths must be positive')
    dx,dy=tx-x,ty-y;distance=math.hypot(dx,dy)
    clamped=max(abs(a-b)+.00001,min(a+b-.00001,distance))
    direction=math.atan2(dy,dx)
    alpha=math.acos(max(-1,min(1,(a*a+clamped*clamped-b*b)/(2*a*clamped))))
    theta=direction+(1 if bend>=0 else -1)*alpha
    elbow=(x+a*math.cos(theta),y+a*math.sin(theta))
    actual_target=(x+clamped*math.cos(direction),y+clamped*math.sin(direction))
    return {'elbow':elbow,'wrist':actual_target,
            'upperAngle':math.degrees(theta),'lowerAngle':math.degrees(math.atan2(actual_target[1]-elbow[1],actual_target[0]-elbow[0])),
            'clamped':abs(clamped-distance)>.00001}