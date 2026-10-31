package com.survivalparadise.nativegame;

/**
 * V79 adjustable player gait: default 100% retains V77's stride-speed
 * synchronization; only the walk-frame clock changes, never velocity,
 * idle breathing, original 4-frame artwork, or NPC movement.
 */
public final class WalkingAnimationV79 {
    private WalkingAnimationV79(){}
    public static final int MIN_PERCENT=50,MAX_PERCENT=200,DEFAULT_PERCENT=100;

    public static float multiplier(int percent){
        return Math.max(MIN_PERCENT,Math.min(MAX_PERCENT,percent))/100f;
    }

    public static float rate(float movementLinkedRate,int gaitPercent){
        return movementLinkedRate*multiplier(gaitPercent);
    }
}
