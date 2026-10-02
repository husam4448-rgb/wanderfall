#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).parent
runtime = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
src_patch = patch_dir / "apply_v0210d2d64_female_head_valid_png.py"

if not runtime.exists():
    raise SystemExit("D2D.66 requires D2D.62 runtime")
if not src_patch.exists():
    raise SystemExit("D2D.66 source head patch missing")

# Extract the already validated female PNG bytes from D2D.64.
src = src_patch.read_text(encoding="utf-8")
m = re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"', src)
if not m:
    raise SystemExit("D2D.66 could not extract validated female head PNG")
female_head_b64 = m.group(1)
if len(female_head_b64) < 1000:
    raise SystemExit("D2D.66 extracted female head data is unexpectedly short")

s = runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.62 FEMALE PROPORTION FIX:"' not in s:
    raise SystemExit("D2D.66 baseline title anchor missing")

# HEAD ONLY. Replace exactly one constant line by line; do not use regex replacement
# strings, so the Base64 data cannot be interpreted as replacement syntax.
lines = s.splitlines()
hits = 0
for i, line in enumerate(lines):
    if line.startswith("const FEMALE_HEAD_B64 :="):
        lines[i] = 'const FEMALE_HEAD_B64 := "' + female_head_b64 + '"'
        hits += 1
if hits != 1:
    raise SystemExit(f"D2D.66 expected one FEMALE_HEAD_B64 constant, found {hits}")

s = "\n".join(lines) + ("\n" if s.endswith("\n") else "")
s = s.replace(
    'title.text = "D2D.62 FEMALE PROPORTION FIX:"',
    'title.text = "D2D.66 FEMALE HEAD VERIFIED:"',
    1
)

# Verify the runtime still contains the original female loader and female draw branch.
if 'tex_head_female = _texture_from_embedded_png(FEMALE_HEAD_B64)' not in s:
    raise SystemExit("D2D.66 female head loader missing")
if 'if female_mode and tex_head_female != null:' not in s:
    raise SystemExit("D2D.66 female head draw branch missing")
if 'draw_texture_rect(tex_head_female' not in s:
    raise SystemExit("D2D.66 female head draw call missing")

# Final on-disk verification before export.
m2 = re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"', s)
if not m2 or m2.group(1) != female_head_b64:
    raise SystemExit("D2D.66 final runtime head data verification failed")

runtime.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e, n1 = re.subn(r'(?m)^version/code=\d+$', 'version/code=139', e, count=1)
e, n2 = re.subn(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.66"', e, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.66 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.66"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.66: verified female head bytes installed into D2D.62 runtime; no other render/body changes.")
