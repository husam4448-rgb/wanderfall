#!/usr/bin/env python3
"""SP283: adapt only outdated NPC-renderer assertions in the v262 visual QA.
All player, zombie, wildlife, real screenshots, combat and frame checks remain.
"""
from pathlib import Path
import sys
path=Path(sys.argv[1])
s=path.read_text()
def patch(old,new,label):
 global s
 n=s.count(old)
 if n!=1:raise RuntimeError(f"{label} expected once, found {n}")
 s=s.replace(old,new,1)
patch(
'''    var nstate: Dictionary = await _state(friend,"capture")
    if nstate.get("preview_actor") == null or nstate.get("viewport") == null:
        _fail("NPC must use genuine layered-actor cached render rather than rectangle")
        return
    if nstate["sprite"].texture == null:
        _fail("NPC source render not cached to texture")
        return''',
'''    var friend_visual: Node2D = friend.get("_sp283_shared_visual") as Node2D
    if friend_visual == null:
        _fail("Friendly NPC shared player-derived renderer missing")
        return
    var friend_body: Node2D = friend_visual.get("sprite") as Node2D
    if friend_body == null or not String(friend_body.get_script().resource_path).contains("baked_actor_visual.gd"):
        _fail("Female NPC does not use approved player female body renderer")
        return''',"FRIENDLY_RETIRED_RENDER")
patch('''    for label in ["zombie","friendly_npc"]:''','''    for label in ["zombie"]:''',"ONE_TINT_LEGACY_LIST")
patch(
'''    var bandit_state: Dictionary = await _state(bandit, "capture")
    if bandit_state.is_empty() or bandit_state["node"].get_child_count() != 1:
        _fail("Bandit not rendered via single final RGBA shader")
        return
    if bandit_state["sprite"].material != bandit_state["material"]:
        _fail("Bandit still has non-uniform alpha overlap")
        return''',
'''    var bandit_visual: Node2D = bandit.get("_sp283_shared_visual") as Node2D
    if bandit_visual == null:
        _fail("Bandit does not have the shared player-derived body")
        return
    var bandit_body: Node2D = bandit_visual.get("sprite") as Node2D
    if bandit_body == null:
        _fail("Bandit body renderer missing")
        return
    var bandit_path: String = String(bandit_body.get_script().resource_path)
    if not (bandit_path.contains("SurvivorWalkSprite.gd") or bandit_path.contains("baked_actor_visual.gd")):
        _fail("Bandit does not reuse approved male/female player body source")
        return''',"BANDIT_RETIRED_RENDER")
patch(
'''    print("SP_V262_ONE_TINT_NPC_QA_PASS zombies, friendly NPCs and bandits all have one final tint")''',
'''    print("SP_V262_ONE_TINT_NPC_QA_PASS zombie has one final tint; female NPC and bandit use same body sources as player")''',"TRUTHFUL_COVERAGE")
path.write_text(s)
print("SP283_COMPAT_LEGACY_TEST_PASS old NPC renderer checks replaced with shared-player source checks; original player/zombie/wildlife/13 screenshot checks retained")
