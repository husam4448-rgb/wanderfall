#!/usr/bin/env python3
"""PC61 public QA unit tests use only original GENERATED fixtures.
NEVER place proprietary B2B source PNGs in CI.
"""
import tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from qa_pc61_mesh_art_compatibility import inspect,PARTS

with tempfile.TemporaryDirectory() as t:
    p=Path(t);ref=p/"reference";candidate=p/"candidate"
    ref.mkdir();candidate.mkdir()
    for n in PARTS:
        a=Image.new("RGBA",(80,120),(0,0,0,0))
        ImageDraw.Draw(a).ellipse((9,5,69,116),fill=(43,65,68,255))
        a.save(ref/(n+".png"))
        a.save(candidate/(n+".png"))
    assert inspect(ref,candidate)["technical_pass"],"Exact fit must pass"
    bad=Image.new("RGBA",(80,120),(0,0,0,0))
    ImageDraw.Draw(bad).ellipse((37,5,69,116),fill=(43,65,68,255))
    bad.save(candidate/"L_leg01.png")
    report=inspect(ref,candidate)
    assert not report["technical_pass"],"Missing thigh region must fail"
    part=next(x for x in report["results"] if x["name"]=="L_leg01")
    assert part["paint_coverage"]<0.70,part
    # Also explicitly reject excess paint outside usable attachment silhouette.
    (candidate/"L_leg01.png").write_bytes((ref/"L_leg01.png").read_bytes())
    wide=Image.new("RGBA",(80,120),(95,95,95,255))
    wide.save(candidate/"R_arm02.png")
    result=inspect(ref,candidate)
    assert not result["technical_pass"],"Excess alpha must fail"
print("PC61_ENVELOPE_QA_PASS accepted_valid=1 rejected_missing_fabric=1 rejected_bleed=1")
