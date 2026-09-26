#!/usr/bin/env python3
"""D2D.3: true 2D-only runtime, gear-responsive baked variants, flatter sprite-art treatment."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# ---------------------------------------------------------------------------
# Runtime baked actor: no dependency on production 3D scripts/resources.
# Select a pre-baked set from live equipment state.
# ---------------------------------------------------------------------------
baked=root/"scripts/art/baked_actor_visual.gd"
baked.write_text(r'''class_name BakedActorVisual
extends Node2D

var set_name := "player_male_t1_a0_b1_h0_w1"
var facing := Vector2.DOWN
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var _anim_time := 0.0
var _last_key := ""
var _sprite: Sprite2D
var _cache: Dictionary = {}
var _equipment: Node = null
var _dynamic_player_set := false
var _body_type := "male"
var _gear_poll := 0.0

const WORLD_SCALE := 0.455
const WALK_FPS := 7.0
const RUN_FPS := 10.0

func _make_flat_sprite_material() -> ShaderMaterial:
    var shader := Shader.new()
    shader.code = """
shader_type canvas_item;
render_mode unshaded;

uniform float bands = 6.0;
uniform float saturation = 0.82;
uniform float edge_strength = 0.58;

void fragment() {
    vec4 src = texture(TEXTURE, UV);
    if (src.a < 0.015) {
        COLOR = vec4(0.0);
        return;
    }

    float lum = dot(src.rgb, vec3(0.299, 0.587, 0.114));
    float q = floor(lum * bands + 0.5) / bands;
    vec3 chroma = src.rgb / max(lum, 0.055);
    vec3 flat = clamp(chroma * q, vec3(0.0), vec3(1.0));
    flat = mix(vec3(q), flat, saturation);

    vec2 px = TEXTURE_PIXEL_SIZE;
    float n = texture(TEXTURE, UV + vec2(0.0, -px.y)).a;
    float s = texture(TEXTURE, UV + vec2(0.0,  px.y)).a;
    float e = texture(TEXTURE, UV + vec2( px.x, 0.0)).a;
    float w = texture(TEXTURE, UV + vec2(-px.x, 0.0)).a;
    float border = 1.0 - step(0.12, min(min(n,s),min(e,w)));
    flat *= mix(1.0, edge_strength, border);

    COLOR = vec4(flat, src.a);
}
"""
    var material := ShaderMaterial.new()
    material.shader = shader
    return material

func _create_sprite() -> void:
    _sprite = Sprite2D.new()
    _sprite.centered = true
    _sprite.position = Vector2(0,-3)
    _sprite.scale = Vector2(WORLD_SCALE,WORLD_SCALE)
    _sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    _sprite.material = _make_flat_sprite_material()
    add_child(_sprite)

func setup(set_name_value: String) -> void:
    _dynamic_player_set = false
    set_name = set_name_value
    _create_sprite()
    _refresh_frame(true)

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:
    _dynamic_player_set = true
    _equipment = equipment_value
    _body_type = "female" if body_type_value == "female" else "male"
    _create_sprite()
    refresh_gear()

func set_body_type(value: String) -> void:
    _body_type = "female" if value == "female" else "male"
    refresh_gear()

func set_facing(value: Vector2) -> void:
    if value.length_squared() > 0.0001:
        facing = value.normalized()
    _refresh_frame(false)

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value

func _has_visual(slot: String) -> bool:
    return _equipment != null and is_instance_valid(_equipment) and _equipment.has_method("get_visual_item") and not String(_equipment.call("get_visual_item",slot)).is_empty()

func _has_weapon() -> bool:
    if _equipment == null or not is_instance_valid(_equipment):
        return false
    if _equipment.has_method("get_weapon_category"):
        return not String(_equipment.call("get_weapon_category")).is_empty()
    return false

func _desired_player_set() -> String:
    # D2D.3 checkpoint bakes canonical visual representatives for the five
    # most readable equipment changes. Exact item-specific art comes after
    # this performance/architecture checkpoint.
    var t := 1 if _has_visual("torso") else 0
    var a := 1 if _has_visual("armor") else 0
    var b := 1 if _has_visual("back") else 0
    var h := 1 if _has_visual("head") else 0
    var w := 1 if _has_weapon() else 0
    # Current player checkpoint is male; retain valid male art if BODY is
    # switched until the female player bake set is added next.
    return "player_male_t%d_a%d_b%d_h%d_w%d" % [t,a,b,h,w]

func refresh_gear() -> void:
    if not _dynamic_player_set:
        return
    var desired := _desired_player_set()
    if desired != set_name:
        set_name = desired
        _last_key = ""
        _refresh_frame(true)

func play_melee(_direction: Vector2 = Vector2.ZERO) -> void:
    pass

func _process(delta: float) -> void:
    if move_velocity.length() > 4.0:
        _anim_time += delta
    else:
        _anim_time = 0.0

    if _dynamic_player_set:
        _gear_poll += delta
        if _gear_poll >= 0.12:
            _gear_poll = 0.0
            refresh_gear()

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
    var cache_key := set_name + "/" + key
    if _cache.has(cache_key):
        return _cache[cache_key]
    var path := ("res:/" + "/assets/generated/d2d/%s/%s.png") % [set_name,key]
    var tex := load(path) as Texture2D
    _cache[cache_key] = tex
    return tex

func _refresh_frame(force: bool) -> void:
    if _sprite == null:
        return
    var state := _state_key()
    var frame_key := "%s_%s_%02d" % [state,_dir_key(),_frame_index(state)]
    var full_key := set_name + "/" + frame_key
    if not force and full_key == _last_key:
        return
    _last_key = full_key
    var tex := _texture_for(frame_key)
    if tex != null:
        _sprite.texture = tex
''',encoding="utf-8")

# ---------------------------------------------------------------------------
# Build-time baker: generate 32 player gear-state combinations + bandit.
# 32*72 + 72 = 2376 PNG frames.
# ---------------------------------------------------------------------------
tools=root/"tools"
baker=tools/"bake_d2d_from_production.gd"
baker.write_text(r'''extends Node

const ProductionVisual = preload("res://scripts/art/production_survivor_visual.gd")
const StaticEquipment = preload("res://scripts/art/static_visual_equipment.gd")

var host: Node2D

func _ready() -> void:
    call_deferred("_run")

func _run() -> void:
    host = Node2D.new()
    add_child(host)
    await get_tree().process_frame

    # Five highly readable equipment states: torso, armor, back, head, weapon.
    # This preserves immediate equip/unequip feedback while keeping runtime pure 2D.
    for torso_on in range(2):
        for armor_on in range(2):
            for back_on in range(2):
                for head_on in range(2):
                    for weapon_on in range(2):
                        var gear := {
                            "head": "wool_beanie" if head_on == 1 else "",
                            "eyes": "",
                            "lower_face": "",
                            "torso": "hoodie" if torso_on == 1 else "",
                            "armor": "tactical_vest" if armor_on == 1 else "",
                            "hands": "work_gloves",
                            "legs": "jeans",
                            "feet": "hiking_boots",
                            "back": "small_backpack" if back_on == 1 else "",
                            "binoculars": ""
                        }
                        var weapon_id := "pistol_9mm" if weapon_on == 1 else ""
                        var set_name := "player_male_t%d_a%d_b%d_h%d_w%d" % [torso_on,armor_on,back_on,head_on,weapon_on]
                        await _bake_set(set_name,"male",gear,weapon_id)

    await _bake_set(
        "bandit_female","female",
        {
            "head":"wool_beanie",
            "eyes":"safety_glasses",
            "lower_face":"cloth_face_wrap",
            "torso":"field_jacket",
            "armor":"tactical_vest",
            "hands":"tactical_gloves",
            "legs":"cargo_pants",
            "feet":"combat_boots",
            "back":"small_backpack",
            "binoculars":""
        },
        "pistol_9mm"
    )

    print("D2D.3 bake complete.")
    get_tree().quit(0)

func _bake_set(set_name: String, body_type: String, gear: Dictionary, weapon_id: String) -> void:
    var equipment = StaticEquipment.new()
    host.add_child(equipment)
    equipment.configure(gear,weapon_id)

    var visual = ProductionVisual.new()
    host.add_child(visual)
    visual.setup_equipment(equipment,body_type)
    if visual.has_method("set_external_aiming"):
        visual.set_external_aiming(true,not weapon_id.is_empty())

    for i in range(3):
        await get_tree().process_frame

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
    await get_tree().process_frame

func _capture_pose(visual: Node, out_dir: String, state: String, dir_name: String, d: Vector2, frame: int, run: bool, phase: float) -> void:
    visual.set_facing(d)
    visual.gait_phase = phase
    visual._pose_dirty = true
    visual._character_render_accum = 1.0
    if state == "idle":
        visual.set_motion_state(Vector2.ZERO,false,false)
    else:
        visual.set_motion_state(d*(190.0 if run else 105.0),run,false)

    await get_tree().process_frame
    visual._character_render_accum = 1.0
    visual._pose_dirty = true
    await get_tree().process_frame

    if visual.viewport == null:
        push_error("No production viewport for bake")
        get_tree().quit(2)
        return
    var image: Image = visual.viewport.get_texture().get_image()
    if image == null or image.is_empty():
        push_error("Empty baked frame")
        get_tree().quit(3)
        return

    # Keep the original anatomical/pose detail. The runtime shader performs
    # the flatter Scavland-like luminance banding and silhouette treatment.
    var filename := "%s/%s_%s_%02d.png" % [out_dir,state,dir_name,frame]
    var err: Error = image.save_png(ProjectSettings.globalize_path(filename))
    if err != OK:
        push_error("Failed save: %s" % filename)
        get_tree().quit(4)
''',encoding="utf-8")

# ---------------------------------------------------------------------------
# Player: eliminate runtime 3D preload + instance, old layered actor and old
# weapon renderer. BakedActorVisual becomes the only character renderer.
# ---------------------------------------------------------------------------
player=root/"scripts/player.gd"
p=player.read_text(encoding="utf-8")

p=p.replace('const ProductionSurvivorVisualScript = preload("res://scripts/art/production_survivor_visual.gd")\n',"",1)

old_ready='''    _actor_visual = LayeredActorVisualScript.new()
    _actor_visual.z_index = -1
    _actor_visual.scale = Vector2(1.06, 1.06)
    add_child(_actor_visual)
    _actor_visual.setup_equipment(equipment, body_type, "player")
    equipment.apparel_changed.connect(_refresh_actor_visual)
    equipment.transmog_changed.connect(_refresh_actor_visual)
    _production_visual = ProductionSurvivorVisualScript.new()
    _production_visual.z_index = 0
    _production_visual.scale = Vector2(1.0, 1.0)
    add_child(_production_visual)
    _production_visual.setup_equipment(equipment, body_type)
    _weapon_visual = WeaponVisualScript.new()
    _weapon_visual.z_index = 3
    _weapon_visual.scale = Vector2(0.72, 0.78)
    add_child(_weapon_visual)
    _weapon_visual.setup_equipment(equipment)
    _baked_visual = BakedActorVisualScript.new()
    _baked_visual.z_index = 0
    add_child(_baked_visual)
    _baked_visual.setup("player_male")
    equipment.weapon_changed.connect(func(_id: String): _refresh_weapon_visual())
    equipment.attachments_changed.connect(_refresh_weapon_visual)
'''
new_ready='''    # D2D.3: one renderer only. No runtime glTF preload, SubViewport,
    # layered fallback character, or separate old weapon sprite.
    _baked_visual = BakedActorVisualScript.new()
    _baked_visual.z_index = 0
    add_child(_baked_visual)
    _baked_visual.setup_equipment(equipment, body_type)
    equipment.apparel_changed.connect(_refresh_actor_visual)
    equipment.transmog_changed.connect(_refresh_actor_visual)
    equipment.weapon_changed.connect(func(_id: String): _refresh_weapon_visual())
    equipment.attachments_changed.connect(_refresh_weapon_visual)
'''
if old_ready not in p:
    raise SystemExit("D2D.3 exact player visual construction block missing")
p=p.replace(old_ready,new_ready,1)

# Refresh functions now drive only baked visual.
start='''func set_body_type(value: String) -> void:
'''
end='''func _update_actor_visual() -> void:
'''
si=p.find(start); ei=p.find(end)
if si<0 or ei<0:
    raise SystemExit("D2D.3 player refresh function range missing")
replacement='''func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"
    if _baked_visual != null and _baked_visual.has_method("set_body_type"):
        _baked_visual.set_body_type(body_type)
    queue_redraw()

func _refresh_actor_visual() -> void:
    if _baked_visual != null and _baked_visual.has_method("refresh_gear"):
        _baked_visual.refresh_gear()

func _refresh_weapon_visual() -> void:
    if _baked_visual != null and _baked_visual.has_method("refresh_gear"):
        _baked_visual.refresh_gear()
    queue_redraw()

func _update_weapon_mount() -> void:
    pass

'''
p=p[:si]+replacement+p[ei:]

# Replace actor update with baked-only logic.
start='''func _update_actor_visual() -> void:
'''
end='''func _physics_process(delta: float) -> void:
'''
si=p.find(start); ei=p.find(end)
if si<0 or ei<0:
    raise SystemExit("D2D.3 player update visual range missing")
replacement='''func _update_actor_visual() -> void:
    var show_actor := current_vehicle == null or not is_instance_valid(current_vehicle)
    if _baked_visual != null:
        _baked_visual.visible = show_actor
        _baked_visual.set_facing(_facing)

'''
p=p[:si]+replacement+p[ei:]

# Remove per-frame calls into old visual objects.
p=re.sub(r'''    if _actor_visual != null and _actor_visual\.has_method\("set_motion_state"\):\n        _actor_visual\.set_motion_state\(velocity, is_sprinting, is_crouching\)\n''',"",p,count=1)
p=re.sub(r'''    if _production_visual != null and _production_visual\.has_method\("set_motion_state"\):\n        _production_visual\.set_motion_state\(velocity, is_sprinting, is_crouching\)\n''',"",p,count=1)

player.write_text(p,encoding="utf-8")

# ---------------------------------------------------------------------------
# Test bandit: keep normal legacy bandits untouched for now, but controlled
# D2D test bandit uses only baked female sprite; no production 3D creation.
# ---------------------------------------------------------------------------
bandit=root/"scripts/combat/bandit.gd"
b=bandit.read_text(encoding="utf-8")
b=b.replace('const ProductionSurvivorVisualScript = preload("res://scripts/art/production_survivor_visual.gd")\n',"",1)

old='''    _actor_visual = LayeredActorVisualScript.new()
    _actor_visual.z_index = -1
    _actor_visual.scale = Vector2(1.02, 1.02)
    add_child(_actor_visual)
    _actor_visual.setup_static(body_type, "bandit", equipped_visual_gear)

    if bool(get_meta("d3d322_test_actor", false)):
        _visual_equipment = StaticVisualEquipmentScript.new()
        add_child(_visual_equipment)
        _visual_equipment.configure(equipped_visual_gear, equipped_weapon_id)
        _production_visual = ProductionSurvivorVisualScript.new()
        _production_visual.z_index = 0
        add_child(_production_visual)
        _production_visual.setup_equipment(_visual_equipment, body_type)
        if _production_visual.has_method("set_external_aiming"):
            _production_visual.set_external_aiming(true, true)

    _weapon_visual = WeaponVisualScript.new()
    _weapon_visual.z_index = 2
    _weapon_visual.scale = Vector2(0.74, 0.80)
    add_child(_weapon_visual)
    _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    if bool(get_meta("d3d322_test_actor", false)):
        _baked_visual = BakedActorVisualScript.new()
        _baked_visual.z_index = 0
        add_child(_baked_visual)
        _baked_visual.setup("bandit_female")
    _refresh_visual_mode()
'''
new='''    if bool(get_meta("d3d322_test_actor", false)):
        _baked_visual = BakedActorVisualScript.new()
        _baked_visual.z_index = 0
        add_child(_baked_visual)
        _baked_visual.setup("bandit_female")
    else:
        _actor_visual = LayeredActorVisualScript.new()
        _actor_visual.z_index = -1
        _actor_visual.scale = Vector2(1.02, 1.02)
        add_child(_actor_visual)
        _actor_visual.setup_static(body_type, "bandit", equipped_visual_gear)
        _weapon_visual = WeaponVisualScript.new()
        _weapon_visual.z_index = 2
        _weapon_visual.scale = Vector2(0.74, 0.80)
        add_child(_weapon_visual)
        _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    _refresh_visual_mode()
'''
if old not in b:
    raise SystemExit("D2D.3 exact bandit visual construction block missing")
b=b.replace(old,new,1)

# Remove live production visual branches in update and surrender.
b=re.sub(r'''    if _production_visual != null:\n        _production_visual\.set_facing\(_visual_facing\)\n        if _production_visual\.has_method\("set_motion_state"\):\n            _production_visual\.set_motion_state\(velocity, velocity\.length\(\) > run_speed \* 0\.75, false\)\n        if _production_visual\.has_method\("set_external_aiming"\):\n            _production_visual\.set_external_aiming\(true, not is_surrendered\)\n''',"",b,count=1)
b=re.sub(r'''    if _production_visual != null and _production_visual\.has_method\("set_external_aiming"\):\n        _production_visual\.set_external_aiming\(true, false\)\n''',"",b,count=1)

# Rewrite visual mode to never touch production.
start='''func _refresh_visual_mode() -> void:
'''
end='''func _physics_process(delta: float) -> void:
'''
si=b.find(start); ei=b.find(end)
if si<0 or ei<0:
    raise SystemExit("D2D.3 bandit visual mode range missing")
mode='''func _refresh_visual_mode() -> void:
    var use_baked := _baked_visual != null and bool(get_meta("d3d322_test_actor", false))
    if _actor_visual != null:
        _actor_visual.visible = not use_baked
    if _baked_visual != null:
        _baked_visual.visible = use_baked
    if _weapon_visual != null:
        _weapon_visual.visible = not use_baked and not is_surrendered

'''
b=b[:si]+mode+b[ei:]
bandit.write_text(b,encoding="utf-8")

# ---------------------------------------------------------------------------
# Version.
# ---------------------------------------------------------------------------
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D2D.2  |  BAKED 3D→2D"' not in h:
    raise SystemExit("D2D.3 HUD anchor missing")
h=h.replace('marker.text = "D2D.2  |  BAKED 3D→2D"',
            'marker.text = "D2D.3  |  TRUE 2D + GEAR"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
e=preset.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=67',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.3"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.3 version anchors missing")
preset.write_text(e,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    s=save.read_text(encoding="utf-8")
    s,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.3"',s,count=1)
    save.write_text(s,encoding="utf-8")

print("Applied D2D.3: no runtime production 3D preload/instance for player or test bandit; 32 gear-responsive player sprite sets; flat 2D shader.")
