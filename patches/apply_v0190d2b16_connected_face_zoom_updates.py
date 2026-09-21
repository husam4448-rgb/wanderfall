#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/art/production_survivor_visual.gd"
if not p.is_file():
    raise SystemExit(f"Missing D2B.16 target: {p}")
s = p.read_text(encoding="utf-8")

def replace_func(src: str, name: str, body: str) -> str:
    start_token = f"func {name}("
    start = src.find(start_token)
    if start < 0:
        raise SystemExit(f"D2B.16 function not found: {name}")
    nxt = src.find("\nfunc ", start + len(start_token))
    if nxt < 0:
        nxt = len(src)
    return src[:start] + body.rstrip() + "\n\n" + src[nxt+1 if nxt < len(src) else nxt:]

# Extra facial tones for more readable anatomy at close zoom.
if "const C_SKIN_SHADOW" not in s:
    anchor = 'const C_SHADOW := Color(0.10, 0.095, 0.085, 1.0)\n'
    add = anchor + '''const C_SKIN_SHADOW := Color(0.38, 0.20, 0.15, 1.0)
const C_SKIN_HILITE := Color(0.74, 0.46, 0.31, 1.0)
const C_EYE := Color(0.035, 0.030, 0.026, 1.0)
const C_EYE_WHITE := Color(0.70, 0.65, 0.56, 1.0)
const C_LIP := Color(0.31, 0.13, 0.11, 1.0)
'''
    if anchor not in s:
        raise SystemExit("D2B.16 palette anchor missing")
    s = s.replace(anchor, add, 1)

draw_func = r'''func _draw() -> void:
    if _pose.is_empty():
        return

    var side: float = _pose["side"]
    var backness: float = _pose["backness"]
    var p_x: float = _pose["perspective_x"]

    var l_hip: Vector2 = _pose["l_hip"]
    var r_hip: Vector2 = _pose["r_hip"]
    var l_knee: Vector2 = _pose["l_knee"]
    var r_knee: Vector2 = _pose["r_knee"]
    var l_ankle: Vector2 = _pose["l_ankle"]
    var r_ankle: Vector2 = _pose["r_ankle"]
    var ls: Vector2 = _pose["ls"]
    var rs: Vector2 = _pose["rs"]
    var le: Vector2 = _pose["le"]
    var re: Vector2 = _pose["re"]
    var lw: Vector2 = _pose["lw"]
    var rw: Vector2 = _pose["rw"]
    var torso_center: Vector2 = _pose["torso_center"]
    var head_center: Vector2 = _pose["head_center"]

    # Back arm roots merge into the body before the torso is painted over them.
    if side > 0.30:
        _draw_shoulder_bridge(torso_center, ls, -1.0, p_x, false)
        _draw_upper_arm(ls, le, false)
    elif side < -0.30:
        _draw_shoulder_bridge(torso_center, rs, 1.0, p_x, false)
        _draw_upper_arm(rs, re, false)
    elif backness > 0.55:
        _draw_shoulder_bridge(torso_center, ls, -1.0, p_x, false)
        _draw_shoulder_bridge(torso_center, rs, 1.0, p_x, false)
        _draw_upper_arm(ls, le, false)
        _draw_upper_arm(rs, re, false)

    if sin(gait_phase) >= 0.0:
        _draw_leg(r_hip, r_knee, r_ankle, false)
        _draw_leg(l_hip, l_knee, l_ankle, true)
    else:
        _draw_leg(l_hip, l_knee, l_ankle, false)
        _draw_leg(r_hip, r_knee, r_ankle, true)

    _draw_backpack(torso_center, p_x, side, backness)

    # Neck is drawn behind both head and torso so it physically joins them.
    _draw_neck(head_center, torso_center, side, backness, p_x)
    _draw_torso(torso_center, p_x, side, backness)
    _draw_head(head_center, side, backness)

    # Front arm roots are explicitly bridged into the shoulder mass.
    if backness <= 0.55:
        if side > 0.30:
            _draw_shoulder_bridge(torso_center, rs, 1.0, p_x, true)
            _draw_upper_arm(rs, re, true)
        elif side < -0.30:
            _draw_shoulder_bridge(torso_center, ls, -1.0, p_x, true)
            _draw_upper_arm(ls, le, true)
        else:
            _draw_shoulder_bridge(torso_center, ls, -1.0, p_x, true)
            _draw_shoulder_bridge(torso_center, rs, 1.0, p_x, true)
            _draw_upper_arm(ls, le, true)
            _draw_upper_arm(rs, re, true)

    # Forearms/hands are still final-pass so gun grip remains readable.
    _draw_forearm_hand(le, lw, true)
    _draw_forearm_hand(re, rw, true)
'''

