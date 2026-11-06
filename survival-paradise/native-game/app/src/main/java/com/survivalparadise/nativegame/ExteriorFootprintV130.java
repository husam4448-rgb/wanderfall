package com.survivalparadise.nativegame;

/**
 * Adaptive enlargement of the legacy enterable building silhouettes.
 * Scaling is anchored to their original USE/entrance landing, not their roof
 * center, so old saves, entrances, caches, and NPC navigation targets stay.
 * Every structure is checked against the nearest other structure and camp.
 */
public final class ExteriorFootprintV130 {
    private ExteriorFootprintV130(){}
    // Exact existing GameView.CAMP_X/Y, intentionally not moved.
    public static final float CAMP_X=1080f,CAMP_Y=710f;
    public static final float ROAD_CLEARANCE=24f;
    public static boolean clinic(ExpeditionSitesV88.Site s){
        return s.kind==ExpeditionSitesV88.CLINIC;
    }
    public static float width(ExpeditionSitesV88.Site s){
        return clinic(s)?210f:85f;
    }
    public static float anchor(ExpeditionSitesV88.Site s){
        return clinic(s)?205f:108f;
    }
    private static final float[] SCALES=new float[ExpeditionSitesV88.SITES.length];
    public static float scale(ExpeditionSitesV88.Site s){
        int id=-1;
        for(int i=0;i<ExpeditionSitesV88.SITES.length;i++)
            if(ExpeditionSitesV88.SITES[i]==s){id=i;break;}
        if(id>=0&&SCALES[id]>0f)return SCALES[id];
        float ideal=clinic(s)?1.74f:2.30f;
        float nearest=Float.POSITIVE_INFINITY;
        for(ExpeditionSitesV88.Site other:ExpeditionSitesV88.SITES){
            if(other==s)continue;
            float distance=(float)Math.hypot(s.x-other.x,s.y-other.y);
            float needed=width(s)+width(other);
            float allowed=(distance-ROAD_CLEARANCE)/(needed);
            if(allowed<nearest)nearest=allowed;
        }
        // Camp settlement centre stays clear of new roofs.
        float campDistance=(float)Math.hypot(
            s.x-CAMP_X,s.y-CAMP_Y);
        float campAllowed=(campDistance-360f)/(width(s)+175f);
        // Preserve at least the original facade scale in cramped sites.
        float result=Math.max(1f,Math.min(ideal,Math.min(nearest,campAllowed)));
        // At the industrial stitch, the old sites may not grow into factories.
        if(s.x>5100f)result=Math.min(result,1f);
        if(id>=0)SCALES[id]=result;
        return result;
    }
    public static float[] bounds(ExpeditionSitesV88.Site s){
        float zoom=scale(s),anchor=anchor(s);
        float w=clinic(s)?210f:85f;
        float top=clinic(s)?-174f:-84f;
        float bottom=clinic(s)?190f:83f;
        return new float[]{s.x-w*zoom,
            s.y+anchor+(top-anchor)*zoom,
            s.x+w*zoom,s.y+anchor+(bottom-anchor)*zoom};
    }
    /** Solid visual hull only, no arbitrary rectangle beyond painted roof. */
    public static boolean blocked(ExpeditionSitesV88.Site site,float x,float y,float radius){
        float zoom=scale(site),a=anchor(site);
        float px=(x-site.x)/zoom;
        float py=a+(y-site.y-a)/zoom;
        float r=radius/zoom;
        if(clinic(site)){
            if(px+r<=-194||px-r>=194||py+r<=-159||py-r>=174)return false;
            // Central original entry/USE corridor is always accessible.
            if(Math.abs(px)<43-r&&py>=113-r)return false;
            return py-r<133f;
        }
        if(px+r<=-83||px-r>=84||py+r<=-83||py-r>=79)return false;
        if(Math.abs(px)<20-r&&py>=30-r)return false;
        return py-r<70;
    }
}
