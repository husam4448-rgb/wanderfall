package com.survivalparadise.nativegame;

/** V99 visual-review fit geometry. Head and body source pixels stay immutable. */
public final class WearableFitV98 {
    private WearableFitV98(){}
    // Source HeadKnifeV82 frame: x24..110, y20..92, pivot 70,92; body origin y136.
    private static final float[] LEFT={-46f,-46f,-46f,-46f};
    private static final float[] RIGHT={40f,42f,42f,42f};
    private static final float[] TOP={-121f,-123f,-120f,-120f};
    private static final float[] BOTTOM={-44f,-95f,-59f,-42f};
    public static float[] head(int type,float scale,float headMultiplier,float bob){
        int i=Math.floorMod(type,4);
        float h=Math.max(.75f,Math.min(1.60f,headMultiplier));
        float s=Math.max(.01f,scale);
        float center=-3f*s;
        float pivot=-44f*s+bob;
        return new float[]{center+(LEFT[i]+3f)*s*h,
            pivot+(TOP[i]+44f)*s*h,
            center+(RIGHT[i]+3f)*s*h,
            pivot+(BOTTOM[i]+44f)*s*h};
    }
    public static boolean torsoPixel(int x,int y,int pixel){
        if(x<33||x>104||y<92||y>109||(pixel>>>24)<220)return false;
        int r=(pixel>>>16)&255,g=(pixel>>>8)&255,b=pixel&255;
        // The approved V31 body has the whole shirt between rows 92–109.
        // Skin ends above it and trousers begin at row 110. Color is NOT an
        // exclusion criterion: several approved shirts are orange/red.
        // All original near-black outline pixels remain immutable.
        return Math.max(r,Math.max(g,b))>=48;
    }
    public static boolean palettePixel(int pixel){
        return (pixel>>>24)>=220 &&
            Math.max((pixel>>>16)&255,Math.max((pixel>>>8)&255,pixel&255))>=48;
    }
    /** Approved clothing colors are copied from existing V56 NPC role color atlases. */
    public static int sourceRole(int outfit){return new int[]{2,7,10}[Math.floorMod(outfit,3)];}
}