neck_func = r'''func _draw_neck(head_center: Vector2, torso_center: Vector2, side: float, backness: float, p_x: float) -> void:
    var top := head_center + Vector2(side*0.20, 4.2)
    var bottom := Vector2(torso_center.x + side*0.15, torso_center.y - 8.6)
    var d := bottom-top
    if d.length_squared() < 0.01:
        return
    var n := Vector2(-d.y,d.x).normalized()
    var top_w := 2.25 * p_x
    var bottom_w := 3.05 * p_x
    var neck := PackedVector2Array([
        top+n*top_w,
        bottom+n*bottom_w,
        bottom-n*bottom_w,
        top-n*top_w
    ])
    var neck_color := C_SKIN_SHADOW if backness > 0.60 else C_SKIN
    draw_polygon(neck, PackedColorArray([neck_color]))
    draw_polyline(_closed(neck), C_OUTLINE, 0.75, false)
    if backness <= 0.60:
        draw_line(top + n*0.4, bottom + n*0.8, C_SKIN_HILITE, 0.55, false)

func _draw_shoulder_bridge(torso_center: Vector2, shoulder: Vector2, side_sign: float, p_x: float, front: bool) -> void:
    # Connect the animated shoulder joint to the torso socket so the arm never floats.
    var socket := torso_center + Vector2(side_sign * 7.15 * p_x, -5.55)
    var fill := C_JACKET_LITE if front else C_JACKET
    draw_line(socket, shoulder, C_OUTLINE, 6.8*p_x, true)
    draw_line(socket, shoulder, fill, 5.45*p_x, true)
    draw_circle(socket, 2.60*p_x, fill, false)
    draw_circle(shoulder, 2.65*p_x, fill, false)
'''

