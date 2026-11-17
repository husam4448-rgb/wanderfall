package com.survivalparadise.nativegame;

/**
 * V150 procedural reload pose, evaluated against the existing 1.25s reload
 * clock. Only the APPROVED weapon and hand drawing transforms are changed.
 * Heads, torso, legs, feet, color atlases, muzzle physics and saves are intact.
 */
public final class ReloadPoseV150 {
    public static final float DURATION=1.25f;
    private ReloadPoseV150(){}

    public static boolean active(float remaining,int weapon){
        return remaining>0f&&weapon>=0&&weapon<11&&weapon!=3;
    }

    /** Progress starts at zero and reaches one exactly as reloading completes. */
    public static float progress(float remaining){
        return clamp01(1f-remaining/DURATION);
    }
    private static float clamp01(float x){
        return Math.max(0f,Math.min(1f,x));
    }
    private static float smooth(float t){
        t=clamp01(t);
        return t*t*(3f-2f*t);
    }
    /** One rise / hold / fall envelope. Never jumps at the end. */
    private static float envelope(float phase,float upEnd,float downStart){
        if(phase<=0f||phase>=1f)return 0f;
        if(phase<upEnd)return smooth(phase/upEnd);
        if(phase<downStart)return 1f;
        return 1f-smooth((phase-downStart)/(1f-downStart));
    }
    /** The firearm pivots below the aim line to expose its receiver. */
    public static float rotateDegrees(float remaining,int weapon){
        if(!active(remaining,weapon))return 0f;
        float drop=(weapon<=2?31f:weapon==7?24f:27f);
        return drop*envelope(progress(remaining),.20f,.77f);
    }
    /** Move the ENTIRE gun + gripping hand closer to the chest and down. */
    public static float lowerPx(float remaining,int weapon){
        return active(remaining,weapon)?
            8f*envelope(progress(remaining),.20f,.77f):0f;
    }
    public static float pullBackPx(float remaining,int weapon){
        return active(remaining,weapon)?
            -7f*envelope(progress(remaining),.20f,.77f):0f;
    }
    /** Support hand leaves the fore-end, reaches the receiver and returns. */
    public static float supportReachPx(float remaining,int weapon){
        if(!active(remaining,weapon)||weapon<=3||weapon==10)return 0f;
        return -29f*envelope(progress(remaining),.37f,.62f);
    }
    public static float supportDownPx(float remaining,int weapon){
        if(!active(remaining,weapon)||weapon<=3||weapon==10)return 0f;
        return 15f*envelope(progress(remaining),.37f,.62f);
    }
}
