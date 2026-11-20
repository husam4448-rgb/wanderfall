package com.survivalparadise.nativegame;

/**
 * V166 authored vocabulary: 16 original, 16 specialized and 16 hand-authored set-piece props.
 * Roles follow actual room labels, not arbitrary building-wide families.
 * Legacy 0..5 furniture and direct 16+sprite layout tags remain compatible;
 * the physical V163 collision and save schema is unchanged.
 */
public final class InteriorRoomArchetypeV166 {
    private InteriorRoomArchetypeV166(){}
    // Each row follows NeighborhoodInteriorV161.names() for its building kind.
    // Atlas 16..31: hotel reception/luggage/service/linen, classroom/lab/
    // study/library, office reception/records, market checkout/refrigeration,
    // factory lathe/bench, clinic bed/trolley.
    // Rows are building themes; columns are actual named rooms. Swapped room
    // labels continue to receive their correct functional content.
    // Each column corresponds to the actual room name in V161. The FIRST
    // role is a staged, multi-object workstation or lived-in furniture
    // grouping; secondary roles furnish its perimeter without duplicating it.
    private static final int[][] PRIMARY={
        {48,49,50,51,49,61}, // apartments
        {52,52,53,62,52,62}, // offices
        {38,38,27,54,61,52}, // market
        {55,63,18,48,63,51},// hotel
        {56,56,57,52,58,61},// school
        {59,59,52,44,60,59},// factory
        {60,60,60,59,60,52},// warehouse
        {48,49,50,50,52,61} // residences
    };
    private static final int[][] SUPPORT={
        {33,0,15,15,0,1},
        {24,2,2,25,3,3},
        {4,27,38,26,13,25},
        {16,6,19,33,6,19},
        {20,20,23,25,21,9},
        {28,29,10,29,13,28},
        {12,13,12,29,13,24},
        {33,0,15,14,2,1}
    };
    private static final int[][] ACCENT={
        {32,35,34,1,35,13},
        {2,36,25,3,10,3},
        {38,4,27,26,38,3},
        {32,35,1,7,35,1},
        {22,22,9,3,21,1},
        {10,29,11,13,12,11},
        {12,12,13,13,12,3},
        {32,35,34,47,36,38}
    };
    private static final int[][] SCENIC={
        {34,35,47,15,35,34},
        {36,36,37,41,10,37},
        {38,38,45,26,38,37},
        {39,35,18,32,35,1},
        {40,40,41,37,42,41},
        {44,44,10,44,45,44},
        {45,45,45,44,45,37},
        {32,35,47,47,36,38}
    };
    private static final int[][] UTILITY={
        {41,34,15,1,34,13},
        {36,41,36,41,10,45},
        {45,38,45,26,45,41},
        {34,19,18,32,19,1},
        {43,43,43,41,43,9},
        {45,45,10,45,45,44},
        {45,45,45,44,45,36},
        {34,41,34,14,41,1}
    };
    private static final int[][] SHARED={
        {48,33,32,50,1,14},
        {24,52,25,41,37,2},
        {4,54,38,27,45,38},
        {55,17,33,16,32,18},
        {20,56,23,22,41,43},
        {28,59,29,45,12,13},
        {12,60,13,29,44,52},
        {48,32,50,34,15,14}
    };
    private static final float[][] SIZES={
        {125,106},{110,76},{139,94},{94,71},
        {142,77},{148,82},{132,110},{101,83},
        {112,76},{103,75},{154,120},{139,77},
        {151,102},{136,84},{130,95},{112,78},
        {151,101},{80,88},{111,83},{93,91},
        {137,86},{144,92},{128,86},{126,78},
        {140,93},{122,95},{133,90},{105,109},
        {145,97},{140,92},{105,135},{101,96},
        {110,78},{144,95},{139,92},{72,78},
        {146,110},{78,57},{126,109},{142,100},
        {148,111},{120,104},{138,103},{130,84},
        {143,101},{129,96},{109,92},{139,111},
        {210,151},{198,159},{215,165},{186,122},
        {193,146},{220,165},{220,150},{238,166},
        {215,160},{203,149},{208,151},{240,172},
        {230,160},{208,152},{190,135},{205,165}
    };
    /**
     * Functional room plans: six or more semantically compatible large
     * furnishings for each room. Repeated desks and seating are deliberate,
     * but unrelated equipment is never added merely to increase variety.
     * Column order matches the actual named V161 rooms, before label swaps.
     */
    // Service and utility spaces use real sink, shelf, cabinet and linen
    // profiles, never a dining table, a stove or a cold-grocery display.
    // Repeating a useful station in these rooms is preferable to falsely
    // introducing incompatible equipment only to inflate variety counts.
    // Classrooms use student desks, boards and teacher stations instead of
    // the generic family-size dining tables; libraries may use study tables.
    private static final int[][][] ROOM_ROLES={
        { // apartments: lounge, bedroom, kitchen, utility, bedroom, storage
            {0,5,6,9,8,7,0,6},
            {1,2,7,9,6,8,1,2},
            {3,4,10,5,6,9,3,4},
            {4,10,6,2,7,11,4,6},
            {1,2,7,9,6,8,1,2},
            {2,6,11,7,10,4,2,6}
        },
        { // offices: reception, workspace, conference, records, server, supply
            {7,2,0,9,6,3,4,8},
            {0,2,4,6,3,9,1,8},
            {9,2,6,0,4,3,7,8},
            {3,6,8,11,4,5,0,2},
            {5,1,8,6,4,3,11,2},
            {8,3,6,11,10,4,2,7}
        },
        { // market: produce, groceries, cold chain, checkout, stock, office
            {0,2,6,5,9,3,10,1},
            {0,2,3,6,5,9,10,1},
            {3,6,5,2,9,10,11,0},
            {1,0,2,9,4,6,10,5},
            {5,6,9,11,2,3,10,0},
            {8,11,4,2,6,10,5,9}
        },
        { // hotel: reception, suite, housekeeping, lounge, suite, laundry
            {3,4,5,2,7,1,3,4},
            {0,1,6,5,4,7,10,2},
            {9,7,6,2,8,1,3,9},
            {4,5,10,7,3,2,1,11},
            {0,1,6,5,4,7,10,2},
            {8,9,7,6,1,2,8,9}
        },
        { // school: classroom desks, library, staff, science, supplies
            {0,1,3,4,2,8,0,3},
            {0,1,3,4,2,8,0,3},
            {2,5,4,3,8,9,0,10},
            {3,4,5,9,2,10,8,1},
            {6,7,11,8,9,5,3,2},
            {8,2,9,10,11,5,8,2}
        },
        { // factory: machine, assembly, control, tools, parts, maintenance
            {0,1,2,3,7,8,9,11},
            {1,2,3,7,8,0,9,11},
            {11,6,4,9,2,3,5,10},
            {2,3,9,8,7,10,0,1},
            {3,7,8,9,2,0,10,1},
            {2,10,9,3,8,11,4,7}
        },
        { // warehouse: receiving, shelves, dispatch, packing, spares, security
            {0,1,2,3,4,5,9,11},
            {0,1,2,5,9,4,11,3},
            {1,2,3,6,5,0,4,7},
            {3,0,1,2,4,6,5,9},
            {0,4,1,5,2,9,3,11},
            {7,8,6,5,9,0,2,4}
        },
        { // residences: living, bedroom, kitchen, dining, work, pantry
            {0,4,8,10,9,6,0,4},
            {1,5,6,10,8,9,1,5},
            {2,3,7,4,8,11,2,3},
            {4,10,0,7,8,11,4,10},
            {9,10,8,4,6,5,9,10},
            {8,11,7,3,6,5,8,11}
        }
    };
    /**
     * A compatible directional role always belongs to the functional room.
     * The generated artwork never substitutes unrelated equipment to pad density.
     */
    public static boolean isRoomFurniture(int theme,int index,int variation,int sprite){
        if(theme<0||theme>=8||index<0||index>=6||
           !InteriorFurnitureCatalogV166.valid(sprite))return false;
        int[] roles=ROOM_ROLES[theme][actualRoom(index,variation)];
        int local=sprite-InteriorFurnitureCatalogV166.FIRST-theme*12;
        for(int role:roles)if(role==local)return true;
        return false;
    }
    private static int actualRoom(int index,int variation){
        int logical=index;
        if((variation&1)!=0){
            if(logical==1)logical=2;
            else if(logical==2)logical=1;
        }
        if((variation&2)!=0){
            if(logical==4)logical=5;
            else if(logical==5)logical=4;
        }
        return logical;
    }
    public static int directional(int theme,int index,int variation,int slot){
        if(theme<0||theme>=8||index<0||index>=6)return -1;
        int[] roles=ROOM_ROLES[theme][actualRoom(index,variation)];
        return InteriorFurnitureCatalogV166.sprite(theme,
            roles[Math.floorMod(slot,roles.length)]);
    }
    public static int sprite(int theme,int index,int variation,int slot){
        if(theme<0||theme>=8||index<0||index>=6)return -1;
        // Preserve the familiar authored room-scale signature station, then
        // add independently authored directional equipment; no repeated
        // desk/paper filler and no random building-wide palette.
        if(slot==0)return PRIMARY[theme][actualRoom(index,variation)];
        return directional(theme,index,variation,slot-1);
    }
    public static int detail(int theme,int index,int variation,int slot){
        return directional(theme,index,variation,slot);
    }
    /**
     * Shared-area furniture palette: reception/checkout, school commons,
     * stock handling and residential seating remain architecture-specific.
     */
    public static int shared(int theme,int station,int variation){
        if(theme<0||theme>=8)return 14;
        // Curated public-area functions, not generic clutter. Offsets across
        // halls vary stock, seating and workstations without spawning minis.
        final int[][] commons={
            {0,5,6,8,9,10,7,2},
            {7,0,2,3,4,8,9,10},
            {0,2,3,5,6,9,10,1},
            {3,4,5,2,7,1,4,5},
            {0,1,2,3,4,8,9,10},
            {0,1,2,3,4,6,7,10},
            {0,1,2,3,4,5,9,11},
            {0,4,6,8,9,10,7,5}
        };
        int[] roles=commons[theme];
        return InteriorFurnitureCatalogV166.sprite(theme,
            roles[Math.floorMod(station+variation,roles.length)]);
    }
    public static float width(int sprite){
        if(InteriorFurnitureCatalogV166.valid(sprite))
            return InteriorFurnitureCatalogV166.width(sprite);
        return SIZES[Math.floorMod(sprite,SIZES.length)][0];
    }
    public static float height(int sprite){
        if(InteriorFurnitureCatalogV166.valid(sprite))
            return InteriorFurnitureCatalogV166.height(sprite);
        return SIZES[Math.floorMod(sprite,SIZES.length)][1];
    }
    public static int legacy(int type,int siteKind,boolean clinic,int index){
        if(clinic){
            switch(type){
                case 0:return 30; // original medical patient bed
                case 1:return 31; // sterile supplies trolley
                case 2:return 2;  // clinician work desk
                case 3:return 46; // authored clinic supplies trolley
                case 4:return 9;  // medical storage cabinet
                default:return 31;
            }
        }
        switch(siteKind){
            case ExpeditionSitesV88.MOTEL:
                return type==0?6:index%7==2?16:index%3==0?19:1;
            case ExpeditionSitesV88.CABIN:
                return type==0?6:(index%3==0?14:1);
            case ExpeditionSitesV88.WORKSHOP:
            case ExpeditionSitesV88.GARAGE:
                return index%3==0?28:29;
            case ExpeditionSitesV88.CHECKPOINT:return index%3==0?2:13;
            case ExpeditionSitesV88.RELAY:
            case ExpeditionSitesV88.TOWER:return index%3==0?2:10;
            case ExpeditionSitesV88.FARM:return index%3==0?14:12;
            default:return index%3==0?12:13;
        }
    }
}
