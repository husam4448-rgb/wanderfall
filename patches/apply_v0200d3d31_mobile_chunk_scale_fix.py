#!/usr/bin/env python3
"""D3D.31: preserve pixelized actor performance, restore proper world scale, and cap mobile chunk window to 3x3."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

# D3D.29 halved the SubViewport dimensions but left the old sprite scale,
# unintentionally making the player roughly half-size on the map.
if 'const VIEW_SIZE := Vector2i(144, 192)' not in s:
    raise SystemExit("D3D.31 pixel viewport anchor missing")
if 'const PLAYER_WORLD_SPRITE_SCALE := 0.238' not in s:
    raise SystemExit("D3D.31 player scale anchor missing")
s=s.replace(
    'const PLAYER_WORLD_SPRITE_SCALE := 0.238',
    'const PLAYER_WORLD_SPRITE_SCALE := 0.540',
    1
)
visual.write_text(s,encoding="utf-8")

# Mobile world budget: retain only a 3x3 chunk neighborhood.
# This cuts static draw commands, resources, wildlife and occlusion candidates
# dramatically compared with the 30+ loaded chunks seen on device.
wm=root/"scripts/world/world_manager.gd"
w=wm.read_text(encoding="utf-8")
w,n1=re.subn(
    r'_profile_active_radius = clampi\(PerformanceManager\.get_chunk_radius\(\),1,2\)',
    '_profile_active_radius = 1',
    w
)
w,n2=re.subn(
    r'_profile_unload_radius = _profile_active_radius',
    '_profile_unload_radius = 1',
    w
)
if n1 < 1 or n2 < 1:
    raise SystemExit("D3D.31 D3D.30 chunk-radius anchors missing")
wm.write_text(w,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.30  |  IDLE ZERO + CHUNK CULL"' not in h:
    raise SystemExit("D3D.31 HUD anchor missing")
h=h.replace(
    'marker.text = "D3D.30  |  IDLE ZERO + CHUNK CULL"',
    'marker.text = "D3D.31  |  PIXEL ACTOR + 3x3 WORLD"',
    1
)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n3=re.subn(r'(?m)^version/code=\d+$','version/code=60',p,count=1)
p,n4=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.31"',p,count=1)
if n3!=1 or n4!=1:
    raise SystemExit("D3D.31 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.31"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.31: pixel actor kept at 144x192/20Hz, player world scale corrected to 0.540, world capped to 3x3 chunks.")
