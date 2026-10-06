#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, sys

repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
game = Path(sys.argv[2] if len(sys.argv) > 2 else "game")
runtime = game / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not runtime.is_file():
    raise SystemExit("PC22 runtime missing: " + str(runtime))

text = runtime.read_text(encoding="utf-8")
if "PLAYER CHARACTERS V22" not in text:
    raise SystemExit("Runtime is not PlayerCharacters_v22")

out = repo / "assets" / "authored2d" / "unified_character" / "arms" / "qa"
out.mkdir(parents=True, exist_ok=True)

def func_body(name):
    m = re.search(r"(?m)^func\s+" + re.escape(name) + r"\s*\([^\n]*", text)
    if not m:
        return None
    start = m.start()
    n = re.search(r"(?m)^func\s+", text[m.end():])
    end = m.end() + n.start() if n else len(text)
    return text[start:end].rstrip()

def vec2_after(fragment):
    m = re.search(r"Vector2\(\s*(-?\d+(?:\.\d+)?)\s*\*?\s*dir_sign?\s*,\s*(-?\d+(?:\.\d+)?)\s*\)", fragment)
    if not m:
        m = re.search(r"Vector2\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)", fragment)
    return [float(m.group(1)), float(m.group(2))] if m else None

lines = text.splitlines()
relevant = []
keys = ("hand_", "hand ", "grip", "weapon", "gun", "pistol", "rifle", "recoil",
        "shoulder", "elbow", "wrist", "arm", "aim_", "angle", "pivot", "_pose_point")
for i, line in enumerate(lines, 1):
    low = line.lower()
    if any(k in low for k in keys):
        relevant.append({"line": i, "text": line})

functions = {}
for name in re.findall(r"(?m)^func\s+([A-Za-z0-9_]+)\s*\(", text):
    low = name.lower()
    if any(k in low for k in ("actor","hand","weapon","gun","pose","arm","leg","aim")):
        body = func_body(name)
        if body:
            functions[name] = body

def regex_vec(pattern):
    m = re.search(pattern, text)
    if not m:
        return None
    return [float(m.group(1)), float(m.group(2))]

pivot = regex_vec(r"var\s+pivot\s*:=\s*base\s*\+\s*Vector2\(\s*([0-9.]+)\s*\*\s*dir_sign\s*,\s*(-?[0-9.]+)\s*\)")
dom = regex_vec(r"hand_rear\s*:=\s*pivot\s*\+\s*_rot\(Vector2\(\s*(-?[0-9.]+)\s*,\s*(-?[0-9.]+)\s*\)")
sup = regex_vec(r"hand_front\s*:=\s*pivot\s*\+\s*_rot\(Vector2\(\s*(-?[0-9.]+)\s*,\s*(-?[0-9.]+)\s*\)")

# PC22 unified manifest is an independent generated summary; compare it against runtime evidence.
canon_path = repo / "assets" / "authored2d" / "unified_character" / "canonical_pc22.json"
canonical = json.loads(canon_path.read_text(encoding="utf-8")) if canon_path.is_file() else {}

checks = {
    "pc22_title": "PLAYER CHARACTERS V22" in text,
    "left_right_only": "var face_right := aim_pos.x >= actor_pos.x" in text,
    "no_eight_direction_markers": not any(x in text for x in ("direction_index","octant_index","eight_direction","8_direction")),
    "visible_procedural_female_arm_chain": "_draw_female_arm_chain(" in text,
    "visible_authored_female_arm": "_draw_female_authored_arm(" in text,
    "visible_authored_upper_arm_texture": bool(re.search(r"(?i)(upper[_ ]?arm).*(preload|load|texture)", text)),
    "visible_authored_forearm_texture": bool(re.search(r"(?i)(forearm).*(preload|load|texture)", text)),
    "weapon_pivot_found": pivot is not None,
    "dominant_hand_socket_found": dom is not None,
    "support_hand_socket_found": sup is not None,
}

report = {
    "standard_id": "PlayerCharacters_v22",
    "runtime_path": str(runtime.relative_to(game)),
    "runtime_sha256": hashlib.sha256(runtime.read_bytes()).hexdigest(),
    "line_count": len(lines),
    "checks": checks,
    "extracted_runtime": {
        "weapon_pivot_from_base": pivot,
        "dominant_hand_from_pivot": dom,
        "support_hand_from_pivot": sup,
    },
    "canonical_manifest": canonical,
    "relevant_lines": relevant,
    "relevant_functions": sorted(functions),
}
(out / "runtime_arm_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

ex = []
ex.append("// PlayerCharacters_v22 arm/hand/weapon audit")
ex.append("// runtime sha256: " + report["runtime_sha256"])
for name, body in functions.items():
    ex.append("\n// ===== " + name + " =====\n")
    ex.append(body)
ex.append("\n// ===== ALL RELEVANT LINES =====\n")
for rec in relevant:
    ex.append("%05d: %s" % (rec["line"], rec["text"]))
(out / "runtime_arm_excerpt.gd.txt").write_text("\n".join(ex), encoding="utf-8")

if not all((checks["pc22_title"], checks["left_right_only"], checks["weapon_pivot_found"])):
    raise SystemExit("Required PC22 runtime anchors missing: " + json.dumps(checks))

print("PC22_ARM_AUDIT_OK")
print(json.dumps(report["extracted_runtime"], sort_keys=True))
