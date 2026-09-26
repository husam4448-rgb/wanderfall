#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/baked_actor_visual.gd"
s=p.read_text()

# Force authored character pixels opaque while removing low-alpha background/noise.
needle='''    _sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    add_child(_sprite)
'''
replacement='''    _sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    var opaque_shader := Shader.new()
    opaque_shader.code = """shader_type canvas_item;
void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    float a = tex.a < 0.08 ? 0.0 : 1.0;
    COLOR = vec4(tex.rgb, a);
}"""
    var opaque_material := ShaderMaterial.new()
    opaque_material.shader = opaque_shader
    _sprite.material = opaque_material
    _sprite.modulate = Color(1.0, 1.0, 1.0, 1.0)
    _sprite.self_modulate = Color(1.0, 1.0, 1.0, 1.0)
    add_child(_sprite)
'''
if needle not in s:
    raise SystemExit("D2D.4.6 sprite setup anchor missing")
s=s.replace(needle,replacement,1)

start=s.find("func _direction_index() -> int:")
end=s.find("\nfunc _atlas_for_current_state()",start)
if start<0 or end<0:
    raise SystemExit("D2D.4.6 direction function missing")
new_dir='''func _direction_index() -> int:
    var d := facing.normalized()
    # Actual atlas order is S, SW, W, NW, N, NE, E, SE.
    # Godot screen-space UP is negative Y.
    if d.y > 0.72:
        if d.x > 0.34: return 7
        if d.x < -0.34: return 1
        return 0
    if d.y < -0.72:
        if d.x > 0.34: return 5
        if d.x < -0.34: return 3
        return 4
    return 6 if d.x >= 0.0 else 2
'''
s=s[:start]+new_dir+s[end:]
p.write_text(s)

h=root/"scripts/mobile_hud.gd"; t=h.read_text()
t=t.replace('marker.text = "D2D.4.5  |  ARMED SPRITE TEST"','marker.text = "D2D.4.6  |  OPAQUE + DIR FIX"')
h.write_text(t)

ep=root/"export_presets.cfg"; e=ep.read_text()
e=re.sub(r'(?m)^version/code=\d+$','version/code=74',e,count=1)
e=re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.4.6"',e,count=1)
ep.write_text(e)

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text()
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.4.6"',q,count=1)
    sm.write_text(q)

print("Applied D2D.4.6 opaque sprite + corrected direction lookup.")
