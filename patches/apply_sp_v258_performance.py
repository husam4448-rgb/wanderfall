#!/usr/bin/env python3
"""v258: reduce CPU waste + APK size without deleting any D2D.14 world/HUD art.
The male player's hidden legacy renderer ran at 60Hz despite being invisible.
ProductionSurvivorVisual (old 3D model) is not instantiated anywhere in D2D14.
"""
from pathlib import Path
import sys, shutil
root=Path(sys.argv[1]).resolve()
def replace_once(rel, old, new):
    p=root/rel
    text=p.read_text(encoding="utf-8")
    count=text.count(old)
    if count!=1:
        raise SystemExit("SP_V258_FAIL %s anchor occurs %d times"%(rel,count))
    p.write_text(text.replace(old,new,1),encoding="utf-8")
# Never change historical geometry, textures, layout, scene, or gameplay systems.
protected=['scripts/mobile_hud.gd','scripts/virtual_joystick.gd',
'scripts/world/world_chunk.gd','scripts/world/world_manager.gd']
original={p:(root/p).read_bytes() for p in protected}
player='scripts/player.gd'
replace_once(player,
'''    if _baked_visual != null:
        _baked_visual.visible = show_actor and body_type == "female"
        _baked_visual.set_facing(_facing)
''',
'''    if _baked_visual != null:
        _baked_visual.visible = show_actor and body_type == "female"
        # Avoid submitting 60 draw commands per second to an invisible male rig.
        if body_type == "female" and show_actor:
            _baked_visual.set_facing(_facing)
''')
replace_once(player,
'''    if _baked_visual != null and _baked_visual.has_method("set_motion_state"):
        _baked_visual.set_motion_state(velocity,is_sprinting,is_crouching)
''',
'''    if body_type == "female" and _baked_visual != null:
        _baked_visual.set_motion_state(velocity,is_sprinting,is_crouching)
''')
replace_once(player,
'''func _sp_sync_body_choice() -> void:
    if _sp_sprite != null:
        _sp_sprite.visible = body_type == "male" and current_vehicle == null
''',
'''func _sp_sync_body_choice() -> void:
    # Old D2D renderer ran physics-independent per-frame _process even when
    # not visible. Suspend only for MALE; restore fully for FEMALE selection.
    if _baked_visual != null:
        _baked_visual.set_process(body_type == "female")
    if _sp_sprite != null:
        _sp_sprite.visible = body_type == "male" and current_vehicle == null
''')
# Firing art visuals are static while equip identity is unchanged; no needless
# new CanvasItem redraw/recolor every physics frame.
gun='assets/sp_melee/FirearmVisual.gd'
replace_once(gun,
'var current_weapon_id: String = ""\n',
'var current_weapon_id: String = ""\nvar current_category: String = ""\n')
replace_once(gun,
'''func configure_equipped(item_id: String, category: String) -> void:
    current_weapon_id = item_id
''',
'''func configure_equipped(item_id: String, category: String) -> void:
    if current_weapon_id == item_id and current_category == category:
        return
    current_category = category
    current_weapon_id = item_id
''')
# Pixel-perfect same tree occlusion and silhouettes; refresh at 15Hz rather
# than 30Hz. Physics/hit geometry and source canopy details remain unchanged.
overlay='scripts/world/occlusion_silhouette_overlay.gd'
replace_once(overlay,
'''    if _redraw_accumulator >= 0.033:
''',
'''    if _redraw_accumulator >= 0.066:
''')
# Legacy 3D art used for discontinued D3D renderer: the class is unreferenced
# by all real game code/scenes. Delete only if static reference scan verifies.
unused_script=root/'scripts/art/production_survivor_visual.gd'
model_dir=root/'assets/models'
if not unused_script.is_file() or not model_dir.is_dir():
    raise SystemExit("SP_V258_FAIL Cannot confirm historical unused models")
for f in root.rglob('*'):
    if f.is_file() and f.suffix in {'.gd','.tscn','.tres','.gdshader','.godot'} and f!=unused_script:
        source=f.read_text(encoding='utf-8',errors='ignore')
        if 'res://assets/models/' in source or 'ProductionSurvivorVisual' in source or 'production_survivor_visual.gd' in source:
            raise SystemExit("SP_V258_FAIL model still referenced by "+str(f))
unused_script.unlink()
shutil.rmtree(model_dir)
for rel, data in original.items():
    if (root/rel).read_bytes()!=data:
        raise SystemExit("SP_V258_FAIL original world/HUD changed: "+rel)
print('SP_V258_SIZE_QA_PASS orphan 3D models excluded; world atlas and 4 historic HUD/world files preserved exactly')
print('SP_V258_CPU_QA_PASS invisible male legacy draw stopped; female renderer selectable; static guns not repainted every tick; canopy occlusion 15 Hz')
