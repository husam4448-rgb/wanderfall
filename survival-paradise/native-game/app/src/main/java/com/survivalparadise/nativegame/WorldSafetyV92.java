package com.survivalparadise.nativegame;
/** Stable collision-safe outdoor portals and protected starting settlement. */
public final class WorldSafetyV92 {
    private WorldSafetyV92(){}
    public static final float CAMP_SAFE_RADIUS=780f;
    public interface Collision { boolean blocked(float x,float y,float radius); }
    public static boolean safe(Collision collision,float x,float y){
        if(collision.blocked(x,y,24f))return false;
        // A valid door must open into a usable walking corridor.
        int accessible=0;
        for(int i=0;i<8;i++){
            float angle=(float)(i*Math.PI/4);
            if(!collision.blocked(x+(float)Math.cos(angle)*60f,
                    y+(float)Math.sin(angle)*60f,20f))accessible++;
        }
        return accessible>=5;
    }
    /** Prefer the actual front-of-door landing; expand outward to unblocked ground. */
    public static float[] resolveExit(Collision collision,float x,float y){
        for(int radius=0;radius<=680;radius+=44){
            int steps=radius==0?1:32;
            for(int j=0;j<steps;j++){
                float theta=(float)(j*Math.PI*2/steps);
                float xx=x+(float)Math.cos(theta)*radius;
                float yy=y+(float)Math.sin(theta)*radius;
                if(safe(collision,xx,yy))return new float[]{xx,yy};
            }
        }
        return new float[]{x,y};
    }
    public static boolean hostileAllowed(float x,float y,float campX,float campY){
        float dx=x-campX,dy=y-campY;
        return dx*dx+dy*dy>=CAMP_SAFE_RADIUS*CAMP_SAFE_RADIUS;
    }
}