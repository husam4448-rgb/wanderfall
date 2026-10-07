#!/usr/bin/env python3
"""Strip PC22 articulated-arm QA harness and finalize the validated production runtime."""
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.is_file():
    raise SystemExit("PC22 arm production finalizer: runtime missing")

s=runtime.read_text(encoding="utf-8")
candidate_titles=(
    'PLAYER CHARACTERS V22 ARM CANDIDATE | CANONICAL IK:',
    'PLAYER CHARACTERS V22 HYBRID ARM V3 | PIVOTED RENDERER:',
)
if not any(title in s for title in candidate_titles):
    raise SystemExit("PC22 arm production finalizer requires validated candidate runtime")

# Remove capture-only state, preserving the real player/NPC rig + role selection state.
s=re.sub(
    r'(?ms)^var pc22_arm_capture_dir := ""\n'
    r'var pc22_arm_capture_index := -1\n'
    r'var pc22_arm_states_per_sex := \d+\n'
    r'var pc22_arm_capture_names := PackedStringArray\(\[.*?^\]\)\n',
    '',
    s,
    count=1,
)

# Runtime geometry/sweep/inheritance validators were required by candidate QA,
# but are deliberately absent from the shipped frame loop.
qa_funcs=(
    "_pc22_arm_runtime_check",
    "_pc22_verify_sweep_case",
    "_pc22_verify_runtime_sweep",
    "_pc22_verify_npc_inheritance",
    "_pc22_verify_role_assets",
    "_pc22_apply_arm_capture_state",
    "_pc22_arm_capture_after_draw",
)
for name in qa_funcs:
    pat=r'(?ms)^func '+re.escape(name)+r'\([^\n]*\n.*?(?=^func |\Z)'
    s,n=re.subn(pat,'',s,count=1)
    if n!=1:
        raise SystemExit("PC22 arm production finalizer could not remove QA function: "+name)

# Remove per-frame QA geometry logging calls.
s=re.sub(r'(?m)^\s*_pc22_arm_runtime_check\([^\n]*\)\n','',s)

# Remove QA-on-start and ARM_CAPTURE_DIR screenshot harness, preserving the
# original PLAYER_CAPTURE_DIR baseline behavior that predates this arm project.
ready_block=r'''(?ms)^    if not _pc22_verify_runtime_sweep\(\):\n.*?^    if OS\.has_environment\("PLAYER_CAPTURE_DIR"\):'''
m=re.search(ready_block,s)
if not m:
    raise SystemExit("PC22 arm production finalizer ready QA block missing")
s=s[:m.start()]+'    if OS.has_environment("PLAYER_CAPTURE_DIR"):'+s[m.end():]

# Remove the baseline visual aim guide from production gameplay. It was useful
# during PC22/arm QA but is not character/weapon art.
s,n=re.subn(
    r'(?m)^\s*draw_line\(actor_pos, aim_pos, Color\(0\.85,0\.72,0\.35,0\.18\), 1\.0\)\n',
    '',
    s,
    count=1,
)
if n not in (0,1):
    raise SystemExit("PC22 arm production aim-guide removal ambiguity")

for candidate_title in (
    'title.text = "PLAYER CHARACTERS V22 ARM CANDIDATE | CANONICAL IK:"',
    'title.text = "PLAYER CHARACTERS V22 HYBRID ARM V3 | PIVOTED RENDERER:"',
):
    if candidate_title in s:
        s=s.replace(
            candidate_title,
            'title.text = "PLAYER CHARACTERS V22 | CANONICAL ARTICULATED ARMS:"',
            1,
        )
        break

# Production identity follows the validated arm candidate but is distinct from
# both baseline PC22 (188) and test candidate (189).
ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=190',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC22-ARMS"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC22 arm production Android version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC22-ARMS"',q,count=1)
    sm.write_text(q,encoding="utf-8")

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

required=(
    'PLAYER CHARACTERS V22 | CANONICAL ARTICULATED ARMS:',
    'func _pc22_solve_elbow(',
    'func _pc22_draw_chain(',
    'var pc22_player_arm_rig :=',
    'var pc22_role :=',
    'PC22_ARM_MALE_UPPER_B64',
    'PC22_ARM_FEMALE_FORE_B64',
    'PC22_ARM_RIFLE_STOCK_B64',
    'PC22_ARM_RIFLE_FRONT_B64',
    'PC22_ARM_MALE_ELBOW_B64',
    'PC22_ARM_FEMALE_ELBOW_B64',
    'func _pc22_v3_draw_elbow_gusset(',
)
for needle in required:
    if needle not in s2:
        raise SystemExit("PC22 production runtime missing: "+needle)

for forbidden in (
    'ARM_CAPTURE_DIR',
    'PC22_ARM_CAPTURE_COMPLETE',
    'PC22_RUNTIME_SWEEP_OK',
    'PC22_NPC_INHERITANCE_OK',
    'PC22_ROLE_ASSETS_OK',
    'func _pc22_arm_runtime_check(',
    'draw_line(actor_pos, aim_pos, Color(0.85,0.72,0.35,0.18), 1.0)',
    'PLAYER CHARACTERS V22 ARM CANDIDATE',
    'PLAYER CHARACTERS V22 HYBRID ARM V3',
):
    if forbidden in s2:
        raise SystemExit("PC22 production runtime retained QA/debug marker: "+forbidden)

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC22 production reintroduced old direction system: "+forbidden)

print("PC22 canonical articulated arms finalized for production")
print("QA capture/sweep hooks removed; two-side canonical rig retained")
print("Production Android version: 190 / 0.21.0-PC22-ARMS")
