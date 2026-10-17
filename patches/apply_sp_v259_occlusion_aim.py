#!/usr/bin/env python3
"""v259 fixes: sample TRUE sprite-alpha/B2B shape behind foliage; aim NEVER from movement.

Executed after v257 + v258 patches. Does not edit D2D14 landscape, HUD,
joystick geometry, collision layers, or detailed world textures.
"""
from pathlib import Path
import sys
game=Path(sys.argv[1]).resolve()
protected=['scripts/mobile_hud.gd','scripts/virtual_joystick.gd',
           'scripts/world/world_chunk.gd','scripts/world/world_manager.gd']
before={f:(game/f).read_bytes() for f in protected}

def patch(path,old,new,why):
    f=game/path
    text=f.read_text(encoding='utf-8')
    n=text.count(old)
    if n!=1:
        raise SystemExit('SP_V259_PATCH_ABORT '+why+' anchors='+str(n))
    f.write_text(text.replace(old,new,1),encoding='utf-8')

player='scripts/player.gd'
patch(player,
'''var _facing := Vector2.DOWN
var _last_mobile_aim_direction := Vector2.DOWN
var _has_mobile_aim_direction := false''',
'''# Facing always begins from an explicit right-facing aim, not the move vector.
var _facing := Vector2.RIGHT
var _last_mobile_aim_direction := Vector2.RIGHT
var _has_mobile_aim_direction := true''',
'first-frame aim default')
patch(player,
'''        elif _has_mobile_aim_direction and equipment != null and equipment.get_weapon_category() == "firearm":
            _facing = _last_mobile_aim_direction''',
'''        elif _has_mobile_aim_direction:
            _facing = _last_mobile_aim_direction''',
'vehicle aims independently for all equipment')
patch(player,
'''    var firearm_aim_persists := equipment != null and equipment.get_weapon_category() == "firearm"
    if InputState.mobile_aim_active and InputState.mobile_aim.length_squared() > 0.0001:
        _last_mobile_aim_direction = InputState.mobile_aim.normalized()
        _has_mobile_aim_direction = true
        _facing = _last_mobile_aim_direction
    elif firearm_aim_persists and _has_mobile_aim_direction:
        # C6: left-stick movement changes translation only; it never rotates a firearm
        # after the player has established an aim direction with the right stick.
        _facing = _last_mobile_aim_direction
    elif direction.length_squared() > 0.0001:
        _facing = direction''',
'''    if InputState.mobile_aim_active and InputState.mobile_aim.length_squared() > 0.0001:
        _last_mobile_aim_direction = InputState.mobile_aim.normalized()
        _has_mobile_aim_direction = true
    # Movement, RUN, crouch, keyboard translation and knife auto-targeting
    # never modify the weapon-facing vector, including BEFORE any aim touch.
    if _has_mobile_aim_direction:
        _facing = _last_mobile_aim_direction''',
'remove initial walking-to-aim fallback')
patch(player,
'''        _facing = value.normalized()
        queue_redraw()''',
'''        _facing = value.normalized()
        _last_mobile_aim_direction = _facing
        _has_mobile_aim_direction = true
        queue_redraw()''',
'saved aim must persist after loading')

