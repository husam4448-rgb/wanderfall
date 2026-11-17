package com.survivalparadise.nativegame;

/**
 * V153 true large-site exterior geometry, anchored to the actual ENTER door.
 * The interior (2720 x 1904) has a corresponding ~80% scale exterior,
 * instead of the old 170-unit-wide shack. Pure collision/render dimensions.
 * Site positions are separated once in ExpeditionSitesV88 to avoid overlaps.
 */
public final class ExteriorFootprintV130 {
    private ExteriorFootprintV130(){}
    public static final float CAMP_X=1080f,CAMP_Y=710f;
    public static final float ROAD_CLEARANCE=140f;
    public static final float DOOR_HALF_WIDTH=92f;
    public static boolean clinic(ExpeditionSitesV88.Site s){
        return s.kind==ExpeditionSitesV88.CLINIC;
    }
    /** Roof half-width in world units, not the old sprite half-width. */
    public static float width(ExpeditionSitesV88.Site s){
        return clinic(s)?1140f:1090f;
    }
    public static float height(ExpeditionSitesV88.Site s){
        return clinic(s)?1640f:1570f;
    }
    /** Door landing remains relative to the site's stable identity. */
    public static float anchor(ExpeditionSitesV88.Site s){
        return clinic(s)?154f:90f;
    }
    /** Retained compatibility method: V153 facades use world geometry directly. */
    public static float scale(ExpeditionSitesV88.Site s){return 1f;}
    public static float[] roofBounds(ExpeditionSitesV88.Site s){
        float doorY=s.y+anchor(s);
        return new float[]{s.x-width(s),doorY-height(s),
            s.x+width(s),doorY-25f};
    }
    /** Draw-culling bounds also include the exterior landing apron. */
    public static float[] bounds(ExpeditionSitesV88.Site s){
        float[] b=roofBounds(s);
        b[3]=s.y+anchor(s)+248f;
        return b;
    }
    private static boolean touches(float x,float y,float r,
                                   float l,float t,float rr,float bb){
        return x+r>l&&x-r<rr&&y+r>t&&y-r<bb;
    }
    /** The solid roof and physical front wall match the painted geometry.
     * An actual gap at the middle front wall keeps the ENTER approach clear.
     */
    public static boolean blocked(ExpeditionSitesV88.Site s,
                                  float x,float y,float radius){
        float r=Math.max(0f,radius),doorY=s.y+anchor(s);
        float left=s.x-width(s),right=s.x+width(s);
        if(touches(x,y,r,left,doorY-height(s),right,doorY-65f))
            return true;
        if(touches(x,y,r,left,doorY-65f,right,doorY-25f)){
            float gapLeft=s.x-DOOR_HALF_WIDTH;
            float gapRight=s.x+DOOR_HALF_WIDTH;
            if(touches(x,y,r,left,doorY-65f,gapLeft,doorY-25f))
                return true;
            if(touches(x,y,r,gapRight,doorY-65f,right,doorY-25f))
                return true;
        }
        return false;
    }
}
