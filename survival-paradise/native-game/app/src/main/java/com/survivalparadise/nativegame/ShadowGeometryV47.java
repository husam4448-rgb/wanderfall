package com.survivalparadise.nativegame;

/** Pure geometry of shadow casting from rectangular pixel-actor and world occluders. */
public final class ShadowGeometryV47 {
    private ShadowGeometryV47(){}
    public static final class Blocker {
        public final float left,top,right,bottom;
        public Blocker(float l,float t,float r,float b){left=l;top=t;right=r;bottom=b;}
        public boolean contains(float x,float y){return x>=left&&x<=right&&y>=top&&y<=bottom;}
    }
    /** True only if a blocking silhouette lies strictly BETWEEN light and receiver. */
    public static boolean blocks(Blocker shape,float sx,float sy,float px,float py){
        // No self shadow when a flashlight is held inside the actor, and do not
        // darken the actual front lit surface of an actor standing within its box.
        if(shape.contains(sx,sy)||shape.contains(px,py))return false;
        float t=Ballistics.segmentBox(sx,sy,px,py,
            shape.left,shape.top,shape.right,shape.bottom);
        return t>=0f && t < .998f && !Float.isInfinite(t);
    }
    public static boolean blocksAny(Blocker[] shapes,int count,float sx,float sy,float px,float py){
        for(int i=0;i<count;i++)if(blocks(shapes[i],sx,sy,px,py))return true;
        return false;
    }
}