#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parent / "apply_v0173_touch_layout_fixes.py"
text = path.read_text(encoding="utf-8")
old = 'subprocess.run(["patch", "-p1", "-i", str(patch_path)], cwd=root, check=True)'
new = 'subprocess.run(["patch", "-p1", "-i", str(patch_path.resolve())], cwd=root, check=True)'
count = text.count(old)
if count == 1:
    path.write_text(text.replace(old, new), encoding="utf-8")
elif new in text:
    pass
else:
    raise SystemExit("Unexpected v0.17.3 applicator shape; refusing an unsafe rewrite")
print("Prepared v0.17.3 applicator for cwd-safe patch execution.")
