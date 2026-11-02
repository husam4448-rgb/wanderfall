package com.survivalparadise.nativegame;

/** Pure geometry: V97 approved overlays use the torso and actual head pivot.
 * Coordinates are relative to V31's immutable character origin and 136px baseline.
 */
public final class WearableFitV97 {
    private WearableFitV97(){}
    // Backpack high enough for upper back yet never intersects the hair or legs.
    // Right-facing rear pack occupies the character's left/rear silhouette.
    public static float[] packBounds(float characterScale){
        float s=Math.max(.01f,characterScale);
        return new float[]{-55f*s,-92f*s,-24f*s,-29f*s};
    }
    // Helmet-specific top, bottom and width relative to the neckline at y=-44.
    // Eyes are left visible for helmets/visors; covered deliberately by masks.
    private static final float[] TOP={-120f,-132f,-127f,-129f};
    private static final float[] BOTTOM={-52f,-95f,-54f,-43f};
    private static final float[] HALF_WIDTH={40f,45f,44f,47f};
    public static float[] headBounds(int headgear,float characterScale,
            float headMultiplier,float breathingBob){
        int i=Math.floorMod(headgear,4);
        float s=Math.max(.01f,characterScale);
        float h=Math.max(.75f,Math.min(1.60f,headMultiplier));
        float centerX=-3f*s;
        float neckline=-44f*s+breathingBob;
        return new float[]{
            centerX-HALF_WIDTH[i]*s*h,
            neckline+(TOP[i]+44f)*s*h,
            centerX+HALF_WIDTH[i]*s*h,
            neckline+(BOTTOM[i]+44f)*s*h
        };
    }
}
