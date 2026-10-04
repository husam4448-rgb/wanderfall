#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image
import base64, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC16 requires PC15 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V15 | SINGLE FEMALE TORSO + FULL LEGS:"' not in s:
    raise SystemExit("PC16 PC15 title anchor missing")

# ----------------------------------------------------------------------
# PC16: refine the actual female leg source, not just its draw rectangle.
# The original source has a pronounced rear upper-leg/seat bulb which becomes
# visible behind the waist. Taper/shift ONLY the upper rows forward, while
# making thigh/calf rows slightly fuller. Both equipped and unequipped textures
# are derived from these same constants, so anatomy remains identical.
# ----------------------------------------------------------------------

m=re.search(r'const FEMALE_LEGS_B64 := "([A-Za-z0-9+/=]+)"',s)
if not m:
    raise SystemExit("PC16 FEMALE_LEGS_B64 missing")
raw=base64.b64decode(m.group(1))
src=Image.open(BytesIO(raw)).convert("RGBA")
if src.size != (32,48):
    raise SystemExit(f"PC16 unexpected female leg source size: {src.size}")

w,h=src.size
out=Image.new("RGBA",(w,h),(0,0,0,0))

def row_params(y):
    # scale, forward shift (right in authored right-facing source)
    if y <= 4:
        return 0.58, 2
    if y <= 11:
        t=(y-4)/7.0
        return 0.58 + (0.78-0.58)*t, 2
    if y <= 18:
        t=(y-11)/7.0
        return 0.78 + (1.08-0.78)*t, 1
    if y <= 31:
        return 1.12, 0
    if y <= 40:
        return 1.10, 0
    return 1.06, 0

for y in range(h):
    scale,shift=row_params(y)
    nw=max(1,int(round(w*scale)))
    row=src.crop((0,y,w,y+1)).resize((nw,1),Image.Resampling.LANCZOS)
    x0=(w-nw)//2 + shift
    # Clip safely to the 32px canvas.
    sx0=0
    if x0 < 0:
        sx0=-x0
        x0=0
    x1=min(w,x0+nw-sx0)
    if x1>x0:
        crop=row.crop((sx0,0,sx0+(x1-x0),1))
        out.alpha_composite(crop,(x0,y))

buf=BytesIO()
out.save(buf,"WEBP",lossless=True,quality=100,method=6)
leg_b64=base64.b64encode(buf.getvalue()).decode("ascii")

for name in ("FEMALE_LEGS_B64","FEMALE_LEGS_FRONT_B64"):
    s,n=re.subn(r'const '+name+r' := "[A-Za-z0-9+/=]+"',
                'const '+name+' := "'+leg_b64+'"',s,count=1)
    if n!=1:
        raise SystemExit("PC16 leg constant replace failed: "+name)

# PC15 fixed the torso layering. Keep that intact; only make the refined leg
# source large enough to read as adult female legs at the current character scale.
old='Vector2(22.6,26.5)'
if s.count(old) != 2:
    raise SystemExit("PC16 expected two PC15 female leg draw widths")
s=s.replace(old,'Vector2(25.6,26.5)')

s=s.replace(
    '(Vector2(16.2,11.2) if female_mode else Vector2(17.0,12.8))',
    '(Vector2(17.0,11.5) if female_mode else Vector2(17.0,12.8))'
)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V15 | SINGLE FEMALE TORSO + FULL LEGS:"',
    'title.text = "PLAYER CHARACTERS V16 | SMOOTH HIP + FULLER LEGS:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V16 | SMOOTH HIP + FULLER LEGS:',
    'Vector2(25.6,26.5)',
    'Vector2(17.0,11.5)',
    'if gear_torso and not female_mode:',
    'if female_mode and not gear_torso:',
):
    if needle not in s2:
        raise SystemExit("PC16 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if 'female_hip_bridge' in actor:
    raise SystemExit("PC16 pelvis/glute bridge returned")
if actor.count('tex_female_vest') != 1:
    raise SystemExit("PC16 single equipped torso invariant broken")
if 'Vector2(22.6,26.5)' in actor:
    raise SystemExit("PC16 PC15 leg width remains")

# Source-level sanity: upper hip rows must be narrower than mid-thigh rows.
a=out.getchannel("A")
def span(y0,y1):
    bb=a.crop((0,y0,w,y1)).getbbox()
    return 0 if bb is None else bb[2]-bb[0]
upper=span(3,12)
mid=span(18,32)
if upper >= mid:
    raise SystemExit(f"PC16 hip taper failed: upper={upper}, mid={mid}")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC16 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=182',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC16"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC16 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC16"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC16 upper female leg/seat source tapered and shifted forward")
print("PC16 thighs/calves widened while gait length remains unchanged")
print("PC16 single equipped torso and no-pelvis-overlay invariants preserved")
