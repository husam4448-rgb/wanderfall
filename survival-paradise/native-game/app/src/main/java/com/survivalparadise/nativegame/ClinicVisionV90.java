package com.survivalparadise.nativegame;
/** Visibility cone follows the true aiming vector and stops at room solids. */
public final class ClinicVisionV90 {
    public static final int RAYS=49;
    public static final float HALF_ANGLE=1.12f,RANGE=655f,NEAR=98f;
    public final float[] xs=new float[RAYS],ys=new float[RAYS];
    public int blockedRays;
    public void trace(float px,float py,float dx,float dy,ClinicInteriorV89 map){
        double dir=Math.atan2(dy,dx);
        blockedRays=0;
        for(int i=0;i<RAYS;i++){
            double angle=dir-HALF_ANGLE+2*HALF_ANGLE*i/(RAYS-1);
            float vx=(float)Math.cos(angle),vy=(float)Math.sin(angle);
            float distance=RANGE;
            for(float d=NEAR;d<=RANGE;d+=17f){
                if(map.blocked(px+vx*d,py+vy*d,4)){
                    distance=Math.max(NEAR,d-17);
                    blockedRays++;break;
                }
            }
            xs[i]=px+vx*distance;ys[i]=py+vy*distance;
        }
    }
    public boolean visible(float px,float py,float dx,float dy,
                           float tx,float ty,ClinicInteriorV89 map){
        float x=tx-px,y=ty-py,d=(float)Math.hypot(x,y);
        if(d<=NEAR)return true;
        float dot=(x*dx+y*dy)/Math.max(.01f,d*(float)Math.hypot(dx,dy));
        if(dot<(float)Math.cos(HALF_ANGLE)||d>RANGE)return false;
        return ClinicActorsV90.lineOfSight(map,px,py,tx,ty);
    }
}
