package com.survivalparadise.nativegame;

/** Deterministic formation slots, world-space and independent of frame rate. */
public final class FollowFormationV61 {
    private FollowFormationV61(){}
    public static final int SCATTER=0,SQUARE=1,CARAVAN=2,LINE=3,RANDOM=4;
    public static final String[] NAMES={"Scattered","Square","Caravan","Line (90°)","Wide random"};
    // Return relative (sideways, rearward) formation coordinates. Player at origin.
    public static float side(int mode,int index,int count,int spacing){
        int i=Math.max(0,index);
        float s=Math.max(52,spacing);
        switch(mode){
            case SQUARE: return (i%3-1)*s;
            case CARAVAN: return (i%2==0?-.36f:.36f)*s;
            case LINE: return (i-(count-1)/2f)*s;
            case RANDOM: return jitter(i,13)*2.1f*s;
            default: return (i%2==0?-1f:1f)*(1f+i/2*.42f)*s;
        }
    }
    public static float rear(int mode,int index,int count,int spacing){
        int i=Math.max(0,index);
        float s=Math.max(52,spacing);
        switch(mode){
            case SQUARE:return (1+i/3)*s;
            case CARAVAN:return (i+1)*s;
            case LINE:return 1.2f*s;
            case RANDOM:return (i+1)*s*1.35f+jitter(i,77)*s*.18f;
            default:return (1f+i/2*.55f)*s;
        }
    }
    private static float jitter(int idx,int salt){
        int k=(idx+1)*73856093^(salt*19349663);
        k^=k>>>13;k*=0x5bd1e995;k^=k>>>15;
        return Math.floorMod(k,1001)/500f-1f;
    }
    /** forwardX/Y are player travel heading; side is 90 degrees clockwise. */
    public static float targetX(float px,float fx,float fy,int mode,int index,int count,int spacing){
        return px-fx*rear(mode,index,count,spacing)-fy*side(mode,index,count,spacing);
    }
    public static float targetY(float py,float fx,float fy,int mode,int index,int count,int spacing){
        return py-fy*rear(mode,index,count,spacing)+fx*side(mode,index,count,spacing);
    }
}
