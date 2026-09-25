#!/usr/bin/env python3
"""D3D.28: remove idle per-frame ecology work and reduce avoidable world simulation overhead."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# ------------------------------------------------------------------
# Natural resources were ALL processing every frame, including healthy trees.
# Hundreds of nodes repeatedly called Time.get_unix_time_from_system() only to
# discover that no regrowth work was needed. Disable processing until depleted.
# ------------------------------------------------------------------
rp=root/"scripts/ecology/natural_resource.gd"
r=rp.read_text(encoding="utf-8")

ready_anchor='''    queue_redraw()

func _process(_delta: float) -> void:
'''
if ready_anchor not in r:
    raise SystemExit("D3D.28 natural-resource ready/process anchor missing")
r=r.replace(ready_anchor,'''    # Healthy resources are static. They need no per-frame callback.
    set_process(_depleted and _ready_at > 0.0)
    queue_redraw()

func _process(_delta: float) -> void:
''',1)

old_process='''func _process(_delta: float) -> void:
    if _depleted and _ready_at > 0.0 and Time.get_unix_time_from_system() >= _ready_at:
        _depleted = false
        _ready_at = 0.0
        _chops_left = 3
        EcologyState.clear_resource_state(resource_id)
        _sync_tree_layer_sprites()
        queue_redraw()
'''
new_process='''func _process(_delta: float) -> void:
    # This callback is enabled only while a depleted resource is waiting to
    # respawn. Static/healthy trees, bushes, water and scrap cost zero process ticks.
    if not _depleted or _ready_at <= 0.0:
        set_process(false)
        return
    if Time.get_unix_time_from_system() < _ready_at:
        return
    _depleted = false
    _ready_at = 0.0
    _chops_left = 3
    EcologyState.clear_resource_state(resource_id)
    _sync_tree_layer_sprites()
    set_process(false)
    queue_redraw()
'''
if old_process not in r:
    raise SystemExit("D3D.28 natural-resource process body missing")
r=r.replace(old_process,new_process,1)

# Any action that starts a regrowth timer must wake this node's process callback.
r,n=re.subn(
    r'(?m)^(\s*)_ready_at = Time\.get_unix_time_from_system\(\) \+ ([^\n]+)$',
    lambda m: m.group(0)+"\n"+m.group(1)+"set_process(true)",
    r
)
if n < 3:
    raise SystemExit("D3D.28 expected multiple resource cooldown anchors")

# If a saved depleted resource is restored, make sure its timer wakes.
load_sig='func _load_state() -> void:\n'
la=r.find(load_sig)
lb=r.find("\nfunc ",la+len(load_sig))
if la<0:
    raise SystemExit("D3D.28 resource load-state function missing")
if lb<0: lb=len(r)
load=r[la:lb]
if "set_process(_depleted and _ready_at > 0.0)" not in load:
    # Append just before the next function; values have already been restored.
    load=load.rstrip()+"\n    set_process(_depleted and _ready_at > 0.0)\n"
    r=r[:la]+load+r[lb:]

# Manual refresh path must also turn processing back off after successful respawn.
refresh_sig='func _refresh_if_ready() -> void:\n'
ra=r.find(refresh_sig)
rb=r.find("\nfunc ",ra+len(refresh_sig))
if ra>=0:
    if rb<0: rb=len(r)
    refresh=r[ra:rb]
    old='''        _sync_tree_layer_sprites()
        queue_redraw()
'''
    if old in refresh:
        refresh=refresh.replace(old,'''        _sync_tree_layer_sprites()
        set_process(false)
        queue_redraw()
''',1)
        r=r[:ra]+refresh+r[rb:]

rp.write_text(r,encoding="utf-8")

# ------------------------------------------------------------------
# Wildlife: avoid redrawing moving animals every physics frame. Canvas redraws
# at 20 Hz are visually sufficient for these small procedural actors; physics
# movement itself remains full-rate so gameplay/collision behavior is unchanged.
# ------------------------------------------------------------------
wp=root/"scripts/ecology/wildlife_actor.gd"
w=wp.read_text(encoding="utf-8")
var_anchor='var _wander_timer'
if var_anchor in w and "var _visual_redraw_accum" not in w:
    i=w.find(var_anchor)
    line_end=w.find("\n",i)
    w=w[:line_end+1]+'var _visual_redraw_accum := 0.0\n'+w[line_end+1:]

phys='func _physics_process(delta: float) -> void:\n'
if phys not in w:
    raise SystemExit("D3D.28 wildlife physics anchor missing")
w=w.replace(phys,phys+'    _visual_redraw_accum += delta\n',1)
old='''    if velocity.length_squared() > 1.0:
        queue_redraw()
'''
new='''    if velocity.length_squared() > 1.0 and _visual_redraw_accum >= 0.05:
        _visual_redraw_accum = 0.0
        queue_redraw()
'''
if old not in w:
    raise SystemExit("D3D.28 wildlife redraw anchor missing")
w=w.replace(old,new,1)
wp.write_text(w,encoding="utf-8")

# Version/build stamp.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.27  |  60FPS WORLD / 30FPS ACTOR"' not in h:
    raise SystemExit("D3D.28 HUD marker anchor missing")
h=h.replace('marker.text = "D3D.27  |  60FPS WORLD / 30FPS ACTOR"',
            'marker.text = "D3D.28  |  ECOLOGY PERF"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=57',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.28"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.28 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.28"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.28: healthy resources no longer process every frame; depleted timers wake only as needed; wildlife redraw capped at 20Hz while physics stays full-rate.")
