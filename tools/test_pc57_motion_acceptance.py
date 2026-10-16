#!/usr/bin/env python3
"""Tests for original PC57 acceptance metrics, including a deliberate broken grip."""
from pc57_motion_acceptance import check
def fixture():
    return {"frames":[{
      "time_seconds":i/30.0,
      "feet":{"left":{"heel_world":[0.0,0.0],"stance":i<16},
              "right":{"heel_world":[10.0,0.0],"stance":i>=16}},
      "hands":{"dominant":{"actual_world":[1.0,3.0],"grip_world":[1.0,3.0]},
               "support":{"actual_world":[15.0,3.0],"grip_world":[15.0,3.0]}}
     } for i in range(32)]}
good=fixture()
assert check(good)["numerical_pass"]
bad=fixture()
bad["frames"][4]["hands"]["support"]["actual_world"]=[24.0,3.0]
assert not check(bad)["numerical_pass"],"Broken foregrip must fail"
sliding=fixture()
sliding["frames"][6]["feet"]["left"]["heel_world"]=[8.0,0.0]
assert not check(sliding)["numerical_pass"],"Sliding planted heel must fail"
print("PC57_ACCEPTANCE_TESTS_PASS positives=1 rejected_broken_grip=1 rejected_foot_sliding=1")
