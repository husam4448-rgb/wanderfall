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
        // Curated work/life ensembles. Distinct anchor roles create a
        // coherent room identity instead of a scattering of generic objects.
        switch(Math.floorMod(slot,7)){
            case 0:return PRIMARY[theme][logical];
            case 1:return SUPPORT[theme][logical];
            case 2:return SCENIC[theme][logical];
            case 3:return ACCENT[theme][logical];
            case 4:return UTILITY[theme][logical];
            case 5:return SUPPORT[theme][logical];
            default:return ACCENT[theme][logical];
        }
    }
    /**
     * Shared-area furniture palette: reception/checkout, school commons,
     * stock handling and residential seating remain architecture-specific.
     */
    public static int shared(int theme,int station,int variation){
        if(theme<0||theme>=8)return 14;
        return SHARED[theme][Math.floorMod(station+variation,SHARED[theme].length)];
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
