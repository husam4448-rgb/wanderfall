package com.survivalparadise.nativegame;

/** Source-locked exterior art at life-sized world scale and matching solid hulls. */
public final class SiteExteriorScaleV130 {
    private SiteExteriorScaleV130(){}
    public static float scale(int type){
        if(type==ExpeditionSitesV88.CLINIC)return 1.65f;
        if(type==ExpeditionSitesV88.RELAY||type==ExpeditionSitesV88.TOWER)
            return 1.85f;
        return 2.25f;
    }
    /** Existing entrance world coordinates remain the reference for every site. */
    public static float doorY(ExpeditionSitesV88.Site site){
        return site.y+(site.kind==ExpeditionSitesV88.CLINIC?154f:90f);
    }
    public static float[] solid(ExpeditionSitesV88.Site site){
        float z=scale(site.kind);
        float door=doorY(site);
        boolean clinic=site.kind==ExpeditionSitesV88.CLINIC;
        // Collision covers visually solid roof and walls, NOT the entry pad,
        // ground apron, signs, animated props, or the exterior of the artwork.
        float minX=clinic?-194f:-78f,maxX=clinic?194f:82f;
        float top=clinic?-159f:-66f,bottom=clinic?126f:65f;
        return new float[]{site.x+minX*z,door+(top-
            (clinic?154f:90f))*z,
            site.x+maxX*z,door+(bottom-(clinic?154f:90f))*z};
    }
    public static boolean blocked(float x,float y,float r){
        for(ExpeditionSitesV88.Site site:ExpeditionSitesV88.SITES){
            float[] q=solid(site);
            if(x+r>q[0]&&x-r<q[2]&&y+r>q[1]&&y-r<q[3])
                return true;
        }
        return false;
    }
    public static boolean near(float x,float y,float range){
        for(ExpeditionSitesV88.Site site:ExpeditionSitesV88.SITES){
            float dx=x-site.x,dy=y-doorY(site);
            if(dx*dx+dy*dy<range*range)return true;
        }
        return false;
    }
}
