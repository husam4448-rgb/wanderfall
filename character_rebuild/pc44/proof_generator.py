"""PC44 independent-limb 2D pose PROOF, not Godot or production art.
Run after source atlas generated: python character_rebuild/pc44/proof_generator.py
"""
from pathlib import Path
import math, json, random
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/"art/male_right"
OUT=ROOT/"pc44/evidence"
S=3
SIZE=(310,315)

def load_parts():
    manifest=json.loads((SRC/"manifest.json").read_text())
    result={}
    for d in manifest["parts"]:
        if d["name"] not in ("head","torso","pelvis","boot_far","boot_near","shin_far","shin_near","thigh_far","thigh_near","rifle"):
            continue
        canvas=Image.new("RGBA",SIZE)
        rect=d["source_rect"]
        canvas.alpha_composite(Image.open(SRC/d["file"]).convert("RGBA"),(rect[0],rect[1]))
        result[d["name"]]=canvas.resize((SIZE[0]*S,SIZE[1]*S))
    return result

def make_segment(a,b,thickness,seed):
    output=Image.new("RGBA",(SIZE[0]*S,SIZE[1]*S))
    ink=ImageDraw.Draw(output)
    ax,ay=a[0]*S,a[1]*S; bx,by=b[0]*S,b[1]*S
    dx,dy=bx-ax,by-ay; L=math.hypot(dx,dy);nx,ny=-dy/L,dx/L
    w0=thickness*S/2;w1=w0*.73
    outline=[(ax+nx*w0,ay+ny*w0),(ax+dx*.48+nx*w0*.95,ay+dy*.48+ny*w0*.95),
      (bx+nx*w1,by+ny*w1),(bx-nx*w1,by-ny*w1),
      (ax+dx*.48-nx*w0*.85,ay+dy*.48-ny*w0*.85),(ax-nx*w0,ay-ny*w0)]
    ink.polygon(outline,fill="#66705a")
    ink.line(outline+[outline[0]],fill="#252922",width=2*S,joint="curve")
    rng=random.Random(seed)
    for j in range(13):
        t=rng.uniform(.08,.88); off=rng.uniform(-.7,.7)
        x=ax+dx*t+nx*off*w0; y=ay+dy*t+ny*off*w0
        ink.line((x-nx*w0*.34,y-ny*w0*.34,x+nx*w0*.35+dx*.045,
           y+ny*w0*.35+dy*.045),fill=(27,35,28,110),width=S)
    for t in (.88,.96):
        x=ax+dx*t;y=ay+dy*t
        ink.line((x-nx*w1*.9,y-ny*w1*.9,x+nx*w1*.9,y+ny*w1*.9),
          fill="#292c24",width=2*S)
    return output

def make_glove(p,radians):
    out=Image.new("RGBA",(SIZE[0]*S,SIZE[1]*S));d=ImageDraw.Draw(out)
    x,y=p[0]*S,p[1]*S;r=5*S
    d.ellipse((x-r,y-r*.7,x+r,y+r*.7),fill="#30302a",outline="#121816",width=2*S)
    for side in (-2,0,2):
        ox=side*S*.4;oy=side*S
        d.line((x+ox,y+oy,x+math.cos(radians)*7*S+ox,
          y-math.sin(radians)*7*S+oy),fill="#4c4b3c",width=2*S)
    return out

def rotate_weapon(image,pivot,degrees):
    px,py=pivot[0]*S,pivot[1]*S; theta=math.radians(degrees)
    co,si=math.cos(theta),math.sin(theta)
    return image.transform(image.size,Image.Transform.AFFINE,
        (co,-si,px*(1-co)+py*si,si,co,py*(1-co)-px*si),Image.Resampling.BICUBIC)

def elbow_between(start,target,upper,lower):
    dx,dy=target[0]-start[0],target[1]-start[1]
    dist=max(.001,min(math.hypot(dx,dy),upper+lower-.001))
    middle=(upper*upper-lower*lower+dist*dist)/(2*dist)
    rise=math.sqrt(max(0,upper*upper-middle*middle))
    return (start[0]+dx*middle/dist-dy*rise/dist,
            start[1]+dy*middle/dist+dx*rise/dist)

def render(parts,degrees):
    ang=math.radians(degrees)
    out=Image.new("RGBA",(SIZE[0]*S,SIZE[1]*S))
    for p in ("boot_far","shin_far","thigh_far","boot_near","shin_near",
       "thigh_near","pelvis","torso","head"):
        out.alpha_composite(parts[p])
    pivot=(149,95)
    def turn(point):
        dx,dy=point[0]-pivot[0],point[1]-pivot[1]
        return (pivot[0]+dx*math.cos(ang)+dy*math.sin(ang),
                pivot[1]-dx*math.sin(ang)+dy*math.cos(ang))
    grip=turn((172,85))
    elbow=elbow_between((91,78),grip,47,42)
    out.alpha_composite(make_segment((91,78),elbow,20,1))
    out.alpha_composite(make_segment(elbow,grip,15,2))
    second_elbow=(147+6*math.sin(ang),99-7*math.sin(ang))
    out.alpha_composite(make_segment((127,82),second_elbow,22,3))
    out.alpha_composite(make_segment(second_elbow,pivot,16,4))
    out.alpha_composite(rotate_weapon(parts["rifle"],pivot,degrees))
    out.alpha_composite(make_glove(grip,ang))
    out.alpha_composite(make_glove(pivot,ang))
    return out

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    art=load_parts()
    angles=(-45,-35,-25,-15,-5,0,5,15,25,35,45)
    for a in angles:
        right=render(art,a)
        right.save(OUT/("pc44_right_%+03d.png"%a))
        left=right.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        left.save(OUT/("pc44_left_%+03d.png"%a))
    print("PC44_ARTICULATED_PROOF_GENERATED count=22 scale=constant visual_qa=PENDING")

if __name__=="__main__":
    main()
