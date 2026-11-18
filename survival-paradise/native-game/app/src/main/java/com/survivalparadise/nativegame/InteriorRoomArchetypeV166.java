package com.survivalparadise.nativegame;

/**
 * V166 authored furniture vocabulary over the 16 existing production sprites.
 * Roles are tied to the six actual room functions, not random building-wide
 * furniture. Roles 16..31 identify direct atlas sprites without changing the
 * older 0..5 saved/layout furniture schema.
 */
public final class InteriorRoomArchetypeV166 {
    private InteriorRoomArchetypeV166(){}
    // Each row follows NeighborhoodInteriorV161.names() for its building kind.
    private static final int[][] PRIMARY={
        {14,0,15,3,0,1},      // apartments: lounge, bedrooms, kitchen, utility
        {2,2,14,3,2,3},       // business: desks, conference, archives, servers
        {4,4,5,5,12,2},      // market: displays, cold goods, tills, stock
        {5,6,9,14,6,3},      // hotel: reception, guest rooms, linen, common area
        {8,8,9,2,10,9},      // education: classroom, library, lab
        {10,10,2,11,11,10},  // factory: machining, assembly, control, parts
        {12,13,12,11,13,2},  // warehouse: receiving, racks, dispatch, packing
        {14,0,15,14,2,1}     // family residence: lounge, bed, cooking, dining
    };
    private static final int[][] SUPPORT={
        {15,1,14,15,1,15},
        {3,3,2,9,3,11},
        {12,13,4,4,13,3},
        {2,7,15,7,7,9},
        {9,9,15,3,9,11},
        {11,11,3,13,12,11},
        {13,12,13,12,12,3},
        {7,1,14,15,3,15}
    };
    private static final float[][] SIZES={
        {125,106},{110,76},{139,94},{94,71},
        {142,77},{148,82},{132,110},{101,83},
        {112,76},{103,75},{154,120},{139,77},
        {151,102},{136,84},{130,95},{112,78}
    };
    public static int sprite(int theme,int index,int variation,int slot){
        if(theme<0||theme>=8||index<0||index>=6)return -1;
        // V161 room name variant swaps: actual role follows the name.
        int logical=index;
        if((variation&1)!=0){
            if(logical==1)logical=2;
            else if(logical==2)logical=1;
        }
        if((variation&2)!=0){
            if(logical==4)logical=5;
            else if(logical==5)logical=4;
        }
        int primary=PRIMARY[theme][logical],secondary=SUPPORT[theme][logical];
        return slot%3==0?primary:slot%3==1?secondary:
            (slot%2==0?primary:secondary);
    }
    public static float width(int sprite){
        return SIZES[Math.floorMod(sprite,SIZES.length)][0];
    }
    public static float height(int sprite){
        return SIZES[Math.floorMod(sprite,SIZES.length)][1];
    }
    public static int legacy(int type,int siteKind,boolean clinic,int index){
        if(clinic){
            switch(type){
                case 0:return 6; // medical bed
                case 1:return 9; // treatment / supplies cabinet
                case 2:return 2; // clinician station
                case 3:return 14; // medical work surface
                case 4:return 10; // equipment
                default:return 3;
            }
        }
        switch(siteKind){
            case ExpeditionSitesV88.MOTEL:
            case ExpeditionSitesV88.CABIN:return type==0?6:(index%3==0?14:1);
            case ExpeditionSitesV88.WORKSHOP:
            case ExpeditionSitesV88.GARAGE:return index%3==0?10:11;
            case ExpeditionSitesV88.CHECKPOINT:return index%3==0?2:13;
            case ExpeditionSitesV88.RELAY:
            case ExpeditionSitesV88.TOWER:return index%3==0?2:10;
            case ExpeditionSitesV88.FARM:return index%3==0?14:12;
            default:return index%3==0?12:13;
        }
    }
}
