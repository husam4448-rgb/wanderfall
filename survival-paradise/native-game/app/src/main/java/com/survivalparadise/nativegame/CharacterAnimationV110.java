package com.survivalparadise.nativegame;

/**
 * V110 visual animation timing for the exact V109 200-character compositor.
 * Timing only: never modifies locked sprites, body pixels, collisions or movement.
 */
public final class CharacterAnimationV110 {
    public static final int BREATH_MIN_PERCENT=25;
    public static final int BREATH_MAX_PERCENT=250;
    public static final int BREATH_DEFAULT_PERCENT=100;

    private CharacterAnimationV110() {}

    public static float breathingMultiplier(int percent) {
        return Math.max(BREATH_MIN_PERCENT,Math.min(BREATH_MAX_PERCENT,percent))/100f;
    }

    /**
     * 0 is the planted idle body. 1..4 select the exact four approved walk poses.
     * The V5 per-character fps is the default to preserve V109's appearance;
     * the old experimental fixed-fps preference is an optional base-rate override.
     * The animation-speed slider ALWAYS scales either base rate, even when the
     * fixed-fps preference is selected.
     */
    public static int bodyFrame(boolean walking,float timeSeconds,int fittedFps,
                                int fixedFps,float walkingMultiplier) {
        if(!walking)return 0;
        float baseFps=fixedFps>0?
            Math.max(1,Math.min(12,fixedFps)):Math.max(1,Math.min(12,fittedFps));
        float speed=Math.max(.5f,Math.min(2f,walkingMultiplier));
        float phase=(timeSeconds*baseFps*speed)%4f;
        if(phase<0f)phase+=4f;
        return 1+(int)Math.floor(phase);
    }

    /** Smooth head-only breathing; returns source pixels, without touching body. */
    public static float breathOffset(boolean walking,float timeSeconds,float amplitude,
                                     float breathingMultiplier) {
        if(walking||amplitude<=0)return 0f;
        float speed=Math.max(.25f,Math.min(2.5f,breathingMultiplier));
        return (float)Math.sin(timeSeconds*4f*speed)*Math.min(36f,amplitude);
    }
}
