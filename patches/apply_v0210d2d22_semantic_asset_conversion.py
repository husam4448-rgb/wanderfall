#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d20_master_texture_islands.gd"
if not script.exists():
    raise SystemExit("D2D.22 requires D2D.21 live-bound islands")

s = script.read_text(encoding="utf-8")

# Replace broad rectangular region ownership with one exclusive semantic owner per cell.
start = s.index("func _region_accepts(region: String, px: float, py: float) -> bool:\n")
end = s.index("func _make_region_mesh(region: String, z_value: int) -> void:\n", start)

semantic = r'''func _dist_to_segment(p: Vector2, a: Vector2, b: Vector2) -> float:
    var ab := b-a
    var denom := ab.length_squared()
    if denom <= 0.0001:
        return p.distance_to(a)
    var t := clampf((p-a).dot(ab)/denom,0.0,1.0)
    return p.distance_to(a+ab*t)

func _semantic_owner(px: float, py: float) -> String:
    # One and only one owner for every mesh cell. Coordinates are in source-texture
    # pixels. Limb centerlines are derived from the actual South bind points.
    var p := Vector2(px,py)

    var arm_l_a := Vector2(164.0,124.0)
    var arm_l_b := Vector2(185.0,198.0)
    var arm_l_c := Vector2(198.0,269.0)
    var arm_r_a := Vector2(54.0,124.0)
    var arm_r_b := Vector2(33.0,198.0)
    var arm_r_c := Vector2(20.0,269.0)

    var leg_l_a := Vector2(137.0,261.0)
    var leg_l_b := Vector2(146.0,350.0)
    var leg_l_c := Vector2(157.0,430.0)
    var leg_r_a := Vector2(81.0,261.0)
    var leg_r_b := Vector2(72.0,350.0)
    var leg_r_c := Vector2(61.0,430.0)

    var d_arm_l := minf(_dist_to_segment(p,arm_l_a,arm_l_b),_dist_to_segment(p,arm_l_b,arm_l_c))
    var d_arm_r := minf(_dist_to_segment(p,arm_r_a,arm_r_b),_dist_to_segment(p,arm_r_b,arm_r_c))
    var d_leg_l := minf(_dist_to_segment(p,leg_l_a,leg_l_b),_dist_to_segment(p,leg_l_b,leg_l_c))
    var d_leg_r := minf(_dist_to_segment(p,leg_r_a,leg_r_b),_dist_to_segment(p,leg_r_b,leg_r_c))

    # Arms terminate before the thigh/short region. The capsule radii are deliberately
    # tight: if a cell is not convincingly limb tissue it stays with the core.
    if py >= 105.0 and py <= 292.0:
        if px >= 139.0 and d_arm_l <= 25.0:
            return "arm_L"
        if px <= 79.0 and d_arm_r <= 25.0:
            return "arm_R"

    # Legs begin below the pelvis/shorts seam. Hip cells near the center stay core.
    if py >= 246.0:
        if px >= 111.0 and d_leg_l <= 32.0:
            return "leg_L"
        if px <= 107.0 and d_leg_r <= 32.0:
            return "leg_R"

    return "core"

func _cell_is_visible(i: int, j: int) -> bool:
    if texture_image == null or texture_image.is_empty():
        return true
    var x0 := float(i)*TEX_W/float(COLS-1)
    var x1 := float(i+1)*TEX_W/float(COLS-1)
    var y0 := float(j)*TEX_H/float(ROWS-1)
    var y1 := float(j+1)*TEX_H/float(ROWS-1)
    var cx := (x0+x1)*0.5
    var cy := (y0+y1)*0.5
    var samples := [
        Vector2(x0,y0),Vector2(x1,y0),Vector2(x1,y1),Vector2(x0,y1),
        Vector2(cx,cy),Vector2(cx,y0),Vector2(cx,y1),Vector2(x0,cy),Vector2(x1,cy)
    ]
    var opaque := 0
    for sample in samples:
        var sx := clampi(int(round(sample.x)),0,int(TEX_W)-1)
        var sy := clampi(int(round(sample.y)),0,int(TEX_H)-1)
        if texture_image.get_pixel(sx,sy).a > 0.06:
            opaque += 1
    return opaque >= 2

func _cell_has_visible_region(region: String, i: int, j: int) -> bool:
    if not _cell_is_visible(i,j):
        return false
    var cx := (float(i)+0.5)*TEX_W/float(COLS-1)
    var cy := (float(j)+0.5)*TEX_H/float(ROWS-1)
    return _semantic_owner(cx,cy) == region

'''
s = s[:start] + semantic + s[end:]

# Denser topology so semantic boundaries and joints are cleaner.
s = s.replace("const COLS := 31\nconst ROWS := 67","const COLS := 37\nconst ROWS := 81",1)