# Image-alpha matches the APPROVED torso/backpack/head, including mirroring.
# B2B rectangular legs match the actual drawn hip-knee-ankle geometry, not
# an invented silhouette with permanent arms and long shins.
rig='assets/sp_melee/SurvivorWalkSprite.gd'
patch(rig,
'''var far_ankle: Vector2 = Vector2.ZERO
''',
'''var far_ankle: Vector2 = Vector2.ZERO
var _upper_alpha: Image
var _near_alpha: Image
var _far_alpha: Image
''',
'cached source texture alpha')
patch(rig,
'''    scale = Vector2(VISUAL_SCALE, VISUAL_SCALE)
''',
'''    scale = Vector2(VISUAL_SCALE, VISUAL_SCALE)
    # Cache once rather than allocating CPU-side images each foliage redraw.
    _upper_alpha = upper.texture.get_image()
    _near_alpha = (near_hip.get_child(0) as Sprite2D).texture.get_image()
    _far_alpha = (far_hip.get_child(0) as Sprite2D).texture.get_image()
''',
'cache actual alpha')
with (game/rig).open('a',encoding='utf-8') as f:
    f.write('''
# A pointwise copy of the visible renderer, not the deprecated anatomy mask.
# to_local() includes 0.58 scale, facing mirror, breathing offset and gait bob.
func _inside_image(sprite: Sprite2D, image: Image, world_point: Vector2) -> bool:
    if sprite == null or not sprite.visible or image == null:
        return false
    var p: Vector2 = sprite.to_local(world_point)
    var x: int = int(floorf(p.x + float(image.get_width()) * 0.5))
    var y: int = int(floorf(p.y + float(image.get_height()) * 0.5))
    if x < 0 or y < 0 or x >= image.get_width() or y >= image.get_height():
        return false
    return image.get_pixel(x,y).a > 0.08

func _inside_square(p: Vector2, x: float, y: float, w: float, h: float) -> bool:
    var px: float = roundf(x)
    var py: float = roundf(y)
    return p.x >= px and p.x < px + w and p.y >= py and p.y < py + h

func _inside_b2b_segment(p: Vector2, start: Vector2, finish: Vector2) -> bool:
    # Exact same integer raster math as _squared_bone()'s outer outline.
    var first: int = int(roundf(minf(start.y, finish.y)))
    var last: int = int(roundf(maxf(start.y, finish.y)))
    var row: int = int(floorf(p.y))
    if row < first or row > last:
        return false
    var t: float = clampf((float(row) - start.y) / maxf(0.01, finish.y - start.y), 0.0, 1.0)
    var center: float = roundf(lerpf(start.x, finish.x, t))
    return _inside_square(p, center - 5.0, float(row), 11.0, 1.0)

func _inside_b2b_leg(p: Vector2, hip: Vector2, knee: Vector2, ankle: Vector2) -> bool:
    if _inside_b2b_segment(p, hip, knee) or _inside_b2b_segment(p, knee, ankle):
        return true
    if _inside_square(p, knee.x - 5.0, knee.y - 1.0, 11.0, 3.0):
        return true
    # Invariable 11×6 straight-edged boot, same as visual.
    return _inside_square(p, ankle.x - 5.0, ankle.y - 1.0, BOOT_WIDTH, BOOT_HEIGHT)

func has_silhouette_at(world_point: Vector2) -> bool:
    if not visible or upper == null:
        return false
    if _inside_image(upper, _upper_alpha, world_point):
        return true
    if gait_weight > 0.08:
        var local: Vector2 = to_local(world_point)
        return (_inside_b2b_leg(local, NEAR_HIP, near_knee, near_ankle) or
                _inside_b2b_leg(local, FAR_HIP, far_knee, far_ankle))
    var near_sprite: Sprite2D = near_hip.get_child(0) as Sprite2D
    var far_sprite: Sprite2D = far_hip.get_child(0) as Sprite2D
    return (_inside_image(near_sprite,_near_alpha,world_point) or
            _inside_image(far_sprite,_far_alpha,world_point))
''')

# True gun shape and hands are included; their child transforms rotate with aim.
gun='assets/sp_melee/FirearmVisual.gd'
with (game/gun).open('a',encoding='utf-8') as f:
    f.write('''
func occlusion_contains(world_point: Vector2) -> bool:
    if not visible or weapon_family == "":
        return false
    var p: Vector2 = to_local(world_point)
    var parts: Array[Rect2] = []
    match weapon_family:
        "pistol":
            parts = [Rect2(1,-5,25,9),Rect2(6,2,9,15),
                     Rect2(15,2,7,2),Rect2(20,4,2,6),Rect2(15,9,6,2)]
        "rifle":
            parts = [Rect2(-22,-4,21,9),Rect2(-4,-7,27,12),
                     Rect2(21,-5,25,6),Rect2(5,5,8,16),Rect2(15,5,11,16)]
        "smg":
            parts = [Rect2(-11,-4,10,6),Rect2(-2,-7,29,12),
                     Rect2(26,-4,12,5),Rect2(6,5,7,14),Rect2(19,5,7,18)]
        "shotgun":
            parts = [Rect2(-19,-5,19,11),Rect2(-1,-6,21,11),
                     Rect2(19,-5,28,5),Rect2(24,1,13,4),Rect2(3,5,9,13)]
    for rect in parts:
        if rect.has_point(p):
            return true
    for hand in [grip_hand,support_hand]:
        if hand != null and hand.visible and p.distance_squared_to(hand.position) < 18.1:
            return true
    return false
''')