head_func = r'''func _draw_head(center: Vector2, side: float, backness: float) -> void:
    # D2B.16 face follows the concept-art language: angular adult skull,
    # heavy brow, defined cheek/jaw, visible nose bridge, beard and messy hair.
    var rx := lerpf(5.05, 4.20, absf(side))
    var sgn := signf(side) if absf(side) > 0.12 else 0.0

    if backness > 0.62:
        var skull := PackedVector2Array([
            center+Vector2(-rx*0.70,-5.1),
            center+Vector2(-rx*0.96,-2.6),
            center+Vector2(-rx*0.88,1.8),
            center+Vector2(-rx*0.56,4.6),
            center+Vector2(-rx*0.18,5.5),
            center+Vector2(rx*0.18,5.5),
            center+Vector2(rx*0.56,4.6),
            center+Vector2(rx*0.88,1.8),
            center+Vector2(rx*0.96,-2.6),
            center+Vector2(rx*0.70,-5.1),
            center+Vector2(0.0,-6.0)
        ])
        draw_polygon(skull, PackedColorArray([C_HAIR]))
        draw_polyline(_closed(skull), C_OUTLINE, 0.95, false)
        # Uneven locks and nape.
        draw_line(center+Vector2(-3.2,-4.1), center+Vector2(-1.6,2.9), C_BEARD, 0.7, false)
        draw_line(center+Vector2(-0.9,-5.0), center+Vector2(-0.2,3.7), C_SHADOW, 0.65, false)
        draw_line(center+Vector2(2.8,-4.0), center+Vector2(1.1,3.1), C_BEARD, 0.7, false)
        draw_circle(center+Vector2(-rx*0.92,0.6), 0.88, C_SKIN, false)
        draw_circle(center+Vector2(rx*0.92,0.6), 0.88, C_SKIN, false)
        return

    # Front/three-quarter/side facial silhouette with cheek and jaw planes.
    var face := PackedVector2Array()
    if absf(side) > 0.35:
        face = PackedVector2Array([
            center+Vector2(-sgn*rx*0.58,-4.9),
            center+Vector2(sgn*rx*0.10,-5.8),
            center+Vector2(sgn*rx*0.63,-4.8),
            center+Vector2(sgn*rx*0.86,-2.7),
            center+Vector2(sgn*rx*0.92,-1.0),
            center+Vector2(sgn*(rx+1.25),0.35),
            center+Vector2(sgn*rx*0.88,1.45),
            center+Vector2(sgn*rx*0.75,2.8),
            center+Vector2(sgn*rx*0.48,4.55),
            center+Vector2(sgn*rx*0.15,5.55),
            center+Vector2(-sgn*rx*0.34,5.05),
            center+Vector2(-sgn*rx*0.69,3.7),
            center+Vector2(-sgn*rx*0.88,1.2),
            center+Vector2(-sgn*rx*0.86,-2.5)
        ])
    else:
        face = PackedVector2Array([
            center+Vector2(-3.45,-4.8),
            center+Vector2(-1.45,-5.75),
            center+Vector2(1.45,-5.75),
            center+Vector2(3.45,-4.8),
            center+Vector2(4.75,-2.3),
            center+Vector2(4.45,1.2),
            center+Vector2(3.45,3.3),
            center+Vector2(2.15,4.75),
            center+Vector2(0.0,5.7),
            center+Vector2(-2.15,4.75),
            center+Vector2(-3.45,3.3),
            center+Vector2(-4.45,1.2),
            center+Vector2(-4.75,-2.3)
        ])
    draw_polygon(face, PackedColorArray([C_SKIN]))
    draw_polyline(_closed(face), C_OUTLINE, 0.9, false)

    # Cheek planes prevent the head from reading as a ball.
    if absf(side) <= 0.35:
        var l_cheek := PackedVector2Array([
            center+Vector2(-4.0,0.3), center+Vector2(-2.0,0.8),
            center+Vector2(-1.3,3.0), center+Vector2(-3.1,3.4)
        ])
        var r_cheek := PackedVector2Array([
            center+Vector2(4.0,0.3), center+Vector2(2.0,0.8),
            center+Vector2(1.3,3.0), center+Vector2(3.1,3.4)
        ])
        draw_polygon(l_cheek, PackedColorArray([C_SKIN_SHADOW]))
        draw_polygon(r_cheek, PackedColorArray([C_SKIN_SHADOW]))
    else:
        var cheek_s := signf(side)
        var cheek := PackedVector2Array([
            center+Vector2(cheek_s*3.9,0.2),
            center+Vector2(cheek_s*2.0,0.7),
            center+Vector2(cheek_s*1.6,3.1),
            center+Vector2(cheek_s*3.2,3.0)
        ])
        draw_polygon(cheek, PackedColorArray([C_SKIN_SHADOW]))

    # Messy concept-art hair with uneven fringe, crown and sideburns.
    var hair := PackedVector2Array([
        center+Vector2(-4.65,-2.4),
        center+Vector2(-4.25,-4.5),
        center+Vector2(-3.2,-5.65),
        center+Vector2(-2.15,-5.25),
        center+Vector2(-1.25,-6.25),
        center+Vector2(-0.15,-5.50),
        center+Vector2(0.75,-6.30),
        center+Vector2(1.65,-5.45),
        center+Vector2(2.85,-5.85),
        center+Vector2(4.15,-4.55),
        center+Vector2(4.75,-2.65),
        center+Vector2(4.15,-1.55),
        center+Vector2(2.75,-1.95),
        center+Vector2(1.75,-2.55),
        center+Vector2(0.55,-1.95),
        center+Vector2(-0.6,-2.55),
        center+Vector2(-1.85,-1.85),
        center+Vector2(-3.0,-2.35),
        center+Vector2(-4.05,-1.55)
    ])
    draw_polygon(hair, PackedColorArray([C_HAIR]))
    draw_polyline(_closed(hair), C_OUTLINE, 0.7, false)

    # Brows and eyes.
    if absf(side) > 0.35:
        var nd := signf(side)
        draw_line(center+Vector2(nd*0.55,-1.8), center+Vector2(nd*2.95,-1.35), C_HAIR, 0.85, false)
        draw_circle(center+Vector2(nd*2.08,-0.70), 0.62, C_EYE_WHITE, false)
        draw_circle(center+Vector2(nd*2.25,-0.70), 0.34, C_EYE, false)
        # Nose bridge + tip is integrated into face rather than a lone triangle.
        draw_line(center+Vector2(nd*1.65,-0.8), center+Vector2(nd*2.55,0.25), C_SKIN_SHADOW, 0.65, false)
        var nose := PackedVector2Array([
            center+Vector2(nd*2.35,-0.45),
            center+Vector2(nd*(rx+1.35),0.35),
            center+Vector2(nd*2.65,1.10),
            center+Vector2(nd*1.95,0.75)
        ])
        draw_polygon(nose, PackedColorArray([C_SKIN_HILITE]))
        draw_circle(center+Vector2(-nd*rx*0.78,0.45), 0.86, C_SKIN_HILITE, false)
    else:
        draw_line(center+Vector2(-3.15,-1.75), center+Vector2(-0.85,-1.28), C_HAIR, 0.85, false)
        draw_line(center+Vector2(0.85,-1.28), center+Vector2(3.15,-1.75), C_HAIR, 0.85, false)
        draw_circle(center+Vector2(-1.80,-0.62), 0.62, C_EYE_WHITE, false)
        draw_circle(center+Vector2(1.80,-0.62), 0.62, C_EYE_WHITE, false)
        draw_circle(center+Vector2(-1.80,-0.62), 0.34, C_EYE, false)
        draw_circle(center+Vector2(1.80,-0.62), 0.34, C_EYE, false)
        # Nose bridge, side planes and tip.
        draw_line(center+Vector2(0.0,-0.40), center+Vector2(-0.55,1.15), C_SKIN_SHADOW, 0.65, false)
        draw_line(center+Vector2(0.0,-0.40), center+Vector2(0.55,1.15), C_SKIN_HILITE, 0.55, false)
        draw_line(center+Vector2(-0.55,1.15), center+Vector2(0.0,1.55), C_SKIN_SHADOW, 0.55, false)
        draw_line(center+Vector2(0.0,1.55), center+Vector2(0.62,1.12), C_SKIN_SHADOW, 0.55, false)

    # Moustache, mouth and angular beard/jaw matching the concept art.
    var shift := Vector2(side*1.35, maxf(0.0,facing.y)*0.65)
    draw_line(center+shift+Vector2(-2.05,1.55), center+shift+Vector2(0.0,1.85), C_HAIR, 0.8, false)
    draw_line(center+shift+Vector2(0.0,1.85), center+shift+Vector2(2.05,1.55), C_HAIR, 0.8, false)
    draw_line(center+shift+Vector2(-1.25,2.35), center+shift+Vector2(1.25,2.35), C_LIP, 0.55, false)

    var beard := PackedVector2Array([
        center+shift+Vector2(-3.75,1.75),
        center+shift+Vector2(-3.45,3.25),
        center+shift+Vector2(-2.25,4.45),
        center+shift+Vector2(-1.10,5.20),
        center+shift+Vector2(0.0,5.55),
        center+shift+Vector2(1.10,5.20),
        center+shift+Vector2(2.25,4.45),
        center+shift+Vector2(3.45,3.25),
        center+shift+Vector2(3.75,1.75),
        center+shift+Vector2(2.55,2.15),
        center+shift+Vector2(1.55,3.15),
        center+shift+Vector2(0.0,3.55),
        center+shift+Vector2(-1.55,3.15),
        center+shift+Vector2(-2.55,2.15)
    ])
    draw_polygon(beard, PackedColorArray([C_BEARD]))
    draw_polyline(_closed(beard), C_OUTLINE, 0.55, false)

    # Beard strand cues.
    draw_line(center+shift+Vector2(-2.65,3.0), center+shift+Vector2(-1.2,4.65), C_HAIR, 0.45, false)
    draw_line(center+shift+Vector2(2.65,3.0), center+shift+Vector2(1.2,4.65), C_HAIR, 0.45, false)
    draw_line(center+shift+Vector2(0.0,3.35), center+shift+Vector2(0.0,5.0), C_HAIR, 0.42, false)
'''

