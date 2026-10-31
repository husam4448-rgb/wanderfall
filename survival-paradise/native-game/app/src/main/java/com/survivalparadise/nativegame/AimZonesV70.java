package com.survivalparadise.nativegame;

/**
 * V70 two physically separate analog zones:
 * center/middle = aim direction at weapon rest, outer ring = extend range,
 * final rim = deliberate radial camera look-around. No timed auto acceleration.
 */
public final class AimZonesV70 {
    public static final float EXTENSION_START=.62f;
    public static final float PAN_START=.90f;
    private AimZonesV70(){}

    public static float clamp(float n,float lo,float hi){
        return Math.max(lo,Math.min(hi,n));
    }

    public static float extendFactor(float stick){
        return clamp((stick-EXTENSION_START)/(PAN_START-EXTENSION_START),0f,1f);
    }

    public static float panFactor(float stick){
        float t=clamp((stick-PAN_START)/(1f-PAN_START),0f,1f);
        return t*t*(3f-2f*t);
    }

    /** Changing aim direction never extends the crosshair inside inner stick zone. */
    public static float reach(float previous,float rest,float actualBulletMax,
                              float stick,float speed,float dt){
        if(stick<=EXTENSION_START) return rest;
        float bounded=Math.max(rest,Math.min(previous,actualBulletMax));
        float travel=clamp(speed,0f,2400f)*extendFactor(stick)*Math.max(0f,dt);
        return Math.min(actualBulletMax,Math.max(rest,bounded+travel));
    }

    /** A CIRCLE, not a viewport-dependent ellipse or independently clamped axes. */
    public static float panX(float dirX,float dirY,float radius,float stick){
        float length=(float)Math.hypot(dirX,dirY);
        if(length<.00001f)return 0f;
        return dirX/length*Math.max(0f,radius)*panFactor(stick);
    }
    public static float panY(float dirX,float dirY,float radius,float stick){
        float length=(float)Math.hypot(dirX,dirY);
        if(length<.00001f)return 0f;
        return dirY/length*Math.max(0f,radius)*panFactor(stick);
    }
}
