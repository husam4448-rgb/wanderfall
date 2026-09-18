#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'game')
p=root/'scripts/art/layered_actor_visual.gd'
s=p.read_text(encoding='utf-8')

def replace_func(src, signature, new):
    start=src.find('func '+signature)
    if start<0: raise SystemExit('missing '+signature)
    nxt=src.find('\nfunc ', start+5)
    if nxt<0: nxt=len(src)
    return src[:start]+new.rstrip()+'\n'+src[nxt:]

if 'var pose_key := "front"' not in s:
    s=s.replace('var facing := Vector2.DOWN\n','var facing := Vector2.DOWN\nvar pose_key := "front"\n',1)

s=replace_func(s,'set_facing(value: Vector2) -> void:',r'''func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    facing = value.normalized()
    pose_key = _resolve_pose_key(facing)
    rotation = 0.0
    queue_redraw()''')

helpers=r'''func _resolve_pose_key(direction: Vector2) -> String:
    if direction.length_squared() <= 0.0001:
        return "front"
    var d := direction.normalized()
    if d.y < -0.72:
        if d.x < -0.34:
            return "up_left"
        if d.x > 0.34:
            return "up_right"
        return "up"
    if d.y > 0.72:
        if d.x < -0.34:
            return "down_left"
        if d.x > 0.34:
            return "down_right"
        return "down"
    if d.x < -0.45:
        return "left"
    if d.x > 0.45:
        return "right"
    return "front"

func _pose_profile(key: String) -> Dictionary:
    match key:
        "up":
            return {"width":0.96,"top_x":0.0,"bottom_x":0.0,"head_x":0.0,"head_y":-0.8,"back":1.0,"left_shoulder_y":0.4,"right_shoulder_y":0.4,"leg_depth":0.0,"side":0.0}
        "up_left":
            return {"width":0.82,"top_x":-1.2,"bottom_x":0.3,"head_x":-1.5,"head_y":-0.5,"back":0.78,"left_shoulder_y":1.0,"right_shoulder_y":-1.0,"leg_depth":-1.3,"side":-0.75}
        "left":
            return {"width":0.66,"top_x":-1.8,"bottom_x":0.7,"head_x":-2.0,"head_y":0.0,"back":0.30,"left_shoulder_y":1.5,"right_shoulder_y":-1.5,"leg_depth":-1.8,"side":-1.0}
        "down_left":
            return {"width":0.84,"top_x":-1.1,"bottom_x":0.2,"head_x":-1.4,"head_y":0.4,"back":0.08,"left_shoulder_y":1.0,"right_shoulder_y":-1.0,"leg_depth":-1.2,"side":-0.72}
        "down":
            return {"width":1.0,"top_x":0.0,"bottom_x":0.0,"head_x":0.0,"head_y":0.6,"back":0.0,"left_shoulder_y":0.0,"right_shoulder_y":0.0,"leg_depth":0.0,"side":0.0}
        "down_right":
            return {"width":0.84,"top_x":1.1,"bottom_x":-0.2,"head_x":1.4,"head_y":0.4,"back":0.08,"left_shoulder_y":-1.0,"right_shoulder_y":1.0,"leg_depth":1.2,"side":0.72}
        "right":
            return {"width":0.66,"top_x":1.8,"bottom_x":-0.7,"head_x":2.0,"head_y":0.0,"back":0.30,"left_shoulder_y":-1.5,"right_shoulder_y":1.5,"leg_depth":1.8,"side":1.0}
        "up_right":
            return {"width":0.82,"top_x":1.2,"bottom_x":-0.3,"head_x":1.5,"head_y":-0.5,"back":0.78,"left_shoulder_y":-1.0,"right_shoulder_y":1.0,"leg_depth":1.3,"side":0.75}
        _:
            return {"width":1.0,"top_x":0.0,"bottom_x":0.0,"head_x":0.0,"head_y":0.0,"back":0.0,"left_shoulder_y":0.0,"right_shoulder_y":0.0,"leg_depth":0.0,"side":0.0}

'''
if 'func _resolve_pose_key' not in s:
    anchor='func _q(v: Vector2) -> Vector2:\n'
    if anchor not in s: raise SystemExit('q anchor missing')
    s=s.replace(anchor,helpers+anchor,1)
p.write_text(s,encoding='utf-8')
print('Applied D2B.3A1 nine-direction pose state.')
