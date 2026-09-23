#!/usr/bin/env python3
"""D3D.16: enforced complete-player world scale plus visible installed-build indicator."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")
old="viewport_sprite.scale = Vector2(0.209, 0.209)"
if s.count(old)!=2:
    raise SystemExit("D3D.16 expected exactly two D3D.15 sprite-scale assignments")
view_anchor="const VIEW_SIZE := Vector2i(288, 384)"
if s.count(view_anchor)!=1:
    raise SystemExit("D3D.16 SubViewport resolution declaration changed")
s=s.replace(view_anchor,view_anchor+"\nconst PLAYER_WORLD_SPRITE_SCALE := 0.266",1)
s=s.replace(old,"viewport_sprite.scale = Vector2(PLAYER_WORLD_SPRITE_SCALE, PLAYER_WORLD_SPRITE_SCALE)")
if s.count("viewport_sprite.scale = ") != 2:
    raise SystemExit("D3D.16 other runtime sprite scale assignments found")
visual.write_text(s,encoding="utf-8")

# An unambiguous, non-interactive build stamp allows an on-device screenshot to
# prove which APK is actually running; do not trust installed APK filename alone.
hud=root/"scripts/mobile_hud.gd"
m=hud.read_text(encoding="utf-8")
anchor="func _build_ui() -> void:\n"
if m.count(anchor)!=1:
    raise SystemExit("D3D.16 HUD creation anchor missing")
helper='''func _add_d3d16_build_stamp() -> void:
    if has_node("D3D16BuildStamp"):
        return
    var marker := Label.new()
    marker.name = "D3D16BuildStamp"
    marker.text = "D3D.16  |  PLAYER 1.55x"
    marker.mouse_filter = Control.MOUSE_FILTER_IGNORE
    marker.add_theme_color_override("font_color", Color(1.0,0.91,0.50,0.94))
    marker.add_theme_color_override("font_shadow_color", Color(0.02,0.03,0.02,0.93))
    marker.add_theme_constant_override("shadow_offset_x",1)
    marker.add_theme_constant_override("shadow_offset_y",1)
    marker.add_theme_font_size_override("font_size",14)
    marker.position = Vector2(maxf(12.0,get_viewport().get_visible_rect().size.x * 0.204), 86.0)
    add_child(marker)

'''
m=m.replace(anchor,helper+anchor+'    call_deferred("_add_d3d16_build_stamp")\n',1)
if m.count('D3D16BuildStamp')<2:
    raise SystemExit("D3D.16 visible build marker not installed")
hud.write_text(m,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=45',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.16"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.16 Android version fields missing")
preset.write_text(p,encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.16"',t,count=1)
    save.write_text(t,encoding="utf-8")
print("Applied D3D.16: deterministic complete-player 2D sprite scale 0.266 (1.55x D3D.14) and visible on-screen APK build stamp.")
