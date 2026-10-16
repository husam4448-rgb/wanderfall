#!/usr/bin/env python3
"""PC57D original Godot native frame checks. Does not replace human visual QA."""
import json, math, sys
from pathlib import Path
from pc57_motion_acceptance import check as grip_and_stance

def evaluate(path):
    frames=json.loads(Path(path).read_text())["frames"]
    if len(frames)!=32:
        raise AssertionError("Require a complete 32-frame cycle")
    parent=grip_and_stance({"frames":frames},slip_limit=1.0,grip_limit=0.25)
    assert parent["numerical_pass"],"Foot stance or rifle grip disconnected: "+str(parent)
    positions={side:[] for side in ("left","right")}
    knees={side:[] for side in ("left","right")}
    contacts={side:[] for side in ("left","right")}
    reach={}
    body=[]
    for frame in frames:
        pelvis=frame["body"]["pelvis_world"]
        body.append(pelvis)
        for side in ("left","right"):
            heel=frame["feet"][side]["heel_world"]
            j=frame["gait"]
            h=j["hip_"+side];k=j["knee_"+side];a=j["ankle_"+side]
            dx=a[0]-h[0];dy=a[1]-h[1]
            cross=dx*(k[1]-h[1])-dy*(k[0]-h[0])
            gap=-cross/math.hypot(dx,dy)
            if gap<=6.0:raise AssertionError(f"{side} knee bent backward/straight: clearance {gap:.2f}")
            knees[side].append(gap)
            positions[side].append(heel)
            contacts[side].append(bool(frame["feet"][side]["stance"]))
            if frame["gait"]["ik_error_"+side]>0.05:raise AssertionError(side+" unreachable IK target")
        if sum(1 for side in ("left","right") if frame["feet"][side]["stance"])!=1:
            raise AssertionError("Incorrect stance alternation")
    max_root_x_step=max(b[0]-a[0] for a,b in zip(body,body[1:]))
    min_root_x_step=min(b[0]-a[0] for a,b in zip(body,body[1:]))
    assert min_root_x_step>0 and max_root_x_step<5.0,"Bad pelvis horizontal continuity"
    bob=max(v[1] for v in body)-min(v[1] for v in body)
    assert 1.3<=bob<=4.0,"No believable/controlled vertical weight shift"
    max_heel_step=0.0;clearance={}
    for side in ("left","right"):
        assert sum(contacts[side])==16,"Stance durations must be equal"
        assert all(contacts[side][:16]) if side=="left" else all(contacts[side][16:]),"Wrong alternating foot"
        max_heel_step=max(max_heel_step,max(math.dist(a,b) for a,b in zip(positions[side],positions[side][1:])))
        clearance[side]=max(490.0-pos[1] for i,pos in enumerate(positions[side]) if not contacts[side][i])
        assert clearance[side]>=15.0 and clearance[side]<=22.0,"Bad swing clearance"
        assert math.dist([positions[side][0][0]-body[0][0],positions[side][0][1]-body[0][1]],
                         [positions[side][-1][0]-body[-1][0],positions[side][-1][1]-body[-1][1]])<9.0,"Cycle seam discontinuity"
    assert max_heel_step<14.0,"Excessive per-frame foot teleport"
    return {"technical_pass":True,"frames":len(frames),"stance":parent["feet"],"grips":parent["hands"],
      "minimum_anterior_knee_clearance_px":{x:round(min(v),3) for x,v in knees.items()},
      "swing_clearance_px":{x:round(v,3) for x,v in clearance.items()},
      "pelvis_bob_px":round(bob,3),"pelvis_dx_range":[round(min_root_x_step,3),round(max_root_x_step,3)],
      "max_heel_travel_between_frames_px":round(max_heel_step,3),
      "visual_approval":"REQUIRED"}

if __name__=="__main__":
    result=evaluate(sys.argv[1])
    print(json.dumps(result,indent=2))
    print("PC57D_NATIVE_ANATOMICAL_GAIT_PASS")
