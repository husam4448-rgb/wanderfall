package com.survivalparadise.nativegame;

/** Independent persistent squad orders; no NPC art/skeleton changes. */
public final class CompanionOrdersV118 {
    public static final int MIN_SPACING=70,MAX_SPACING=450,DEFAULT_SPACING=125;
    private CompanionOrdersV118(){}
    public static int spacing(int requested){
        return Math.max(MIN_SPACING,Math.min(MAX_SPACING,requested));
    }
    public static boolean mayMove(boolean stay){return !stay;}
    public static boolean mayShoot(boolean holdFire){return !holdFire;}
    /** Non-teleporting followers settle into individual formation slots. */
    public static float targetX(float px,float fx,float fy,int mode,int index,int count,int spacing){
        return FollowFormationV61.targetX(px,fx,fy,mode,index,count,spacing(spacing));
    }
    public static float targetY(float py,float fx,float fy,int mode,int index,int count,int spacing){
        return FollowFormationV61.targetY(py,fx,fy,mode,index,count,spacing(spacing));
    }
}
