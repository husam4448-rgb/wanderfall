#!/usr/bin/env python3
"""Render magnified frame-by-frame QA evidence for the PC22 canonical articulated arms."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, math, sys

repo=Path(sys.argv[1] if len(sys.argv)>1 else ".")
base=repo/"assets/authored2d/unified_character"
arms=base/"arms"
qa=arms/"qa"
qa.mkdir(parents=True,exist_ok=True)
canonical=json.loads((base/"canonical_pc22.json").read_text(encoding="utf-8"))

def load_spec(sex):
    return json.loads((base/f"core/{sex}/arm_spec.json").read_text(encoding="utf-8"))

def add(a,b): return (a[0]+b[0],a[1]+b[1])
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def mul(a,k): return (a[0]*k,a[1]*k)
def length(v): return math.hypot(v[0],v[1])
def rot(v,a):
    x,y=v; return (x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a))
def pose(v,a,sign):
    return rot((v[0]*sign,v[1]),a*sign)

def solve(shoulder,wrist,L1,L2,prev=None):
    d=sub(wrist,shoulder); dist=length(d)
    if dist<=abs(L1-L2) or dist>=L1+L2:
        raise ValueError("unreachable wrist target")
    u=(d[0]/dist,d[1]/dist)
    along=(L1*L1-L2*L2+dist*dist)/(2*dist)
    h=math.sqrt(max(0,L1*L1-along*along))
    p=(-u[1],u[0])
    c1=add(add(shoulder,mul(u,along)),mul(p,h))
    c2=add(add(shoulder,mul(u,along)),mul(p,-h))
    if prev is None: return max((c1,c2),key=lambda q:q[1])
    return min((c1,c2),key=lambda q:length(sub(q,prev)))

def fit(img,size_px):
    return img.resize((max(1,int(size_px[0])),max(1,int(size_px[1]))),Image.Resampling.LANCZOS)

def paste_center(dst,img,center):
    x=int(round(center[0]-img.width/2)); y=int(round(center[1]-img.height/2))
    dst.alpha_composite(img,(x,y))

def paste_sprite(dst,img,center,size,scale,flip=False,rotation=0.0):
    w=max(1,int(round(size[0]*scale))); h=max(1,int(round(size[1]*scale)))
    s=fit(img,(w,h))
    if flip: s=s.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if abs(rotation)>1e-7:
        s=s.rotate(-math.degrees(rotation),resample=Image.Resampling.BICUBIC,expand=True)
    paste_center(dst,s,center)

def paste_segment(dst,img,a,b,width,scale,overlap):
    d=sub(b,a); seglen=length(d)
    mid=((a[0]+b[0])*0.5,(a[1]+b[1])*0.5)
    w=max(2,int(round(width*scale)))
    h=max(3,int(round((seglen+2*overlap)*scale)))
    s=fit(img,(w,h))
    theta=math.atan2(d[1],d[0])
    # Source segment is vertical. Rotation 90-theta visually aligns its long axis to a->b.
    s=s.rotate(90.0-math.degrees(theta),resample=Image.Resampling.BICUBIC,expand=True)
    paste_center(dst,s,mid)

def asset(sex,name):
    return Image.open(arms/sex/name).convert("RGBA")

def body_asset(sex,name):
    return Image.open(base/f"core/{sex}/{name}").convert("RGBA")

def actor_points(sex,spec,aim_deg=0.0,weapon="rifle",movement=None,recoil=0.0,face=1):
    a=math.radians(aim_deg)
    basep=(0.0,0.0)
    if movement:
        basep=(movement.get("sway",0.0),-movement.get("bob",0.0))
    pivot=add(basep,(spec["weapon_socket"][0]*face,spec["weapon_socket"][1]))
    if recoil:
        pivot=add(pivot,pose((-1.45*recoil,0),a,face))
    rear=add(basep,(spec["shoulder_rear"][0]*face,spec["shoulder_rear"][1]))
    front=add(basep,(spec["shoulder_front"][0]*face,spec["shoulder_front"][1]))
    dom=add(pivot,pose(tuple(spec["dominant_hand_grip_socket"]),a,face))
    sup=add(pivot,pose(tuple(spec["support_hand_grip_socket"]),a,face))
    if weapon=="rifle":
        sup=add(sup,pose((0,spec["support_hand_vertical_offset_right"] if face>0 else spec["support_hand_vertical_offset_left"]),a,face))
    elif weapon=="pistol_two":
        sup=add(dom,pose((3.2,1.8),a,face))
    else:
        # Natural free support hand for one-handed pistol.
        sup=add(front,(1.0*face,18.0))
    e1=solve(rear,dom,spec["upper_arm_length"],spec["forearm_length"])
    e2=solve(front,sup,spec["upper_arm_length"],spec["forearm_length"])
    return {"base":basep,"pivot":pivot,"rear_shoulder":rear,"front_shoulder":front,
            "dominant_wrist":dom,"support_wrist":sup,"dominant_elbow":e1,"support_elbow":e2,"angle":a}

def fk_free_arm(shoulder,L1,L2,upper_deg,flex_deg,face):
    ua=math.radians(upper_deg if face>0 else 180-upper_deg)
    # Image coordinates: screen-down positive y.
    elbow=add(shoulder,(math.cos(ua)*L1,math.sin(ua)*L1))
    fa=ua+math.radians(flex_deg*face)
    wrist=add(elbow,(math.cos(fa)*L2,math.sin(fa)*L2))
    return elbow,wrist

def render_pose(sex,label,kind,aim=0.0,phase=0.0,recoil=0.0,tile=420):
    spec=load_spec(sex); face=1
    scale=8.0
    origin=(tile*0.44,tile*0.55)
    def px(p): return (origin[0]+p[0]*scale,origin[1]+p[1]*scale)

    im=Image.new("RGBA",(tile,tile),(22,28,29,255))
    torso=body_asset(sex,"torso_base.png")
    head=body_asset(sex,"head_right.png")
    rearleg=body_asset(sex,"leg_rear_base.png")
    frontleg=body_asset(sex,"leg_front_base.png")
    upper=asset(sex,f"SP_PC22_{sex.title()}_UpperArm_Right.png")
    fore=asset(sex,f"SP_PC22_{sex.title()}_Forearm_Right.png")
    hdom=asset(sex,f"SP_PC22_{sex.title()}_Hand_Dominant_Right.png")
    hsup=asset(sex,f"SP_PC22_{sex.title()}_Hand_Support_Right.png")

    stride=0.0
    if kind=="walk": stride=5.0*math.sin(phase)
    if kind=="run": stride=8.0*math.sin(phase)
    bob=(1.3 if kind=="walk" else 2.2 if kind=="run" else 0.0)*abs(math.sin(phase))*0.45
    basep=(0,-bob)

    # Legs behind body.
    legsize=canonical[sex]["leg_size"]
    hip=canonical[sex]["hip_span"]
    paste_sprite(im,rearleg,px(add(basep,(-hip,-stride*0.05+12))),legsize,scale)
    paste_sprite(im,frontleg,px(add(basep,(hip,stride*0.05+12))),legsize,scale)

    weapon_mode=None
    if kind.startswith("pistol"): weapon_mode="pistol"
    if kind.startswith("rifle") or kind in ("recoil","walk_aim"): weapon_mode="rifle"

    if weapon_mode:
        pts=actor_points(sex,spec,aim,weapon_mode,movement={"bob":bob},recoil=recoil,face=face)
        rear=(pts["rear_shoulder"],pts["dominant_elbow"],pts["dominant_wrist"])
        front=(pts["front_shoulder"],pts["support_elbow"],pts["support_wrist"])
    elif kind=="elbow90":
        sh1=add(basep,tuple(spec["shoulder_rear"]))
        sh2=add(basep,tuple(spec["shoulder_front"]))
        e1,w1=fk_free_arm(sh1,spec["upper_arm_length"],spec["forearm_length"],55,90,face)
        e2,w2=fk_free_arm(sh2,spec["upper_arm_length"],spec["forearm_length"],105,-35,face)
        rear=(sh1,e1,w1); front=(sh2,e2,w2)
        pts={"angle":0,"pivot":(0,0)}
    else:
        sh1=add(basep,tuple(spec["shoulder_rear"])); sh2=add(basep,tuple(spec["shoulder_front"]))
        amp=0.0
        if kind=="walk": amp=20*math.sin(phase)
        if kind=="run": amp=34*math.sin(phase)
        e1,w1=fk_free_arm(sh1,spec["upper_arm_length"],spec["forearm_length"],82-amp,20+abs(amp)*0.30,face)
        e2,w2=fk_free_arm(sh2,spec["upper_arm_length"],spec["forearm_length"],82+amp,20+abs(amp)*0.30,face)
        rear=(sh1,e1,w1); front=(sh2,e2,w2)
        pts={"angle":0,"pivot":(0,0)}

    ov=spec["joint_overlap_each_end"]
    # Rear arm first, torso covers shoulder overlap.
    paste_segment(im,upper,px(rear[0]),px(rear[1]),spec["upper_arm_width"]*scale/scale,1.0,ov*scale/scale)
    paste_segment(im,fore,px(rear[1]),px(rear[2]),spec["forearm_width"]*scale/scale,1.0,ov*scale/scale)

    torso_center=add(basep,tuple(canonical[sex]["torso_center"]))
    paste_sprite(im,torso,px(torso_center),canonical[sex]["torso_size"],scale)

    # Front chain over torso but torso overlap remains covered by alpha-heavy shoulder region.
    paste_segment(im,upper,px(front[0]),px(front[1]),spec["upper_arm_width"],scale,ov)
    paste_segment(im,fore,px(front[1]),px(front[2]),spec["forearm_width"],scale,ov)

    neck=canonical[sex]["neck_socket"]
    head_center=add(basep,(neck[0],neck[1]-canonical[sex]["head_size"][1]*0.22))
    paste_sprite(im,head,px(head_center),canonical[sex]["head_size"],scale)

    if weapon_mode:
        p=pts["pivot"]; a=pts["angle"]
        # QA weapon is deliberately simple; it marks exact PC22 grip relationship.
        d=ImageDraw.Draw(im)
        def q(v): return px(add(p,pose(v,a,face)))
        stock=q((-3,0)); muzzle=q((24,0)); grip0=q((3,2)); grip1=q((2,8))
        d.line([stock,muzzle],fill=(48,53,55,255),width=max(3,int(scale*1.3)))
        d.line([grip0,grip1],fill=(43,37,34,255),width=max(3,int(scale*1.1)))

    # Hands are distinct assets and always land on solved wrist targets.
    for hand,w in ((hdom,rear[2]),(hsup,front[2])):
        sz=spec["hand_size"]
        paste_sprite(im,hand,px(w),sz,scale,rotation=pts.get("angle",0))

    # QA joint markers (not production): small rings aid magnified inspection.
    d=ImageDraw.Draw(im)
    for p in (rear[0],rear[1],rear[2],front[0],front[1],front[2]):
        x,y=px(p); r=2
        d.ellipse((x-r,y-r,x+r,y+r),outline=(238,188,74,220),width=1)

    d.rectangle((0,tile-32,tile, tile),fill=(10,13,14,220))
    d.text((10,tile-25),label,fill=(235,235,228,255))
    return im

poses=[
 ("Neutral","idle",0,0,0),
 ("Elbow 90°","elbow90",0,0,0),
 ("Walk A","walk",0,math.pi/2,0),
 ("Walk B","walk",0,3*math.pi/2,0),
 ("Run A","run",0,math.pi/2,0),
 ("Run B","run",0,3*math.pi/2,0),
 ("Pistol 0°","pistol",0,0,0),
 ("Pistol +60°","pistol",60,0,0),
 ("Pistol -60°","pistol",-60,0,0),
 ("Rifle 0°","rifle",0,0,0),
 ("Rifle +60°","rifle",60,0,0),
 ("Rifle -60°","rifle",-60,0,0),
 ("Recoil","recoil",0,0,1),
 ("Aim max up","rifle",math.degrees(canonical["shared_motion"]["aim_angle_clamp_rad"]),0,0),
 ("Aim max down","rifle",-math.degrees(canonical["shared_motion"]["aim_angle_clamp_rad"]),0,0),
 ("Walk + aim","walk_aim",35,math.pi/2,0),
]

for sex in ("male","female"):
    frames=[render_pose(sex,*p) for p in poses]
    cols=4; rows=4; tile=420
    sheet=Image.new("RGBA",(cols*tile,rows*tile),(15,19,20,255))
    for i,fr in enumerate(frames):
        sheet.alpha_composite(fr,((i%cols)*tile,(i//cols)*tile))
    sheet.convert("RGB").save(qa/f"{sex}_arm_contact_sheet.jpg",quality=94,subsampling=0)

    # Magnified crops for shoulder/elbow/wrist checks from representative rifle-horizontal frame.
    ref=frames[9]
    # Keep three nested scales as explicit review evidence.
    ref.resize((840,840),Image.Resampling.NEAREST).convert("RGB").save(qa/f"{sex}_inspection_2x.jpg",quality=95)
    ref.resize((1260,1260),Image.Resampling.NEAREST).convert("RGB").save(qa/f"{sex}_inspection_max.jpg",quality=95)

    # Optional animated QA: walk and aim sweep.
    walk=[render_pose(sex,"Walk", "walk",0, i*math.pi/6,0,300) for i in range(12)]
    walk[0].save(qa/f"{sex}_walk.gif",save_all=True,append_images=walk[1:],duration=70,loop=0,disposal=2)

    aim=[]
    clamp=math.degrees(canonical["shared_motion"]["aim_angle_clamp_rad"])
    for i in range(25):
        t=i/24
        ang=-clamp+2*clamp*t
        aim.append(render_pose(sex,"Aim sweep","rifle",ang,0,0,300))
    aim[0].save(qa/f"{sex}_aim_sweep.gif",save_all=True,append_images=aim[1:],duration=60,loop=0,disposal=2)

    rec=[]
    for i in range(10):
        rr=max(0,1-i/9)
        rec.append(render_pose(sex,"Rifle recoil","recoil",0,0,rr,300))
    rec[0].save(qa/f"{sex}_rifle_recoil.gif",save_all=True,append_images=rec[1:],duration=55,loop=0,disposal=2)

print("PC22_ARM_VISUAL_QA_RENDERED")
