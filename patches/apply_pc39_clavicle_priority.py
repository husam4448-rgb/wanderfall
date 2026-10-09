#!/usr/bin/env python3
"""PC39 stock->shoulder constraint precedence over arm reach adjustment.

PC38 physically calibrated the rifle butt to the true rear-shoulder anchor
then broke that contact by translating the whole rifle to make the support
wrist reachable. PC39 instead preserves gun/butt geometry and flexes the
body-owned FRONT clavicle/shoulder (up to a measured 2.35 world-unit reach
adjustment) so the painted support hand stays on the handguard. Both arms
are solved by existing PC23 two-bone IK after this shared shoulder state.

Unsupported >2.35 joint reach gets a bounded residual and must fail PC39
feasibility QA; do not falsely approve it. No weapon art and no pistol change.

PC39_LEGACY_FRONT_CLAVICLE=1 reproduces precisely the previous PC38
projection for actual A/B Godot capture.
Apply AFTER PC38 stock-to-shoulder patch.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=runtime.read_text(encoding="utf8")
a='''        if pc38_excess>0.0:
            # Project target into support-arm reach disk. Whole rifle and both
            # palms move together; no elongated arm or sliding support palm.
            pc38_ideal_grip -= (pc38_support_wrist-pc22_front_shoulder).normalized()*pc38_excess
'''
b='''        if pc38_excess>0.0:
            var pc39_to_hand: Vector2 = (pc38_support_wrist-pc22_front_shoulder).normalized()
            if OS.get_environment("PC39_LEGACY_FRONT_CLAVICLE") == "1":
                # Exact previous PC38 visual baseline, for direct Godot A/B.
                pc38_ideal_grip -= pc39_to_hand*pc38_excess
            else:
                # The butt/stock *must remain at the rear shoulder*. Do not
                # shift the gun to compensate for front-arm reach: relocate the
                # actual body-owned support clavicle first. Both wrist targets
                # are kept on the measured visual trigger/handguard contacts.
                var pc39_clavicle_shift: float = minf(pc38_excess,2.35)
                pc22_front_shoulder += pc39_to_hand*pc39_clavicle_shift
                if pc38_excess>2.35:
                    # Residual indicates a requested posture this skeleton
                    # still cannot solve. Preserve bone reach, but do NOT
                    # silently treat this pose as an approved rifle stance.
                    pc38_ideal_grip -= pc39_to_hand*(pc38_excess-2.35)
'''
if s.count(a)!=1:raise SystemExit("PC39 fails closed: PC38 source reach fix anchor missing or duplicated")
s=s.replace(a,b,1)
runtime.write_text(s,encoding="utf8")
if "pc22_front_shoulder += pc39_to_hand*pc39_clavicle_shift" not in s:
    raise SystemExit("PC39 source rewrite validation failed")
print("PC39 prioritizes painted rifle butt-to-rear-shoulder constraint; front anatomical clavicle resolves support IK reach.")
print("PC39_LEGACY_FRONT_CLAVICLE=1 restores PC38 exactly for 100-frame A/B Godot evidence.")
