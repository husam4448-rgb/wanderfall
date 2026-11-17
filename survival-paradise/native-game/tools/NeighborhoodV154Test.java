package com.survivalparadise.nativegame;

/** V154 district QA: scale, density, variants, reliable collision and saves. */
public final class NeighborhoodV154Test {
    private static void ok(boolean value,String reason){
        if(!value)throw new AssertionError(reason);
    }
    private static boolean overlap(float l,float t,float r,float b,
                                   float ll,float tt,float rr,float bb,float gap){
        return l<rr+gap&&r>ll-gap&&t<bb+gap&&b>tt-gap;
    }
    public static void main(String[] args){
        int total=0,nearOrigin=0;
        boolean[] kinds=new boolean[NeighborhoodV154.TYPES];
        for(int ty=-3;ty<=3;ty++)for(int tx=-3;tx<=3;tx++)
            for(int slot=0;slot<6;slot++){
                NeighborhoodV154.Building b=NeighborhoodV154.get(tx,ty,slot);
                if(b==null)continue;
                total++;kinds[b.kind]=true;
                if(Math.abs(tx)<=1&&Math.abs(ty)<=1)nearOrigin++;
                ok(b.width>=1100f&&b.height>=1000f,
                    "building shrank to shack "+tx+" "+ty+" "+slot);
                ok(b.width<=1450f&&b.height<=1350f,
                    "building escaped its parcel");
                ok(b.tileX==tx&&b.tileY==ty&&b.slot==slot,
                    "district cell identity drift");
                ok(NeighborhoodV154.get(tx,ty,slot)==b,
                    "inefficient uncached geometry allocation");
                ok(NeighborhoodV154.blocked(b.left+b.width*.5f,
                    b.top+b.height*.5f,12f),"roof is not solid");
                ok(!NeighborhoodV154.blocked(b.doorX,b.bottom()+78f,12f),
                    "usable sidewalk is a phantom wall");
                ok(!NeighborhoodV154.blocked(b.left-84f,b.top+b.height*.5f,12f),
                    "collision spills outside masonry");
                float t=NeighborhoodV154.firstImpact(
                    b.left-86f,b.top+b.height*.5f,
                    b.left+110f,b.top+b.height*.5f);
                ok(t>=0f&&t<=1f,"gunfire passes through large building");
                float pass=NeighborhoodV154.firstImpact(
                    b.left-70f,b.bottom()+70f,
                    b.right()+70f,b.bottom()+70f);
                ok(pass==Float.POSITIVE_INFINITY,
                    "bullets hit invisible sidewalk");
                float[] clear=NeighborhoodV154.clearSavedPosition(
                    b.doorX,b.top+b.height*.5f);
                ok(!NeighborhoodV154.blocked(clear[0],clear[1],24f),
                    "old save trapped under new block");
                for(ExpeditionSitesV88.Site site:ExpeditionSitesV88.SITES){
                    float[] sb=ExteriorFootprintV130.bounds(site);
                    ok(!overlap(b.left,b.top,b.right(),b.bottom()+150f,
                        sb[0],sb[1],sb[2],sb[3],185f),
                        "district overlaps named entrance: "+site.name);
                }
                ok(!overlap(b.left,b.top,b.right(),b.bottom()+150f,
                        1420f,-100000f,1800f,100000f,75f),
                    "urban lot clips north-south highway");
                ok(!overlap(b.left,b.top,b.right(),b.bottom()+150f,
                        -100000f,855f,100000f,1220f,75f),
                    "urban lot clips main highway");
                // Neighboring cells and slots must remain independent.
                for(int ky=ty-1;ky<=ty+1;ky++)
                    for(int kx=tx-1;kx<=tx+1;kx++)
                        for(int z=0;z<6;z++){
                            NeighborhoodV154.Building other=NeighborhoodV154.get(kx,ky,z);
                            if(other==null||other==b)continue;
                            ok(!b.overlaps(other.left,other.top,
                                other.right(),other.bottom(),50f),
                                "roof overlap / impossible street");
                        }
            }
        ok(total>=70,"world too sparse: "+total);
        ok(nearOrigin>=8,"opening world still looks deserted: "+nearOrigin);
        for(int i=0;i<kinds.length;i++)
            ok(kinds[i],"missing building variety "+NeighborhoodV154.LABELS[i]);
        ok(!NeighborhoodV154.blocked(1080f,710f,30f),
            "starting camp blocked");
        ok(!NeighborhoodV154.blocked(1605f,1050f,30f),
            "main crossroads blocked");
        ok(!NeighborhoodV154.blocked(5600f,1036f,20f),
            "industrial transition blocked");
        System.out.println("PASS V154: "+total+" full-sized buildings in 49 "+
            "districts, "+nearOrigin+" near starter region, eight variants, "+
            "clear roads, saved position, physical bullets and site access");
    }
}
