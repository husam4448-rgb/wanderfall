#!/usr/bin/env python3
"""D3D.29: pixelized low-resolution character SubViewport performance pass."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

# Halve each character render dimension: 288x384 -> 144x192.
if 'const VIEW_SIZE := Vector2i(288, 384)' not in s:
    raise SystemExit("D3D.29 VIEW_SIZE anchor missing")
s=s.replace('const VIEW_SIZE := Vector2i(288, 384)',
            'const VIEW_SIZE := Vector2i(144, 192)',1)

# Pixel-art presentation: nearest-neighbour instead of linear filtering.
if 'viewport_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR' not in s:
    raise SystemExit("D3D.29 viewport filter anchor missing")
s=s.replace('viewport_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR',
            'viewport_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST',1)

# Character renderer can update at 20Hz without affecting physics/world FPS.
if 'const CHARACTER_RENDER_HZ := 30.0' not in s:
    raise SystemExit("D3D.29 character render Hz anchor missing")
s=s.replace('const CHARACTER_RENDER_HZ := 30.0',
            'const CHARACTER_RENDER_HZ := 20.0',1)

visual.write_text(s,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.28  |  ECOLOGY PERF"' not in h:
    raise SystemExit("D3D.29 HUD marker anchor missing")
h=h.replace('marker.text = "D3D.28  |  ECOLOGY PERF"',
            'marker.text = "D3D.29  |  PIXEL ACTOR PERF"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=58',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.29"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.29 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.29"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.29: 144x192 nearest-neighbour character renderer at 20Hz.")
