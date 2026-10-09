#!/usr/bin/env python3
"""PC29: move skeletal ankle inside boot while keeping boot/ground fixed.

The original knee solver used the *top of the boot* as anatomical ankle,
making hip->ankle too short and keeping both knees over-bent. This shifts only
the rigged ankle deeper into the existing boot, not the planted boot itself.
PC29_LEGACY_STANCE=1 preserves prior PC28 artwork+IK for A/B validation.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=p.read_text(encoding="utf-8")
start='''    var pc28_segmented: bool = OS.get_environment("PC28_LEGACY_KNEE") != "1" and move_vec.length() > 0.05
    if pc28_segmented:
'''
modified='''    var pc28_segmented: bool = OS.get_environment("PC28_LEGACY_KNEE") != "1" and move_vec.length() > 0.05
    var pc29_posture_enabled: bool = pc28_segmented and OS.get_environment("PC29_LEGACY_STANCE") != "1"
    var pc29_original_boot_socket: Vector2 = ankle
    if pc29_posture_enabled:
        # In the legacy artwork, the ankle point sat at the top of the boot.
        # Proper skeletal ankle is lower inside footwear, improving knee
        # extension without raising or shifting planted/swinging shoes.
        ankle += Vector2(0.0,4.10 if female_mode else 4.25)
    if pc28_segmented:
'''
if s.count(start)!=1:
    raise SystemExit("PC29 knee anchor not found once")
s=s.replace(start,modified,1)
boot='''    var boot_center := ankle + Vector2(((1.0 if female_mode else 0.4) * dir_sign), (6.2 if female_mode else 6.8))
'''
fixed='''    var foot_socket: Vector2 = pc29_original_boot_socket if pc29_posture_enabled else ankle
    var boot_center := foot_socket + Vector2(((1.0 if female_mode else 0.4) * dir_sign), (6.2 if female_mode else 6.8))
'''
if s.count(boot)!=1:
    raise SystemExit("PC29 footwear socket anchor not found once")
s=s.replace(boot,fixed,1)
p.write_text(s,encoding="utf-8")
e=root/"export_presets.cfg"
q=e.read_text(encoding="utf-8")
if q.count("version/code=199")!=1 or q.count('version/name="0.22.0-PC28-KNEE-CUFF-REPAIR"')!=1:
    raise SystemExit("PC29 expected verified cuff version 199")
e.write_text(q.replace("version/code=199","version/code=200",1).replace(
    'version/name="0.22.0-PC28-KNEE-CUFF-REPAIR"',
    'version/name="0.22.0-PC29-KNEE-STANCE"',1),encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.is_file():
    v=save.read_text(encoding="utf-8")
    a='const GAME_VERSION := "0.22.0-PC28-KNEE-CUFF-REPAIR"'
    if v.count(a)!=1:
        raise SystemExit("PC29 save version mismatch")
    save.write_text(v.replace(a,'const GAME_VERSION := "0.22.0-PC29-KNEE-STANCE"',1),encoding="utf-8")
print("PC29 anatomical ankle set inside textured boot; planted boot sockets unchanged. APK version 200.")
