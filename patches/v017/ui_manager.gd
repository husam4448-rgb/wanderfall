extends Node

var _registered_panels: Array[WeakRef] = []
var _active_panel: Control = null
var _active_id := ""
var _icon_cache: Dictionary = {}

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS

func register_panel(panel: Control, panel_id: String = "") -> void:
    if panel == null:
        return
    for ref in _registered_panels:
        if ref.get_ref() == panel:
            return
    _registered_panels.append(weakref(panel))
    panel.set_meta("wanderfall_panel_id", panel_id)
    decorate_panel(panel)

func toggle_panel(panel: Control, panel_id: String = "") -> void:
    if panel == null:
        return
    if panel.visible and _active_panel == panel:
        close_panel(panel)
        return
    open_panel(panel, panel_id)

func open_panel(panel: Control, panel_id: String = "") -> void:
    if panel == null:
        return
    close_all(panel)
    panel.visible = true
    _active_panel = panel
    _active_id = panel_id

func close_panel(panel: Control) -> void:
    if panel == null:
        return
    panel.visible = false
    if _active_panel == panel:
        _active_panel = null
        _active_id = ""

func close_all(except: Control = null) -> void:
    var kept: Array[WeakRef] = []
    for ref in _registered_panels:
        var panel = ref.get_ref()
        if panel == null or not is_instance_valid(panel):
            continue
        kept.append(ref)
        if panel != except:
            panel.visible = false
    _registered_panels = kept
    if except != null:
        _active_panel = except
        _active_id = String(except.get_meta("wanderfall_panel_id", ""))
    else:
        _active_panel = null
        _active_id = ""

func has_open_panel() -> bool:
    return _active_panel != null and is_instance_valid(_active_panel) and _active_panel.visible

func _unhandled_input(event: InputEvent) -> void:
    if not has_open_panel():
        return
    if event is InputEventScreenTouch and event.pressed:
        close_all()
        get_viewport().set_input_as_handled()
    elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        close_all()
        get_viewport().set_input_as_handled()
    elif event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
        close_all()
        get_viewport().set_input_as_handled()

func decorate_button(button: Button, label_text: String = "", icon_key: String = "") -> void:
    if button == null:
        return
    var key := icon_key if not icon_key.is_empty() else icon_for_label(label_text)
    if not key.is_empty():
        var texture := _load_icon(key)
        if texture != null:
            button.icon = texture
            button.icon_max_width = 22
            button.expand_icon = false
    button.add_theme_color_override("font_color", Color("f0f4ed"))
    button.add_theme_color_override("font_hover_color", Color.WHITE)
    button.add_theme_color_override("font_pressed_color", Color("d5e4d2"))
    button.add_theme_constant_override("icon_max_width", 22)
    button.add_theme_stylebox_override("normal", _button_box(Color("26322f"), Color("667c72"), 1))
    button.add_theme_stylebox_override("hover", _button_box(Color("33433f"), Color("91b59e"), 2))
    button.add_theme_stylebox_override("pressed", _button_box(Color("1d2926"), Color("b7d6bd"), 2))
    button.add_theme_stylebox_override("disabled", _button_box(Color(0.12, 0.15, 0.14, 0.68), Color(0.33, 0.38, 0.35, 0.55), 1))

func decorate_panel(panel: Control) -> void:
    if not panel is PanelContainer:
        return
    var box := StyleBoxFlat.new()
    box.bg_color = Color(0.055, 0.075, 0.070, 0.94)
    box.border_color = Color(0.38, 0.50, 0.44, 0.82)
    box.set_border_width_all(1)
    box.set_corner_radius_all(10)
    box.content_margin_left = 14.0
    box.content_margin_right = 14.0
    box.content_margin_top = 12.0
    box.content_margin_bottom = 12.0
    panel.add_theme_stylebox_override("panel", box)

func decorate_status_bar(bar: ProgressBar, stat_name: String) -> void:
    if bar == null:
        return
    var colors := {
        "health": Color("d95955"),
        "stamina": Color("55b878"),
        "hunger": Color("d89b45"),
        "thirst": Color("4f9ed7"),
        "fatigue": Color("a984d1"),
        "encumbrance": Color("c4aa67")
    }
    var background := StyleBoxFlat.new()
    background.bg_color = Color(0.07, 0.09, 0.085, 0.88)
    background.set_corner_radius_all(5)
    var fill := StyleBoxFlat.new()
    fill.bg_color = colors.get(stat_name, Color("72a982"))
    fill.set_corner_radius_all(5)
    bar.add_theme_stylebox_override("background", background)
    bar.add_theme_stylebox_override("fill", fill)

func icon_for_label(label_text: String) -> String:
    var text := label_text.to_upper()
    if text.contains("ATTACK"): return "attack"
    if text.contains("RELOAD"): return "reload"
    if text.contains("SWAP"): return "swap"
    if text.contains("RUN"): return "run"
    if text.contains("CROUCH"): return "crouch"
    if text == "USE" or text.contains("USE ITEM") or text.contains("INTERACT"): return "use"
    if text.contains("BAG") or text.contains("INVENTORY"): return "bag"
    if text.contains("GEAR") or text.contains("EQUIP") or text.contains("TRANSMOG"): return "gear"
    if text.contains("SETTINGS") or text.contains("PRESET"): return "settings"
    if text.begins_with("SAVE") or text.contains("AUTOSAVE"): return "save"
    if text.begins_with("LOAD"): return "load"
    if text.contains("PERF") or text.contains("MODE") or text == "AUTO": return "performance"
    if text.contains("EVENT") or text.contains("OFFER") or text.contains("CONTRACT"): return "events"
    if text.contains("CAMP") or text.contains("BUILD"): return "camp"
    if text.contains("VEH") or text.contains("ENTER") or text.contains("REFUEL") or text.contains("REPAIR"): return "vehicle"
    if text.contains("A11Y") or text.contains("ACCESS"): return "accessibility"
    if text.contains("DEV") or text.contains("SPAWN"): return "dev"
    if text.contains("CLOSE") or text.contains("BACK"): return "close"
    if text.contains("NEXT"): return "next"
    if text.contains("PREV"): return "prev"
    if text == "+": return "zoom_in"
    if text == "−" or text == "-": return "zoom_out"
    return ""

func _load_icon(key: String) -> Texture2D:
    if _icon_cache.has(key):
        return _icon_cache[key]
    var path := "res:" + "//assets/ui/icons/" + key + ".svg"
    if not ResourceLoader.exists(path):
        return null
    var texture = load(path)
    if texture is Texture2D:
        _icon_cache[key] = texture
        return texture
    return null

func _button_box(bg: Color, border: Color, width: int) -> StyleBoxFlat:
    var box := StyleBoxFlat.new()
    box.bg_color = bg
    box.border_color = border
    box.set_border_width_all(width)
    box.set_corner_radius_all(8)
    box.content_margin_left = 10.0
    box.content_margin_right = 10.0
    box.content_margin_top = 7.0
    box.content_margin_bottom = 7.0
    return box
