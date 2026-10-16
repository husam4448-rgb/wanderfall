#!/usr/bin/env python3
"""PC56 structural rig contract verifier. No proprietary art/assets involved."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
contract=json.loads((ROOT/"pc56/b2b_reference_rig_contract.json").read_text())
assert contract["status"]=="STRUCTURAL_REFERENCE_ONLY_RAW_ART_UNAVAILABLE"
nodes=contract["original_template"]["nodes"]
name_to_parent={n["id"]:n["parent"] for n in nodes}
assert len(name_to_parent)==len(nodes), "Duplicate bone IDs"
assert name_to_parent["root"] is None
for name in name_to_parent:
    visited=set()
    current=name
    while current is not None:
        assert current not in visited, f"Cycle in {name}"
        visited.add(current)
        if current!= "root":
            assert name_to_parent[current] in name_to_parent, f"Orphan {current}"
        current=name_to_parent[current]
required={"front_foot","back_foot","front_thigh","front_shin","back_thigh","back_shin",
          "near_upper_arm","near_forearm","near_hand","far_upper_arm","far_forearm","far_hand",
          "rifle_trigger_grip","rifle_support_grip","rifle_stock","rifle_muzzle"}
assert required <= name_to_parent.keys()
assert name_to_parent["front_foot"]=="front_shin"
assert name_to_parent["back_foot"]=="back_shin"
assert name_to_parent["rifle_trigger_grip"]=="rifle"
assert name_to_parent["rifle_support_grip"]=="rifle"
constraints=contract["original_template"]["constraints"]
assert len(constraints)==4
for c in constraints:
    assert c["type"]=="two_bone_ik"
    a,b=c["chain"]
    assert name_to_parent[b]==a, f"Non-contiguous IK: {a}/{b}"
    assert c["target"] not in (a,b)
assert all(x["bend"]=="ANATOMICAL_FRONT" for x in constraints[:2])
print("PC56_CONTRACT_PASS",len(nodes),"bones",len(constraints),"IK chains")
print("NOTE: STRUCTURE ONLY; no B2B textures/animations or rendered visual pass")
