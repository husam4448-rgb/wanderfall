#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.67 requires D2D.62 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.62 FEMALE PROPORTION FIX:"' not in s:
    raise SystemExit("D2D.67 baseline title anchor missing")

head_lines=[line for line in s.splitlines() if "tex_head_right" in line or "tex_head_female" in line]
print("D2D.67 FINAL RUNTIME HEAD REFERENCES:")
for line in head_lines:
    print(line)

pattern=r'draw_texture_rect\(tex_head_right,\s*(Rect2\([^\n]+\)),\s*false\)'
matches=list(re.finditer(pattern,s))
print("D2D.67 male head draw call count before patch:",len(matches))
if not matches:
    raise SystemExit("D2D.67 found no male head draw calls to patch")

def repl(m):
    rect=m.group(1)
    return ('draw_texture_rect((tex_head_female if female_mode and tex_head_female != null '
            'else tex_head_right), '+rect+', false)')

s=re.sub(pattern,repl,s)

if "tex_head_female if female_mode" not in s:
    raise SystemExit("D2D.67 forced-gender head selector not installed")

s=s.replace('title.text = "D2D.62 FEMALE PROPORTION FIX:"',
            'title.text = "D2D.67 FINAL HEAD DRAW FIX:"',1)
runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
print("D2D.67 FINAL SELECTOR COUNT:",s2.count("tex_head_female if female_mode"))
remaining=len(re.findall(r'draw_texture_rect\(tex_head_right,',s2))
print("D2D.67 REMAINING BARE MALE DRAW COUNT:",remaining)
if remaining != 0:
    raise SystemExit("D2D.67 still has an unconditional male head draw")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=140',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.67"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.67 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"',
             'const GAME_VERSION := "0.21.0D2D.67"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.67: final runtime male head draw calls now select female texture whenever FEMALE mode is active.")
