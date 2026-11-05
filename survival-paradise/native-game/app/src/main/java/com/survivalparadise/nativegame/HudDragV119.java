package com.survivalparadise.nativegame;

/** Safe HUD editor dispatch independent of original gameplay action indexing. */
public final class HudDragV119 {
    private HudDragV119(){}
    public static boolean isLegacyAction(int id,int count) {
        return id>=0&&id<count;
    }
    /** Contextual TALK and top HUD are not LegacyControlsV58 defaults. */
    public static boolean isSeparateControl(int id,int legacyCount){
        return id>=legacyCount;
    }
    /** Preserve the grab point when starting drag; prevent 1st-frame jumping. */
    public static float grabOffset(float pointer,float visibleLeft){
        return pointer-visibleLeft;
    }
    public static int horizontalOffset(float pointer,float grabbedOffset,
                                       float originalLeft,float width,float screenWidth) {
        float requested=pointer-grabbedOffset-originalLeft;
        float min=-originalLeft;
        float max=Math.max(min,screenWidth-originalLeft-width);
        return Math.round(Math.max(min,Math.min(max,requested)));
    }
    public static int verticalOffset(float pointer,float grabbedOffset,
                                     float originalTop,float height,float screenHeight) {
        float requested=pointer-grabbedOffset-originalTop;
        float min=-originalTop;
        float max=Math.max(min,screenHeight-originalTop-height);
        return Math.round(Math.max(min,Math.min(max,requested)));
    }
}
