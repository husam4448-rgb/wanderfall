#!/usr/bin/env python3
"""Independent Survival Paradise animation metrics, no third-party runtime/asset data.
Input frames: time_seconds, feet[left/right]{heel_world, stance},
hands[dominant/support]{actual_world,grip_world}. Units: world pixels.
"""
import json,math,sys
from pathlib import Path

def check(data,slip_limit=2.0,grip_limit=2.0):
    frames=data["frames"]
    if len(frames)<16:raise ValueError("At least 16 frames")
    times=[f["time_seconds"] for f in frames]
    if any(not math.isfinite(t) for t in times) or any(b<=a for a,b in zip(times,times[1:])):
        raise ValueError("Nonincreasing frame times")
    result={"frames":len(frames),"feet":{},"hands":{},"visual_approval":"REQUIRED_SEPARATELY"}
    for side in ("left","right"):
        groups=[];g=[]
        for f in frames:
            foot=f["feet"][side];coords=foot["heel_world"]
            if len(coords)!=2 or not all(map(math.isfinite,coords)):raise ValueError("Invalid heel")
            if foot["stance"]:g.append(coords)
            elif g:groups.append(g);g=[]
        if g:groups.append(g)
        if not groups:raise ValueError("No stance for "+side)
        err=max(math.dist(g[0],p) for g in groups for p in g)
        result["feet"][side]={"max_stance_drift_px":round(err,4),"passes":err<=slip_limit}
    for side in ("dominant","support"):
        err=max(math.dist(f["hands"][side]["actual_world"],f["hands"][side]["grip_world"]) for f in frames)
        if not math.isfinite(err):raise ValueError("Nonfinite hand error")
        result["hands"][side]={"max_grip_error_px":round(err,4),"passes":err<=grip_limit}
    result["numerical_pass"]=all(x["passes"] for k in ("feet","hands") for x in result[k].values())
    return result

if __name__=="__main__":
    output=check(json.loads(Path(sys.argv[1]).read_text()))
    print(json.dumps(output,indent=2))
    sys.exit(0 if output["numerical_pass"] else 1)
