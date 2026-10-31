package com.survivalparadise.nativegame;

/**
 * Original analog aiming restored from V61: the stick's POSITION controls
 * aiming direction and marker distance immediately. No timed extension,
 * cursor acceleration, smoothing stages or three-zone control.
 */
public final class ClassicAimV71 {
    public static final float DEADZONE=.12f;
    public static final float TRAVEL=205f; // V61 range: 130..335 world px
    private ClassicAimV71() {}

    public static float distance(float rest,float bulletMax,float deflection) {
        float capped=Math.min(1f,Math.max(0f,deflection));
        if(capped<=DEADZONE)return rest;
        return Math.min(bulletMax,rest+TRAVEL*capped);
    }
    public static float heading(float axis,float magnitude,float previous){
        return magnitude>DEADZONE?axis/Math.max(.001f,magnitude):previous;
    }
    public static float thumb(float axis,float rawMagnitude){
        return rawMagnitude>.00001f?axis/Math.max(1f,rawMagnitude):0f;
    }
    /** Circular pan proportional to stick extension ONLY when explicitly enabled. */
    public static float panFactor(float magnitude,float threshold){
        float start=Math.min(.90f,Math.max(.20f,threshold));
        return Math.max(0f,Math.min(1f,(magnitude-start)/(1f-start)));
    }
}
