#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

def read(rel):
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"Missing D2B.2C target: {p}")
    return p, p.read_text(encoding="utf-8")

player_path, player = read("scripts/player.gd")

old_motion = '''    velocity = direction * speed
    move_and_slide()
    _update_actor_visual()
'''
new_motion = '''    velocity = direction * speed
    if _actor_visual != null and _actor_visual.has_method("set_motion_state"):
        _actor_visual.set_motion_state(velocity, is_sprinting, is_crouching)
    move_and_slide()
    _update_actor_visual()
'''
if new_motion not in player:
    if old_motion not in player:
        raise SystemExit("D2B.2C motion-state anchor missing")
    player = player.replace(old_motion, new_motion, 1)

needle = "        _swing_melee(data)\n"
count = player.count(needle)
if count <= 0:
    raise SystemExit("D2B.2C melee swing call missing")
replacement = '''        if _actor_visual != null and _actor_visual.has_method("play_melee"):
            _actor_visual.play_melee(_facing)
        if _weapon_visual != null and _weapon_visual.has_method("play_melee"):
            _weapon_visual.play_melee()
        _swing_melee(data)
'''
if "play_melee(_facing)" not in player:
    player = player.replace(needle, replacement)

bash_anchor = "    _attack_cooldown = 0.42\n    var bash_range := 58.0\n"
if bash_anchor in player and "var bash_range := 58.0" in player:
    player = player.replace(
        bash_anchor,
        '''    _attack_cooldown = 0.42
    if _actor_visual != null and _actor_visual.has_method("play_melee"):
        _actor_visual.play_melee(_facing)
    var bash_range := 58.0
''',
        1,
    )

player_path.write_text(player, encoding="utf-8")

save_path, save = read("scripts/save/save_manager.gd")
if 'const GAME_VERSION := "0.19.0D2B.1"' in save:
    save = save.replace('const GAME_VERSION := "0.19.0D2B.1"', 'const GAME_VERSION := "0.19.0D2B.2"', 1)
    save_path.write_text(save, encoding="utf-8")

print(f"Applied v0.19.0D2B.2C locomotion-driven articulated animation and melee joint triggers ({count} melee call paths).")
