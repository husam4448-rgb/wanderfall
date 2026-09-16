extends CanvasLayer

var root: ColorRect
var menu_panel: PanelContainer
var main_box: VBoxContainer
var load_box: VBoxContainer
var settings_box: VBoxContainer
var mods_box: VBoxContainer
var continue_button: Button
var message_label: Label
var settings_summary: Label
var load_buttons: Array[Button] = []

func _ready() -> void:
    layer = 100
    process_mode = Node.PROCESS_MODE_ALWAYS
    _build_ui()
    _refresh()
    get_tree().paused = true

func _build_ui() -> void:
    root = ColorRect.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root.color = Color("101815")
    root.mouse_filter = Control.MOUSE_FILTER_STOP
    add_child(root)

    var glow := ColorRect.new()
    glow.color = Color(0.20, 0.34, 0.25, 0.28)
    glow.anchor_right = 0.42
    glow.anchor_bottom = 1.0
    root.add_child(glow)

    var title := Label.new()
    title.text = "WANDERFALL"
    title.position = Vector2(58, 58)
    title.add_theme_font_size_override("font_size", 44)
    title.add_theme_color_override("font_color", Color("e9f0dc"))
    root.add_child(title)

    var subtitle := Label.new()
    subtitle.text = "OFFLINE SURVIVAL SANDBOX  •  v0.17"
    subtitle.position = Vector2(62, 114)
    subtitle.add_theme_font_size_override("font_size", 15)
    subtitle.add_theme_color_override("font_color", Color("9db49f"))
    root.add_child(subtitle)

    var flavor := Label.new()
    flavor.text = "Scavenge. Endure. Build something that lasts."
    flavor.position = Vector2(62, 158)
    flavor.add_theme_font_size_override("font_size", 18)
    flavor.add_theme_color_override("font_color", Color("cad7c6"))
    root.add_child(flavor)

    menu_panel = PanelContainer.new()
    menu_panel.custom_minimum_size = Vector2(420, 510)
    menu_panel.anchor_left = 0.57
    menu_panel.anchor_top = 0.50
    menu_panel.anchor_right = 0.57
    menu_panel.anchor_bottom = 0.50
    menu_panel.offset_left = -210
    menu_panel.offset_top = -255
    menu_panel.offset_right = 210
    menu_panel.offset_bottom = 255
    UIManager.decorate_panel(menu_panel)
    root.add_child(menu_panel)

    var stack := VBoxContainer.new()
    stack.add_theme_constant_override("separation", 10)
    menu_panel.add_child(stack)

    main_box = VBoxContainer.new()
    main_box.add_theme_constant_override("separation", 9)
    stack.add_child(main_box)
    var menu_title := Label.new()
    menu_title.text = "MAIN MENU"
    menu_title.add_theme_font_size_override("font_size", 24)
    main_box.add_child(menu_title)

    continue_button = _menu_button("CONTINUE", "load")
    continue_button.pressed.connect(_continue_game)
    main_box.add_child(continue_button)
    var new_game := _menu_button("NEW GAME", "new_game")
    new_game.pressed.connect(_start_new_game)
    main_box.add_child(new_game)
    var load_game := _menu_button("LOAD SAVE", "load")
    load_game.pressed.connect(func(): _show_section(load_box))
    main_box.add_child(load_game)
    var settings := _menu_button("SETTINGS", "settings")
    settings.pressed.connect(func(): _show_section(settings_box); _refresh_settings())
    main_box.add_child(settings)
    var mods := _menu_button("MODS", "mods")
    mods.pressed.connect(func(): _show_section(mods_box))
    main_box.add_child(mods)
    var exit := _menu_button("EXIT", "exit")
    exit.pressed.connect(func(): get_tree().quit())
    main_box.add_child(exit)

    message_label = Label.new()
    message_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    message_label.add_theme_font_size_override("font_size", 13)
    message_label.add_theme_color_override("font_color", Color("d3c18a"))
    main_box.add_child(message_label)

    load_box = VBoxContainer.new()
    load_box.visible = false
    load_box.add_theme_constant_override("separation", 8)
    stack.add_child(load_box)
    var load_title := Label.new()
    load_title.text = "LOAD SAVE"
    load_title.add_theme_font_size_override("font_size", 22)
    load_box.add_child(load_title)
    var slots := [SaveManager.AUTOSAVE_SLOT, "slot_1", "slot_2", "slot_3"]
    for slot_id in slots:
        var b := _menu_button("SAVE SLOT", "load")
        b.pressed.connect(_load_slot.bind(String(slot_id)))
        load_buttons.append(b)
        load_box.add_child(b)
    var load_back := _menu_button("BACK", "close")
    load_back.pressed.connect(func(): _show_section(main_box); _refresh())
    load_box.add_child(load_back)

    settings_box = VBoxContainer.new()
    settings_box.visible = false
    settings_box.add_theme_constant_override("separation", 8)
    stack.add_child(settings_box)
    var settings_title := Label.new()
    settings_title.text = "SETTINGS"
    settings_title.add_theme_font_size_override("font_size", 22)
    settings_box.add_child(settings_title)
    settings_summary = Label.new()
    settings_summary.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    settings_summary.add_theme_font_size_override("font_size", 13)
    settings_box.add_child(settings_summary)
    var perf := _menu_button("PERFORMANCE MODE", "performance")
    perf.pressed.connect(func(): PerformanceManager.cycle_profile(); _refresh_settings())
    settings_box.add_child(perf)
    var difficulty := _menu_button("DIFFICULTY PRESET", "settings")
    difficulty.pressed.connect(func(): GameSettings.cycle_preset(); _refresh_settings())
    settings_box.add_child(difficulty)
    var text_scale := _menu_button("TEXT / UI SCALE", "settings")
    text_scale.pressed.connect(func(): GameSettings.cycle_scalar("text_scale"); _refresh_settings())
    settings_box.add_child(text_scale)
    var touch_scale := _menu_button("TOUCH CONTROL SIZE", "settings")
    touch_scale.pressed.connect(func(): GameSettings.cycle_scalar("touch_scale"); _refresh_settings())
    settings_box.add_child(touch_scale)
    var flashes := _menu_button("REDUCED FLASHES", "accessibility")
    flashes.pressed.connect(func(): GameSettings.toggle_flag("reduced_flashes"); _refresh_settings())
    settings_box.add_child(flashes)
    var settings_back := _menu_button("BACK", "close")
    settings_back.pressed.connect(func(): _show_section(main_box); _refresh())
    settings_box.add_child(settings_back)

    mods_box = VBoxContainer.new()
    mods_box.visible = false
    mods_box.add_theme_constant_override("separation", 10)
    stack.add_child(mods_box)
    var mods_title := Label.new()
    mods_title.text = "MODS"
    mods_title.add_theme_font_size_override("font_size", 22)
    mods_box.add_child(mods_title)
    var mods_info := Label.new()
    mods_info.text = "Wanderfall is being kept data-driven for offline mod support.\n\nThis development build exposes the MODS entry now; external package loading will be enabled only after the data-mod sandbox and save compatibility rules are finalized."
    mods_info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    mods_info.custom_minimum_size = Vector2(360, 190)
    mods_info.add_theme_font_size_override("font_size", 14)
    mods_box.add_child(mods_info)
    var mods_back := _menu_button("BACK", "close")
    mods_back.pressed.connect(func(): _show_section(main_box))
    mods_box.add_child(mods_back)

