#!/usr/bin/env python3
"""PC40 true stock/torso layer correction.

PC22–PC39 draws the small stock butt sprite BEFORE an opaque equipment vest
and torso. Therefore mathematically correct stock/shoulder contacts disappear
inside the chest, making rifle look unshouldered. Move stock sprite to the
anatomical layer AFTER equipped torso+backpack and BEFORE neck/head, shoulder
sleeves, grip hands and rifle receiver. Maintain identical weapon transforms,
frame targets and original texture pixels. This is a rendering-order change,
not another grip/shoulder position offset.

PC40_LEGACY_STOCK_LAYER=1 preserves PC39 layer order for exact A/B.
Apply after PC39 clavicle patch.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
path=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=path.read_text(encoding="utf8")
old='''    # Rifle stock remains rear-depth. The short firing-wrist bridge is deferred
    # until after torso draw so it cannot disappear completely under the body.
    if weapon_visible and weapon_two_handed:
        if tex_pc22_rifle_stock != null:
            _pc30_draw_fitted_rifle_piece(tex_pc22_rifle_stock,pc22_dom_grip,pc22_arm_angle,dir_sign)
'''
new='''    # PC40 baseline switch: previous rifle stock was drawn BEFORE the opaque
    # equipped torso/vest, hiding the physical shoulder/butt contact.
    if OS.get_environment("PC40_LEGACY_STOCK_LAYER") == "1":
        if weapon_visible and weapon_two_handed and tex_pc22_rifle_stock != null:
            _pc30_draw_fitted_rifle_piece(tex_pc22_rifle_stock,pc22_dom_grip,pc22_arm_angle,dir_sign)
'''
if s.count(old)!=1:raise SystemExit("PC40 old rear-stock layer anchor mismatch")
s=s.replace(old,new,1)
marker='''    # D2D.36 strict two-state head system.'''
code='''    # PC40 close the stock/shoulder layer contract: vest and backpack below,
    # stock butt above torso but below near-arm glove and head/neck. The actual
    # pixel butt position is the same PC39 stock-to-shoulder contact; only
    # visibility changes. Never draw stock after the foreground firing hand.
    if OS.get_environment("PC40_LEGACY_STOCK_LAYER") != "1":
        if weapon_visible and weapon_two_handed and tex_pc22_rifle_stock != null:
            _pc30_draw_fitted_rifle_piece(tex_pc22_rifle_stock,pc22_dom_grip,pc22_arm_angle,dir_sign)

'''
if s.count(marker)!=1:raise SystemExit("PC40 head layer boundary not unique")
s=s.replace(marker,code+marker,1)
path.write_text(s,encoding="utf8")
print("PC40 stock butt is visible above clothing but stays behind head and nearer arm/hand source sprites.")
print("PC40_LEGACY_STOCK_LAYER=1 restores PC39 art order without geometry change.")
