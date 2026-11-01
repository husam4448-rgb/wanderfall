package com.survivalparadise.nativegame;
/** Fixed visual HUD geometry and stable target point for V86 aim-to-place. */
public final class WorldUiV86 {
    private WorldUiV86(){}
    public static final float BAG_W=130f,BAG_H=52f,BAG_Y_OFFSET=395f;
    public static final float PLACE_MIN=95f,PLACE_MAX=345f;
    public static float bagX(float viewW){return viewW-190f-BAG_W*.5f;}
    public static float bagY(float viewH){return Math.max(72f,viewH-BAG_Y_OFFSET);}
    public static boolean bagHit(float x,float y,float width,float height){
        float l=bagX(width),t=bagY(height);
        return x>=l&&x<=l+BAG_W&&y>=t&&y<=t+BAG_H;
    }
    public static float placeDistance(float cursorDistance){
        return Math.max(PLACE_MIN,Math.min(PLACE_MAX,cursorDistance));
    }
    public static float targetX(float playerX,float aimX,float cursorDistance){
        return playerX+aimX*placeDistance(cursorDistance);
    }
    public static float targetY(float playerY,float aimY,float cursorDistance){
        return playerY-42f+aimY*placeDistance(cursorDistance);
    }
}
