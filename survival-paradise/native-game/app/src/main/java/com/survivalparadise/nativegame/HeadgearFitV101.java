package com.survivalparadise.nativegame;

/** Pure attachment geometry for V31, no body/head source modification. */
public final class HeadgearFitV101 {
    private HeadgearFitV101() {}
    public static final int FRAME_WIDTH=144,FRAME_HEIGHT=128,PIXEL_STEP=9;
    public static final int[] COLUMNS={12,10,10,12};
    public static final int[] ROWS={10,6,9,10};
    public static final int[] X={15,24,24,15};
    public static final int[] Y={11,11,11,11};
    /** [left,top,right,bottom] in actor-local drawing coordinates. */
    public static float[] bounds(float characterScale,float headMultiplier,float idleBob){
        float s=Math.max(.001f,characterScale);
        float h=Math.max(.75f,Math.min(1.60f,headMultiplier));
        float pivot=-44f*s+idleBob;
        return new float[]{-70f*s*h,pivot-92f*s*h,
            (FRAME_WIDTH-70f)*s*h,pivot+(FRAME_HEIGHT-92f)*s*h};
    }
}
