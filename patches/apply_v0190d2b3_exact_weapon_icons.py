#!/usr/bin/env python3
from pathlib import Path
import json
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

def read(rel):
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"Missing D2B3 target: {p}")
    return p, p.read_text(encoding="utf-8")

def replace_once(rel, old, new):
    p, s = read(rel)
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"D2B3 anchor missing in {rel}: {old[:160]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

items = json.loads((root / "data/items.json").read_text(encoding="utf-8"))
colors = {str(x.get("id", "")): str(x.get("world_color", "8d8d85")) for x in items if isinstance(x, dict)}
icon_dir = root / "assets/ui/item_icons/items"
icon_dir.mkdir(parents=True, exist_ok=True)

bodies = {
    "pistol_9mm": '<rect x="14" y="22" width="31" height="9" rx="2" fill="{c}"/><rect x="20" y="18" width="23" height="5" fill="{hi}"/><path d="M22 31 L34 31 L31 51 L21 51 Z" fill="{lo}"/>',
    "revolver_357": '<rect x="13" y="23" width="35" height="8" rx="2" fill="{c}"/><circle cx="28" cy="31" r="9" fill="{hi}"/><circle cx="28" cy="31" r="4" fill="{lo}"/><path d="M20 37 L31 37 L28 53 L18 53 Z" fill="{lo}"/>',
    "smg_9mm": '<path d="M8 24 L18 20 L24 22 L24 31 L12 34 L8 31 Z" fill="{lo}"/><rect x="20" y="22" width="31" height="11" fill="{c}"/><path d="M28 33 L38 33 L42 53 L30 53 Z" fill="{lo}"/><rect x="49" y="25" width="8" height="5" fill="{hi}"/>',
    "rifle_556": '<path d="M4 25 L16 19 L27 22 L27 32 L14 37 L4 33 Z" fill="{lo}"/><rect x="23" y="22" width="25" height="11" fill="{c}"/><path d="M31 33 L41 33 L46 52 L34 52 Z" fill="{lo}"/><rect x="46" y="25" width="15" height="5" fill="{hi}"/>',
    "shotgun_12g": '<path d="M3 27 L17 20 L30 23 L28 34 L13 39 L3 35 Z" fill="#7b5a3d"/><rect x="25" y="24" width="36" height="7" fill="{c}"/><rect x="36" y="32" width="17" height="6" fill="#76563b"/><rect x="29" y="34" width="32" height="3" fill="{lo}"/>',
    "hunting_rifle": '<path d="M2 27 L18 19 L32 23 L29 34 L12 41 L2 36 Z" fill="#76563b"/><rect x="27" y="24" width="17" height="8" fill="{c}"/><rect x="42" y="26" width="20" height="4" fill="{hi}"/><path d="M32 33 L38 33 L42 45 L35 45 Z" fill="#66482f"/>',
    "knife": '<rect x="8" y="27" width="17" height="9" rx="2" fill="#4b3d31"/><path d="M25 28 L58 32 L25 36 Z" fill="{hi}"/>',
    "hatchet": '<rect x="7" y="29" width="42" height="7" rx="3" fill="#76563b"/><path d="M42 18 L58 21 L58 43 L42 46 L38 32 Z" fill="{hi}"/>',
    "crowbar": '<path d="M8 43 L49 24 Q58 20 58 12" fill="none" stroke="{c}" stroke-width="7" stroke-linecap="round"/><path d="M8 43 L13 51" stroke="{hi}" stroke-width="5" stroke-linecap="round"/>',
    "machete": '<rect x="5" y="28" width="16" height="9" rx="2" fill="#4d3d30"/><path d="M21 26 L56 27 L61 32 L49 40 L21 38 Z" fill="{hi}"/>',
    "baseball_bat": '<path d="M9 39 L50 21" stroke="{c}" stroke-width="10" stroke-linecap="round"/><path d="M7 40 L19 35" stroke="{lo}" stroke-width="5" stroke-linecap="round"/>',
    "sledgehammer": '<path d="M8 42 L44 27" stroke="#785a3b" stroke-width="7" stroke-linecap="round"/><rect x="39" y="17" width="18" height="22" rx="2" fill="{c}"/>',
    "spear": '<path d="M4 39 L51 27" stroke="#806343" stroke-width="5" stroke-linecap="round"/><path d="M48 20 L62 25 L52 35 Z" fill="{hi}"/>',
    "laser_module": '<rect x="10" y="25" width="42" height="15" rx="4" fill="{c}"/><circle cx="53" cy="32" r="6" fill="#d14949"/><rect x="18" y="20" width="13" height="6" fill="{lo}"/>',
    "weapon_light": '<rect x="11" y="26" width="34" height="14" rx="5" fill="{lo}"/><path d="M45 23 L58 27 L58 39 L45 43 Z" fill="{c}"/><circle cx="55" cy="33" r="5" fill="#e0ce77"/>',
    "red_dot": '<rect x="9" y="34" width="46" height="7" rx="2" fill="{lo}"/><rect x="20" y="22" width="25" height="14" rx="4" fill="{c}"/><circle cx="33" cy="28" r="5" fill="#b54c45"/>',
    "scope_4x": '<rect x="10" y="28" width="44" height="10" rx="4" fill="{c}"/><circle cx="12" cy="33" r="10" fill="{hi}"/><circle cx="53" cy="33" r="11" fill="{hi}"/><rect x="25" y="38" width="6" height="8" fill="{lo}"/><rect x="38" y="38" width="6" height="8" fill="{lo}"/>',
    "suppressor_9mm": '<rect x="8" y="27" width="48" height="13" rx="5" fill="{c}"/><rect x="12" y="25" width="5" height="17" fill="{hi}"/><circle cx="56" cy="33" r="6" fill="{lo}"/>',
    "rifle_suppressor": '<rect x="5" y="25" width="54" height="16" rx="5" fill="{c}"/><rect x="12" y="23" width="6" height="20" fill="{hi}"/><rect x="24" y="25" width="4" height="16" fill="{lo}"/><circle cx="59" cy="33" r="7" fill="{lo}"/>',
}