upper_func = r'''func _draw_upper_arm(shoulder: Vector2, elbow: Vector2, front: bool) -> void:
    var shade := C_JACKET_LITE if front else C_JACKET
    _draw_shaped_limb(shoulder, elbow, 6.0, 6.7, 4.8, 0.45, shade, C_OUTLINE)

    var d := (elbow-shoulder).normalized()
    if d.length_squared() < 0.001:
        return
    var n := Vector2(-d.y,d.x)
    # Shoulder seam only; no closed elbow ring.
    draw_arc(shoulder, 3.0, d.angle()-1.15, d.angle()+1.15, 8, C_STITCH, 0.60, false)
    var cuff := elbow - d*0.9
    draw_line(cuff-n*2.05, cuff+n*2.05, C_STITCH, 0.62, false)
'''

forearm_func = r'''func _draw_forearm_hand(elbow: Vector2, wrist: Vector2, front: bool) -> void:
    var total := wrist-elbow
    if total.length_squared() < 0.001:
        return
    var dir := total.normalized()

    # Begin slightly behind the elbow so the upper arm and forearm overlap,
    # then paint a joint mass over both outlines: one continuous bent arm.
    var fore_start := elbow - dir*1.15
    var mid := elbow + total*0.68
    _draw_shaped_limb(fore_start, mid, 5.2, 5.8, 4.1, 0.46, C_SKIN, C_OUTLINE)

    # Elbow blend covers the two segment end-caps / black seam.
    draw_circle(elbow, 2.55, C_SKIN, false)
    var bend_n := Vector2(-dir.y,dir.x)
    draw_arc(elbow, 2.60, dir.angle()-0.95, dir.angle()+0.95, 8, C_SKIN_SHADOW, 0.55, false)

    _draw_shaped_limb(mid, wrist, 4.25, 4.45, 3.75, 0.55, C_GLOVE, C_OUTLINE)

    var d := (wrist-mid).normalized()
    if d.length_squared() < 0.001:
        d = Vector2.DOWN
    var n := Vector2(-d.y,d.x)
    var hand_len := 3.8
    var hand_w := 4.3
    var tip := wrist + d*hand_len
    var hand := PackedVector2Array([
        wrist+n*hand_w*0.48-d*0.5,
        wrist-n*hand_w*0.48-d*0.5,
        tip-n*hand_w*0.34,
        tip+n*hand_w*0.34
    ])
    draw_polygon(hand, PackedColorArray([C_GLOVE]))
    draw_polyline(_closed(hand), C_OUTLINE, 0.82, false)
    draw_line(wrist+n*1.45+d*1.0, wrist-n*1.45+d*1.0, C_METAL, 0.62, false)
    draw_line(wrist+n*0.65+d*1.6, tip+n*0.45-d*0.4, C_OUTLINE, 0.42, false)
    draw_line(wrist-n*0.65+d*1.6, tip-n*0.45-d*0.4, C_OUTLINE, 0.42, false)
'''

