package com.survivalparadise.nativegame;

/**
 * V112 additive user calibration on top of each approved V5 head placement.
 * Source coordinates are the exact 200x260 character sheet coordinates.
 * Zero means precisely the approved V5 fitting, including all 51 overrides.
 * No source bitmap, body, walking pose, neck pivot or weapon rig is changed.
 */
public final class HeadFitOffsetsV112 {
    public static final int OFFSET_MIN=-24,OFFSET_MAX=24;
    private HeadFitOffsetsV112(){}

    public static int clampOffset(int offset){
        return Math.max(OFFSET_MIN,Math.min(OFFSET_MAX,offset));
    }
    /** The approved V5 X fit is never overwritten; user offset is additive. */
    public static int x(int headWidth,int approvedHorizontal,int userHorizontal){
        return Math.round((200f-headWidth)*.5f+approvedHorizontal+10f+
            clampOffset(userHorizontal));
    }
    /** Preserves the V110 smooth, independent head-only breathing offset. */
    public static int y(int headHeight,int approvedVertical,float breath,int userVertical){
        return Math.round(200f-headHeight+approvedVertical-3f+breath+
            clampOffset(userVertical));
    }
}
