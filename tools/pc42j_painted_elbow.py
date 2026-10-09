#!/usr/bin/env python3
"""PC42J authored, anatomically seated rolled sleeve and hidden elbow backing.

Unlike PC42G-I, this atlas is NOT an alpha-tapered or warped source strip.
The cuff's folded contour, transverse rolled edge, stitch line and cloth
pleats are individually hand-drawn shapes at elbow-local coordinates.
Clothing shades are sampled from the approved source outfit; back material
is intentionally drawn for rotation that the flat reference never depicted.

Art is experimental until actual Godot five-angle visual inspection.
"""
from pathlib import Path
import json
import math
from PIL import Image, ImageDraw
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"pc42-static-prototype/assets"
manifest=json.loads((OUT/"pc42h_arm_sources.json").read_text())
base=Image.open(OUT/"approved_reference_panel.png").convert("RGB")
assert base.size==(236,254),"Approved source canvas unexpectedly changed"
shoulder=np.array(manifest["joint_frames"]["far_shoulder"],np.float64)
elbow=np.array(manifest["joint_frames"]["far_elbow"],np.float64)
wrist=np.array(manifest["joint_frames"]["weapon_support_grip"],np.float64)
assert np.linalg.norm(elbow-np.array([143,95]))<.01
tangent=(elbow-shoulder)/np.linalg.norm(elbow-shoulder)
normal=np.array([-tangent[1],tangent[0]])
S=5
def xy(u,v):
    p=elbow+tangent*float(u)+normal*float(v)
    return (round(float(p[0])*S),round(float(p[1])*S))
def points(data):return [xy(u,v) for u,v in data]
def rgb(x,y):
    return tuple(int(z) for z in base.getpixel((x,y)))
# The original camouflaged jacket provides the full palette.
cloth_shadow=rgb(112,103)
cloth_base=rgb(117,100)
cloth_light=rgb(107,88)
warm_pleat=rgb(115,91)
dark_hem=rgb(104,95)
skin_bounce=rgb(121,90)

def layer():
    return Image.new("RGBA",(236*S,254*S),(0,0,0,0))
def poly(draw,verts,color):
    draw.polygon(points(verts),fill=tuple(color)+(255,))
def stroke(draw,verts,color,width=1.0):
    draw.line(points(verts),fill=tuple(color)+(255,),
              width=max(1,round(width*S)),joint="curve")
def finish(image,name):
    small=image.resize((236,254),Image.Resampling.LANCZOS)
    if small.getbbox() is None:raise RuntimeError("Empty painted asset "+name)
    arr=np.asarray(small)
    yy,xx=np.nonzero(arr[:,:,3]>12)
    if not len(xx)>=25:raise RuntimeError("Too little authored joint detail "+name)
    if not (126<=xx.min()<=146 and xx.max()<=159 and 78<=yy.min()<=105 and yy.max()<=116):
        raise RuntimeError("Authored paint outside elbow corridor: "+str([xx.min(),xx.max(),yy.min(),yy.max()]))
    small.save(OUT/(name+".png"))
    return {"pixels":int(len(xx)), "bbox":[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]}

# The inside cloth is positioned under the arm and revealed only on bending.
# It is a CLOSED fabric shape, not a stretched rectangle. Its tapered proximal
# termination lies underneath the actual upper-sleeve garment.
backing=layer();d=ImageDraw.Draw(backing)
poly(d,[(-7,-4.8),(-6,-6.3),(-3,-6.9),(-.5,-6.3),(1.7,-4.9),
        (2.9,-2.4),(2.5,.3),(2.7,2.1),(1.1,5.7),(-2,6.7),
        (-5,5.9),(-7,3.6),(-7.9,.6),(-7.2,-2.4)],cloth_shadow)
poly(d,[(-6.4,-3.7),(-3.4,-5.7),(-.7,-5.8),(1.7,-3.8),
        (1.2,.8),(.2,4.7),(-3.5,5.7),(-6,3)],cloth_base)