shaped_func = r'''func _draw_shaped_limb(a: Vector2, b: Vector2, start_w: float, bulge_w: float, end_w: float, bulge_pos: float, fill: Color, outline: Color) -> void:
    var d := b-a
    if d.length_squared() < 0.001:
        return
    var dir := d.normalized()
    var n := Vector2(-dir.y,dir.x)
    var q1 := a.lerp(b, clampf(bulge_pos-0.17, 0.16, 0.60))
    var q2 := a.lerp(b, clampf(bulge_pos+0.18, 0.40, 0.84))

    var poly := PackedVector2Array([
        a+n*start_w*0.50,
        q1+n*bulge_w*0.53,
        q2+n*bulge_w*0.47,
        b+n*end_w*0.50,
        b-n*end_w*0.50,
        q2-n*bulge_w*0.47,
        q1-n*bulge_w*0.53,
        a-n*start_w*0.50
    ])
    draw_polygon(poly, PackedColorArray([fill]))
    draw_polyline(_closed(poly), outline, 0.82, false)
    # Only soften the origin; distal joint is blended by the next segment.
    draw_circle(a, start_w*0.43, fill, false)
'''

s = replace_func(s, "_draw", draw_func)
# Insert helpers before head if absent.
if "func _draw_neck(" not in s:
    idx = s.find("func _draw_head(")
    if idx < 0:
        raise SystemExit("D2B.16 head insertion anchor missing")
    s = s[:idx] + neck_func + "\n\n" + s[idx:]
