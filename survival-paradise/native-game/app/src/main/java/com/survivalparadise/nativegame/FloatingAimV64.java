package com.survivalparadise.nativegame;

/** Pure-Java V64 analog-stick to mouse-pointer response. No Android dependency. */
public final class FloatingAimV64 {
    private FloatingAimV64() {}

    static float clamp(float value,float lower,float upper){
        return Math.max(lower,Math.min(upper,value));
    }

    /** Returns signed-stick velocity magnitude in [0,1]. Zero inside deadzone. */
    public static float response(float stickMagnitude,float deadzone,float curve){
        float dead=clamp(deadzone,0f,.40f);
        float normalized=clamp((stickMagnitude-dead)/(1f-dead),0f,1f);
        return (float)Math.pow(normalized,clamp(curve,.6f,2.5f));
    }

    /** Keep full-screen traversal comparable across Android aspect ratios and zoom. */
    public static float scaledSpeed(float userPixelsPerSecond,float visibleWorldWidth){
        float factor=clamp(visibleWorldWidth/1300f,.65f,2.2f);
        return clamp(userPixelsPerSecond,200f,10000f)*factor;
    }

    /** Smooth 0→1 camera drive when a moving pointer approaches the indicated edge. */
    public static float edgeStrength(float pointerScreen,float screenWidth,
                                     float edgeMargin,float signedVelocity){
        if(Math.abs(signedVelocity)<.00001f)return 0f;
        float distance=signedVelocity>0f?screenWidth-pointerScreen:pointerScreen;
        return clamp((edgeMargin-distance)/Math.max(1f,edgeMargin),0f,1f);
    }
}
