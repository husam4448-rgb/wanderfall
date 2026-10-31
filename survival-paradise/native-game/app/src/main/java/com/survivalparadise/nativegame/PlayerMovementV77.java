package com.survivalparadise.nativegame;

/** V77: change locomotion only, never simulation, projectile speed, or clock. */
public final class PlayerMovementV77 {
    private PlayerMovementV77(){}
    public static final int DEFAULT_PERCENT=130;
    public static final int MIN_PERCENT=75,MAX_PERCENT=200;
    public static float multiplier(int percent){
        return Math.max(MIN_PERCENT,Math.min(MAX_PERCENT,percent))/100f;
    }
    public static float speed(float weaponBase,float multiplier,float runFactor,boolean crouch){
        return weaponBase*multiplier*runFactor*(crouch?.53f:1f);
    }
    public static float gait(float multiplier,boolean running){
        // Animation follows stride speed; do not alter the original sprite frames.
        return (running?9.7f:8.2f)*multiplier;
    }
}