s = replace_func(s, "_draw_head", head_func)
s = replace_func(s, "_draw_upper_arm", upper_func)
s = replace_func(s, "_draw_forearm_hand", forearm_func)
s = replace_func(s, "_draw_shaped_limb", shaped_func)

p.write_text(s, encoding="utf-8")

# ---------------------------------------------------------------------------
# One additional close-zoom layer.
# Patch the actual camera/zoom controller found in reconstructed source.
# ---------------------------------------------------------------------------
zoom_patched = False
zoom_diagnostics = []
for gp in root.rglob("*.gd"):
    text = gp.read_text(encoding="utf-8")
    if "zoom" not in text.lower():
        continue
    for ln in text.splitlines():
        if "zoom" in ln.lower():
            zoom_diagnostics.append(f"{gp.relative_to(root)}: {ln.strip()}")

    original = text

    # Common explicit max constants.
    def bump_const(m):
        nonlocal_zoom = float(m.group(2))
        bumped = max(nonlocal_zoom * 1.25, nonlocal_zoom + 0.25)
        return m.group(1) + (f"{bumped:.2f}".rstrip("0").rstrip("."))

    patterns = [
        r'(?im)^(\s*(?:const|var)\s+\w*ZOOM_MAX\w*\s*(?::=|=)\s*)([0-9]+(?:\.[0-9]+)?)',
        r'(?im)^(\s*(?:const|var)\s+MAX_?ZOOM\w*\s*(?::=|=)\s*)([0-9]+(?:\.[0-9]+)?)',
    ]
    for pat in patterns:
        def repl(m):
            val = float(m.group(2))
            bumped = max(val * 1.25, val + 0.25)
            return m.group(1) + (f"{bumped:.2f}".rstrip("0").rstrip("."))
        text, n = re.subn(pat, repl, text, count=1)
        if n:
            zoom_patched = True
            break

    # Zoom preset arrays of Vector2 values: append one 25% closer step.
    if not zoom_patched or text == original:
        arr_pat = re.compile(r'(?is)((?:const|var)\s+\w*zoom\w*\s*(?::=|=)\s*\[)(.*?)(\])')
        am = arr_pat.search(text)
        if am and "Vector2" in am.group(2):
            vals = re.findall(r'Vector2\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\)', am.group(2))
            if vals:
                x, y = map(float, vals[-1])
                nx, ny = x*1.25, y*1.25
                extra = f", Vector2({nx:.3f}, {ny:.3f})"
                text = text[:am.end(2)] + extra + text[am.end(2):]
                zoom_patched = True

    # Scalar preset arrays.
    if not zoom_patched or text == original:
        am = re.search(r'(?is)((?:const|var)\s+\w*zoom\w*\s*(?::=|=)\s*\[)([0-9.,\s]+)(\])', text)
        if am:
            vals = [float(v) for v in re.findall(r'[0-9]+(?:\.[0-9]+)?', am.group(2))]
            if len(vals) >= 2:
                nv = vals[-1] + (vals[-1]-vals[-2])
                text = text[:am.end(2)] + f", {nv:.3f}" + text[am.end(2):]
                zoom_patched = True

    # Clamp-based controller: increase the upper clamp by one 25% step.
    if text == original:
        clamp_pat = re.compile(r'(clampf\([^\n]*?zoom[^\n]*?,\s*[0-9.]+\s*,\s*)([0-9]+(?:\.[0-9]+)?)(\s*\))', re.I)
        cm = clamp_pat.search(text)
        if cm:
            val = float(cm.group(2))
            nv = max(val*1.25, val+0.25)
            text = text[:cm.start(2)] + (f"{nv:.2f}".rstrip("0").rstrip(".")) + text[cm.end(2):]
            zoom_patched = True

    if text != original:
        gp.write_text(text, encoding="utf-8")

