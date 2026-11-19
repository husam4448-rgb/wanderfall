package com.survivalparadise.nativegame;

/**
 * V166 authored furniture vocabulary over the 16 existing production sprites.
 * Roles are tied to the six actual room functions, not random building-wide
 * furniture. Roles 16..31 identify direct atlas sprites without changing the
 * older 0..5 saved/layout furniture schema. This pass corrects scene identity
 * with existing art; new room-specific artwork is still required for approval.
 */
public final class InteriorRoomArchetypeV166 {
    private InteriorRoomArchetypeV166(){}
    // Each row follows NeighborhoodInteriorV161.names() for its building kind.
    private static final int[][] PRIMARY={
        {14,0,6,15,0,1},      // apartments: table, sleeping, kitchen, linen
        {2,2,3,3,2,3},       // offices: workstations, reception, records, servers
        {4,4,5,5,12,13},     // market: shelving, checkouts, freight and stock
        {2,6,6,7,7,1},       // hotel: check-in desk, guest beds, lounge, linen
        {8,8,9,8,2,9},       // school: student desks, library, lab workstation
        {10,10,11,11,11,10},// factory: machinery, control and parts assembly
        {12,13,12,11,13,2}, // warehouse: loading, racks, dispatch, office
        {14,0,15,14,1,6}    // residence: dining, beds, kitchen and storage
    };
    private static final int[][] SUPPORT={
        {15,1,14,15,1,15},
        {3,3,2,3,3,2},
        {5,13,4,4,13,4},
        {7,7,1,14,7,1},
        {9,9,8,9,9,8},
        {11,11,10,13,12,11},
        {13,12,13,12,12,3},
        {7,1,14,15,1,15}
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
    /**
     * Shared-area furniture palette: reception/checkout, school commons,
     * stock handling and residential seating remain architecture-specific.
     */
    public static int shared(int theme,int station,int variation){
        if(theme<0||theme>=8)return 14;
        final int[][] palette={
            {14,15,7,1}, // apartment commons: tables, kitchen, seating
            {2,3,2,3},   // office: desks and records
            {4,5,4,5},   // market: checkouts and merchandising
            {2,7,14,7},  // hotel: reception desk, lounge and service table
            {8,9,8,9},   // school: study desks and bookcases; no machinery
            {10,11,10,11},
            {12,13,12,13},
            {14,15,7,1}
        };
        return palette[theme][Math.floorMod(station+variation,4)];
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
