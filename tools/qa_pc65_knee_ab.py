#!/usr/bin/env python3
"""Compare ACTUAL Godot A/B captures, rejecting a cosmetic-only 'stiffness' toggle.
Only original Survival Paradise art and source-free IK geometry are used.
"""
import json,math,sys
from pathlib import Path
import numpy as np
from PIL import Image
base=Path(sys.argv[1]);new=Path(sys.argv[2])
a=json.loads((base/"pose_metrics.json").read_text());b=json.loads((new/"pose_metrics.json").read_text())
A=a["frames"];B=b["frames"]
assert len(A)==len(B)==32
assert abs(a["knee_stiffness"])<1e-4
assert 0.60<=b["knee_stiffness"]<=0.70
assert [x["frame"] for x in A]==[x["frame"] for x in B]==list(range(32))
angles=[];moved=[];pixels=[];hinge_errors=[]
for i,(x,y) in enumerate(zip(A,B)):
    for key in ("hip","knee","ankle","heel"):
        assert np.allclose(x[key],y[key],atol=.0002), f"{key} IK/motion regression frame {i}"
    assert x["stance"]==y["stance"]
    assert abs(x["boot_pitch"]-y["boot_pitch"])<1e-7
    p=np.asarray(x["cloth_vertices"],float).reshape(6,10,2)
    q=np.asarray(y["cloth_vertices"],float).reshape(6,10,2)
    assert np.isfinite(p).all() and np.isfinite(q).all()
    moved.append(float(np.linalg.norm(p-q,axis=-1).max()))
    hip=np.array(x["hip"]);knee=np.array(x["knee"]);ankle=np.array(x["ankle"])
    reference=[]
    for t in (.4,.6):
        reference.append(hip+(knee-hip)*t/.54 if t<=.54 else knee+(ankle-knee)*(t-.54)/.46)
    reference=np.asarray(reference)
    c0=p[2:4,4:6].mean(axis=1)
    c1=q[2:4,4:6].mean(axis=1)
    err0=float(np.linalg.norm(c0-reference,axis=1).sum())
    err1=float(np.linalg.norm(c1-reference,axis=1).sum())
    assert err1<err0*.72, f"Frame {i}: central knee did not become hinge-like"
    hinge_errors.append((err0,err1))
    im0=np.asarray(Image.open(base/f"frame_{i:03d}.png").convert("RGB"),np.int16)
    im1=np.asarray(Image.open(new/f"frame_{i:03d}.png").convert("RGB"),np.int16)
    assert im0.shape==im1.shape==(650,860,3)
    pixels.append(int(np.sum(np.max(abs(im0-im1),axis=-1)>14)))
assert max(moved)>3.0,"No meaningful knee deformation"
assert np.median(pixels)>20,"Render output identical"
result={"frames_per_variant":32,"source":"Native Godot 4.7.2 original-SP art only",
        "knee_stiffness_baseline":a["knee_stiffness"],
        "knee_stiffness_new":b["knee_stiffness"],
        "ankle_heel_hip_and_IK_paths_unchanged":True,
        "maximum_modified_fabric_vertex_motion_px":round(max(moved),3),
        "median_recolored_pixels_per_frame":int(np.median(pixels)),
        "mean_midband_distance_to_rigid_hinge_baseline_px":round(float(np.mean([v[0] for v in hinge_errors])),3),
        "mean_midband_distance_to_rigid_hinge_stiff_px":round(float(np.mean([v[1] for v in hinge_errors])),3),
        "midband_hinge_error_reduction_percent":round((1-np.mean([v[1] for v in hinge_errors])/np.mean([v[0] for v in hinge_errors]))*100,2),
        "technical_compare_pass":True,"visual_approval":"REQUIRED_SEPARATELY"}
(new/"PC65_Knee_AB_Comparison.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
print("PC65_NATIVE_KNEE_STIFFNESS_AB_PASS")
