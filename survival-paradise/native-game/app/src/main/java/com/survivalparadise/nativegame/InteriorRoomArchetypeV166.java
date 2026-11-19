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
    private static final int[][] PRIMARY={
        {33,35,47,13,35,34},
        {36,36,2,41,36,34},
        {38,38,27,26,38,36},
        {39,35,46,33,35,46},
        {40,40,41,36,42,41},
        {44,44,36,44,45,44},
        {45,45,45,44,45,36},
        {33,35,47,47,36,41}
    };
    private static final int[][] SUPPORT={
        {32,34,15,14,34,41},
        {24,2,25,25,3,3},
        {4,27,38,26,13,25},
        {16,18,19,17,18,19},
        {20,22,23,25,21,23},
        {28,29,2,29,13,28},
        {12,13,12,29,13,24},
        {14,0,15,32,1,6}
    };
    private static final int[][] ACCENT={
        {34,1,14,15,1,13},
        {3,3,25,3,25,2},
        {4,13,12,26,4,3},
        {17,1,18,7,18,1},
        {22,20,9,3,21,1},
        {10,29,11,13,12,11},
        {12,12,13,13,12,3},
        {15,7,1,14,15,1}
    };
    private static final int[][] SCENIC={
        {32,35,47,37,32,34},
        {39,36,37,41,36,37},
        {38,38,45,26,38,37},
        {39,35,46,32,35,46},
        {40,40,41,37,42,43},
        {44,44,37,44,45,44},
        {45,45,45,44,45,37},
        {32,35,47,47,36,41}
    };
    private static final int[][] UTILITY={
        {41,34,32,13,34,13},
        {36,41,36,41,37,45},
        {45,6,45,26,45,41},
        {34,3,45,32,3,45},
        {43,43,43,41,43,45},
        {45,45,41,45,45,44},
        {45,45,45,44,45,36},
        {34,41,32,34,41,38}
    };
    private static final int[][] SHARED={
        {33,32,34,47,7,14},
        {24,36,25,41,37,2},
        {4,26,38,27,45,38},
        {39,17,33,16,32,18},
        {20,40,23,22,41,43},
        {28,44,29,45,12,13},
        {12,45,13,29,44,36},
        {33,32,47,34,15,14}
    };
    // Physical rectangles for all 48 rendered art cells; scaling is uniform
    // per object, and collision is exactly the chosen visual bounding box.
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
        {143,101},{129,96},{109,92},{139,111}
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
                case 3:return 31; // equipment cart
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
