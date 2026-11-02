package com.survivalparadise.nativegame;

/** V100 visual-only prototype, coordinates mapped to the immutable V31 head.
 * Head pivot is (70,92), rendering origin (70,136). Each attachment shares
 * the player's or NPC's head-size multiplier, including idle head bob.
 */
public final class HeadgearFitV100 {
    private HeadgearFitV100(){}
    // Gas mask / combat helmet / riot visor / full hazmat hood.
    private static final float[] LEFT={-54f,-48f,-47f,-49f};
    private static final float[] RIGHT={50f,46f,45f,47f};
    private static final float[] TOP={-119f,-129f,-128f,-130f};
    private static final float[] BOTTOM={-36f,-86f,-51f,-40f};
    public static float[] bounds(int type,float scale,float actualHeadSize,float bob){
        int i=Math.floorMod(type,4);
        float s=Math.max(.001f,scale);
        float h=Math.max(.75f,Math.min(1.6f,actualHeadSize));
        float pivot=-44f*s+bob;
        return new float[]{LEFT[i]*s*h,pivot+(TOP[i]+44f)*s*h,
            RIGHT[i]*s*h,pivot+(BOTTOM[i]+44f)*s*h};
    }
}
