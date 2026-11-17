package com.survivalparadise.nativegame;

/**
 * Industrial blocks are physical compounds rather than a small standalone
 * shed. The older V126 alpha-traced main hall and these exact two opaque
 * attached wings share one collision model with the V155 Canvas drawing.
 *
 * All coordinates are sector-local, so legacy door (700,810), district ID,
 * seed, stockpile coordinates, yard gate and road locations remain unchanged.
 */
public final class IndustrialComplexV155 {
    private IndustrialComplexV155(){}

    public static final class Wing {
        public final float x,y,w,h;
        Wing(float x,float y,float w,float h){
            this.x=x;this.y=y;this.w=w;this.h=h;
        }
        public boolean blocks(float px,float py,float radius){
            return px+radius>x&&px-radius<x+w&&
                   py+radius>y&&py-radius<y+h;
        }
    }
    public static Wing left(IndustrialOpenWorldV124.Plot site){
        float x=site.x,y=site.y;
        int k=site.kind;
        return new Wing(x+173f,y+664f,257f,177f+(k%3)*6f);
    }
    public static Wing right(IndustrialOpenWorldV124.Plot site){
        float x=site.x,y=site.y;
        int k=site.kind;
        return new Wing(x+1052f,y+672f,192f,153f+(k%4)*4f);
    }
    public static boolean blocks(IndustrialOpenWorldV124.Plot site,
                                 float x,float y,float radius){
        if(!site.enterable())return false;
        return left(site).blocks(x,y,radius)||
               right(site).blocks(x,y,radius);
    }
    /** Full masonry footprint, including its attached service wings. */
    public static float[] bounds(IndustrialOpenWorldV124.Plot site){
        Wing l=left(site),r=right(site);
        return new float[]{
            Math.min(site.buildingX-12f,Math.min(l.x,r.x)),
            Math.min(site.buildingY-22f,Math.min(l.y,r.y)),
            Math.max(site.buildingX+site.buildingW+12f,
                     Math.max(l.x+l.w,r.x+r.w)),
            Math.max(site.buildingY+site.buildingH+24f,
                     Math.max(l.y+l.h,r.y+r.h))
        };
    }
}