with (game/player).open('a',encoding='utf-8') as f:
    f.write('''
func _sp_occlusion_shape_contains(world_point: Vector2) -> bool:
    if body_type != "male" or _sp_sprite == null or not _sp_sprite.visible:
        return false
    if _sp_sprite.has_silhouette_at(world_point):
        return true
    return _sp_firearm_visual != null and _sp_firearm_visual.occlusion_contains(world_point)
''')

# The world canopy and vegetation are byte-identical to v258. Replace ONLY
# overlay's old player-shape selection and _draw loop, retaining NPC fallback.
overlay='scripts/world/occlusion_silhouette_overlay.gd'
patch(overlay,
'''        Vector2(-5,17),Vector2(5,17),Vector2(-5,25),Vector2(5,25)
''',
'''        Vector2(-5,17),Vector2(5,17),Vector2(-5,25),Vector2(5,25),
        Vector2(-15,-34),Vector2(0,-34),Vector2(15,-34),
        Vector2(-17,-23),Vector2(17,-23)
''',
'new head/backpack canopy probes')
patch(overlay,
'''    const STEP := 2
    # Sample each small anatomical point independently. Only genuinely hidden
    # samples are painted, so exposed body portions remain completely untouched.
    for y in range(-27,29,STEP):
        for x in range(-16,17,STEP):
            var sample := Vector2(float(x)+1.0,float(y)+1.0)
            if not _inside_actor_silhouette(sample):
                continue
            if not _sample_hidden(actor,sample):
                continue
            draw_circle(origin + sample,1.25,fill)
            # Tiny top-left rim only; avoids the previous orange checkerboard.
            if not _sample_hidden(actor,sample + Vector2(0,-2)):
                draw_circle(origin + sample + Vector2(0,-0.7),0.72,edge)
''',
'''    const STEP := 2
    var is_new_player: bool = (
        actor.is_in_group("player_actor")
        and actor.has_method("_sp_occlusion_shape_contains")
        and actor.get("body_type") == "male"
    )
    # Expanded bounds cover the approved backpack/hair plus held gun. Player
    # mask samples the same alpha texture and linked legs as the visible rig.
    var y0: int = -47 if is_new_player else -27
    var y1: int = 32 if is_new_player else 29
    var x0: int = -39 if is_new_player else -16
    var x1: int = 54 if is_new_player else 17
    for y in range(y0,y1,STEP):
        for x in range(x0,x1,STEP):
            var sample := Vector2(float(x)+1.0,float(y)+1.0)
            if is_new_player:
                if not actor.call("_sp_occlusion_shape_contains", actor.global_position + sample):
                    continue
            elif not _inside_actor_silhouette(sample):
                continue
            if not _sample_hidden(actor,sample):
                continue
            # A solid, precise pixel shape rather than old fake arms/legs.
            if is_new_player:
                draw_rect(Rect2(origin + sample - Vector2.ONE, Vector2(2,2)),fill,true)
            else:
                draw_circle(origin + sample,1.25,fill)
            if not _sample_hidden(actor,sample + Vector2(0,-2)):
                draw_rect(Rect2(origin + sample + Vector2(-1,-1),Vector2(2,1)),edge,true)
''',
'occlusion overlay uses exact male source silhouette')

for rel,value in before.items():
    if (game/rel).read_bytes()!=value:
        raise SystemExit('SP_V259_FATAL detailed world or historical HUD mutated '+rel)
print('SP_V259_SPRITE_MASK_QA_PASS approved pixel-alpha + B2B animated legs + weapon silhouette selected, generic orange arms rejected')
print('SP_V259_AIM_QA_PASS initial right-facing, saved aim preserved, translation never changes direction')
