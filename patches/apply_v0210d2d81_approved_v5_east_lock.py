#!/usr/bin/env python3
from pathlib import Path
import re, sys, hashlib, base64

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).parent
runtime = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
asset_file = patch_dir / "d2d81_assets" / "female_v5_east.b64"

if not runtime.exists():
    raise SystemExit("D2D.81 requires D2D.80 runtime")
if not asset_file.exists():
    raise SystemExit("D2D.81 approved V5 East asset missing")

v5_b64 = asset_file.read_text(encoding="utf-8").strip()
if not v5_b64:
    raise SystemExit("D2D.81 approved V5 East asset empty")
raw = base64.b64decode(v5_b64)
if hashlib.sha256(raw).hexdigest() != "561e70ad2aa9c4b76e403569843aaf718f976542b2bf57a8f3a269788cbf9953":
    raise SystemExit("D2D.81 approved V5 East asset SHA mismatch")

s = runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.80 CLEANUP BASELINE:"' not in s:
    raise SystemExit("D2D.81 D2D.80 title anchor missing")

# Embed the approved static East-facing body checkpoint.
if "const FEMALE_APPROVED_V5_EAST_B64 :=" not in s:
    m = re.search(r'(const FEMALE_NECK_B64 := "[^"]+"\n)', s)
    if not m:
        raise SystemExit("D2D.81 female neck constant anchor missing")
    s = s.replace(
        m.group(1),
        m.group(1) + 'const FEMALE_APPROVED_V5_EAST_B64 := "' + v5_b64 + '"\n',
        1
    )

if "var tex_female_approved_v5_east: Texture2D = null" not in s:
    anchor = "var tex_female_neck: Texture2D = null\n"
    if anchor not in s:
        raise SystemExit("D2D.81 female neck texture var anchor missing")
    s = s.replace(anchor, anchor + "var tex_female_approved_v5_east: Texture2D = null\n", 1)

if "tex_female_approved_v5_east = _texture_from_embedded_webp" not in s:
    anchor = "    tex_female_neck = _texture_from_embedded_webp(FEMALE_NECK_B64)\n"
    if anchor not in s:
        raise SystemExit("D2D.81 female neck texture load anchor missing")
    s = s.replace(
        anchor,
        anchor + "    tex_female_approved_v5_east = _texture_from_embedded_webp(FEMALE_APPROVED_V5_EAST_B64)\n",
        1
    )

# Phase-D visual lock:
# render the approved static East-facing composite as one authored sprite.
# This intentionally bypasses the experimental D2D.77-79 body-piece renderer
# for female mode so the engine must reproduce the approved static silhouette
# before we resume per-part rigging.
base_anchor = "    var base := actor_pos + Vector2(sway, -bob)\n"
if base_anchor not in s:
    raise SystemExit("D2D.81 actor base anchor missing")

static_block = '''    var base := actor_pos + Vector2(sway, -bob)

    # D2D.81: APPROVED V5 EAST VISUAL LOCK.
    # Single-direction integration checkpoint only.
    # The visible female body is the approved static authored composite;
    # no procedural bars, polygons, or experimental body geometry are rendered.
    if female_mode:
        _draw_oval(base + Vector2(0,51.0), Vector2(27.0,6.5), Color(0,0,0,0.36))
        if tex_female_approved_v5_east != null:
            # Source crop is 127x241 = half-resolution of the approved 4x static.
            # Display envelope restores the approved world-size proportions.
            draw_texture_rect(
                tex_female_approved_v5_east,
                Rect2(base + Vector2(-16.25,-65.0), Vector2(63.5,120.5)),
                false
            )
        return
'''
s = s.replace(base_anchor, static_block, 1)

s = s.replace(
    'title.text = "D2D.80 CLEANUP BASELINE:"',
    'title.text = "D2D.81 APPROVED V5 EAST LOCK:"',
    1
)

runtime.write_text(s, encoding="utf-8")

# Regression checks.
s2 = runtime.read_text(encoding="utf-8")
for needle in (
    "FEMALE_APPROVED_V5_EAST_B64",
    "tex_female_approved_v5_east",
    "D2D.81: APPROVED V5 EAST VISUAL LOCK",
    "Vector2(63.5,120.5)",
):
    if needle not in s2:
        raise SystemExit("D2D.81 verification missing: " + needle)

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e, n1 = re.subn(r'(?m)^version/code=\d+$', 'version/code=154', e, count=1)
e, n2 = re.subn(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.81"', e, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.81 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts" / "save" / "save_manager.gd"
if sm.exists():
    q = sm.read_text(encoding="utf-8")
    q = re.sub(
        r'const GAME_VERSION := "[^"]+"',
        'const GAME_VERSION := "0.21.0D2D.81"',
        q,
        count=1
    )
    sm.write_text(q, encoding="utf-8")

print("D2D.81 approved V5 East static visual lock installed")
print("D2D.81 asset SHA verified:", hashlib.sha256(raw).hexdigest())
print("D2D.81 intentionally freezes female to approved East pose for visual acceptance")