svg_template = '''<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 64 64">
<path d="M5 54 Q32 62 59 54" fill="none" stroke="#11181a" stroke-opacity="0.35" stroke-width="4"/>
{body}
</svg>\n'''

def shade(hex_color, factor):
    h = hex_color.lstrip('#')
    if len(h) != 6:
        h = '8d8d85'
    rgb = [int(h[i:i+2], 16) for i in (0,2,4)]
    if factor >= 1.0:
        out = [round(v + (255-v)*(factor-1.0)) for v in rgb]
    else:
        out = [round(v*factor) for v in rgb]
    return '#%02x%02x%02x' % tuple(max(0,min(255,v)) for v in out)

for item_id, body in bodies.items():
    c = '#' + colors.get(item_id, '8d8d85').lstrip('#')
    rendered = body.format(c=c, hi=shade(c, 1.22), lo=shade(c, 0.68))
    (icon_dir / f"{item_id}.svg").write_text(svg_template.format(body=rendered), encoding="utf-8")

replace_once(
    "scripts/items/item_database.gd",
    '''func get_icon_path(item_id: String) -> String:
    var category := get_category(item_id)
    var candidate := "res:/" + "/assets/ui/item_icons/" + category + ".svg"
    var fallback := "res:/" + "/assets/ui/item_icons/misc.svg"
    return candidate if ResourceLoader.exists(candidate) else fallback
''',
    '''func get_icon_path(item_id: String) -> String:
    var exact := "res:/" + "/assets/ui/item_icons/items/" + item_id + ".svg"
    if ResourceLoader.exists(exact):
        return exact
    var category := get_category(item_id)
    var candidate := "res:/" + "/assets/ui/item_icons/" + category + ".svg"
    var fallback := "res:/" + "/assets/ui/item_icons/misc.svg"
    return candidate if ResourceLoader.exists(candidate) else fallback
''',
)

