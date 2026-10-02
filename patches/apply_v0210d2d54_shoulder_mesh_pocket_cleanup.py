#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.54 requires D2D.53 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.53 GEAR:"', 'title.text = "D2D.54 GEAR:"', 1)

# Replace D2D.53 visible shoulder discs with an UNDERLAY fill.
# Because the torso texture is drawn after the fill, only its transparent shoulder
# socket reveals the material. No circular patch can protrude around the shoulder.
old_base = '''    if not gear_torso:
        # Same authored torso silhouette/dimensions as equipped state.
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
        # Cover the authored shoulder socket with matching cloth.
        var shoulder_cap := base + Vector2(-8.0 * dir_sign,-8.1)
        draw_circle(shoulder_cap,4.15,Color("4e594b"))
        draw_circle(shoulder_cap + Vector2(0.35 * dir_sign,-0.15),2.7,Color("566253"))
'''
new_base = '''    if not gear_torso:
        # D2D.54: sleeve material sits BEHIND the authored torso.
        # Only the transparent shoulder socket reveals it.
        var shoulder_fill := base + Vector2(-8.0 * dir_sign,-8.1)
        draw_circle(shoulder_fill,4.05,Color("4e594b"))
        draw_line(shoulder_fill + Vector2(-2.2 * dir_sign,-1.0),
                  shoulder_fill + Vector2(2.0 * dir_sign,1.1),
                  Color("596455"),1.0,true)
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if old_base not in s:
    raise SystemExit("D2D.54 base shoulder anchor missing")
s = s.replace(old_base,new_base,1)

old_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
    # D2D.53: armor/fabric shoulder patch closes the black transparent socket.
    var shoulder_cap := base + Vector2(-8.0 * dir_sign,-8.1)
    draw_circle(shoulder_cap,4.2,Color("655f50"))
    draw_circle(shoulder_cap + Vector2(0.35 * dir_sign,-0.2),2.75,Color("77705e"))
'''
new_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    # D2D.54: matching armor/sleeve mesh under the transparent shoulder socket.
    # Vest is drawn over it so the fill cannot look like an external round patch.
    var shoulder_fill := base + Vector2(-8.0 * dir_sign,-8.1)
    draw_circle(shoulder_fill,4.05,Color("514d42"))
    draw_line(shoulder_fill + Vector2(-2.1 * dir_sign,-1.1),
              shoulder_fill + Vector2(2.0 * dir_sign,1.0),
              Color("6c6657"),1.0,true)
    draw_line(shoulder_fill + Vector2(-1.7 * dir_sign,1.2),
              shoulder_fill + Vector2(1.7 * dir_sign,-1.2),
              Color("403d35"),0.8,true)
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if old_vest not in s:
    raise SystemExit("D2D.54 geared shoulder anchor missing")
s = s.replace(old_vest,new_vest,1)

# Remove D2D.53 stride-only pocket cover; it failed at idle because stride == 0.
old_pocket = '''    # D2D.53: remove the visually misplaced inner-thigh pocket from the forward leg.
    # Patch follows leg rotation so it stays attached during gait.
    if stride > 0.0:
        var patch_center := mid + _pose_point(Vector2(-2.2 * dir_sign,-4.0), leg_angle, 1.0)
        var patch_color := Color("716856") if gear_legs else Color("394247")
        draw_set_transform(patch_center,leg_angle,Vector2.ONE)
        draw_rect(Rect2(Vector2(-2.2,-2.8),Vector2(4.4,5.6)),patch_color,true)
        draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

'''
if old_pocket not in s:
    raise SystemExit("D2D.54 old pocket patch missing")
s = s.replace(old_pocket,'',1)

# Insert an always-active cleanup for the visually near/forward leg.
# side*dir_sign > 0 selects the near leg consistently when the actor mirrors L/R.
boot_anchor = '''    # D2D.50: slightly forward and lower relative to ankle.
    var boot_center := ankle + Vector2(0.4 * dir_sign, 6.8)
'''
pocket_fix = '''    # D2D.54: remove the inner-thigh cargo pocket from the near/forward leg.
    # This runs at idle AND during gait.
    if side * dir_sign > 0.0:
        var clean_center := mid + _pose_point(Vector2(-2.7 * dir_sign,-4.6),leg_angle,1.0)
        var clean_color := Color("5c574a") if gear_legs else Color("394247")
        draw_set_transform(clean_center,leg_angle,Vector2.ONE)
        draw_rect(Rect2(Vector2(-2.8,-3.3),Vector2(5.6,6.6)),clean_color,true)
        # subtle longitudinal cloth/camo lines so the cleanup reads as fabric, not a patch
        var detail := Color("4b493f") if gear_legs else Color("333b40")
        draw_line(Vector2(-1.7,-2.7),Vector2(-1.7,2.7),detail,0.65,true)
        draw_line(Vector2(0.8,-2.7),Vector2(0.8,2.7),detail,0.55,true)
        draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

    # D2D.50: slightly forward and lower relative to ankle.
    var boot_center := ankle + Vector2(0.4 * dir_sign, 6.8)
'''
if boot_anchor not in s:
    raise SystemExit("D2D.54 boot anchor missing")
s=s.replace(boot_anchor,pocket_fix,1)

script.write_text(s,encoding="utf-8")

ep = root / "export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=127',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.54"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.54 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.54"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.54: shoulder socket underlay mesh and idle-safe forward-thigh pocket removal.")
