#!/usr/bin/env python3
"""D3D.13A: dual-stick visible overdrag latches, compact knobs and larger circles."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
stick=root/"scripts/virtual_joystick.gd"
s=stick.read_text(encoding="utf-8")
def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("D3D.13 stick anchor missing: "+label)
    s=s.replace(old,new,1)

rep("var follow_base := true\n","var follow_base := false\nvar edge_lock_enabled := true\nvar edge_lock_ratio := 1.12\nvar _latched := false\nvar _edge_armed := false\n","latch state")
rep("        if UIManager.layout_edit_mode and _active_pointer != -1:\n            _release()\n",
    "        if UIManager.layout_edit_mode:\n            if _latched:\n                _clear_lock()\n            if _active_pointer != -1:\n                _release()\n","layout-edit unlock")
rep("    if _active_pointer == -1:\n        _home_position = position\n        _gesture_home = position\n        _value = Vector2.ZERO\n",
    "    if _active_pointer == -1 and not _latched:\n        _home_position = position\n        _gesture_home = position\n        _value = Vector2.ZERO\n","mobile setup latch retention")
rep("func sync_home_from_current() -> void:\n    if _active_pointer == -1:\n",
    "func sync_home_from_current() -> void:\n    if _active_pointer == -1 and not _latched:\n","home sync")

def replace_func(signature,body):
    global s
    marker="func "+signature+":\n"
    i=s.find(marker)
    if i<0:raise SystemExit("D3D.13 missing func "+signature)
    j=s.find("\nfunc ",i+len(marker))
    if j<0:j=len(s)
    s=s[:i]+body.rstrip()+"\n"+s[j:]

replace_func("_gui_input(event: InputEvent) -> void",r'''func _gui_input(event: InputEvent) -> void:
    if floating_mode or UIManager.layout_edit_mode:
        return
    if event is InputEventScreenTouch:
        if event.pressed and _latched:
            _clear_lock()
            accept_event()
            return
        if event.pressed and _active_pointer == -1:
            _active_pointer = event.index
            _gesture_home = position
            _home_position = position
            _update_from_global(global_position + event.position)
            accept_event()
        elif not event.pressed and event.index == _active_pointer:
            _release()
            accept_event()
    elif event is InputEventScreenDrag and event.index == _active_pointer:
        _update_from_global(global_position + event.position)
        accept_event()
    elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
        if event.pressed and _latched:
            _clear_lock()
            accept_event()
            return
        if event.pressed and _active_pointer == -1:
            _active_pointer = -2
            _gesture_home = position
            _home_position = position
            _update_from_global(global_position + event.position)
        elif not event.pressed and _active_pointer == -2:
            _release()
        accept_event()
    elif event is InputEventMouseMotion and _active_pointer == -2 and Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
        _update_from_global(global_position + event.position)
        accept_event()
''')

replace_func("_unhandled_input(event: InputEvent) -> void",r'''func _unhandled_input(event: InputEvent) -> void:
    if not floating_mode or UIManager.layout_edit_mode:
        return
    if event is InputEventScreenTouch:
        if event.pressed and _latched:
            if _touches_visible_stick(event.position):
                _clear_lock()
                get_viewport().set_input_as_handled()
            return
        if event.pressed and _active_pointer == -1 and _in_activation_zone(event.position):
            _active_pointer = event.index
            _gesture_home = _home_position
            position = event.position - size * 0.5
            _update_from_global(event.position)
            get_viewport().set_input_as_handled()
        elif not event.pressed and event.index == _active_pointer:
            _release()
            get_viewport().set_input_as_handled()
    elif event is InputEventScreenDrag and event.index == _active_pointer:
        _update_from_global(event.position)
        get_viewport().set_input_as_handled()
    elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
        if event.pressed and _latched:
            if _touches_visible_stick(event.position):
                _clear_lock()
                get_viewport().set_input_as_handled()
            return
        if event.pressed and _active_pointer == -1 and _in_activation_zone(event.position):
            _active_pointer = -2
            _gesture_home = _home_position
            position = event.position - size * 0.5
            _update_from_global(event.position)
            get_viewport().set_input_as_handled()
        elif not event.pressed and _active_pointer == -2:
            _release()
            get_viewport().set_input_as_handled()
    elif event is InputEventMouseMotion and _active_pointer == -2 and Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
        _update_from_global(event.position)
        get_viewport().set_input_as_handled()

func _touches_visible_stick(pointer: Vector2) -> bool:
    return pointer.distance_to(global_position + size * 0.5) <= radius * edge_lock_ratio + 18.0
''')

replace_func("_update_from_global(global_pointer: Vector2) -> void",r'''func _update_from_global(global_pointer: Vector2) -> void:
    var center_global := global_position + size * 0.5
    var delta := global_pointer - center_global
    var travel := delta.length()
    _edge_armed = edge_lock_enabled and travel >= radius * edge_lock_ratio
    # Keep the stationary red ring aligned with the intended lock boundary.
    if follow_base and not edge_lock_enabled and travel > radius:
        var shift := delta.normalized() * (travel - radius)
        position += shift
        center_global += shift
        delta = global_pointer - center_global
    _value = (delta / maxf(radius,1.0)).limit_length(1.0)
    vector_changed.emit(_value)
    queue_redraw()
''')

replace_func("_release() -> void",r'''func _release() -> void:
    _active_pointer = -1
    if _edge_armed and _value.length_squared() > 0.01 and not UIManager.layout_edit_mode:
        _latched = true
        _edge_armed = false
        _value = _value.normalized()
        vector_changed.emit(_value)
        queue_redraw()
        return
    _latched = false
    _edge_armed = false
    _value = Vector2.ZERO
    vector_changed.emit(_value)
    position = _home_position if floating_mode else _gesture_home
    queue_redraw()

func _clear_lock() -> void:
    _latched = false
    _edge_armed = false
    _active_pointer = -1
    _value = Vector2.ZERO
    vector_changed.emit(_value)
    position = _home_position if floating_mode else _gesture_home
    queue_redraw()
''')

replace_func("_draw() -> void",r'''func _draw() -> void:
    var center := size * 0.5
    draw_circle(center,radius,Color(0.05,0.08,0.08,0.25))
    var red := Color(0.92,0.19,0.19,0.66) if _latched else Color(0.89,0.20,0.20,0.34)
    draw_arc(center,radius*edge_lock_ratio,0.0,TAU,80,red,8.0,true)
    draw_arc(center,radius,0.0,TAU,64,Color(0.85,0.93,0.87,0.55),2.5,true)
    if _latched:
        draw_arc(center,radius*edge_lock_ratio+5.0,0.0,TAU,80,Color(1.0,0.34,0.28,0.48),2.0,true)
    draw_circle(center+_value*radius,knob_radius,Color(0.87,0.95,0.88,0.84))
''')
stick.write_text(s,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
m=hud.read_text(encoding="utf-8")
# New IDs apply the larger defaults even if an old layout was saved.
m=re.sub(r'"joystick_v0200d3d10"','"joystick_v0200d3d13"',m,count=1)
m=re.sub(r'"aim_joystick_v0200d3d10"','"aim_joystick_v0200d3d13"',m,count=1)
m,nmove=re.subn(r'var move_size := clampf\([^\n]+\)',
    'var move_size := clampf(short_side * 0.365 * clampf(ts, 0.85, 1.30), 225.0, 370.0)',m,count=1)
m,naim=re.subn(r'var aim_size := clampf\([^\n]+\)',
    'var aim_size := clampf(move_size * 0.98, 220.0, 360.0)',m,count=1)
if not nmove or not naim:
    raise SystemExit("D3D.13 HUD responsive size anchors missing")
# The white marker shrinks independently from the enlarged actual touch field.
m,nknob=re.subn(r'joystick\.knob_radius\s*=\s*move_size\s*\*\s*0\.\d+',
    'joystick.knob_radius = move_size * 0.105',m,count=1)
m,naknob=re.subn(r'aim_joystick\.knob_radius\s*=\s*aim_size\s*\*\s*0\.\d+',
    'aim_joystick.knob_radius = aim_size * 0.105',m,count=1)
if not nknob or not naknob:
    raise SystemExit("D3D.13 HUD knob anchors missing")
m=m.replace('    _build_ui()\n',
    '    _build_ui()\n    joystick.follow_base = false\n    aim_joystick.follow_base = false\n',1)
hud.write_text(m,encoding="utf-8")
print("D3D.13A: visible faint-red edge rings, independent tap-release input latches and larger control zones with smaller white markers.")
