package com.survivalparadise.nativegame;

/**
 * Side-facing 2D aim pitch mapped to a small, neck-anchored head rotation.
 * The original head bitmap, V5 per-character fits, body, and weapon rig
 * are not modified. The parent Canvas handles left/right mirroring.
 */
public final class HeadAimV111 {
    public static final int DEFAULT_MAX_DEGREES=10;
    public static final int MAX_DEGREES=15;
    private static final float FULL_TILT_PITCH_RADIANS=(float)(Math.PI/4.0);
    private static final float EASE_PER_SECOND=11f;
    private HeadAimV111(){}

    public static int limit(int maxDegrees) {
        return Math.max(0,Math.min(MAX_DEGREES,maxDegrees));
    }
    /** Upward aim is negative, downward aim positive, regardless of facing. */
    public static float targetDegrees(float pitchRadians,int maxDegrees) {
        if(!Float.isFinite(pitchRadians))return 0f;
        float pitch=Math.max(-1f,Math.min(1f,pitchRadians/FULL_TILT_PITCH_RADIANS));
        return pitch*limit(maxDegrees);
    }
    /** Smoothing is stable across refresh rates and clamps long frame gaps. */
    public static float follow(float current,float target,float dt) {
        if(!Float.isFinite(current)||!Float.isFinite(target))return 0f;
        float delta=Math.max(0f,Math.min(.10f,dt));
        float blend=1f-(float)Math.exp(-EASE_PER_SECOND*delta);
        float next=current+(target-current)*blend;
        return Math.max(-MAX_DEGREES,Math.min(MAX_DEGREES,next));
    }
    /** Rotation pivot stays on the fitted neckline; no body transform. */
    public static float neckX(float headLeft,float headWidth) {
        return headLeft+headWidth*.5f;
    }
    public static float neckY(float headBottom,float bodyUnit) {
        return headBottom-4f*bodyUnit;
    }
}
