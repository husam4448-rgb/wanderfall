package com.survivalparadise.nativegame;

/** Prevents high-delta-time actor steps from tunneling through thin walls. */
public final class SweptWorldCollisionV157 {
    private SweptWorldCollisionV157(){}
    public interface Test {boolean blocked(float x,float y,float r);}
    public static boolean clear(Test collision,float x0,float y0,
                                float x1,float y1,float radius){
        if(!Float.isFinite(x0)||!Float.isFinite(y0)||
           !Float.isFinite(x1)||!Float.isFinite(y1))return false;
        float distance=(float)Math.hypot(x1-x0,y1-y0);
        // No large teleport can leap over an opaque facade side/front.
        int steps=Math.max(1,(int)Math.ceil(distance/Math.max(7f,radius*.60f)));
        if(steps>2048)return false;
        for(int i=1;i<=steps;i++){
            float f=i/(float)steps;
            if(collision.blocked(x0+(x1-x0)*f,y0+(y1-y0)*f,radius))
                return false;
        }
        return true;
    }
}
