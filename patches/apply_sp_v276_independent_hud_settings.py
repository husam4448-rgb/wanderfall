#!/usr/bin/env python3
"""SP276: keep mobile HUD canvas independent from graphics preset changes;
make main-menu UI Settings a functional entry for HUD/control editing.

The current engine renders the entire 2D root at the preset resolution.
Until the game world is isolated in a SubViewport, changing its size also
changes all touch target coordinate systems. Pin the 2D virtual canvas once,
retain FPS caps and per-profile world/effect detail changes; conserve GPU
work on Galaxy S8 by using its existing Battery Saver resolution as the pin.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
def replace(rel,old,new,label):
    f=root/rel
    s=f.read_text(encoding="utf-8")
    n=s.count(old)
    if n!=1:
        raise RuntimeError("SP276_ANCHOR %s %s: %s"%(rel,label,n))
    f.write_text(s.replace(old,new,1),encoding="utf-8")

perf="scripts/performance/performance_manager.gd"
replace(perf,'''var _high_windows := 0
''','''var _high_windows := 0
# Separate user-selected QUALITY/FPS from the touch-UI coordinate space.
# This stays stable for the session and across save loads/preset changes.
var _sp276_fixed_canvas_size: Vector2i = Vector2i.ZERO
''',"persistent UI frame")
replace(perf,'''    if root != null:
        # Viewport stretch renders the 2D scene at this virtual resolution, then scales to the physical display.
        # This is the actual pixel-work reduction path used by Battery/Balanced/Smooth modes.
        root.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
        var scale := clampf(float(data.get("resolution_scale", 1.0)), 0.60, 1.0)
        root.content_scale_size = Vector2i(
            maxi(640, int(round(BASE_RENDER_SIZE.x * scale))),
            maxi(360, int(round(BASE_RENDER_SIZE.y * scale)))
        )
    quality_changed.emit()''','''    if root != null:
        # Root CONTENT_SCALE_SIZE owns both game visuals and HUD controls.
        # Never change it on PERFORMANCE profile changes: the previous code
        # re-laid-out all touch targets and invalidated saved HUD positions.
        if _sp276_fixed_canvas_size == Vector2i.ZERO:
            var model: String = OS.get_model_name().to_upper()
            var is_s8: bool = OS.get_name() == "Android" and (
                model.contains("SM-G950") or model.contains("GALAXY S8"))
            var fixed_scale: float = 0.72 if is_s8 else 0.85
            _sp276_fixed_canvas_size = Vector2i(
                maxi(640, int(round(BASE_RENDER_SIZE.x * fixed_scale))),
                maxi(360, int(round(BASE_RENDER_SIZE.y * fixed_scale)))
            )
        root.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
        if root.content_scale_size != _sp276_fixed_canvas_size:
            root.content_scale_size = _sp276_fixed_canvas_size
    quality_changed.emit()''',"fixed profile-independent virtual canvas")
replace(perf,'''func get_resolution_scale() -> float:
    return float(PROFILES.get(effective_profile, PROFILES["Balanced 60"]).get("resolution_scale", 1.0))''','''func get_resolution_scale() -> float:
    # Report ACTUAL raster scale; profile quality density remains dynamic.
    if _sp276_fixed_canvas_size != Vector2i.ZERO:
        return float(_sp276_fixed_canvas_size.x) / float(BASE_RENDER_SIZE.x)
    return float(PROFILES.get(effective_profile, PROFILES["Balanced 60"]).get("resolution_scale", 1.0))''',"accurate effective render metric")

menu="scripts/ui/main_menu.gd"
replace(menu,'''var settings_box: VBoxContainer
var mods_box: VBoxContainer''','''var settings_box: VBoxContainer
var ui_settings_box: VBoxContainer
var ui_settings_button: Button
var ui_size_button: Button
var control_size_button: Button
var text_size_button: Button
var touch_size_button: Button
var ui_summary: Label
var mods_box: VBoxContainer''',"menu UI state")

replace(menu,'''    var text_scale := _menu_button("TEXT / UI SCALE", "settings")
    text_scale.pressed.connect(func(): GameSettings.cycle_scalar("text_scale"); _refresh_settings())
    settings_box.add_child(text_scale)''','''    var text_scale := _menu_button("TEXT SIZE", "settings")
    text_scale.pressed.connect(func(): GameSettings.cycle_scalar("text_scale"); _refresh_settings())
    settings_box.add_child(text_scale)
    ui_settings_button = _menu_button("UI SETTINGS / CONTROLS", "settings")
    ui_settings_button.pressed.connect(func(): _show_section(ui_settings_box); _refresh_ui_settings())
    settings_box.add_child(ui_settings_button)''',"actual settings entry")
replace(menu,'''    var mods_back := _menu_button("BACK", "close")
''','''    var mods_back := _menu_button("BACK", "close")
''',"unchanged mods anchor test") if False else None
replace(menu,'''    mods_box = VBoxContainer.new()
''','''    _sp276_build_ui_settings_box(stack)
    mods_box = VBoxContainer.new()
''',"build real menu HUD settings")
replace(menu,'''for item in [main_box, load_box, settings_box, mods_box]:''','''for item in [main_box, load_box, settings_box, ui_settings_box, mods_box]:''',"section switcher")
replace(menu,'''func _refresh_settings() -> void:
''', '''func _sp276_build_ui_settings_box(stack: VBoxContainer) -> void:
    ui_settings_box = VBoxContainer.new()
    ui_settings_box.visible = false
    ui_settings_box.add_theme_constant_override("separation", 5)
    stack.add_child(ui_settings_box)
    var title_label := Label.new()
    title_label.text = "UI SETTINGS"
    title_label.add_theme_font_size_override("font_size", 19)
    ui_settings_box.add_child(title_label)
    ui_summary = Label.new()
    ui_summary.add_theme_font_size_override("font_size", 12)
    ui_summary.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    ui_settings_box.add_child(ui_summary)
    ui_size_button = _menu_button("HUD WINDOW SIZE", "settings")
    ui_size_button.pressed.connect(func(): GameSettings.cycle_scalar("ui_scale"); _refresh_ui_settings())
    ui_settings_box.add_child(ui_size_button)
    control_size_button = _menu_button("CONTROL SIZE", "settings")
    control_size_button.pressed.connect(func(): GameSettings.cycle_scalar("control_scale"); _refresh_ui_settings())
    ui_settings_box.add_child(control_size_button)
    text_size_button = _menu_button("TEXT SIZE", "settings")
    text_size_button.pressed.connect(func(): GameSettings.cycle_scalar("text_scale"); _refresh_ui_settings())
    ui_settings_box.add_child(text_size_button)
    touch_size_button = _menu_button("TOUCH SENSITIVITY SIZE", "settings")
    touch_size_button.pressed.connect(func(): GameSettings.cycle_scalar("touch_scale"); _refresh_ui_settings())
    ui_settings_box.add_child(touch_size_button)
    var edit := _menu_button("EDIT CONTROLS IN GAME", "settings")
    edit.pressed.connect(_sp276_open_layout_editor)
    ui_settings_box.add_child(edit)
    var back := _menu_button("BACK TO SETTINGS", "close")
    back.pressed.connect(func(): _show_section(settings_box); _refresh_settings())
    ui_settings_box.add_child(back)
    _refresh_ui_settings()

func _refresh_ui_settings() -> void:
    if ui_summary == null:
        return
    ui_summary.text = "HUD %.2fx   CONTROLS %.2fx   TEXT %.2fx   TOUCH %.2fx" % [
        GameSettings.ui_scale, GameSettings.control_scale, GameSettings.text_scale, GameSettings.touch_scale]
    ui_size_button.text = "HUD WINDOW SIZE: %.2fx" % GameSettings.ui_scale
    control_size_button.text = "CONTROL SIZE: %.2fx" % GameSettings.control_scale
    text_size_button.text = "TEXT SIZE: %.2fx" % GameSettings.text_scale
    touch_size_button.text = "TOUCH SIZE: %.2fx" % GameSettings.touch_scale

func _sp276_open_layout_editor() -> void:
    if not _session_active:
        ui_summary.text = "Start or resume gameplay to reposition touch controls."
        return
    var scene: Node = get_tree().current_scene
    if scene == null:
        ui_summary.text = "Game scene not available."
        return
    var settings_hud: Node = null
    for node in scene.find_children("*", "CanvasLayer", true, false):
        if node.has_method("_open_control_editor"):
            settings_hud = node
            break
    if settings_hud == null:
        ui_summary.text = "Controls editor is not available in this scene."
        return
    # Main-menu CanvasLayer 100 otherwise obscures the real editor at layer 80.
    # Preserve session so MENU returns here later without losing gameplay.
    root.visible = false
    GameSettings.set_pause_reason("main_menu", false)
    settings_hud.call("_open_control_editor")

func _refresh_settings() -> void:
''',"functional menu settings handlers")
assert (root/menu).read_text().count("UI SETTINGS / CONTROLS")==1
assert (root/perf).read_text().count("root.content_scale_size = _sp276_fixed_canvas_size")==1
print("SP276_UI_INDEPENDENCE_PATCH_PASS root HUD canvas stable between quality profiles")
print("SP276_MENU_UI_SETTINGS_PATCH_PASS actual HUD/control/text/touch size controls + in-game editor entry")
