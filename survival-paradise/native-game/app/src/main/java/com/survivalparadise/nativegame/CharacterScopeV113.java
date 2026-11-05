package com.survivalparadise.nativegame;

/**
 * Player keeps pre-V113 preference keys and current calibration. NPCs have
 * separate independent settings with neutral defaults. No character art changes.
 */
public final class CharacterScopeV113 {
    public static final int PLAYER=0,NPCS=1;
    public static final String SCOPE_KEY="characterSliderTargetV113";
    private CharacterScopeV113(){}

    public static String key(String key,int scope){
        return scope==NPCS?key+"NpcV113":key;
    }
    public static int percent(int value,int lo,int hi){
        return Math.max(lo,Math.min(hi,value));
    }
    /** 100% is exactly the approved V5 head scale for each character. */
    public static float headSizeMultiplier(int percent){
        return percent(percent,75,160)/100f;
    }
}
