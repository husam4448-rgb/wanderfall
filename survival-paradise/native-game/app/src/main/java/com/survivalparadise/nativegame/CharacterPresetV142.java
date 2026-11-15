package com.survivalparadise.nativegame;

/** V142 body-only reference from November 15 screenshot.
 * Original head calibration and each of 200 head bitmaps are never altered.
 */
public final class CharacterPresetV142 {
    private CharacterPresetV142(){}
    public static final int TORSO=77,PELVIS=72,
        PIVOT_X=9,PIVOT_Y=-24,BREATH=4,
        BREATH_SPEED=100,WALK_FPS=4,WALK_SPEED=107,
        GLOBAL_SCALE=92;
    public static final String[] BODY_KEYS={
        "bodyWidthV114","pelvisWidthV115",
        "weaponPivotXV117","weaponPivotYV117",
        "fitIdleBreathV108","idleBreathingSpeedV110",
        "fitWalkFpsV108","walkingAnimationSpeedV79"
    };
    public static final int[] BODY_VALUES={
        TORSO,PELVIS,PIVOT_X,PIVOT_Y,BREATH,BREATH_SPEED,
        WALK_FPS,WALK_SPEED
    };
    public static String scopeKey(String key,boolean npc){
        return npc?key+"NpcV113":key;
    }
}
