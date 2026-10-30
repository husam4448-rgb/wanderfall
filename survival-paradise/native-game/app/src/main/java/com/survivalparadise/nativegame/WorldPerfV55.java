package com.survivalparadise.nativegame;

/**
 * Conservative camera and swept-segment broad phase.
 * These gates only skip work whose final pixels or collision cannot be visible.
 * No approved sprite alpha mask, weapon, or hit geometry is changed.
 */
public final class WorldPerfV55 {
    private WorldPerfV55(){}
    public static boolean nearView(float x,float y,float camX,float camY,
                                   float width,float height,float margin){
        return x>=camX-margin&&x<=camX+width+margin
            &&y>=camY-margin&&y<=camY+height+margin;
    }
    /** A conservative X/Y interval overlap. Caller supplies extra tolerance for art/hitbox size. */
    public static boolean segmentNearRect(float x0,float y0,float x1,float y1,
                                          float rx,float ry,float rw,float rh,float pad){
        float minX=Math.min(x0,x1)-pad,maxX=Math.max(x0,x1)+pad;
        float minY=Math.min(y0,y1)-pad,maxY=Math.max(y0,y1)+pad;
        return maxX>=rx&&minX<=rx+rw&&maxY>=ry&&minY<=ry+rh;
    }
    public static boolean segmentNearActor(float x0,float y0,float x1,float y1,
                                           float ax,float ay,float displayScale){
        // Larger than the original 260x160 sprite at 135% scaling, including
        // extended weapon/aim positions; never reject a genuine sprite-alpha hit.
        float halfW=140f*Math.max(1f,displayScale);
        float above=170f*Math.max(1f,displayScale);
        return segmentNearRect(x0,y0,x1,y1,ax-halfW,ay-above,2*halfW,above+35f,0);
    }
    public static boolean distantFrom(float ax,float ay,float bx,float by,float radius){
        double dx=(double)ax-bx,dy=(double)ay-by;
        return dx*dx+dy*dy>(double)radius*radius;
    }
}
