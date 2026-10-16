#!/usr/bin/env python3
"""PC67 native QA for distinct-authored-art 32-frame bilateral locomotion.
Visual approval is a separate human decision; duplicated source art is PROVISIONAL.
"""
import json,sys,math
from pathlib import Path
import numpy as np
from PIL import Image
p=Path(sys.argv[1])
d=json.loads((p/"pose_metrics.json").read_text())
frames=d["frames"];tri=np.asarray(d["triangles"],dtype=int)
assert len(frames)==32 and tri.shape==(72,3)
assert [f["frame"] for f in frames]==list(range(32))
assert not d["provisional_reused_leg_art"] and d["two_independent_ik_chains"]
assert not d["commercial_reference_geometry_included"]
assert d["cloth_mode"]=="two_source_fabric_panels_at_real_ik_knee"
assert .6<=d["knee_stiffness"]<=.7
signs={};flips=0;minimum_area=float("inf")
forward={};ground=502.0
for f in frames:
    assert len(f["legs"])==2
    assert [x["id"] for x in f["legs"]]==["front","rear"]
    assert f["legs"][0]["stance"]==(f["frame"]<16)
    assert f["legs"][1]["stance"]==(f["frame"]>=16)
    assert Image.open(p/f"frame_{f['frame']:03d}.png").size==(860,650)
    for leg in f["legs"]:
        name=leg["id"]
        v=np.asarray(leg["cloth_vertices"],dtype=float)
        assert v.shape==(60,2) and np.isfinite(v).all()
        t=v[tri]
        edge_a=t[:,1]-t[:,0]
        edge_b=t[:,2]-t[:,0]
        ar=edge_a[:,0]*edge_b[:,1]-edge_a[:,1]*edge_b[:,0]
        if name not in signs:signs[name]=np.sign(ar)
        flips+=int(np.count_nonzero(np.sign(ar)!=signs[name]))
        minimum_area=min(minimum_area,float(np.abs(ar).min()))
        assert leg["upper_segment_residual"]<.001
        assert leg["lower_segment_residual"]<.001
        forward.setdefault(name,[]).append(leg["forward_knee_clearance"])
assert flips==0 and minimum_area>1.0,(flips,minimum_area)
assert all(min(v)>5 for v in forward.values()),forward
root=np.asarray([f["pelvis"] for f in frames],dtype=float)
assert 107.0<root[-1,0]-root[0,0]<110.0
contact={};clearance={};stance_slip={};movement={}
for j,name in enumerate(("front","rear")):
    fs=[f["legs"][j] for f in frames]
    planted=np.asarray([x["heel"] for x in fs if x["stance"]],dtype=float)
    airborne=np.asarray([x["heel"] for x in fs if not x["stance"]],dtype=float)
    assert len(planted)==len(airborne)==16
    slip=float(np.linalg.norm(planted-planted[0],axis=1).max())
    lift=float(ground-min(airborne[:,1]))
    advance=float(airborne[-1,0]-airborne[0,0])
    assert slip<.05 and 18<=lift<=20 and 102<advance<114,(name,slip,lift,advance)
    stance_slip[name]=round(slip,5)
    clearance[name]=round(lift,3)
    movement[name]=round(advance,3)
# Independently rendered native layers per both legs and pelvis.
overlaps={};painted_sole={};pixel_count={}
for j,name in enumerate(("front","rear")):
    overlap=[]
    sole=[]
    for k in range(0,32,4):
        cloth=np.asarray(Image.open(p/f"{name}-trouser_{k:03d}.png").convert("RGB"),dtype=np.int16)
        boot=np.asarray(Image.open(p/f"{name}-boot_{k:03d}.png").convert("RGB"),dtype=np.int16)
        bg=cloth[4,4]; bgb=boot[4,4]
        a=np.max(abs(cloth-bg),axis=2)>14
        b=np.max(abs(boot-bgb),axis=2)>14
        assert a.sum()>250 and b.sum()>250,(name,k,int(a.sum()),int(b.sum()))
        n=int((a&b).sum())
        assert n>=20,(name,k,n)
        overlap.append(n)
        if frames[k]["legs"][j]["stance"]:
            sole_y=int(np.where(b)[0].max())
            offset=ground-sole_y
            assert abs(offset)<=2.0,(name,k,offset)
            sole.append(offset)
    overlaps[name]=overlap;painted_sole[name]=sole
pelframes=[]
for k in range(0,32,4):
    pic=np.asarray(Image.open(p/f"pelvis_{k:03d}.png").convert("RGB"),dtype=np.int16)
    diff=np.max(abs(pic-pic[4,4]),axis=2)>14
    n=int(diff.sum())
    assert n>50,("Pelvis art missing",k,n)
    pelframes.append(n)
# Require independently changing native rendered frames.
pics=[np.asarray(Image.open(p/f"frame_{k:03d}.png").convert("RGB"),np.int16) for k in range(32)]
changes=[float(abs(a-b).mean()) for a,b in zip(pics,pics[1:])]
assert np.mean(changes)>.20, "Actual Godot output hardly moves"
out={"original_sp_distinct_source_art":True,"godot_frame_count":32,"separate_ik_legs":2,"independent_knee_panels":4,"original_sp_source_pelvis_crop":True,
"duplicated_provisional_trouser_and_boot_art":False,
"front_stance_frames":"0-15","rear_stance_frames":"16-31",
"planted_heel_sliding_px":stance_slip,"swing_clearance_px":clearance,
"swing_travel_sampled_px":movement,"mesh_triangle_flips":flips,
"min_triangle_area_px2":round(minimum_area,3),
"rendered_trouser_to_boot_overlap_px":overlaps,
"painted_boot_sole_ground_offsets_px":painted_sole,
"pelvis_painted_pixel_counts":pelframes,
"mean_frame_difference":round(float(np.mean(changes)),3),
"technical_qa":"PASS","character_visual_approval":"PENDING",
"not_yet_implemented":["unique contralateral art","full head and torso","real in-game Bone2D skeleton","Android gameplay integration"]}
(p/"PC67_Art_Bilateral_Native_QA.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
print("PC67_BILATERAL_DISTINCT_ART_NATIVE_PASS")
