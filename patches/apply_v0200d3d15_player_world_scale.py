#!/usr/bin/env python3
"""D3D.15: scale the complete rendered player in world space, without changing its rig."""
from pathlib import Path
import re
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
path=root/"scripts/art/production_survivor_visual.gd"
s=path.read_text(encoding="utf-8")

# Increase the on-map silhouette by ~22%. The rigged body, all equipped
# garments, backpack and right-hand-held pistol are drawn to the SAME
# SubViewport, so scaling its 2D output keeps every attachment aligned.
# Do not inflate only actor_root, a limb mesh, or an individual costume.
old="viewport_sprite.scale = Vector2(0.171, 0.171)"
new="viewport_sprite.scale = Vector2(0.209, 0.209)"
matches=s.count(old)
if matches != 2:
    raise SystemExit(f"D3D.15 expected exactly two world-sprite scale anchors, found {matches}")
s=s.replace(old,new)
if s.count(new)!=2:
    raise SystemExit("D3D.15 failed to update both initial and runtime player scales")
path.write_text(s,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,ncode=re.subn(r"(?m)^version/code=\d+$","version/code=44",p,count=1)
p,nname=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.15"',p,count=1)
if ncode!=1 or nname!=1:
    raise SystemExit("D3D.15 Android version metadata missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.15"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.15: player world silhouette +22.2% via complete sprite scaling; gear, backpack, hair, hands and pistol retain their anatomical registration.")
