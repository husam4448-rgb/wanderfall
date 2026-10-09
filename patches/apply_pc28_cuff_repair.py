#!/usr/bin/env python3
"""PC28 follow-up: textured ankle cuff repair without moving foot sockets.

Fixes visual shin-to-boot gap caused by source texture transparent margins.
Preserves the two-bone IK and original art. Set PC28_CUFF_LEGACY=1 for A/B.
Run AFTER apply_pc28_articulated_knees.py.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=runtime.read_text(encoding="utf-8")
old='''    draw_texture_rect_region(tex,Rect2(-cloth_width*0.42,-0.95,cloth_width*0.84,f.length()+1.85),shin_source)
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)
'''
new='''    # Extend lower art slightly beneath the boot collar, keeping the actual
    # boot socket fixed on the original stance/swing path.
    var cuff_ext: float = 0.0 if OS.get_environment("PC28_CUFF_LEGACY") == "1" else 4.0
    draw_texture_rect_region(tex,Rect2(-cloth_width*0.42,-0.95,cloth_width*0.84,f.length()+1.85+cuff_ext),shin_source)
    if cuff_ext > 0.0 and f.length() > 0.01:
        # Small secondary seam-free ankle strip samples approved pant fabric.
        # This deliberately overlaps the boot top, concealing transparency
        # at the bottom of the original trouser sheet.
        var bootward: Vector2 = f.normalized()
        var cuff_start: Vector2 = ankle-bootward*1.45
        draw_set_transform(cuff_start,f.angle()-PI*0.5,Vector2(flip,1.0))
        draw_texture_rect_region(tex,Rect2(-cloth_width*0.34,-0.3,cloth_width*0.68,4.65),
            Rect2(0.0,sh*0.765,sw,sh*0.19))
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)
'''
if s.count(old)!=1:
    raise SystemExit("PC28 cuff source anchor was not found uniquely")
runtime.write_text(s.replace(old,new,1),encoding="utf-8")
e=root/"export_presets.cfg"
q=e.read_text(encoding="utf-8")
if q.count("version/code=198")!=1 or q.count('version/name="0.22.0-PC28-ARTICULATED-KNEES"')!=1:
    raise SystemExit("PC28 expected APK version 198")
q=q.replace("version/code=198","version/code=199",1)
q=q.replace('version/name="0.22.0-PC28-ARTICULATED-KNEES"',
            'version/name="0.22.0-PC28-KNEE-CUFF-REPAIR"',1)
e.write_text(q,encoding="utf-8")
sm=root/"scripts/save/save_manager.gd"
if sm.is_file():
    v=sm.read_text(encoding="utf-8")
    base='const GAME_VERSION := "0.22.0-PC28-ARTICULATED-KNEES"'
    if v.count(base)!=1:
        raise SystemExit("PC28 cuff save version input mismatch")
    sm.write_text(v.replace(base,
           'const GAME_VERSION := "0.22.0-PC28-KNEE-CUFF-REPAIR"',1),encoding="utf-8")
print("PC28 cuff candidate ready. Original ankle and foot IK unchanged; PC28_CUFF_LEGACY=1 for A/B.")