replace_once(
    "scripts/content/world_item_sprite.gd",
    'class_name WorldItemSprite\nextends Node2D\n',
    'class_name WorldItemSprite\nextends Node2D\n\nconst WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")\n',
)
replace_once(
    "scripts/content/world_item_sprite.gd",
    'var quantity := 1\n',
    'var quantity := 1\nvar _weapon_visual: Node2D = null\n',
)
replace_once(
    "scripts/content/world_item_sprite.gd",
    '''func setup(id_value: String, quantity_value: int = 1) -> void:
    item_id = id_value
    quantity = maxi(1, quantity_value)
    queue_redraw()
''',
    '''func setup(id_value: String, quantity_value: int = 1) -> void:
    item_id = id_value
    quantity = maxi(1, quantity_value)
    if is_inside_tree():
        _sync_exact_weapon_visual()
    queue_redraw()

func _ready() -> void:
    _sync_exact_weapon_visual()

func _sync_exact_weapon_visual() -> void:
    var category := ItemDatabase.get_category(item_id)
    var should_show := category in ["firearm", "melee"]
    if should_show and _weapon_visual == null:
        _weapon_visual = WeaponVisualScript.new()
        _weapon_visual.scale = Vector2(0.68, 0.68)
        _weapon_visual.rotation = -0.45
        add_child(_weapon_visual)
    if _weapon_visual != null:
        _weapon_visual.visible = should_show
        if should_show:
            _weapon_visual.setup_static(item_id, {})
''',
)
replace_once(
    "scripts/content/world_item_sprite.gd",
    '''    _draw_ellipse(Vector2(0, 8), Vector2(12, 5), Color(0.03,0.04,0.04,0.28))
    match category:
        "firearm":
            draw_rect(Rect2(-15,-4,25,6), c, true); draw_rect(Rect2(5,1,6,9), c.darkened(0.25), true)
        "melee":
            draw_line(Vector2(-11,8), Vector2(11,-8), c, 4.0); draw_circle(Vector2(11,-8),3.0,c.lightened(0.2))
''',
    '''    _draw_ellipse(Vector2(0, 8), Vector2(12, 5), Color(0.03,0.04,0.04,0.28))
    if category in ["firearm", "melee"]:
        return
    if category == "attachment":
        match item_id:
            "laser_module":
                draw_rect(Rect2(-11,-5,20,9), c, true); draw_circle(Vector2(10,-1),3.0,Color("d14949"))
            "weapon_light":
                draw_rect(Rect2(-11,-5,18,9), c.darkened(0.18), true); draw_circle(Vector2(9,-1),4.0,Color("e0ce77"))
            "red_dot":
                draw_rect(Rect2(-10,1,20,4), c.darkened(0.2), true); draw_rect(Rect2(-5,-7,11,8), c, true); draw_circle(Vector2(1,-4),2.0,Color("b54c45"))
            "scope_4x":
                draw_rect(Rect2(-13,-4,26,7), c, true); draw_circle(Vector2(-13,-1),5,c.lightened(0.14)); draw_circle(Vector2(13,-1),6,c.lightened(0.14))
            "suppressor_9mm":
                draw_rect(Rect2(-13,-4,26,8), c, true)
            "rifle_suppressor":
                draw_rect(Rect2(-16,-5,32,10), c, true)
        return
    match category:
''',
)

replace_once(
    "scripts/save/save_manager.gd",
    'const GAME_VERSION := "0.19.0D2A"\n',
    'const GAME_VERSION := "0.19.0D2B"\n',
)

print(f"Applied v0.19.0D2B3 exact weapon/attachment inventory icons and world-drop silhouettes ({len(bodies)} item icons).")
