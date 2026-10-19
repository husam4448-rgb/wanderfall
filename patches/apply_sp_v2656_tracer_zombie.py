#!/usr/bin/env python3
"""Install v265.6 firearm tracers / zombie source art on verified v265.5.
Guard original gameplay, ballistics, controls and save compatibility.
"""
import sys,re,shutil
from pathlib import Path
root=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
protected=["scripts/mobile_hud.gd","scripts/virtual_joystick.gd",
           "scripts/save/save_manager.gd","scripts/world/world_manager.gd",
           "scripts/items/item_database.gd","scripts/combat/equipment.gd"]
before={p:(root/p).read_bytes() for p in protected}
def once(s,a,b,label):
    n=s.count(a)
    if n!=1:
        raise RuntimeError("SP_V2656_PATCH_ABORT %s: %d anchors"%(label,n))
    return s.replace(a,b,1)
def replace_draw(s,content):
    mark="func _draw() -> void:\n"
    if s.count(mark)!=1:
        raise RuntimeError("zombie draw count")
    return s[:s.index(mark)]+content
def edit(path,fn):
    target=root/path
    old=target.read_text()
    new=fn(old)
    if old==new:raise RuntimeError("SP2656 NOOP "+path)
    target.write_text(new)
newfx=root/"scripts/combat/sp_v2656_tracer_fx.gd"
shutil.copy2(repo/"combat/sp_v2656_tracer_fx.gd",newfx)
frames=root/"assets/biomes/v2656"
assert len(list(frames.glob("zombie_*.png")))==8,"zombie art missing"
# Visual-only overlays; player damage selection, consumes and noise stay intact.
def player(s):
    s=once(s,'const WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")',
'''const WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")
const SP2656_TRACER = preload("res://scripts/combat/sp_v2656_tracer_fx.gd")''',"fx import")
    s=once(s,'var _muzzle_flash_timer := 0.0',
'''var _muzzle_flash_timer := 0.0
var _sp2656_fx: Node2D = null''',"fx field")
    s=once(s,'    _sp_setup_approved_survivor()',
'''    _sp_setup_approved_survivor()
    _sp2656_fx = SP2656_TRACER.new()
    _sp2656_fx.name = "SP_2656_TransientBulletTracers"
    add_child(_sp2656_fx)''',"fx creation")
    shot='''    # One cosmetic streak per real accepted shot. NO second ballistic query,
    # damage multiplier, aim override, inventory modification or hit scan.
    if _sp2656_fx != null:
        var direction: Vector2 = _facing.normalized()
        var muzzle_world: Vector2 = global_position+direction*29.0
        if body_type == "male" and _sp_firearm_visual != null and _sp_firearm_visual.visible:
            muzzle_world = _sp_firearm_visual.to_global(
                Vector2(_sp_firearm_visual._muzzle_x(),0.0))
        elif _weapon_visual != null and _weapon_visual.has_method("get_muzzle_distance"):
            muzzle_world = global_position+direction*float(
                _weapon_visual.get_muzzle_distance())*absf(_weapon_visual.scale.x)
        var visual_end: Vector2 = target.global_position if target != null else (
            muzzle_world+direction*weapon_range)
        var ammo_name: String = String(data.get("ammo_id",""))
        var suppressed: bool = String(
            equipment.attachments.get("muzzle","")).contains("suppressor")
        _sp2656_fx.fire_visual(muzzle_world,visual_end,
            equipment.equipped_weapon_id,ammo_name,suppressed)
'''
    s=once(s,'    NoiseManager.emit_noise(global_position, float(data.get("noise", 500.0)), "player")',
            shot+'    NoiseManager.emit_noise(global_position, float(data.get("noise", 500.0)), "player")',"attach to real shoot")
    s=once(s,'''    if not GameSettings.reduced_flashes and PerformanceManager.get_effects_density() >= 0.45 and _muzzle_flash_timer > 0.0:
        draw_circle(weapon_end + _facing * 4.0, 5.5, Color(1.0, 0.75, 0.24, 0.92))
''','''    # v265.6 removed the obsolete player-root muzzle circle. The approved
    # FirearmVisual draws its small weapon-tip-shaped flash; tracers use
    # a reusable CanvasItem and never reintroduce large circles.
''',"remove obsolete circle")
    s=once(s,'        _sp_firearm_visual.fired()',
           '''        if not GameSettings.reduced_flashes:
            _sp_firearm_visual.fired()''',"respect reduced flashes")
    return s
edit("scripts/player.gd",player)