func _menu_button(text_value: String, icon_key: String) -> Button:
    var button := Button.new()
    button.text = text_value
    button.custom_minimum_size = Vector2(360, 54)
    button.focus_mode = Control.FOCUS_NONE
    button.add_theme_font_size_override("font_size", 16)
    button.alignment = HORIZONTAL_ALIGNMENT_LEFT
    UIManager.decorate_button(button, text_value, icon_key)
    return button

func _show_section(section: Control) -> void:
    for item in [main_box, load_box, settings_box, mods_box]:
        if item != null:
            item.visible = item == section

func _refresh() -> void:
    if continue_button == null:
        return
    var latest := SaveManager.get_latest_save_slot()
    continue_button.disabled = latest.is_empty()
    continue_button.text = "CONTINUE" if latest.is_empty() else "CONTINUE  •  %s" % latest.replace("_", " ").capitalize()
    var slots := [SaveManager.AUTOSAVE_SLOT, "slot_1", "slot_2", "slot_3"]
    for i in range(load_buttons.size()):
        var slot_id: String = slots[i]
        load_buttons[i].text = SaveManager.get_slot_summary(slot_id)
        load_buttons[i].disabled = not SaveManager.slot_exists(slot_id)

func _refresh_settings() -> void:
    if settings_summary == null:
        return
    settings_summary.text = "Performance: %s\nDifficulty: %s\nText/UI scale: ×%.2f\nTouch controls: ×%.2f\nReduced flashes: %s" % [
        PerformanceManager.requested_profile,
        GameSettings.current_preset,
        GameSettings.text_scale,
        GameSettings.touch_scale,
        "ON" if GameSettings.reduced_flashes else "OFF"
    ]

func _start_new_game() -> void:
    message_label.text = ""
    UIManager.close_all()
    InputState.reset_mobile_state()
    root.visible = false
    get_tree().paused = false

func _continue_game() -> void:
    var latest := SaveManager.get_latest_save_slot()
    if latest.is_empty():
        message_label.text = "No valid save was found."
        return
    _load_slot(latest)

func _load_slot(slot_id: String) -> void:
    var result := SaveManager.load_slot(slot_id)
    if not bool(result.get("ok", false)):
        message_label.text = String(result.get("message", "Load failed."))
        _show_section(main_box)
        return
    _start_new_game()

func _input(event: InputEvent) -> void:
    if not root.visible:
        return
    if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
        if not main_box.visible:
            _show_section(main_box)
            _refresh()
        get_viewport().set_input_as_handled()
