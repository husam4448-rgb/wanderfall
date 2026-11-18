package com.survivalparadise.nativegame;

/** Contract tests for authored city/village/outpost material selection. */
public final class V166SettlementGroundTest {
    private static void ok(boolean b,String reason){
        if(!b)throw new AssertionError(reason);
    }
    public static void main(String[] ignored){
        ok(WorldCivilizationV159.CITY==0&&WorldCivilizationV159.VILLAGE==1,
            "Parcel type IDs changed");
        int seedVariation=0;
        for(int parcel=0;parcel<3;parcel++){
            int[] counts=new int[3];
            for(int gy=-20;gy<20;gy++)for(int gx=-20;gx<20;gx++){
                int a=SettlementGroundSelectionV166.material(parcel,gx,gy,14901,2);
                int b=SettlementGroundSelectionV166.material(parcel,gx,gy,14901,2);
                int alt=SettlementGroundSelectionV166.material(parcel,gx,gy,87291,2);
                ok(a==b&&a>=0&&a<=2,"Non deterministic material");
                counts[a]++;
                if(a!=alt)seedVariation++;
                int h=SettlementGroundSelectionV166.anchorHash(gx,gy,14901,2);
                ok(h==SettlementGroundSelectionV166.anchorHash(gx,gy,14901,2),
                    "World anchored brush jitter changed");
            }
            ok(counts[SettlementGroundSelectionV166.GRASS]>40,"No open greens");
            ok(counts[SettlementGroundSelectionV166.COMPACTED]>20,
                "Missing compacted ground");
            ok(counts[SettlementGroundSelectionV166.DRY]>20,"Missing dry lots");
        }
        ok(seedVariation>600,"Insufficient differences across world seeds");
        System.out.println("PASS V166: 3 settlement materials, feathered source selection, seeded clusters");
    }
}
