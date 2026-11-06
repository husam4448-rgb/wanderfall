package com.survivalparadise.nativegame;

/** Independent fitted-head collider in world coordinates.
 * Head bounds are obtained from the SAME approved V5/V109 geometry used for
 * rendering. World X mirroring and partial head tilt are included.
 */
public final class HeadCollisionV131 {
    private HeadCollisionV131(){}
    public static float[] worldBounds(float actorX,float actorY,int facing,
            float left,float top,float right,float bottom,float tiltDegrees){
        float height=bottom-top,width=right-left;
        // Rotating the approved head about the neck enlarges its possible
        // footprint without changing its visible pixel geometry.
        float radians=(float)Math.toRadians(Math.min(35,Math.abs(tiltDegrees)));
        float xPad=3f+(float)Math.sin(radians)*height*.56f;
        float yPad=3f+(float)Math.sin(radians)*width*.56f;
        float xa=actorX+facing*left,xb=actorX+facing*right;
        return new float[]{Math.min(xa,xb)-xPad,actorY+top-yPad,
            Math.max(xa,xb)+xPad,actorY+bottom+yPad};
    }
    /** Return first continuous projectile intersection t (0..1), or +Infinity. */
    public static float firstHit(float x0,float y0,float x1,float y1,
                                 float[] bounds){
        if(bounds==null||bounds.length!=4)return Float.POSITIVE_INFINITY;
        return Ballistics.segmentBox(x0,y0,x1,y1,
            bounds[0],bounds[1],bounds[2],bounds[3]);
    }
}