poly(d,[(-5.8,-2.5),(-3.7,-4.1),(-.1,-4.1),(.6,-2.3),
        (-.3,-.8),(-3,-1.4),(-4.5,1.3),(-6.3,.9)],warm_pleat)
poly(d,[(-5,2.5),(-3.4,1.1),(-1.7,2.5),(-1.4,4.8),(-4.2,5.1)],cloth_light)
stroke(d,[(-6.1,4.1),(-5,5),(-3.9,5.3)],dark_hem,.75)
stroke(d,[(-5.8,-4.8),(-3.4,-5.8),(-1,-5.3)],cloth_light,.55)

# Physically separate rolled tubular cloth RIM, asymmetrical sewn hem and
# genuine cuff opening. Its interior is darker; skin is rendered by the
# existing far-forearm on a DIFFERENT Bone2D, so the elbow remains functional.
rim=layer();d=ImageDraw.Draw(rim)
poly(d,[(-2.2,-5.9),(.2,-6.1),(1.7,-5.3),(3.0,-3.3),
        (3.5,-.6),(2.9,2.3),(1.8,4.6),(-.9,5.9),
        (-2.7,5.0),(-3.9,3.2),(-4,1.3),(-3.3,-1.5)],dark_hem)
poly(d,[(-2.5,-4.9),(-.5,-5.4),(1,-4.8),(2,-2.6),
        (2.1,-.2),(1.3,2.5),(-.4,4.7),(-2.1,4),
        (-3.1,2.7),(-3.1,0),(-2.6,-2.7)],cloth_base)
poly(d,[(-2.1,-3.8),(-1,-4.4),(.4,-3.9),(1.1,-2.2),
        (1.3,-.9),(.1,-1.8),(-.9,-1.5),(-2.6,-.2)],cloth_light)
poly(d,[(-1,3.0),(.4,2.2),(1.1,.9),(.8,3.5),(-.8,4.8),(-2,3.9)],warm_pleat)
stroke(d,[(-2.6,-4.3),(-3.5,-2.2),(-3.8,.7),(-2.9,3.2),
          (-1.1,5.1),(.7,4.4)],dark_hem,.9)
stroke(d,[(-.9,-5.1),(.7,-4.3),(1.9,-2.6),(2.5,-.1),
          (1.8,2.4)],cloth_light,.65)
stroke(d,[(1.7,-4.1),(2.8,-1.8),(2.6,1.5),(1.5,3.7)],cloth_shadow,.6)
# Localized hand-authored stitch highlights to avoid a featureless cuff tube.
for u,v in [(-2.8,-2.4),(-2.9,-.2),(-2.1,2),(-1.1,4.2),(1.9,-2.2),(2,0)]:
    center=xy(u,v)
    rr=max(1,round(.20*S))
    d.ellipse((center[0]-rr,center[1]-rr,center[0]+rr,center[1]+rr),
              fill=tuple(skin_bounce)+(205,))
report={
    "pc42j_far_elbow_backcloth":finish(backing,"pc42j_far_elbow_backcloth"),
    "pc42j_far_rolled_cuff":finish(rim,"pc42j_far_rolled_cuff")
}
data={"phase":"PC42J native painted elbow topology and separate cloth layers",
 "art_type":"hand-authored independently closed sleeve backing and transverse rolled cuff",
 "not_used":"no geometric texture-stripe warp, no alpha taper, no arbitrary rifle offsets",
 "source_color_reference":"approved PC42 male jacket RGB sampled from original reference",
 "joint_coords": {"shoulder":shoulder.tolist(),"elbow":elbow.tolist(),"wrist":wrist.tolist()},
 "layers":report,"visual_qa":"UNREVIEWED; inspect real Godot angle closeups",
 "weapon_contact_changed":False,"apk":None}
(OUT/"pc42j_artwork_manifest.json").write_text(json.dumps(data,indent=2)+"\n")
print("PC42J_AUTHORED_ELBOW_LAYERS_READY "+json.dumps(report))
