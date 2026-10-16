#!/usr/bin/env python3
"""PC64 actual Godot original-art pair acceptance gate.
Numerical PASS never overrides independently inspected visual FAIL.
"""
import json,math,sys
from pathlib import Path
import numpy as np
from PIL import Image

folder=Path(sys.argv[1])
data=json.loads((folder/"pose_metrics.json").read_text())
frames=data["frames"];triangles=np.asarray(data["triangles"],dtype=int)
assert len(frames)==32
assert triangles.shape==(90,3)
assert [f["frame"] for f in frames]==list(range(32))
assert not data["commercial_reference_geometry_included"]
all_images=[]
reference_signs=None
flips=0;min_area=1e9
forward=[]
for f in frames:
    p=np.asarray(f["cloth_vertices"],dtype=float)
    assert p.shape==(60,2) and np.isfinite(p).all()
    triangles_xyz=p[triangles]
    twice_area=(triangles_xyz[:,1,0]-triangles_xyz[:,0,0])*(triangles_xyz[:,2,1]-triangles_xyz[:,0,1])-(triangles_xyz[:,2,0]-triangles_xyz[:,0,0])*(triangles_xyz[:,1,1]-triangles_xyz[:,0,1])
    if reference_signs is None:reference_signs=np.sign(twice_area)
    flips+=int(np.count_nonzero((np.sign(twice_area)!=reference_signs)&(abs(twice_area)>.01)))
    min_area=min(min_area,float(abs(twice_area).min()))
    forward.append(float(f["forward_knee_clearance"]))
    assert f["upper_segment_residual"]<.001 and f["lower_segment_residual"]<.001,"Bone length error"
    png=folder/f"frame_{f['frame']:03d}.png"
    assert png.exists(),png
    image=np.asarray(Image.open(png).convert("RGB"),dtype=np.uint8)
    assert image.shape==(650,860,3)
    all_images.append(image)
assert flips==0,f"Mesh inverted triangle(s): {flips}"
assert min(forward)>5,"Knee is backward or nearly locked at angle"

# Test ACTUAL heel-world positions from the rigid boot pivot and its rendered sole.
stance=np.asarray([f["heel"] for f in frames if f["stance"]],dtype=float)
assert len(stance)==16
max_slip=float(np.linalg.norm(stance-stance[0],axis=1).max())
assert max_slip<.05,"Stance heel slid by %.2fpx"%max_slip
swing=np.asarray([f["heel"] for f in frames if not f["stance"]],dtype=float)
swing_clearance=float(stance[0,1]-np.min(swing[:,1]))
assert 17<swing_clearance<21,"Abnormal swing foot lift"
step=float(swing[-1,0]-stance[0,0])
assert 50<step<57,"Unexpected step length"

# Independently captured actual Godot layers for eight key phases.
# Distinguish backgrounds by per-layer pixels from the sampled empty corner.
overlaps=[]; connectedness=[]
for frame in range(0,32,4):
    thigh=np.asarray(Image.open(folder/f"trousers_{frame:03d}.png").convert("RGB"),dtype=np.int16)
    boot=np.asarray(Image.open(folder/f"boot_{frame:03d}.png").convert("RGB"),dtype=np.int16)
    bg_thigh=thigh[5,5,:]
    bg_boot=boot[5,5,:]
    # Source textures use dark cloth; compare each channel with its own bg.
    amask=np.max(np.abs(thigh-bg_thigh),axis=2)>14
    bmask=np.max(np.abs(boot-bg_boot),axis=2)>14
    overlap=int(np.count_nonzero(amask & bmask))
    overlaps.append(overlap)
    assert amask.sum()>250 and bmask.sum()>250,"Missing actual painted part"
    connectedness.append(overlap>0)
assert all(connectedness),"Rendered trouser / boot gap in at least one of eight phases"

movement=float(np.mean([np.abs(b.astype("int16")-a.astype("int16")).mean() for a,b in zip(all_images,all_images[1:])]))
assert movement>.15,"Native frames look unchanged"
result={"capture_frames":32,"independent_body_parts":2,"native_Godot":True,
    "commercial_geometry_committed":False,
    "max_planted_heel_sliding_px":round(max_slip,4),
    "swing_foot_lift_px":round(swing_clearance,4),
    "step_length_px":round(step,4),
    "smallest_forward_knee_clearance_px":round(min(forward),4),
    "inverted_mesh_triangles":flips,
    "minimum_triangle_area":round(min_area,4),
    "rendered_ankle_overlap_px_each_phase":overlaps,
    "mean_interframe_rgb_change":round(movement,4),
    "numerical_pass":True,"visual_approval":"PENDING ACTUAL GIF INSPECTION"}
(folder/"PC64_Pair_Native_QA.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
print("PC64_TWO_ORIGINAL_PARTS_NUMERICAL_PASS")
