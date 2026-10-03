#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC04 requires PC03 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V03 | ANATOMY + TORSO FIT:"' not in s:
    raise SystemExit("PC04 PC03 title anchor missing")

# PC03 kept the old female torso art; therefore the base collar + curved seam
# belt still need to render. Restore that overlay for unequipped mode.
old_overlay='''    if female_mode and gear_torso:
        # Equipped vest still needs a front collar and seam belt. The new
        # unequipped torso has both authored directly into its silhouette.
        _draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)
        _draw_equipment_texture(tex_female_waist_belt_gear, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)
'''
new_overlay='''    if female_mode:
        # Until the dedicated production torso asset is installed, both states
        # keep the proven D2D.93 front collar + curved seam-belt treatment.
        var pc_collar := tex_female_front_collar_gear if gear_torso else tex_female_front_collar_base
        var pc_belt := tex_female_waist_belt_gear if gear_torso else tex_female_waist_belt_base
        _draw_equipment_texture(pc_collar, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)
        _draw_equipment_texture(pc_belt, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)
'''
if old_overlay not in s:
    raise SystemExit("PC04 female final-overlay anchor missing")
s=s.replace(old_overlay,new_overlay,1)

# ---------------------------------------------------------------
# Deterministic visual QA harness.
# Runs only in CI when PLAYER_CAPTURE_DIR is set. Normal APK behavior is
# unaffected. It captures eight canonical production states:
# female/male x base/equipped x right/left.
# ---------------------------------------------------------------
state_anchor='var shot_flash := 0.0\n'
if state_anchor not in s:
    raise SystemExit("PC04 capture state anchor missing")
s=s.replace(state_anchor,state_anchor+'''var pc_capture_dir := ""
var pc_capture_index := -1
var pc_capture_names := PackedStringArray([
    "female_base_right",
    "female_equipped_right",
    "female_base_left",
    "female_equipped_left",
    "male_base_right",
    "male_equipped_right",
    "male_base_left",
    "male_equipped_left"
])
''',1)

ready_anchor='''    _build_gear_ui()
    queue_redraw()
'''
ready_new='''    _build_gear_ui()
    if OS.has_environment("PLAYER_CAPTURE_DIR"):
        pc_capture_dir = OS.get_environment("PLAYER_CAPTURE_DIR")
        DirAccess.make_dir_recursive_absolute(pc_capture_dir)
        RenderingServer.frame_post_draw.connect(_pc_capture_after_draw)
        pc_capture_index = 0
        _pc_apply_capture_state(pc_capture_index)
    queue_redraw()
'''
if ready_anchor not in s:
    raise SystemExit("PC04 ready/capture anchor missing")
s=s.replace(ready_anchor,ready_new,1)

capture_anchor='func _texture_from_embedded_png(encoded: String) -> Texture2D:\n'
capture_helpers='''func _pc_apply_capture_state(idx: int) -> void:
    female_mode = idx < 4
    var equipped := (idx % 2) == 1
    var right := (idx % 4) < 2
    gear_head = equipped
    gear_torso = equipped
    gear_back = equipped
    gear_legs = equipped
    gear_boots = equipped
    gear_gloves = equipped
    visual_zoom = 4.0
    actor_pos = Vector2(640,360)
    aim_pos = actor_pos + Vector2(250.0 if right else -250.0, -25.0)
    move_vec = Vector2.ZERO
    step_phase = 0.0
    shot_recoil = 0.0
    shot_flash = 0.0
    _refresh_gear_buttons()
    _apply_visual_zoom()
    queue_redraw()

func _pc_capture_after_draw() -> void:
    if pc_capture_index < 0 or pc_capture_index >= pc_capture_names.size():
        return
    var image := get_viewport().get_texture().get_image()
    if image == null or image.is_empty():
        push_error("PC04 capture viewport image is empty")
        get_tree().quit(8)
        return
    var out_path := pc_capture_dir.path_join(pc_capture_names[pc_capture_index] + ".png")
    var err := image.save_png(out_path)
    if err != OK:
        push_error("PC04 capture save failed: %s" % err)
        get_tree().quit(9)
        return
    print("PC_CAPTURE:", out_path)
    pc_capture_index += 1
    if pc_capture_index >= pc_capture_names.size():
        print("PC_PERF_FPS:", Engine.get_frames_per_second())
        print("PC_PERF_STATIC_MEMORY:", Performance.get_monitor(Performance.MEMORY_STATIC))
        print("PC_PERF_OBJECTS:", Performance.get_monitor(Performance.OBJECT_COUNT))
        pc_capture_index = -1
        get_tree().quit()
        return
    _pc_apply_capture_state(pc_capture_index)

'''
if capture_anchor not in s:
    raise SystemExit("PC04 capture helper insertion anchor missing")
s=s.replace(capture_anchor,capture_helpers+capture_anchor,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V03 | ANATOMY + TORSO FIT:"',
    'title.text = "PLAYER CHARACTERS V04 | VISUAL QA BASELINE:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")
for needle in (
    'PLAYER CHARACTERS V04 | VISUAL QA BASELINE:',
    'func _pc_apply_capture_state(',
    'func _pc_capture_after_draw(',
    '"female_base_right"',
    'var pc_collar :=',
    'var pc_belt :=',
):
    if needle not in s2:
        raise SystemExit("PC04 verification missing: "+needle)
if 'var face_right := aim_pos.x >= actor_pos.x' not in s2:
    raise SystemExit("PC04 lost two-side body facing")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=170',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC04"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC04 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC04"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC04 restored female base collar/belt on current torso")
print("PC04 deterministic 8-state visual QA capture harness added")
print("PC04 body facing remains exactly Left/Right")
