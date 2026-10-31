package com.survivalparadise.nativegame;

/** Small, strictly bounded aim-look camera displacement, independent of weapon range. */
public final class BoundedCameraV69 {
    private BoundedCameraV69(){}

    /**
     * A hard maximum in WORLD units, also bounded by a small visible-screen
     * fraction. Zoom reduces world movement, not the visible character safety.
     */
    public static float limit(float preference,float screenWidth,float screenHeight,float zoom){
        float boundedPreference=Math.max(0f,Math.min(180f,preference));
        float visibleWorldHeight=Math.max(1f,Math.min(screenWidth,screenHeight))/
                                 Math.max(.1f,zoom);
        return Math.min(boundedPreference,visibleWorldHeight*.12f);
    }

    /** Camera starts to look ahead only when the reticle exceeds safe viewport area. */
    public static float beyondMargin(float cursorOffset,float halfVisible){
        float edge=Math.max(0f,halfVisible);
        return cursorOffset-Math.max(-edge,Math.min(edge,cursorOffset));
    }

    /** Factor for normalizing diagonal displacement into a strict circular limit. */
    public static float radialFactor(float x,float y,float maximum){
        float range=(float)Math.hypot(x,y);
        float cap=Math.max(0f,maximum);
        return range>cap && range>.0001f?cap/range:1f;
    }
}
