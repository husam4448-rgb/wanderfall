#!/usr/bin/env python3
"""Update the 2026 v281 save behavior assertion for v284's user-wide FPS preference.
The user-wide FPS slider deliberately takes precedence over a per-game save cap;
all original CPU/AI/quality/facing tests remain.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text()
a='''    if int(perf.call("get_fps_cap")) != 30:
        _fail("FPS-only setting not preserved by save/load")
        return'''
b='''    # User explicitly selected PRESET (0) after saving the game at 30 FPS.
    # v284's independent user-wide setting takes precedence on game load,
    # rather than silently restoring the old per-save 30-FPS override.
    if int(perf.call("get_fps_cap")) != 60:
        _fail("user-wide FPS preference was overwritten by an old save")
        return'''
assert s.count(a)==1
s=s.replace(a,b)
p.write_text(s)
print("SP284_PRECEDENCE_QA_PASS new render preference overrides older game save")
