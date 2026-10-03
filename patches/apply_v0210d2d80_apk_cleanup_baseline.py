#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.80 requires D2D.79 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.79 FEMALE PREVIEW RECOVERY:"' not in s:
    raise SystemExit("D2D.80 D2D.79 title anchor missing")

# Cleanup build only: do not modify current female visual geometry.
s=s.replace('title.text = "D2D.79 FEMALE PREVIEW RECOVERY:"',
            'title.text = "D2D.80 CLEANUP BASELINE:"',1)
runtime.write_text(s,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")

# Current Android target is ARM64 only. Preserve the preset while explicitly
# disabling legacy 32-bit ARM and desktop Android architectures.
def set_or_insert(key, value):
    global e
    pattern=r'(?m)^'+re.escape(key)+r'=.*$'
    if re.search(pattern,e):
        e=re.sub(pattern,key+'='+value,e,count=1)
    else:
        anchor='[preset.0.options]'
        if anchor not in e:
            raise SystemExit("D2D.80 Android preset options anchor missing")
        e=e.replace(anchor,anchor+'\n'+key+'='+value,1)

set_or_insert('architectures/armeabi-v7a','false')
set_or_insert('architectures/arm64-v8a','true')
set_or_insert('architectures/x86','false')
set_or_insert('architectures/x86_64','false')

e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=153',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.80"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.80 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.80"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.80 cleanup baseline: visuals unchanged")
print("D2D.80 Android export: ARM64 only")