if not zoom_patched:
    print("D2B.16 zoom diagnostics:")
    for line in zoom_diagnostics[:120]:
        print(line)
    raise SystemExit("D2B.16 could not locate the camera zoom limit/preset; see diagnostics above.")

# ---------------------------------------------------------------------------
# Android updateability: preserve package ID, increment version code/name,
# and point debug export at the persistent keystore prepared by CI.
# ---------------------------------------------------------------------------
preset = root / "export_presets.cfg"
if not preset.is_file():
    raise SystemExit("D2B.16 export_presets.cfg missing")
ep = preset.read_text(encoding="utf-8")
ep, n_code = re.subn(r'(?m)^version/code=\d+', 'version/code=27', ep, count=1)
ep, n_name = re.subn(r'(?m)^version/name="[^"]*"', 'version/name="0.19.0D2B.16"', ep, count=1)
if not n_code:
    raise SystemExit("D2B.16 version/code field not found")
if not n_name:
    raise SystemExit("D2B.16 version/name field not found")

# Keep the existing package identity; only signing/version are changed.
if 'package/unique_name="org.wanderfall.game"' not in ep:
    raise SystemExit("D2B.16 package ID changed unexpectedly")

def set_opt(text: str, key: str, value: str) -> str:
    pat = rf'(?m)^{re.escape(key)}=.*$'
    if re.search(pat, text):
        return re.sub(pat, f'{key}={value}', text, count=1)
    marker = '[preset.0.options]\n'
    if marker not in text:
        raise SystemExit(f"D2B.16 cannot insert export option {key}")
    return text.replace(marker, marker + f'{key}={value}\n', 1)

ep = set_opt(ep, 'keystore/debug', '"/home/runner/.android/debug.keystore"')
ep = set_opt(ep, 'keystore/debug_user', '"androiddebugkey"')
ep = set_opt(ep, 'keystore/debug_password', '"android"')
preset.write_text(ep, encoding="utf-8")

sp = root / "scripts/save/save_manager.gd"
if sp.is_file():
    x = sp.read_text(encoding="utf-8")
    x = x.replace('const GAME_VERSION := "0.19.0D2B.15"', 'const GAME_VERSION := "0.19.0D2B.16"')
    sp.write_text(x, encoding="utf-8")

print("Applied v0.19.0D2B.16: neck + seamless shoulders/elbows + concept-art face + extra close zoom + persistent-update export settings.")
