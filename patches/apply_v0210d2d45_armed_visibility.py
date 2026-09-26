#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/baked_actor_visual.gd"; s=p.read_text()
s=s.replace('res://assets/authored2d/d2d44_player_unarmed.png','res://assets/authored2d/d2d43_player_armed.webp')
p.write_text(s)
h=root/"scripts/mobile_hud.gd"; t=h.read_text()
t=t.replace('marker.text = "D2D.4.4  |  PLAYER VISIBILITY"','marker.text = "D2D.4.5  |  ARMED SPRITE TEST"')
h.write_text(t)
ep=root/"export_presets.cfg"; e=ep.read_text()
e=re.sub(r'(?m)^version/code=\d+$','version/code=73',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.4.5"',e,count=1)
ep.write_text(e)
sm=root/"scripts/save/save_manager.gd"
if sm.exists():
 q=sm.read_text(); q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.4.5"',q,count=1); sm.write_text(q)
print("Applied D2D.4.5 proven armed-sprite visibility test")
