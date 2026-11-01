package com.survivalparadise.nativegame;

/**
 * V82 geometry-only visual polish. Original approved sprite pixels stay unchanged:
 * head crop exactly ends where shirt starts, and knife arc becomes a short line.
 */
public final class HeadKnifeV82 {
    private HeadKnifeV82(){}
    public static final int HEAD_TOP=20,HEAD_BOTTOM=92,HEAD_LEFT=24,HEAD_RIGHT=110;
    public static final int HEAD_PIVOT_X=70,HEAD_PIVOT_Y=92;
    public static final int HEAD_MIN=75,HEAD_MAX=160,HEAD_DEFAULT=100;
    public static final float KNIFE_SIZE=1.55f;
    public static final float KNIFE_TRAIL_LENGTH=22f;
    public static final float MELEE_SWEEP_DEGREES=54f; // 27 each side, not 144
    public static float headMultiplier(int percent){
        return Math.max(HEAD_MIN,Math.min(HEAD_MAX,percent))/100f;
    }
    public static boolean defaultHead(float h){return Math.abs(h-1f)<.0001f;}
    public static float headLeft(float s,float h){
        return (HEAD_LEFT-HEAD_PIVOT_X)*s*h;
    }
    public static float headRight(float s,float h){
        return (HEAD_RIGHT-HEAD_PIVOT_X)*s*h;
    }
    public static float headBottom(float s,float bob){
        return (HEAD_BOTTOM-136)*s+bob;
    }
    public static float headTop(float s,float h,float bob){
        return headBottom(s,bob)-(HEAD_BOTTOM-HEAD_TOP)*s*h;
    }
    public static float sweep(float progress){
        float p=Math.max(0f,Math.min(1f,progress));
        float eased=p*p*(3f-2f*p);
        return (eased-.5f)*MELEE_SWEEP_DEGREES;
    }
    public static float localBearing(int knifeDirection,int face){
        float bearing=knifeDirection*45f;
        return face<0?180f-bearing:bearing;
    }
}
