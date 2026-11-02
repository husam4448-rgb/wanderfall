package com.survivalparadise.nativegame;

/** V98 fit geometry in the canonical head frame; original body atlas is untouched. */
public final class WearableFitV98 {
    private WearableFitV98(){}
    // Source HeadKnifeV82 frame: x24..110, y20..92, pivot 70,92; body origin y136.
    private static final float[] LEFT={-38f,-45f,-43f,-45f};
    private static final float[] RIGHT={35f,42f,40f,42f};
    private static final float[] TOP={-117f,-120f,-119f,-120f};
    private static final float[] BOTTOM={-46f,-93f,-65f,-44f};
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
        if(x<43||x>108||y<92||y>109||(pixel>>>24)<220)return false;
        int r=(pixel>>>16)&255,g=(pixel>>>8)&255,b=pixel&255;
        // Protect near-black pixel outlines and skin/face/pants shades.
        if(Math.max(r,Math.max(g,b))<48)return false;
        if(r>g*1.13f && g>b*1.08f)return false;
        return true;
    }
    public static boolean palettePixel(int pixel){
        return (pixel>>>24)>=220 &&
            Math.max((pixel>>>16)&255,Math.max((pixel>>>8)&255,pixel&255))>=48;
    }
    /** Approved clothing colors are copied from existing V56 NPC role color atlases. */
    public static int sourceRole(int outfit){return new int[]{2,7,10}[Math.floorMod(outfit,3)];}
}
