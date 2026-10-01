#!/usr/bin/env python3
from pathlib import Path
import re, sys, base64, hashlib

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parents[1]

chunk_dir = repo_root / "art_source" / "d2d26" / "head_south_chunks"
chunks = [chunk_dir / f"{i:02d}.txt" for i in range(5)]
missing = [str(p) for p in chunks if not p.exists()]
if missing:
    raise SystemExit(f"D2D.26 head chunks missing: {missing}")

encoded = "".join(p.read_text(encoding="utf-8").strip() for p in chunks)
head_bytes = base64.b64decode(encoded, validate=True)
expected = "15471bbdfb04ca54a0595445aab3d31f437cd135f6a4f64a630b2d14a9e8f13e"
actual = hashlib.sha256(head_bytes).hexdigest()
if actual != expected:
    raise SystemExit(f"D2D.26 South head SHA mismatch: {actual}")

asset_dir = root / "assets" / "d2d26"
asset_dir.mkdir(parents=True, exist_ok=True)
(asset_dir / "head_south.png").write_bytes(head_bytes)

src_path = root / "scripts" / "art" / "d2d25_normalized_cutout_lab.gd"
if not src_path.exists():
    raise SystemExit("D2D.25 runtime script missing")
s = src_path.read_text(encoding="utf-8")

s = s.replace(
    'const NORTH_ATLAS := preload("res://assets/d2d23/north.webp")',
    'const NORTH_ATLAS := preload("res://assets/d2d23/north.webp")\nconst SOUTH_HEAD_D2D26 := preload("res://assets/d2d26/head_south.png")',
    1
)

repls = {
    '"upper_arm_L":{"size":[50,95],"pos":[82,141]}': '"upper_arm_L":{"size":[50,95],"pos":[82,141]}',
    '"upper_arm_R":{"size":[49,96],"pos":[230,141]}': '"upper_arm_R":{"size":[50,95],"pos":[230,141]}',
    '"forearm_hand_L":{"size":[47,108],"pos":[75,187]}': '"forearm_hand_L":{"size":[42,94],"pos":[86,197]}',
    '"forearm_hand_R":{"size":[46,108],"pos":[240,187]}': '"forearm_hand_R":{"size":[42,94],"pos":[234,197]}',
    '"upper_arm_L":{"size":[39,78],"pos":[89,126]}': '"upper_arm_L":{"size":[45,90],"pos":[86,126]}',
    '"upper_arm_R":{"size":[38,78],"pos":[216,126]}': '"upper_arm_R":{"size":[45,90],"pos":[213,126]}',
    '"forearm_hand_L":{"size":[47,108],"pos":[68,187]}': '"forearm_hand_L":{"size":[40,92],"pos":[89,190]}',
    '"forearm_hand_R":{"size":[45,106],"pos":[231,191]}': '"forearm_hand_R":{"size":[40,92],"pos":[216,190]}'
}
for old, new in repls.items():
    if old not in s:
        raise SystemExit(f"D2D.26 arm normalization anchor missing: {old}")
    s = s.replace(old, new, 1)

old_func = '''func _normalized_texture(part: String) -> Texture2D:
    var rr: Array = _raw_rect(part)
    var spec: Dictionary = _normal()[part]
    var sz: Array = spec["size"]
    var src := _atlas_image().get_region(Rect2i(int(rr[0]),int(rr[1]),int(rr[2]),int(rr[3])))
    src.resize(int(sz[0]),int(sz[1]),Image.INTERPOLATE_NEAREST)
    return ImageTexture.create_from_image(src)
'''
new_func = '''func _normalized_texture(part: String) -> Texture2D:
    if part == "head" and current_dir == "south":
        return SOUTH_HEAD_D2D26
    var rr: Array = _raw_rect(part)
    var spec: Dictionary = _normal()[part]
    var sz: Array = spec["size"]
    var src := _atlas_image().get_region(Rect2i(int(rr[0]),int(rr[1]),int(rr[2]),int(rr[3])))
    src.resize(int(sz[0]),int(sz[1]),Image.INTERPOLATE_NEAREST)
    return ImageTexture.create_from_image(src)
'''
if old_func not in s:
    raise SystemExit("D2D.26 texture function anchor missing")
s = s.replace(old_func, new_func, 1)

s = s.replace(
    'title.text = "D2D.25 — NORMALIZED CUTOUT ASSET LAB"',
    'title.text = "D2D.26 — ARM NORMALIZATION + APPROVED FACE"',
    1
)
s = s.replace(
    'subtitle.text = "Full-body reference calibrated • baked pixel dimensions • runtime scale locked 1.00x"',
    'subtitle.text = "Neutral calibration • matched arm proportions • approved South face • runtime scale 1.00x"',
    1
)
s = s.replace(
    'note.text = "This checkpoint tests neutral proportions only. Elbow and knee animation stay disabled until the normalized body is approved."',
    'note.text = "Neutral-only checkpoint. Forearms are narrower/shorter than upper arms, elbow centers are aligned, and the approved South face is now the runtime asset."',
    1
)
s = s.replace(
    '"NEXT ONLY AFTER PASS:\\nelbow flex → backward knee pose"',
    '"NEXT ONLY AFTER PASS:\\nelbow flex → backward knee pose"',
    1
)

# Correct visible elbow overlay markers to the new centers.
s = s.replace(
    'Vector2(100,202),Vector2(263,202),',
    'Vector2(107,205),Vector2(255,205),',
    1
)
s = s.replace(
    'Vector2(98,199),Vector2(246,202),',
    'Vector2(108,193),Vector2(236,193),',
    1
)

dst = root / "scripts" / "art" / "d2d26_arm_normalization_lab.gd"
dst.write_text(s, encoding="utf-8")

scene = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/art/d2d26_arm_normalization_lab.gd" id="1"]

[node name="D2D26ArmNormalizationLab" type="Node2D"]
script = ExtResource("1")
"""
(root / "scenes" / "d2d26_arm_normalization_lab.tscn").write_text(scene, encoding="utf-8")

project = root / "project.godot"
q = project.read_text(encoding="utf-8")
q,n = re.subn(r'(?m)^run/main_scene=.*$', 'run/main_scene="res://scenes/d2d26_arm_normalization_lab.tscn"', q, count=1)
if n != 1:
    raise SystemExit("D2D.26 main_scene anchor missing")
project.write_text(q, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$', 'version/code=99', e, count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.26"', e, count=1)
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"', 'const GAME_VERSION := "0.21.0D2D.26"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print(f"Applied D2D.26 arm normalization + approved South face. Head SHA: {actual}")
