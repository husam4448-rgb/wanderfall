package com.survivalparadise.nativegame;

/** V161 regression: seeded neighborhood interiors, re-entry and collision. */
public final class V161NeighborhoodInteriorTest {
    private static void check(boolean yes,String what){
        if(!yes)throw new AssertionError(what);
    }
    public static void main(String[] args){
        int verified=0,industrial=0;
        for(int seed:new int[]{14901,87011,15247}){
            WorldCivilizationV159.Plan plan=WorldCivilizationV159.generate(seed,null,
                WorldGeographyV160.prepare(seed,null));
            for(WorldCivilizationV159.Parcel parcel:plan.parcels){
                for(int slot=0;slot<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;slot++){
                    NeighborhoodV154.Building building=NeighborhoodV154.get(
                        parcel.tx,parcel.ty,slot,plan);
                    if(building==null)continue;
                    int id=NeighborhoodInteriorV161.siteId(building,seed);
                    check(id>=NeighborhoodInteriorV161.SITE_BASE,
                        "Neighborhood ID conflicts with a legacy site");
                    check(id==NeighborhoodInteriorV161.siteId(
                            NeighborhoodV154.get(parcel.tx,parcel.ty,slot,plan),seed),
                            "Building identity changed");
                    NeighborhoodInteriorV161 room=new NeighborhoodInteriorV161(building,seed);
                    check(room.sceneFurniture().length>0&&room.sceneFurniture().length<=48,
                        "No valid per-site furniture was generated");
                    check(room.storages.length==14,"Lost loot containers");
                    check(room.roomNames().length==6,"Incomplete room labels");
                    check(!room.blocked(ClinicInteriorV89.ENTRANCE_X,
                            ClinicInteriorV89.ENTRANCE_Y,15f),"Indoor spawn blocked");
                    check(!room.blocked(ClinicInteriorV89.EXIT_X,
                            ClinicInteriorV89.EXIT_Y,15f),"Indoor exit blocked");
                    String save=room.encode();
                    NeighborhoodInteriorV161 reloaded=new NeighborhoodInteriorV161(building,seed);
                    reloaded.decode(save);
                    check(reloaded.encode().equals(save),"Re-entry reset stored loot");
                    if(room.theme==NeighborhoodV154.FACTORY||
                       room.theme==NeighborhoodV154.WAREHOUSE)industrial++;
                    verified++;
                }
            }
        }
        check(verified>25,"No generated buildings were exercised");
        check(industrial>0,"No factories or warehouses were exercised");
        System.out.println("PASS V161: "+verified+
            " seed-specific buildings, spawn, exit and re-entry storage");
    }
}
