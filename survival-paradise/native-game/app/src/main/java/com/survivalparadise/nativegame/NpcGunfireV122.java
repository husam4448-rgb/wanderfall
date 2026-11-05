package com.survivalparadise.nativegame;

/**
 * Shared firearm-only NPC gunfire guard. Indoor damage remains hitscan
 * (existing V90 gameplay), but a transient real-shot visual travels toward
 * the impact on the same tick. Outdoors use existing physical Shot objects.
 */
public final class NpcGunfireV122 {
    public static final float INDOOR_ROUND_SPEED=1850f;
    public static final float INDOOR_ROUND_MAX_LIFE=.35f;
    private NpcGunfireV122(){}
    public static boolean firearm(int weapon){return GunEffectsV119.firearm(weapon);}
    public static float life(float x0,float y0,float x1,float y1){
        return Math.min(INDOOR_ROUND_MAX_LIFE,
            (float)Math.hypot(x1-x0,y1-y0)/INDOOR_ROUND_SPEED);
    }
    public static float[] velocity(float x0,float y0,float x1,float y1){
        float dx=x1-x0,dy=y1-y0;
        float m=Math.max(.001f,(float)Math.hypot(dx,dy));
        return new float[]{dx/m*INDOOR_ROUND_SPEED,dy/m*INDOOR_ROUND_SPEED};
    }
}
