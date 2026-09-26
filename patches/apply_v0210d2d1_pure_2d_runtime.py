#!/usr/bin/env python3
"""D2D.1: first true 2D runtime checkpoint. Disable live 3D character renderer for player and test bandit."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# Player: force pure 2D layered actor + 2D weapon visual.
player=root/"scripts/player.gd"
p=player.read_text(encoding="utf-8")
old='''    var use_production: bool = false
    if _production_visual != null and _production_visual.has_method("is_supported_visual"):
        use_production = bool(_production_visual.call("is_supported_visual"))
'''
new='''    # D2D.1: pure 2D runtime. Keep the 3D production node dormant for rollback/reference,
    # but never render it in gameplay.
    var use_production: bool = false
'''
if old not in p:
    raise SystemExit("D2D.1 player production-selection anchor missing")
p=p.replace(old,new,1)

# Slightly enlarge the 2D layered actor for readability while staying below prior 3D size.
p=p.replace('_actor_visual.scale = Vector2(0.84, 0.84)',
            '_actor_visual.scale = Vector2(1.06, 1.06)',1)
# 2D weapon proportion tuned to actor.
p=p.replace('_weapon_visual.scale = Vector2(0.60, 0.66)',
            '_weapon_visual.scale = Vector2(0.72, 0.78)',1)
player.write_text(p,encoding="utf-8")

# Bandit: make controlled test enemy visually distinct and pure 2D.
bandit=root/"scripts/combat/bandit.gd"
b=bandit.read_text(encoding="utf-8")
# Force test actor identity female and authored hostile gear.
load_anchor='''func _build_visual_loadout() -> void:
    if bool(get_meta("d3d322_test_actor", false)):
        body_type = "male"
        equipped_visual_gear = {
            "head": "boonie_hat",
            "eyes": "",
            "lower_face": "cloth_face_wrap",
            "torso": "field_jacket",
            "armor": "tactical_vest",
            "hands": "tactical_gloves",
            "legs": "cargo_pants",
            "feet": "combat_boots",
            "back": "small_backpack",
            "binoculars": ""
        }
'''
replace='''func _build_visual_loadout() -> void:
    if bool(get_meta("d3d322_test_actor", false)):
        # D2D.1 test bandit: deliberately different silhouette from the male player.
        body_type = "female"
        equipped_visual_gear = {
            "head": "wool_beanie",
            "eyes": "safety_glasses",
            "lower_face": "cloth_face_wrap",
            "torso": "hoodie",
            "armor": "tactical_vest",
            "hands": "tactical_gloves",
            "legs": "cargo_pants",
            "feet": "combat_boots",
            "back": "small_backpack",
            "binoculars": ""
        }
'''
if load_anchor not in b:
    raise SystemExit("D2D.1 bandit test loadout anchor missing")
b=b.replace(load_anchor,replace,1)

# Force layered 2D visual even if D3D.32.3 production node exists.
mode_old='''func _refresh_visual_mode() -> void:
    var use_production := _production_visual != null and bool(get_meta("d3d322_test_actor", false))
'''
mode_new='''func _refresh_visual_mode() -> void:
    # D2D.1: all combat actors use the true 2D layered renderer.
    var use_production := false
'''
if mode_old not in b:
    raise SystemExit("D2D.1 bandit visual-mode anchor missing")
b=b.replace(mode_old,mode_new,1)

# Increase 2D bandit scale slightly for parity with 2D player.
b=b.replace('_actor_visual.scale = Vector2(0.84, 0.84)',
            '_actor_visual.scale = Vector2(1.02, 1.02)',1)
b=b.replace('_weapon_visual.scale = Vector2(0.84, 0.84)',
            '_weapon_visual.scale = Vector2(0.74, 0.80)',1)
bandit.write_text(b,encoding="utf-8")

# Improve bandit colors/readability in pure 2D without touching player identity.
visual=root/"scripts/art/layered_actor_visual.gd"
v=visual.read_text(encoding="utf-8")
v=v.replace(
    'var torso_color := _color(torso_id, Color("59685c") if role != "bandit" else Color("6a4d42"))',
    'var torso_color := _color(torso_id, Color("59685c") if role != "bandit" else Color("493c46"))',
    1
)
visual.write_text(v,encoding="utf-8")

# HUD/version: new D2D track.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.32.3  |  PRODUCTION BANDIT"' not in h:
    raise SystemExit("D2D.1 HUD version anchor missing")
h=h.replace('marker.text = "D3D.32.3  |  PRODUCTION BANDIT"',
            'marker.text = "D2D.1  |  PURE 2D RUNTIME"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
e=preset.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=65',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.1"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.1 version anchors missing")
preset.write_text(e,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    s=save.read_text(encoding="utf-8")
    s,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.1"',s,count=1)
    save.write_text(s,encoding="utf-8")

print("Applied D2D.1: player and combat-test bandit now render exclusively through pure 2D actor/weapon visuals; live 3D rendering disabled.")
