package com.survivalparadise.nativegame;

/**
 * V144 unique legacy clothing art IDs. Stable V92 item IDs and V140 saved
 * equipment slots are deliberately unchanged. The V139 renderer loads these
 * from the additional, optional V144 archive and falls back to V142 styles
 * when art is unavailable. Never render anything on the original head.
 */
public final class LegacyOutfitVisualV144 {
    private LegacyOutfitVisualV144() {}
    public static final int FIRST_TORSO=20,FIRST_PANTS=20,FIRST_BOOT=5;
    public static int torso(int legacy,int fallback){
        return legacy>=0&&legacy<3?FIRST_TORSO+legacy:fallback;
    }
    public static int pants(int legacy,int fallback){
        return legacy>=0&&legacy<3?FIRST_PANTS+legacy:fallback;
    }
    public static int boots(int legacy,int fallback){
        return legacy>=0&&legacy<3?FIRST_BOOT+legacy:fallback;
    }
    public static int headgear(int legacy){return -1;}
}
