#!/usr/bin/env python3
"""D2D.2: bake developed ProductionSurvivorVisual poses to PNGs, then use only Sprite2D at runtime."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# ---------------------------------------------------------------------------
# Baked runtime visual: zero live 3D, uses build-generated PNG frames.
# ---------------------------------------------------------------------------
baked=root/"scripts/art/baked_actor_visual.gd"
baked.write_text(r'''class_name BakedActorVisual
extends Node2D

var set_name := "player_male"
var facing := Vector2.DOWN
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var _anim_time := 0.0
var _last_key := ""
var _sprite: Sprite2D
var _cache: Dictionary = {}

const WORLD_SCALE := 0.455
const WALK_FPS := 7.0
const RUN_FPS := 10.0

func setup(set_name_value: String) -> void:
    set_name = set_name_value
    _sprite = Sprite2D.new()
    _sprite.centered = true
    _sprite.position = Vector2(0,-3)
    _sprite.scale = Vector2(WORLD_SCALE,WORLD_SCALE)
    _sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    add_child(_sprite)
    _refresh_frame(true)

func set_facing(value: Vector2) -> void:
    if value.length_squared() > 0.0001:
        facing = value.normalized()
    _refresh_frame(false)

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value

func refresh_gear() -> void:
    pass

func play_melee(_direction: Vector2 = Vector2.ZERO) -> void:
    pass

func _process(delta: float) -> void:
    if move_velocity.length() > 4.0:
        _anim_time += delta
    else:
        _anim_time = 0.0
    _refresh_frame(false)

func _dir_key() -> String:
    var d := facing.normalized()
    if d.y < -0.72:
        if d.x < -0.34: return "northwest"
        if d.x > 0.34: return "northeast"
        return "north"
    if d.y > 0.72:
        if d.x < -0.34: return "southwest"
        if d.x > 0.34: return "southeast"
        return "south"
    return "west" if d.x < 0.0 else "east"

func _state_key() -> String:
    if move_velocity.length() <= 4.0:
        return "idle"
    return "run" if sprinting else "walk"

func _frame_index(state: String) -> int:
    if state == "idle":
        return 0
    var fps := RUN_FPS if state == "run" else WALK_FPS
    return int(floor(_anim_time * fps)) % 4

func _texture_for(key: String) -> Texture2D:
    if _cache.has(key):
        return _cache[key]
    var path := ("res:/" + "/assets/generated/d2d/%s/%s.png") % [set_name,key]
    var tex := load(path) as Texture2D
    _cache[key] = tex
    return tex

func _refresh_frame(force: bool) -> void:
    if _sprite == null:
        return
    var state := _state_key()
    var key := "%s_%s_%02d" % [state,_dir_key(),_frame_index(state)]
    if not force and key == _last_key:
        return
    _last_key = key
    var tex := _texture_for(key)
    if tex != null:
        _sprite.texture = tex
''',encoding="utf-8")

# ---------------------------------------------------------------------------
# Build-time baker. Uses the exact D3D.32.x production rig, then saves PNGs.
# ---------------------------------------------------------------------------
tools=root/"tools"
tools.mkdir(parents=True,exist_ok=True)
baker=tools/"bake_d2d_from_production.gd"
baker.write_text(r'''extends SceneTree

const ProductionVisual = preload("res://scripts/art/production_survivor_visual.gd")
const StaticEquipment = preload("res://scripts/art/static_visual_equipment.gd")

var host: Node2D

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    host = Node2D.new()
    root.add_child(host)
    await process_frame
    await _bake_set(
        "player_male","male",
        {"head":"","eyes":"","lower_face":"","torso":"hoodie","armor":"","hands":"work_gloves","legs":"jeans","feet":"hiking_boots","back":"small_backpack"},
        "pistol_9mm"
    )
    await _bake_set(
        "bandit_female","female",
        {"head":"wool_beanie","eyes":"safety_glasses","lower_face":"cloth_face_wrap","torso":"field_jacket","armor":"tactical_vest","hands":"tactical_gloves","legs":"cargo_pants","feet":"combat_boots","back":"small_backpack"},
        "pistol_9mm"
    )
    print("D2D bake complete.")
    quit(0)

func _bake_set(set_name: String, body_type: String, gear: Dictionary, weapon_id: String) -> void:
    var equipment = StaticEquipment.new()
    host.add_child(equipment)
    equipment.configure(gear,weapon_id)

    var visual = ProductionVisual.new()
    host.add_child(visual)
    visual.setup_equipment(equipment,body_type)
    if visual.has_method("set_external_aiming"):
        visual.set_external_aiming(true,true)

    # Let glTF meshes/materials settle.
    for i in range(4):
        await process_frame

    var out_dir := ("res:/" + "/assets/generated/d2d/%s") % set_name
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir))

    var dirs := {
        "north":Vector2.UP,
        "northeast":Vector2(1,-1).normalized(),
        "east":Vector2.RIGHT,
        "southeast":Vector2(1,1).normalized(),
        "south":Vector2.DOWN,
        "southwest":Vector2(-1,1).normalized(),
        "west":Vector2.LEFT,
        "northwest":Vector2(-1,-1).normalized()
    }
    for dir_name in dirs.keys():
        var d: Vector2 = dirs[dir_name]
        await _capture_pose(visual,out_dir,"idle",dir_name,d,0,false,0.0)
        for frame in range(4):
            await _capture_pose(visual,out_dir,"walk",dir_name,d,frame,false,TAU*float(frame)/4.0)
        for frame in range(4):
            await _capture_pose(visual,out_dir,"run",dir_name,d,frame,true,TAU*float(frame)/4.0)

    host.remove_child(visual)
    visual.queue_free()
    host.remove_child(equipment)
    equipment.queue_free()
    await process_frame

func _capture_pose(visual: Node, out_dir: String, state: String, dir_name: String, d: Vector2, frame: int, run: bool, phase: float) -> void:
    visual.set_facing(d)
    visual.gait_phase = phase
    visual._pose_dirty = true
    visual._character_render_accum = 1.0
    if state == "idle":
        visual.set_motion_state(Vector2.ZERO,false,false)
    else:
        visual.set_motion_state(d*(190.0 if run else 105.0),run,false)
    # Two frames: process pose then render SubViewport.
    await process_frame
    visual._character_render_accum = 1.0
    visual._pose_dirty = true
    await process_frame
    await process_frame

    if visual.viewport == null:
        push_error("No production viewport for bake")
        quit(2)
        return
    var image: Image = visual.viewport.get_texture().get_image()
    if image == null or image.is_empty():
        push_error("Empty baked frame")
        quit(3)
        return
    var filename := "%s/%s_%s_%02d.png" % [out_dir,state,dir_name,frame]
    var err: Error = image.save_png(ProjectSettings.globalize_path(filename))
    if err != OK:
        push_error("Failed save: %s" % filename)
        quit(4)
''',encoding="utf-8")

# ---------------------------------------------------------------------------
# Player: replace old layered + live ProductionSurvivor visual with baked sprite.
# ---------------------------------------------------------------------------
player=root/"scripts/player.gd"
p=player.read_text(encoding="utf-8")
if 'const BakedActorVisualScript' not in p:
    p=p.replace(
        '''const ProductionSurvivorVisualScript = preload("res://scripts/art/production_survivor_visual.gd")
''',
        '''const ProductionSurvivorVisualScript = preload("res://scripts/art/production_survivor_visual.gd")
const BakedActorVisualScript = preload("res://scripts/art/baked_actor_visual.gd")
''',1)
if 'var _baked_visual' not in p:
    p=p.replace('''var _production_visual: Node2D = null
''',
                '''var _production_visual: Node2D = null
var _baked_visual: Node2D = null
''',1)

# D2D.1 still creates both old visuals. Keep creation for code compatibility but hide/disable them.
ready_anchor='''    _weapon_visual.setup_equipment(equipment)
    equipment.weapon_changed.connect(func(_id: String): _refresh_weapon_visual())
'''
if ready_anchor not in p:
    raise SystemExit("D2D.2 player ready anchor missing")
p=p.replace(ready_anchor,'''    _weapon_visual.setup_equipment(equipment)
    _baked_visual = BakedActorVisualScript.new()
    _baked_visual.z_index = 0
    add_child(_baked_visual)
    _baked_visual.setup("player_male")
    equipment.weapon_changed.connect(func(_id: String): _refresh_weapon_visual())
''',1)

# Update actor visibility and facing: baked visual is authoritative.
start='''func _update_actor_visual() -> void:
'''
end='''func _physics_process(delta: float) -> void:
'''
si=p.find(start); ei=p.find(end)
if si<0 or ei<0:
    raise SystemExit("D2D.2 player update actor block missing")
new_update='''func _update_actor_visual() -> void:
    var show_actor := current_vehicle == null or not is_instance_valid(current_vehicle)
    if _actor_visual != null:
        _actor_visual.visible = false
    if _production_visual != null:
        _production_visual.visible = false
        _production_visual.set_process(false)
        if _production_visual.get("viewport") != null:
            _production_visual.viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
    if _baked_visual != null:
        _baked_visual.visible = show_actor
        _baked_visual.set_facing(_facing)
    if _weapon_visual != null:
        # Gun is baked from the developed 3D hand/grip pose.
        _weapon_visual.visible = false

'''
p=p[:si]+new_update+p[ei:]

# Motion state to baked visual.
motion_anchor='''    if _actor_visual != null and _actor_visual.has_method("set_motion_state"):
        _actor_visual.set_motion_state(velocity, is_sprinting, is_crouching)
'''
if motion_anchor in p:
    p=p.replace(motion_anchor,motion_anchor+'''    if _baked_visual != null and _baked_visual.has_method("set_motion_state"):
        _baked_visual.set_motion_state(velocity,is_sprinting,is_crouching)
''',1)

# body type currently male test; if switched, baked set can later select female.
player.write_text(p,encoding="utf-8")

# ---------------------------------------------------------------------------
# Test bandit: distinct baked female production model, no live 3D.
# ---------------------------------------------------------------------------
bandit=root/"scripts/combat/bandit.gd"
b=bandit.read_text(encoding="utf-8")
if 'const BakedActorVisualScript' not in b:
    b=b.replace(
        '''const StaticVisualEquipmentScript = preload("res://scripts/art/static_visual_equipment.gd")
''',
        '''const StaticVisualEquipmentScript = preload("res://scripts/art/static_visual_equipment.gd")
const BakedActorVisualScript = preload("res://scripts/art/baked_actor_visual.gd")
''',1)
if 'var _baked_visual' not in b:
    b=b.replace('''var _production_visual: Node2D = null
''',
                '''var _production_visual: Node2D = null
var _baked_visual: Node2D = null
''',1)

bandit_ready='''    _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    _refresh_visual_mode()
'''
if bandit_ready not in b:
    raise SystemExit("D2D.2 bandit ready anchor missing")
b=b.replace(bandit_ready,'''    _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    if bool(get_meta("d3d322_test_actor", false)):
        _baked_visual = BakedActorVisualScript.new()
        _baked_visual.z_index = 0
        add_child(_baked_visual)
        _baked_visual.setup("bandit_female")
    _refresh_visual_mode()
''',1)

mode_start='''func _refresh_visual_mode() -> void:
'''
mode_end='''func _physics_process(delta: float) -> void:
'''
si=b.find(mode_start); ei=b.find(mode_end)
if si<0 or ei<0:
    raise SystemExit("D2D.2 bandit mode block missing")
mode='''func _refresh_visual_mode() -> void:
    var use_baked := _baked_visual != null and bool(get_meta("d3d322_test_actor", false))
    if _actor_visual != null:
        _actor_visual.visible = not use_baked
    if _production_visual != null:
        _production_visual.visible = false
        _production_visual.set_process(false)
        if _production_visual.get("viewport") != null:
            _production_visual.viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
    if _baked_visual != null:
        _baked_visual.visible = use_baked
    if _weapon_visual != null:
        _weapon_visual.visible = not use_baked and not is_surrendered

'''
b=b[:si]+mode+b[ei:]

# facing/motion into baked visual.
face_anchor='''    if _production_visual != null:
        _production_visual.set_facing(_visual_facing)
'''
if face_anchor in b:
    b=b.replace(face_anchor,'''    if _production_visual != null:
        _production_visual.set_facing(_visual_facing)
'''+'''    if _baked_visual != null:
        _baked_visual.set_facing(_visual_facing)
        if _baked_visual.has_method("set_motion_state"):
            _baked_visual.set_motion_state(velocity,velocity.length() > run_speed*0.75,false)
''',1)
bandit.write_text(b,encoding="utf-8")

# ---------------------------------------------------------------------------
# Version.
# ---------------------------------------------------------------------------
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D2D.1  |  PURE 2D RUNTIME"' not in h:
    raise SystemExit("D2D.2 HUD anchor missing")
h=h.replace('marker.text = "D2D.1  |  PURE 2D RUNTIME"',
            'marker.text = "D2D.2  |  BAKED 3D→2D"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
e=preset.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=66',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.2"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.2 version anchors missing")
preset.write_text(e,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    s=save.read_text(encoding="utf-8")
    s,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.2"',s,count=1)
    save.write_text(s,encoding="utf-8")

print("Applied D2D.2: build-time production-rig sprite bake + runtime Sprite2D cache; no old layered player fallback.")
