package com.survivalparadise.nativegame;

/** V153 exterior/interior size, true wall/door collision and plot spacing. */
public final class ExteriorFootprintV130Test {
    private static void ok(boolean v,String why){if(!v)throw new AssertionError(why);}
    private static boolean overlap(float[] a,float[] b,float gap){
        return a[0]<b[2]+gap&&a[2]>b[0]-gap&&
               a[1]<b[3]+gap&&a[3]>b[1]-gap;
    }
    public static void main(String[] args){
        int clinics=0,buildings=0;
        for(ExpeditionSitesV88.Site s:ExpeditionSitesV88.SITES){
            float[] b=ExteriorFootprintV130.roofBounds(s);
            float[] whole=ExteriorFootprintV130.bounds(s);
            float doorY=s.y+ExteriorFootprintV130.anchor(s);
            float width=b[2]-b[0],height=b[3]-b[1];
            ok(width>=.78f*ClinicInteriorV89.WIDTH&&
               height>=.78f*ClinicInteriorV89.HEIGHT,
               "shack outside an institutional interior: "+s.name);
            ok(width<=ClinicInteriorV89.WIDTH&&height<=ClinicInteriorV89.HEIGHT,
               "exterior larger than its room map: "+s.name);
            ok(whole[0]<=b[0]&&whole[2]>=b[2]&&whole[3]>b[3],
               "culling bounds missing apron: "+s.name);
            ok(ExteriorFootprintV130.blocked(s,s.x,doorY-185f,12f),
               "non-solid main roof: "+s.name);
            ok(!ExteriorFootprintV130.blocked(s,s.x,doorY-45f,12f),
               "visible doorway corridor is blocked: "+s.name);
            ok(!ExteriorFootprintV130.blocked(s,s.x,doorY,18f),
               "ENTER button approach is blocked: "+s.name);
            ok(!ExteriorFootprintV130.blocked(s,s.x+120f,doorY+36f,16f),
               "supply cache hidden inside building: "+s.name);
            ok(120f*120f+36f*36f<138f*138f,
               "new supplies must be reachable from the entry");
            ok(ExteriorFootprintV130.blocked(s,
               s.x+ExteriorFootprintV130.DOOR_HALF_WIDTH+32f,doorY-45f,8f),
               "front wall missing to the right of doorway: "+s.name);
            ok(!ExteriorFootprintV130.blocked(s,1080f,710f,20f),
               "camp blocked by building: "+s.name);
            ok(!overlap(b,new float[]{1430f,-100000f,1790f,100000f},60f),
               "building blocks old north-south road: "+s.name);
            ok(!overlap(b,new float[]{-100000f,863f,100000f,1210f},60f),
               "building blocks old east-west highway: "+s.name);
            ok(!overlap(b,new float[]{5500f,-6400f,100000f,9000f},0f),
               "building clipped into industrial biome: "+s.name);
            for(ExpeditionSitesV88.Site other:ExpeditionSitesV88.SITES){
                if(s==other)continue;
                float[] c=ExteriorFootprintV130.roofBounds(other);
                ok(!overlap(b,c,ExteriorFootprintV130.ROAD_CLEARANCE),
                    "neighbor roof overlap: "+s.name+" / "+other.name);
            }
            if(ExteriorFootprintV130.clinic(s))clinics++;
            buildings++;
        }
        ok(buildings==26&&clinics==1,"site IDs or clinic lost");
        System.out.println("PASS V153: "+buildings+" exterior campuses, 78%+ interior scale, "+
            "clear full-size roofs, usable doors, preserved roads, camp and industrial border");
    }
}
