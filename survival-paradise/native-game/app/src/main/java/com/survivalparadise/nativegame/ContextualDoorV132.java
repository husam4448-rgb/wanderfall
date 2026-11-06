package com.survivalparadise.nativegame;

/**
 * V132 contextual building door behavior. Pure geometry and visibility rules:
 * the button appears only beside an entrance/exit (or in HUD edit mode).
 * Legacy USE/INTERACT gameplay never invokes a doorway transition.
 */
public final class ContextualDoorV132 {
    private ContextualDoorV132(){}
    public static final float INDUSTRIAL_RADIUS=152f;
    public static final float FIXED_RADIUS=108f;
    public static final float SHELTER_RADIUS=112f;
    public static final float EXIT_RADIUS=110f;

    public static boolean near(float x,float y,float targetX,float targetY,float radius){
        if(!Float.isFinite(x)||!Float.isFinite(y)||
           !Float.isFinite(targetX)||!Float.isFinite(targetY)||
           radius<=0f)return false;
        float dx=x-targetX,dy=y-targetY;
        return dx*dx+dy*dy<radius*radius;
    }
    public static boolean fixedDoor(float x,float y,float siteX,
                                    float siteY,boolean clinic){
        return near(x,y,siteX,siteY+(clinic?154f:90f),FIXED_RADIUS);
    }
    public static boolean shelterDoor(float x,float y,float shelterX,float shelterY){
        return near(x,y,shelterX,shelterY+42f,SHELTER_RADIUS);
    }
    public static boolean indoorExit(float x,float y,float exitX,float exitY){
        return near(x,y,exitX,exitY,EXIT_RADIUS);
    }
    public static boolean visible(boolean editing,boolean playing,
                                  boolean paused,boolean dead,
                                  boolean enabled,boolean doorNear){
        if(editing)return true;
        return playing&&!paused&&!dead&&enabled&&doorNear;
    }
}
