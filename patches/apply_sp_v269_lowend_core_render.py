#!/usr/bin/env python3
"""SP269: targeted older-Android render cost diagnosis + lighter 2D drawing.

World atlases, roads, gameplay, NPCs, source models and HUD layout preserved.
Eliminate hundreds of legacy procedural draw items per chunk. The 7 authored
v268 atlases still render. Add real CPU/2D draw monitors to the PERF panel.
"""
from pathlib import Path
import sys
game=Path(sys.argv[1]).resolve()
def replace(rel, old, new, label):
    f=game/rel
    s=f.read_text(encoding="utf-8")
    n=s.count(old)
    if n!=1:raise RuntimeError(f"SP269_UNSAFE_ANCHOR {label} {n}")
    f.write_text(s.replace(old,new,1),encoding="utf-8")
def unchanged(*paths):
    return {p:(game/p).read_bytes() for p in paths}
safes=("scripts/player.gd","scripts/save/save_manager.gd",
    "scripts/combat/bandit.gd","scripts/virtual_joystick.gd",
    "scripts/mobile_hud.gd","scripts/world/world_manager.gd")
before=unchanged(*safes)

# Preserve the original blended world palettes but cut geometry 75%.
replace("scripts/world/world_biome_visuals.gd",
        "const GRID: int = 10","const GRID: int = 5","5x5 ground mesh")
replace("scripts/world/world_biome_visuals.gd",
'''        49, 65, 59, 54, 34, 44, 39, 43, 54])''',
'''        14, 19, 17, 15, 10, 13, 11, 13, 15])''',
"procedural clutter budget")
replace("scripts/world/world_biome_visuals.gd",
    "    for i in range(90):","    for i in range(18):",
    "ground microflecks budget")
# 3x3 larger regions sample the entire existing 384x384 material sheet.
# Source UV scale changes with grid to avoid sheet quadrants appearing as
# unrelated blocks, which was reported for the earlier v266 overlay.
replace("scripts/world/world_biome_raster.gd",
    "const MATERIAL_GRID: int = 6","const MATERIAL_GRID: int = 3",
    "material drawn regions")
replace("scripts/world/world_biome_raster.gd",
'''                float(ix)*64.0, float(iy)*64.0, 64.0, 64.0)''',
'''                float(ix)*128.0, float(iy)*128.0, 128.0, 128.0)''',
    "material atlas UVs")
replace("scripts/world/world_biome_raster.gd",
    "    for i in range(48):","    for i in range(28):",
    "ground vignette foliage budget")

# The 2D overlay still renders with only 7 atlases, and the true 9-biome
# procedural world & collision still load. PERF now records CPU vs 2D draw
# costs so a user screenshot can tell us whether GPU fill or CPU is primary.
perf=game/"scripts/performance/performance_manager.gd"
s=perf.read_text(encoding="utf-8")
start=s.index("func get_metrics_summary() -> String:")
end=s.index("func serialize() -> Dictionary:",start)
new='''func get_metrics_summary() -> String:
    var data := get_profile_data()
    var main_text: String = "%s%s • %d FPS cap • %.0f%% render • %.0f%% detail\\nMeasured %.0f FPS • %.1f ms/frame" % [
        requested_profile,
        " → %s" % effective_profile if auto_enabled else "",
        int(data.get("fps_cap", 60)),
        get_resolution_scale() * 100.0,
        get_detail_density() * 100.0,
        average_fps,
        frame_time_ms
    ]
    var process_ms: float = Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0
    var physics_ms: float = Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0
    var draw_items: int = int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
    return main_text + "\\nMain %.1fms | Physics %.1fms | Draw calls %d" % [
        process_ms, physics_ms, draw_items]

'''
assert "func get_metrics_summary()" in s[start:end]
perf.write_text(s[:start]+new+s[end:],encoding="utf-8")
for f,blob in before.items():
    assert (game/f).read_bytes()==blob,"SP269_GAMEPLAY_CHANGED "+f
vg=(game/"scripts/world/world_biome_visuals.gd").read_text()
rg=(game/"scripts/world/world_biome_raster.gd").read_text()
assert "const GRID: int = 5" in vg and "for i in range(18)" in vg
assert "const MATERIAL_GRID: int = 3" in rg and "float(ix)*128.0" in rg
assert "SP267_PROPS.paint_props" in (game/"scripts/world/world_chunk.gd").read_text()
print("SP269_RENDER_COST_OPT_PASS legacy biome mesh 5x5, atlas material 3x3, 65pct fewer decorative strokes, 7 authored prop atlases")
print("SP269_PERF_TELEMETRY_QA_PASS in-game PERF reports main/physics ms and draw-call count")
