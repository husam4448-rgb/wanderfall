package com.survivalparadise.nativegame;

/**
 * V114 original V109 source atlas has 200x260 pixels.
 * The upper torso occupies y=160..179 (20 source pixels), while
 * pants and legs begin at y=180. This data was verified directly
 * against all four walk poses and the approved idle pose.
 *
 * Narrow only the torso X extent about the center; NO scaling or
 * recoloring of any pixel in y>=180, including feet and moving legs.
 */
public final class TorsoWidthV114 {
    public static final int MIN_PERCENT=55;
    public static final int MAX_PERCENT=100;
    public static final int DEFAULT_PERCENT=100;
    public static final int SPRITE_WIDTH=200;
    public static final int TORSO_TOP=160;
    public static final int LOWER_BODY_TOP=180;
    public static final int SPRITE_HEIGHT=260;

    private TorsoWidthV114(){}

    public static int percent(int requested) {
        return Math.max(MIN_PERCENT,Math.min(MAX_PERCENT,requested));
    }
    /** Symmetric source-space margin from x=0 and x=200. */
    public static float margin(int requested){
        return (SPRITE_WIDTH*(1f-percent(requested)/100f))*0.5f;
    }
    public static float left(float bodyLeft,float pixelsPerUnit,int requested) {
        return bodyLeft+margin(requested)*pixelsPerUnit;
    }
    public static float right(float bodyLeft,float pixelsPerUnit,int requested) {
        return bodyLeft+(SPRITE_WIDTH-margin(requested))*pixelsPerUnit;
    }
    public static boolean isUnchangedLowerBody(int y) {
        return y>=LOWER_BODY_TOP&&y<SPRITE_HEIGHT;
    }
}
