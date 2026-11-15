package com.survivalparadise.nativegame;

/** Link all pre-V140 equippable non-head garments to approved V139 sprites.
 * Head gear remains inventory/effects only by permanent V138 policy.
 * No new raster artwork and no modifications to approved 200 original heads.
 */
public final class LegacyOutfitVisualV142 {
    private LegacyOutfitVisualV142(){}
    // Canvas work jacket -> Workwear; weather coat -> Winter;
    // plate carrier -> Armor.
    private static final int[] TORSO={9,16,6};
    // Cargo trousers -> Military; ripstop -> Ranger; tactical -> Armor.
    private static final int[] PANTS={10,18,6};
    // Steel-toe work boots -> reinforced work; trail -> trail; tactical -> combat.
    private static final int[] BOOTS={3,4,1};
    public static int torso(int legacy,int fallback){
        return legacy>=0&&legacy<TORSO.length?TORSO[legacy]:fallback;
    }
    public static int pants(int legacy,int fallback){
        return legacy>=0&&legacy<PANTS.length?PANTS[legacy]:fallback;
    }
    public static int boots(int legacy,int fallback){
        return legacy>=0&&legacy<BOOTS.length?BOOTS[legacy]:fallback;
    }
    public static int headgear(int legacy){return -1;} // ALWAYS invisible.
}
