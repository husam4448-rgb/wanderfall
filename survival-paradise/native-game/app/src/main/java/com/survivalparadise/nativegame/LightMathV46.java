package com.survivalparadise.nativegame;

/** Pure-Java lighting attenuation shared by the renderer and tests. */
public final class LightMathV46 {
    private LightMathV46(){}
    public static float pointStrength(float dx,float dy,float radius,float power){
        if(radius<=0||power<=0)return 0;
        float distance=(float)Math.hypot(dx,dy);
        if(distance>=radius)return 0;
        float t=1f-distance/radius;
        return Math.min(1,Math.max(0,power*t*t*(.87f+.13f*t)));
    }
    public static float flashlightStrength(float dx,float dy,float ux,float uy,float reach){
        float d=(float)Math.hypot(dx,dy);
        if(reach<=0||d>reach)return 0;
        if(d<2)return .99f;
        float forward=(dx*ux+dy*uy)/d;
        float half=.50f;
        if(forward<(float)Math.cos(half))return 0;
        float side=(ux*dy-uy*dx)/d;
        float relative=(float)Math.atan2(side,forward)/half;
        float edge=1f-Math.abs(relative);
        float fade=1f-.43f*d/reach;
        return Math.min(1f,Math.max(0f,(.16f+.83f*edge*edge)*fade));
    }
    public static int shadowAlpha(int ambientDarkness,float lightStrength){
        int dark=Math.max(0,Math.min(248,ambientDarkness));
        return Math.max(0,Math.round(dark*(1f-Math.max(0f,Math.min(1f,lightStrength)))));
    }
}