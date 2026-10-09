#!/usr/bin/env python3
"""PC41 preserve original source RGB while occluding the rifle butt by authored shoulder art.

PC40 moved a short flat-stock PNG above opaque clothing and exposed an obvious
rectangular butt. PC41 splits visual *compositing*, not weapon geometry:
 - create a derivative of existing real rifle-stock PNG, alpha feathering only
   the trailing shoulder-inserted section of the stock; RGB remains unchanged;
 - render the true authored shoulder-cap texture *over* the stock butt, below
   the head and foreground rifle/hand, at the existing anatomical rear shoulder.
 - keep original PC40 renderer via PC41_LEGACY_MASK=1 for strict A/B.
No arm/weapon/stock pivot, IK, muzzle, equipment socket, or source sprites changed.
"""
from pathlib import Path
import sys
from PIL import Image
repo=Path(__file__).resolve().parents[1]
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
src=repo/"assets/authored2d/unified_character/arms/hybrid_v3/weapons/SP_PC22_Rifle_Stock_V3.png"
dst=root/"assets/authored2d/unified_character/arms/hybrid_v3/weapons/SP_PC41_Stock_ShoulderMasked.png"
orig=Image.open(src).convert("RGBA")
dst.parent.mkdir(parents=True,exist_ok=True)
modified=orig.copy()
# Alpha-only feather: the butt enters BELOW the deltoid/vest shoulder;
# preserve full original RGB, all forward receiver pixels, and source scale.
assert orig.width==96 and orig.height==30
changes=0
for y in range(orig.height):
    for x in range(orig.width):
        r,g,b,a=orig.getpixel((x,y))
        if a==0:continue
        if x<=6:
            factor=0.08
        elif x>=24:
            factor=1.0
        else:
            t=(x-6)/18.0
            factor=.08+.92*t*t*(3-2*t)
        # The source cloth shoulder mask is the real dynamic near-side cap,
        # drawn later at the actual rear shoulder.
        new_alpha=round(a*factor)
        if new_alpha!=a:changes+=1
        modified.putpixel((x,y),(r,g,b,new_alpha))
if changes<20:raise RuntimeError("PC41 original source opaque butt not masked")
modified.save(dst)
sfile=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=sfile.read_text(encoding="utf8")
anchor='const PC37AimPose2D = preload("res://scripts/art/pc37_aim_pose_2d.gd")\n'
if s.count(anchor)!=1:raise RuntimeError("PC41 constant placement anchor missing")
s=s.replace(anchor,anchor+'const PC41StockShoulderMasked = preload("res://assets/authored2d/unified_character/arms/hybrid_v3/weapons/SP_PC41_Stock_ShoulderMasked.png")\n',1)
block='''    if OS.get_environment("PC40_LEGACY_STOCK_LAYER") != "1":
        if weapon_visible and weapon_two_handed and tex_pc22_rifle_stock != null:
            _pc30_draw_fitted_rifle_piece(tex_pc22_rifle_stock,pc22_dom_grip,pc22_arm_angle,dir_sign)

'''
if s.count(block)!=1:raise RuntimeError("PC41 PC40 stock layer block not exactly once")
replacement='''    if OS.get_environment("PC40_LEGACY_STOCK_LAYER") != "1":
        if weapon_visible and weapon_two_handed and tex_pc22_rifle_stock != null:
            if OS.get_environment("PC41_LEGACY_MASK") == "1":
                _pc30_draw_fitted_rifle_piece(tex_pc22_rifle_stock,pc22_dom_grip,pc22_arm_angle,dir_sign)
            else:
                # The rifle butt's rear portion slips beneath the deltoid
                # source-art shoulder cap; the forward stock remains continuous.
                _pc30_draw_fitted_rifle_piece(PC41StockShoulderMasked,pc22_dom_grip,pc22_arm_angle,dir_sign)
                _pc22_v3_draw_cap(_pc22_shoulder_cap_texture(),pc22_rear_shoulder,pc22_rear_elbow,dir_sign)

'''
s=s.replace(block,replacement,1)
sfile.write_text(s,encoding="utf8")
print(f"PC41_SOURCE_ALPHA_MASK_OK dimensions={orig.size} changed_opaque_pixels={changes}, RGB original untouched")
print("PC41 true authored shoulder cap used in near depth, original PC40 available with PC41_LEGACY_MASK=1")
