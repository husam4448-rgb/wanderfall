#!/usr/bin/env python3
"""D2D.4.1: fix authored atlas frame geometry by deriving cell sizes from texture dimensions."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

p=root/"scripts/art/baked_actor_visual.gd"
s=p.read_text(encoding="utf-8")

s=s.replace('''const PLAYER_CELL := Vector2i(32,44)
const BANDIT_CELL := Vector2i(100,150)
''','''# Cell geometry is derived from the imported atlas itself.
# Player: 8 columns x 9 rows (idle + 4 walk + 4 run).
# Bandit: 8 columns x 1 row.
''',1)

old='''func _texture_for(col: int, row: int) -> Texture2D:
    var key := "%d:%d" % [col,row]
    if _frame_cache.has(key):
        return _frame_cache[key]
    var at := AtlasTexture.new()
    at.atlas = _atlas
    var cell := BANDIT_CELL if set_name == "bandit_female" else PLAYER_CELL
    at.region = Rect2i(col * cell.x,row * cell.y,cell.x,cell.y)
    _frame_cache[key] = at
    return at
'''
new='''func _texture_for(col: int, row: int) -> Texture2D:
    var key := "%d:%d" % [col,row]
    if _frame_cache.has(key):
        return _frame_cache[key]
    if _atlas == null:
        return null
    var columns := 8
    var rows := 1 if set_name == "bandit_female" else 9
    var cell_w := maxi(1, int(_atlas.get_width() / columns))
    var cell_h := maxi(1, int(_atlas.get_height() / rows))
    var safe_col := clampi(col,0,columns-1)
    var safe_row := clampi(row,0,rows-1)
    var at := AtlasTexture.new()
    at.atlas = _atlas
    at.region = Rect2i(safe_col * cell_w,safe_row * cell_h,cell_w,cell_h)
    _frame_cache[key] = at
    return at
'''
if old not in s:
    raise SystemExit("D2D.4.1 atlas region block missing")
s=s.replace(old,new,1)

# Keep authored sprites readable at world scale regardless of source frame resolution.
anchor='''    _sprite.texture = _texture_for(col,row)
'''
if anchor not in s:
    raise SystemExit("D2D.4.1 frame assignment anchor missing")
s=s.replace(anchor,'''    _sprite.texture = _texture_for(col,row)
    if _sprite.texture != null:
        var size := _sprite.texture.get_size()
        if size.y > 0.0:
            # Normalize authored frame height to ~58 world pixels.
            var target_height := 58.0 if set_name != "bandit_female" else 56.0
            var scale_factor := target_height / size.y
            _sprite.scale = Vector2(scale_factor,scale_factor)
''',1)

p.write_text(s,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D2D.4  |  AUTHORED 2D"' not in h:
    raise SystemExit("D2D.4.1 HUD anchor missing")
h=h.replace('marker.text = "D2D.4  |  AUTHORED 2D"',
            'marker.text = "D2D.4.1  |  ATLAS FIX"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
e=preset.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=69',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.4.1"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.4.1 version anchors missing")
preset.write_text(e,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.4.1"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D2D.4.1: dynamic authored-atlas cells + normalized sprite world scale.")
