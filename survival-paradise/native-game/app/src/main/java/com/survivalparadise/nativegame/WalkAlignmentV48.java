package com.survivalparadise.nativegame;

/**
 * V48 render-only x-anchor correction for the approved 4-frame walking atlas.
 * The source frame silhouette offsets are 16,20,24,20, despite identical
 * world-space torso and weapon pivots. Never change the original PNG data.
 */
public final class WalkAlignmentV48 {
    private WalkAlignmentV48(){}
    public static final int[] WALK_SOURCE_OFFSETS_X={4,0,-4,0};
    public static final float BASE_CHARACTER_SCALE=.76f;
    public static int sourceOffsetX(int frame){
        return WALK_SOURCE_OFFSETS_X[Math.max(0,Math.min(3,frame))];
    }
    public static float worldOffsetX(int frame,int facing,float characterScale){
        return sourceOffsetX(frame)*BASE_CHARACTER_SCALE*characterScale*(facing<0?-1f:1f);
    }
}