# The hostiles keep their native accuracy/cover, and use the SAME visual
# emitter only when a real shot is attempted.
def bandit(s):
    s=once(s,'extends HostileActor\n',
'''extends HostileActor
const SP2656_TRACER = preload("res://scripts/combat/sp_v2656_tracer_fx.gd")
var _sp2656_fx: Node2D = null
''',"bandit fx import")
    s=once(s,'    _fire_timer = fire_cooldown\n    var weapon_data := ItemDatabase.get_item(equipped_weapon_id)',
'''    _fire_timer = fire_cooldown
    var weapon_data := ItemDatabase.get_item(equipped_weapon_id)
    if target_player != null and is_instance_valid(target_player):
        if _sp2656_fx == null:
            _sp2656_fx = SP2656_TRACER.new()
            _sp2656_fx.name = "HostileShotStreak"
            add_child(_sp2656_fx)
        var aim: Vector2 = (target_player.global_position-global_position).normalized()
        var muzzle: Vector2 = global_position+aim*28.0
        var ammo: String = String(weapon_data.get("ammo_id",""))
        var suppressed: bool = String(weapon_attachments.get("muzzle","")).contains("suppressor")
        _sp2656_fx.fire_visual(muzzle,target_player.global_position,
            equipped_weapon_id,ammo,suppressed)''',"hostile fx")
    return s
edit("scripts/combat/bandit.gd",bandit)

# Zombie AI, collider, attack logic, saves and health stay byte-for-byte
# unchanged above the draw site; new display uses 8 source-image frames.
def zombie(s):
    s=once(s,'extends HostileActor\n',
'''extends HostileActor
const SP2656_RIGHT = [
    preload("res://assets/biomes/v2656/zombie_right_0.png"),
    preload("res://assets/biomes/v2656/zombie_right_1.png"),
    preload("res://assets/biomes/v2656/zombie_right_2.png"),
    preload("res://assets/biomes/v2656/zombie_right_3.png")
]
const SP2656_LEFT = [
    preload("res://assets/biomes/v2656/zombie_left_0.png"),
    preload("res://assets/biomes/v2656/zombie_left_1.png"),
    preload("res://assets/biomes/v2656/zombie_left_2.png"),
    preload("res://assets/biomes/v2656/zombie_left_3.png")
]
var _sp2656_clock: float = 0.0
var _sp2656_face_right: bool = true
''',"zombie source sprites")
    s=once(s,'    move_and_slide()\n    queue_redraw()',
'''    move_and_slide()
    if velocity.length_squared()>16.0:
        _sp2656_clock += delta*(4.5 if chasing else 2.5)
        if absf(velocity.x)>5.0:
            _sp2656_face_right = velocity.x>=0.0
    else:
        _sp2656_clock = 0.0
    queue_redraw()''',"zombie gait")
    return replace_draw(s,'''func _draw() -> void:
    var frames: Array = SP2656_RIGHT if _sp2656_face_right else SP2656_LEFT
    var index: int = posmod(int(_sp2656_clock),4)
    var img: Texture2D = frames[index]
    # Compact top-down figure at world character scale. No torso squares,
    # head circles, decorative polygon limbs or duplicate body primitive.
    draw_texture_rect(img,Rect2(-20,-41,40,60),false)
    _draw_health_bar()
''')
edit("scripts/combat/zombie.gd",zombie)
# Align the occlusion overlay with the same exact zombie sprite silhouette.
def overlay(s):
    s=once(s,'const ZOMBIE_MASK: Texture2D = preload("res://assets/sp_melee/v261_zombie_mask.png")',
             'const ZOMBIE_MASK: Texture2D = preload("res://assets/biomes/v2656/zombie_right_0.png")',
             'zombie occlusion sprite')
    s=once(s,'    sprite.texture = ZOMBIE_MASK\n    sprite.texture_filter',
           '    sprite.texture = ZOMBIE_MASK\n    sprite.position = Vector2(0.0,-11.0)\n    sprite.texture_filter',
           'zombie true alpha world anchor')
    return s
edit("scripts/world/occlusion_silhouette_overlay.gd",overlay)
for name,data in before.items():
    if (root/name).read_bytes()!=data:
        raise RuntimeError("protected source changed: "+name)
assert '_muzzle_flash_timer > 0.0' not in (root/"scripts/player.gd").read_text()
assert 'draw_circle(Vector2(0, -12)' not in (root/"scripts/combat/zombie.gd").read_text()
print("SP_V2656_PRESENTATION_PASS compact zombies, matching mask, no legacy circular muzzle flash, weapon/ammo tracers, intact gameplay")
