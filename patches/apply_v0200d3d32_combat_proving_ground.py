#!/usr/bin/env python3
"""D3D.32: first controlled combat proving-ground on top of the D3D.31 performance baseline."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# Spawn exactly one lightweight hostile near the exterior player after streaming starts.
wm=root/"scripts/world/world_manager.gd"
w=wm.read_text(encoding="utf-8")
anchor='''    var current_floor := String(player.get_meta("current_floor", "exterior"))
    if current_floor != "exterior":
        return

    var center := world_to_chunk(player.global_position)
'''
if anchor not in w:
    raise SystemExit("D3D.32 world-manager player anchor missing")
replacement='''    var current_floor := String(player.get_meta("current_floor", "exterior"))
    if current_floor != "exterior":
        return

    # D3D.32 controlled combat proving ground.
    # Keep this deliberately to one actor so device FPS impact is measurable.
    if not bool(get_meta("d3d32_combat_spawned", false)):
        set_meta("d3d32_combat_spawned", true)
        if get_tree().get_nodes_in_group("hostile_actor").is_empty():
            var bandit_script := load("res://scripts/combat/bandit.gd")
            if bandit_script != null:
                var bandit = bandit_script.new()
                bandit.name = "D3D32_Combat_Test_Bandit"
                get_parent().add_child(bandit)
                bandit.global_position = player.global_position + Vector2(260.0, -60.0)

    var center := world_to_chunk(player.global_position)
'''
w=w.replace(anchor,replacement,1)
wm.write_text(w,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.31  |  PIXEL ACTOR + 3x3 WORLD"' not in h:
    raise SystemExit("D3D.32 HUD anchor missing")
h=h.replace(
    'marker.text = "D3D.31  |  PIXEL ACTOR + 3x3 WORLD"',
    'marker.text = "D3D.32  |  COMBAT PROVING GROUND"',
    1
)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=61',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.32"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.32 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.32"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.32: one controlled bandit combat encounter near the player; existing AI, firearm damage, death and loot systems preserved.")
