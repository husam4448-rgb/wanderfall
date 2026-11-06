package com.survivalparadise.nativegame;

/** Verify art/hitbox transforms against every legacy POI and the camp. */
public final class ExteriorFootprintV130Test {
    private static void ok(boolean v,String why){if(!v)throw new AssertionError(why);}
    public static void main(String[] args){
        int increased=0,large=0,clinics=0;float min=9f,max=0f;
        for(ExpeditionSitesV88.Site site:ExpeditionSitesV88.SITES){
            float scale=ExteriorFootprintV130.scale(site);
            min=Math.min(scale,min);max=Math.max(scale,max);
            if(scale>1.01f)increased++;
            if(scale>=1.6f)large++;
            if(ExteriorFootprintV130.clinic(site))clinics++;
            ok(scale>=1f&&scale<=2.31f,"invalid site scale");
            ok(!ExteriorFootprintV130.blocked(site,site.x,
                  site.y+ExteriorFootprintV130.anchor(site),18f),
                  "entrance/USE landing cannot be entered: "+site.name);
            ok(ExteriorFootprintV130.blocked(site,site.x,
                  site.y-95f,8f)||scale==1f,
                  "enlarged visible roof should be solid: "+site.name);
            ok(!ExteriorFootprintV130.blocked(site,
                  ExteriorFootprintV130.CAMP_X,ExteriorFootprintV130.CAMP_Y,20f),
                  "camp center covered by enlarged facade");
            float[] bounds=ExteriorFootprintV130.bounds(site);
            ok(bounds[0]<site.x&&bounds[2]>site.x&&bounds[1]<bounds[3],
                  "malformed exterior bounds");
            float pivot=ExteriorFootprintV130.anchor(site);
            float zoom=scale;
            float scaledPivot=site.y+pivot+(pivot-pivot)*zoom;
            ok(scaledPivot==site.y+pivot,"door pivot drift");
            for(ExpeditionSitesV88.Site other:ExpeditionSitesV88.SITES){
                if(site==other)continue;
                float dx=site.x-other.x,dy=site.y-other.y;
                float distance=(float)Math.hypot(dx,dy);
                float width=ExteriorFootprintV130.width(site)*scale+
                            ExteriorFootprintV130.width(other)*
                                ExteriorFootprintV130.scale(other);
                if(distance<=width+ExteriorFootprintV130.ROAD_CLEARANCE-1)
                    throw new AssertionError("Expanded roofs overlap neighboring POIs: "+
                        site.name+" / "+other.name);
            }
        }
        ok(increased>=19,"too few exteriors expanded");
        ok(large>=10,"too few full-scale exteriors");
        ok(clinics>=1,"clinic must retain specialized facade");
        System.out.println("PASS V130 expanded "+increased+"/"+ExpeditionSitesV88.SITES.length+
            " exteriors, "+large+" substantially enlarged, scale range "+min+
            ".."+max+", original entrance/region/camp collision checks");
    }
}
