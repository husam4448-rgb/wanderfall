package com.survivalparadise.nativegame;
/** Stateless light geometry: no rendering dependencies, suitable for deterministic QA. */
public final class LightGeometryV45 {
    private LightGeometryV45(){}
    public static boolean inCone(float ox,float oy,float dx,float dy,float x,float y,
                                 float reach,float halfAngle){
        float xx=x-ox,yy=y-oy,dist=(float)Math.hypot(xx,yy);
        if(dist>reach)return false;
        if(dist<.0001f)return true;
        float n=(float)Math.hypot(dx,dy);
        if(n<.0001f)return false;
        return (xx*dx+yy*dy)/(dist*n)>=(float)Math.cos(halfAngle);
    }
    /** Length to first opaque box along a ray, shortened by a two-pixel contact margin. */
    public static float rayBox(float x,float y,float dx,float dy,float maxRange,
                               float left,float top,float right,float bottom){
        float n=(float)Math.hypot(dx,dy);
        if(n<.00001f)return 0;
        float x1=x+dx/n*maxRange,y1=y+dy/n*maxRange;
        float intersection=Ballistics.segmentBox(x,y,x1,y1,left,top,right,bottom);
        if(!Float.isFinite(intersection))return maxRange;
        return Math.min(maxRange,Math.max(0,intersection*maxRange-2));
    }
    /** Positional radial falloff. No light means zero illumination. */
    public static float radialIntensity(float x,float y,float sourceX,float sourceY,
                                        float reach,float strength){
        float d=(float)Math.hypot(x-sourceX,y-sourceY);
        if(reach<=0||d>=reach)return 0;
        float k=Math.max(0f,1-d/reach);
        return Math.max(0,Math.min(1,strength))*k*k;
    }
}