# Add cell-count validation state.
s = s.replace('var meshes := {}\nvar texture_image: Image',
'''var meshes := {}
var region_cells := {"core":0,"arm_L":0,"arm_R":0,"leg_L":0,"leg_R":0}
var texture_image: Image''',1)

# Count actual accepted cells in each island.
needle = '''            if not _cell_has_visible_region(region,i,j):
                continue
            var a: int = index_map[Vector2i(i,j)]'''
repl = '''            if not _cell_has_visible_region(region,i,j):
                continue
            region_cells[region] = int(region_cells.get(region,0))+1
            var a: int = index_map[Vector2i(i,j)]'''
if needle not in s:
    raise SystemExit("D2D.22 cell count anchor missing")
s = s.replace(needle,repl,1)

# Replace the full arm test with an isolated forearm proof and the leg test with one knee.
arm_start = s.index('    if test_mode == "arm":\n')
leg_start = s.index('    elif test_mode == "leg":\n',arm_start)
aim_start = s.index('    elif test_mode == "aim":\n',leg_start)

arm_block = r'''    if test_mode == "arm":
        # Acceptance proof: only one forearm bends. No shoulder swing, no opposite arm.
        var flex := 0.5+0.5*sin(elapsed*1.35)
        bones["forearm_L"].rotation = deg_to_rad(34.0)*flex
        bones["hand_L"].rotation = -deg_to_rad(8.0)*flex

'''
leg_block = r'''    elif test_mode == "leg":
        # Acceptance proof: only one knee flexes. Pelvis and opposite leg remain static.
        var flex := 0.5+0.5*sin(elapsed*1.20)
        bones["shin_L"].rotation = -deg_to_rad(12.0)*flex
        var sl: Vector2 = bones["shin_L"].rest.origin
        var fl: Vector2 = bones["foot_L"].rest.origin
        bones["shin_L"].position = Vector2(sl.x,sl.y*(1.0-0.035*flex))
        bones["foot_L"].position = Vector2(fl.x,fl.y*(1.0-0.055*flex))
        bones["foot_L"].rotation = deg_to_rad(5.0)*flex

'''
s = s[:arm_start] + arm_block + leg_block + s[aim_start:]

# Disable full aim in this validation build. It must not be accepted until semantic conversion passes.
aim_start = s.index('    elif test_mode == "aim":\n')
proc_start = s.index('func _process(delta: float) -> void:\n',aim_start)
aim_block = r'''    elif test_mode == "aim":
        # Intentionally neutral in D2D.22. Full two-arm aiming is gated behind
        # successful semantic reconstruction + single-joint tests.
        pass

'''
s = s[:aim_start] + aim_block + s[proc_start:]

# UI/title/labels.
s = s.replace('D2D.21 — LIVE-BOUND MULTI-ISLAND SKIN',
              'D2D.22 — SEMANTIC ASSET-CONVERSION LAB',1)
s = s.replace('South prototype • live Skeleton2D binding • isolated topology • chest-only breathing',
              'South prototype • exclusive semantic ownership • reconstruction-first validation',1)
s = s.replace('Each island is now bound after entering the scene tree, then weighted to the live Skeleton2D.',
              'Every visible mesh cell has exactly one anatomical owner. No duplicated arm/leg pixels.',1)
s = s.replace('ARM BEND TEST','ONE FOREARM TEST',1)
s = s.replace('LEG / KNEE FLEX TEST','ONE KNEE TEST',1)
s = s.replace('FORWARD AIM / FORESHORTEN','AIM LOCKED UNTIL PASS',1)

footer_old = '''Acceptance:\n• no cross-body texture wedges\n• chest breathing only\n• head/arms sway without scaling\n• elbows/knees deform locally'''
footer_new = '''D2D.22 acceptance gate:\n• neutral reconstructs one body\n• no duplicate limbs\n• one forearm bends locally\n• one knee bends locally\n• full aim remains locked'''
s = s.replace(footer_old,footer_new,1)

# Add a validation summary to the label area.
anchor = '    zoom_label.text = "MESH ZOOM: %.2fx" % user_zoom\n'
if anchor not in s:
    raise SystemExit("D2D.22 label anchor missing")
s = s.replace(anchor,anchor + '''    var assigned := 0
    for key in region_cells.keys():
        assigned += int(region_cells[key])
    zoom_label.tooltip_text = "Semantic cells: %d | core %d | arms %d/%d | legs %d/%d" % [
        assigned,
        int(region_cells["core"]),
        int(region_cells["arm_L"]),int(region_cells["arm_R"]),
        int(region_cells["leg_L"]),int(region_cells["leg_R"])
    ]
''',1)

script.write_text(s,encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$','version/code=95',e,count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.22"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.22"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.22 exclusive semantic asset-conversion validation lab.")
