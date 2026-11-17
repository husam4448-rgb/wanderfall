package com.survivalparadise.nativegame;

/**
 * V161 deterministic enterable neighborhood interior.
 * V159/V160 city parcels and 26 V153 site identities remain unchanged.
 * Geometry, labels, and item positions derive from the saved world seed.
 */
public final class NeighborhoodInteriorV161 extends ExpeditionInteriorV91 {
    public static final int SITE_BASE=200000;
    public final NeighborhoodV154.Building building;
    public final int theme,variation,seed;
    private final float[][] furniture;
    private final String[] rooms;

    public static int siteId(NeighborhoodV154.Building b,int seed){
        int h=IndustrialWorldV123.hash(b.tileX*47+b.slot*7,
                b.tileY*53+b.slot*17,seed^0x161D00);
        return SITE_BASE+Math.floorMod(h,900000000);
    }
    public static String saveKey(NeighborhoodV154.Building b,int seed){
        return "neighborhood_v161_"+seed+"_"+b.tileX+"_"+b.tileY+"_"+b.slot;
    }
    private static int siteKind(int theme){
        switch(theme){
            case NeighborhoodV154.MARKET:return ExpeditionSitesV88.DEPOT;
            case NeighborhoodV154.HOTEL:return ExpeditionSitesV88.MOTEL;
            case NeighborhoodV154.SCHOOL:return ExpeditionSitesV88.CHECKPOINT;
            case NeighborhoodV154.FACTORY:return ExpeditionSitesV88.WORKSHOP;
            case NeighborhoodV154.WAREHOUSE:return ExpeditionSitesV88.DEPOT;
            case NeighborhoodV154.OFFICES:return ExpeditionSitesV88.RELAY;
            default:return ExpeditionSitesV88.CABIN;
        }
    }
    private static ExpeditionSitesV88.Site site(NeighborhoodV154.Building b){
        return new ExpeditionSitesV88.Site(siteKind(b.kind),b.doorX,b.doorY,
                NeighborhoodV154.LABELS[b.kind],true);
    }
    private static String[] names(int theme,int variant){
        final String[][] layouts={
            {"ENTRY LOUNGE","APARTMENT A","SHARED KITCHEN","BATH & UTILITY","APARTMENT B","STORAGE"},
            {"RECEPTION","OPEN OFFICE","MEETING ROOM","RECORDS","SERVER ROOM","SUPPLY ROOM"},
            {"PRODUCE","GROCERY AISLES","COLD STORAGE","CHECKOUT","BACK STOCK","MANAGER OFFICE"},
            {"RECEPTION","GUEST SUITE","HOUSEKEEPING","HALL LOUNGE","GUEST SUITE","LAUNDRY"},
            {"CLASSROOM A","CLASSROOM B","LIBRARY","STAFF OFFICE","LABORATORY","STORAGE"},
            {"MACHINE HALL","ASSEMBLY LINE","CONTROL ROOM","TOOL ROOM","PARTS BAY","MAINTENANCE"},
            {"RECEIVING","PALLET RACKS","DISPATCH","PACKING LINE","SPARE PARTS","SECURITY"},
            {"LIVING ROOM","BEDROOM","KITCHEN","DINING ROOM","WORK ROOM","PANTRY"}
        };
        String[] selected=layouts[Math.floorMod(theme,layouts.length)].clone();
        if((variant&1)==1){
            String temp=selected[1];selected[1]=selected[2];selected[2]=temp;
        }
        if((variant&2)==2){
            String temp=selected[4];selected[4]=selected[5];selected[5]=temp;
        }
        return selected;
    }
    public NeighborhoodInteriorV161(NeighborhoodV154.Building b,int worldSeed){
        super(site(b));
        building=b;theme=b.kind;variation=b.variation;seed=worldSeed;
        rooms=names(theme,variation);
        float[][] source=super.sceneFurniture();
        furniture=new float[source.length][];
        int global=IndustrialWorldV123.hash(b.tileX*19+b.slot,b.tileY*23,worldSeed);
        for(int i=0;i<source.length;i++){
            furniture[i]=source[i].clone();
            if(i>=source.length-2)continue; // preserve unobstructed main corridor
            int h=IndustrialWorldV123.hash(i*31+b.slot,b.tileX*7+b.tileY,global);
            // Controlled offsets preserve the inherited room doors and walls.
            furniture[i][1]+=(Math.floorMod(h,5)-2)*7f;
            furniture[i][2]+=(Math.floorMod(h>>>6,5)-2)*5f;
            // A factory has machinery, a hotel beds, school desks, and so on.
            int[] styles=theme==NeighborhoodV154.HOTEL?
                new int[]{0,0,5,0,1,0}:
                theme==NeighborhoodV154.FACTORY?
                new int[]{4,4,3,4,5,4}:
                theme==NeighborhoodV154.WAREHOUSE?
                new int[]{5,5,3,5,1,5}:
                theme==NeighborhoodV154.SCHOOL?
                new int[]{2,2,1,2,5,3}:
                theme==NeighborhoodV154.MARKET?
                new int[]{1,5,1,3,5,1}:
                theme==NeighborhoodV154.OFFICES?
                new int[]{2,2,1,2,4,5}:
                theme==NeighborhoodV154.RESIDENCES||theme==NeighborhoodV154.APARTMENTS?
                new int[]{0,1,3,0,2,5}:
                new int[]{2,1,3,0,1,5};
            furniture[i][0]=styles[Math.floorMod(i+variation/3+Math.floorMod(h,3),styles.length)];
        }
        // Site-specific loot exists in actual reachable cabinets and containers.
        for(int i=0;i<storages.length;i++){
            Storage old=storages[i];
            int h=IndustrialWorldV123.hash(b.tileX*31+b.slot*11+i,
                    b.tileY*37+variation,worldSeed);
            int[] items=new int[8];
            items[0]=1+Math.floorMod(h,4);
            items[1]=(theme==NeighborhoodV154.HOTEL||
                      theme==NeighborhoodV154.RESIDENCES||
                      theme==NeighborhoodV154.APARTMENTS)&&i%3==0?1:0;
            items[2]=(theme==NeighborhoodV154.WAREHOUSE||
                      theme==NeighborhoodV154.FACTORY)&&i%4==0?1:0;
            items[3]=i%4==0?1+Math.floorMod(h>>>8,2):0;
            items[4]=i%5==0?1:0;
            items[5]=i%3==0?1:0;
            items[6]=i%5==0?2:0;
            items[7]=i%4==0?1:0;
            storages[i]=new Storage(old.x,old.y,
                    (theme==NeighborhoodV154.WAREHOUSE?"PALLET CRATE":
                     theme==NeighborhoodV154.MARKET?"STORE SHELF":
                     theme==NeighborhoodV154.SCHOOL?"SCHOOL CABINET":
                     theme==NeighborhoodV154.FACTORY?"PARTS BIN":
                     theme==NeighborhoodV154.OFFICES?"FILE DRAWER":
                     theme==NeighborhoodV154.HOTEL?"ROOM LOCKER":"HOME STORAGE"),
                    items);
        }
    }
    @Override public String[] roomNames(){return rooms;}
    @Override public float[][] sceneFurniture(){return furniture;}
    @Override public boolean blocked(float x,float y,float r){
        if(x-r<23*EXPANSION_V90||x+r>1577*EXPANSION_V90||
           y-r<23*EXPANSION_V90||y+r>1095*EXPANSION_V90)return true;
        for(float[] q:sceneWalls())
            if(x+r>q[0]&&x-r<q[0]+q[2]&&y+r>q[1]&&y-r<q[1]+q[3])
                return true;
        for(float[] q:furniture)
            if(x+r>q[1]+4&&x-r<q[1]+q[3]-4&&
               y+r>q[2]+4&&y-r<q[2]+q[4]-4)return true;
        return false;
    }
}
