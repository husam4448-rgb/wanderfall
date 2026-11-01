package com.survivalparadise.nativegame;
/** Allocation-free finite-state decision helper. Inputs are world distances in px. */
public final class BanditBrainV88 {
    private BanditBrainV88(){}
    public static final int PATROL=0,CHASE=1,STRAFE=2,RETREAT=3,GUARD=4;
    public static final float ALERT_RANGE=590f,FIRE_RANGE=330f,STOP_DISTANCE=215f;
    public static int state(float distance,float hp,boolean hasCover){
        if(hp<24&&distance<420)return RETREAT;
        if(distance>ALERT_RANGE)return PATROL;
        if(distance>FIRE_RANGE)return CHASE;
        return hasCover?GUARD:STRAFE;
    }
    public static float speed(int mode){
        return mode==RETREAT?125f:mode==CHASE?108f:mode==PATROL?54f:72f;
    }
    public static float moveX(int mode,float dirX,float dirY,int side){
        if(mode==RETREAT)return -dirX;
        if(mode==CHASE)return dirX;
        if(mode==STRAFE)return -dirY*side;
        if(mode==GUARD)return 0f;
        return dirX;
    }
    public static float moveY(int mode,float dirX,float dirY,int side){
        if(mode==RETREAT)return -dirY;
        if(mode==CHASE)return dirY;
        if(mode==STRAFE)return dirX*side;
        if(mode==GUARD)return 0f;
        return dirY;
    }
    public static boolean shouldShoot(int mode,float distance,float cooldown,
                                      boolean unobstructed){
        return cooldown<=0&&distance<=FIRE_RANGE&&unobstructed&&
            (mode==STRAFE||mode==GUARD||mode==RETREAT);
    }
}
