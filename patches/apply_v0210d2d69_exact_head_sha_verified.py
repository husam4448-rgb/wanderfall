#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
patch_dir=Path(__file__).parent
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.69 requires D2D.62 runtime")

EXPECTED_SHA="2222f1bf7f05a2c9bd649e9da5e09ab6278124f500eac135d19447ba1ed8627e"

# Find the exact uploaded 96x96 female-head PNG bytes among the previous head patches.
# We do not trust filenames or labels; we trust the SHA-256 of the actual uploaded cutout.
candidates=[
    patch_dir/"apply_v0210d2d68_exact_female_head.py",
    patch_dir/"apply_v0210d2d66_verified_female_head_only.py",
    patch_dir/"apply_v0210d2d64_female_head_valid_png.py",
    patch_dir/"apply_v0210d2d61_female_cutout_fix.py",
]
female_head_b64=None
source_name=None
for p in candidates:
    if not p.exists():
        continue
    txt=p.read_text(encoding="utf-8")
    # inspect every long PNG-looking base64 literal in the file
    for m in re.finditer(r'([A-Za-z0-9+/]{1000,}={0,2})', txt):
        b64=m.group(1)
        try:
            raw=base64.b64decode(b64, validate=True)
        except Exception:
            continue
        if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            continue
        sha=hashlib.sha256(raw).hexdigest()
        if sha==EXPECTED_SHA:
            female_head_b64=b64
            source_name=p.name
            break
    if female_head_b64:
        break

if not female_head_b64:
    raise SystemExit("D2D.69 exact uploaded female head PNG not found by SHA-256")

raw=base64.b64decode(female_head_b64)
if len(raw)!=21085:
    raise SystemExit(f"D2D.69 unexpected exact female head byte size: {len(raw)}")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.62 FEMALE PROPORTION FIX:"' not in s:
    raise SystemExit("D2D.69 D2D.62 baseline title anchor missing")

# Replace the female head payload by exact bytes, line-by-line to avoid regex replacement corruption.
lines=s.splitlines()
hits=0
for i,line in enumerate(lines):
    if line.startswith("const FEMALE_HEAD_B64 :="):
        lines[i]='const FEMALE_HEAD_B64 := "'+female_head_b64+'"'
        hits+=1
if hits!=1:
    raise SystemExit(f"D2D.69 expected one FEMALE_HEAD_B64 line, found {hits}")
s="\n".join(lines)+("\n" if s.endswith("\n") else "")

# Final bare-head layer: every male head texture draw must select the female texture in FEMALE mode.
pat=r'draw_texture_rect\(tex_head_right,\s*(Rect2\([^\n]+\)),\s*false\)'
male_draws=len(re.findall(pat,s))
if male_draws<1:
    raise SystemExit("D2D.69 could not locate the final male bare-head draw")
s=re.sub(
    pat,
    lambda m: 'draw_texture_rect((tex_head_female if female_mode and tex_head_female != null else tex_head_right), '+m.group(1)+', false)',
    s
)

# Remove the older female branch ambiguity by forcing its draw rectangle to exact female texture.
s=s.replace(
'''        if female_mode and tex_head_female != null:
            # Female profile uses the same neck pivot/aim rotation as the male rig.
            draw_texture_rect(tex_head_female, Rect2(Vector2(-8.1,-17.7), Vector2(16.2,18.9)), false)
        else:''',
'''        if female_mode and tex_head_female != null:
            # D2D.69 exact uploaded female cutout.
            draw_texture_rect(tex_head_female, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
        else:''',
1)

s=s.replace(
    'title.text = "D2D.62 FEMALE PROPORTION FIX:"',
    'title.text = "D2D.69 EXACT HEAD SHA VERIFIED:"',
    1
)

# Hard verification of final runtime before export.
m=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if not m:
    raise SystemExit("D2D.69 final head constant missing")
final_raw=base64.b64decode(m.group(1), validate=True)
final_sha=hashlib.sha256(final_raw).hexdigest()
if final_sha!=EXPECTED_SHA:
    raise SystemExit(f"D2D.69 final runtime female head SHA mismatch: {final_sha}")
if 'tex_head_female = _texture_from_embedded_png(FEMALE_HEAD_B64)' not in s:
    raise SystemExit("D2D.69 female texture loader missing")
remaining=len(re.findall(r'draw_texture_rect\(tex_head_right,',s))
if remaining:
    raise SystemExit(f"D2D.69 unconditional male bare-head draw remains: {remaining}")

runtime.write_text(s,encoding="utf-8")
print("D2D.69 exact female head source:",source_name)
print("D2D.69 exact female head bytes:",len(final_raw))
print("D2D.69 exact female head SHA256:",final_sha)
print("D2D.69 male head draws patched:",male_draws)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=142',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.69"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.69 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.69"',t,count=1)
    sm.write_text(t,encoding="utf-8")
