#!/usr/bin/env python3
"""PC27: alternate foot swing and planted stance in the original one-piece leg.

Keeps source leg/boot textures and hip geometry, fixes phase cancellation
caused by large static ankle offset, and compensates body bob. No new character
sprites or weapon/arm changes. PC27_LEGACY_GAIT=1 allows exact visual A/B.
Run AFTER PC26 patch.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=p.read_text(encoding="utf-8")
anchor='''    var hip := base + Vector2(side * hip_span, hip_y)
    var knee := base + Vector2(side * knee_span + stride * 0.22, (18.8 if female_mode else 18.0))
    var ankle := base + Vector2(side * ankle_span + stride * 0.62, (26.4 if female_mode else 25.0) - min(abs(stride) * 0.10, 1.8))
'''
if s.count(anchor)!=1:
    raise SystemExit("PC27 source leg IK targets not found uniquely")
new='''    var hip := base + Vector2(side * hip_span, hip_y)
    var knee := base + Vector2(side * knee_span + stride * 0.22, (18.8 if female_mode else 18.0))
    var ankle := base + Vector2(side * ankle_span + stride * 0.62, (26.4 if female_mode else 25.0) - min(abs(stride) * 0.10, 1.8))
    # PC27: the two feet now move through opposing full strides around the
    # same body center. Large static side offsets previously cancelled one
    # half of the sine cycle, leaving a short shuffle then huge split.
    # Only the swinging foot lifts; planted stance compensates the body's
    # shared bob, preventing both feet from rising simultaneously.
    if OS.get_environment("PC27_LEGACY_GAIT") != "1" and move_vec.length() > 0.05:
        var shared_bob: float = absf(sin(step_phase))*(2.2 if running else 1.3)
        var swing_lift: float = maxf(0.0,stride)*(0.20 if running else 0.21)
        var knee_base_y: float = 18.8 if female_mode else 18.0
        var ankle_base_y: float = 26.4 if female_mode else 25.0
        knee = base+Vector2((side*knee_span*0.44+stride*0.44)*dir_sign,
            knee_base_y+shared_bob*0.42-swing_lift*0.56)
        ankle = base+Vector2((side*0.72+stride*0.92)*dir_sign,
            ankle_base_y+shared_bob-swing_lift)
'''
s=s.replace(anchor,new,1)
p.write_text(s,encoding="utf-8")
if s.count("PC27_LEGACY_GAIT")!=1:
    raise SystemExit("PC27 visual comparator regression")
ep=root/"export_presets.cfg"
ex=ep.read_text(encoding="utf-8")
if ex.count("version/code=196")!=1 or ex.count('version/name="0.22.0-PC26-GAIT-EVIDENCE"')!=1:
    raise SystemExit("PC27 input APK version is not PC26")
ex=ex.replace("version/code=196","version/code=197",1)
ex=ex.replace('version/name="0.22.0-PC26-GAIT-EVIDENCE"',
              'version/name="0.22.0-PC27-BALANCED-GAIT"',1)
ep.write_text(ex,encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.is_file():
    x=save.read_text(encoding="utf-8")
    if x.count('const GAME_VERSION := "0.22.0-PC26-GAIT-EVIDENCE"')!=1:
        raise SystemExit("PC27 input save version is not PC26")
    save.write_text(x.replace('const GAME_VERSION := "0.22.0-PC26-GAIT-EVIDENCE"',
                              'const GAME_VERSION := "0.22.0-PC27-BALANCED-GAIT"',1),encoding="utf-8")
print("PC27 alternating planted/swing-foot gait enabled; legacy AB preserved")
