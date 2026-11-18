package com.survivalparadise.nativegame;

/** Pure art mapping. Does not affect procedural floor plans, saves or collision. */
public final class InteriorFloorSelectionV166 {
    private InteriorFloorSelectionV166(){}
    public static final int OAK=0,TERRAZZO=1,VINYL=2,CARPET=3,
        LINO=4,EPOXY=5,CONCRETE=6,PARQUET=7;
    public static final int TILE_COUNT=8,TILE_SIZE=256;

    public static int hallway(int theme){
        switch(theme){
            case NeighborhoodV154.APARTMENTS:return OAK;
            case NeighborhoodV154.OFFICES:return TERRAZZO;
            case NeighborhoodV154.MARKET:return VINYL;
            case NeighborhoodV154.HOTEL:return OAK;
            case NeighborhoodV154.SCHOOL:return LINO;
            case NeighborhoodV154.FACTORY:return EPOXY;
            case NeighborhoodV154.WAREHOUSE:return CONCRETE;
            case NeighborhoodV154.RESIDENCES:return PARQUET;
            default:return CONCRETE;
        }
    }
    /** Name-based so V161's seeded room swaps retain appropriate flooring. */
    public static int room(int theme,String label){
        String name=label==null?"":label;
        if(name.contains("BATH")||name.contains("LAUNDRY")||
           name.contains("LABORATORY")||name.contains("COLD STORAGE"))
            return name.contains("LAUNDRY")?LINO:TERRAZZO;
        if(name.contains("KITCHEN")||name.contains("PANTRY")||
           name.contains("PRODUCE")||name.contains("GROCERY")||
           name.contains("CHECKOUT"))return VINYL;
        if(name.contains("GUEST SUITE")||name.contains("HALL LOUNGE"))
            return CARPET;
        if(name.contains("LIBRARY")||name.contains("LIVING")||
           name.contains("BEDROOM")||name.contains("APARTMENT"))
            return theme==NeighborhoodV154.RESIDENCES?PARQUET:OAK;
        if(name.contains("TOOL")||name.contains("PARTS")||
           name.contains("MAINTENANCE")||name.contains("RECEIVING")||
           name.contains("PALLET"))return CONCRETE;
        if(name.contains("MACHINE")||name.contains("ASSEMBLY")||
           name.contains("CONTROL")||name.contains("PACKING"))return EPOXY;
        if(name.contains("CLASSROOM")||name.contains("SCHOOL"))
            return LINO;
        return hallway(theme);
    }
    public static int legacy(int siteKind,boolean clinic){
        if(clinic)return LINO;
        if(siteKind==ExpeditionSitesV88.WORKSHOP||siteKind==ExpeditionSitesV88.DEPOT)
            return CONCRETE;
        if(siteKind==ExpeditionSitesV88.MOTEL)return CARPET;
        return OAK;
    }
    public static int phase(int seed,int room){
        return WorldChunkModel.hash(seed^0x166f100,room*67+19);
    }
}
