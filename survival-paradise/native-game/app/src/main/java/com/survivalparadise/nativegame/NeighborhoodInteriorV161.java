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
    public final NeighborhoodLayoutV163 layoutV163;

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
        layoutV163=new NeighborhoodLayoutV163(b,worldSeed);
        // V163: actual floor plan, partition walls and prop locations change
        // deterministically per building. No V89/V161 six-room grid reuse.
        furniture=layoutV163.furniture;
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
            storages[i]=new Storage(layoutV163.caches[i][0],layoutV163.caches[i][1],
                    (theme==NeighborhoodV154.WAREHOUSE?"PALLET CRATE":
                     theme==NeighborhoodV154.MARKET?"STORE SHELF":
                     theme==NeighborhoodV154.SCHOOL?"SCHOOL CABINET":
                     theme==NeighborhoodV154.FACTORY?"PARTS BIN":
                     theme==NeighborhoodV154.OFFICES?"FILE DRAWER":
                     theme==NeighborhoodV154.HOTEL?"ROOM LOCKER":"HOME STORAGE"),
                    items);
        }
    }
    @Override public float[][] sceneWalls(){return layoutV163.walls;}
    public float[][] sceneDoorPositionsV163(){return layoutV163.doors;}
    public float[][] sceneLabelPositionsV163(){return layoutV163.labels;}
    public boolean doorVerticalV163(int room){return layoutV163.doorVertical(room);}
    @Override public String[] roomNames(){return rooms;}
    @Override public float[][] sceneFurniture(){return furniture;}
    @Override public boolean blocked(float x,float y,float r){
        return layoutV163.blocked(x,y,r);
    }
}
