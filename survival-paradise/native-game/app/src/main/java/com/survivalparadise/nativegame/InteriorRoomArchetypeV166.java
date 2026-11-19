package com.survivalparadise.nativegame;

/**
 * V166 authored vocabulary: 16 original and 16 specialized transparent props.
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
    private static final int[][] PRIMARY={
        {14,0,15,1,6,1},     // apartment lounge, bed, kitchen, utility
        {24,2,2,25,3,25},   // office reception, work, meeting, records
        {4,4,27,26,12,2},  // market produce, aisles, cold storage, till
        {16,6,19,18,6,19}, // hotel lobby, suite, housekeeping, lounge
        {20,20,23,2,21,23},// school classrooms, library, office, lab
        {28,29,2,29,13,28},// factory machine hall, assembly, control, tools
        {12,13,12,29,13,24},// warehouse receiving, racks, packing, security
        {14,0,15,14,1,6}   // residence living, sleep, kitchen, dining
    };
    private static final int[][] SUPPORT={
        {15,1,14,15,1,15},
        {2,25,14,3,25,3},
        {13,27,13,4,13,25},
        {17,18,3,7,18,1},
        {22,22,22,25,22,9},
        {29,11,3,11,12,29},
        {13,12,13,12,12,3},
        {7,1,14,15,1,15}
    };
    private static final int[][] ACCENT={
        {7,1,14,15,1,15},
        {3,3,25,3,25,2},
        {4,13,12,26,4,3},
        {7,1,18,14,1,3},
        {23,23,9,3,21,1},
        {10,29,11,13,12,11},
        {12,12,13,13,12,3},
        {15,7,1,14,15,1}
    };
    private static final int[][] SHARED={
        {14,15,7,1},  // apartment shared kitchen + seating
        {24,2,25,3},  // office lobby + records
        {4,26,4,27},  // market aisles + checkout + cold displays
        {16,17,18,7}, // hotel reception, luggage, services, lounge
        {20,23,22,23},// school classroom and study/library commons
        {28,29,10,11},// factory shop machinery and tool benches
        {12,13,29,12},// warehouse freight and work surfaces
        {14,15,7,1}
    };
    private static final float[][] SIZES={
        {125,106},{110,76},{139,94},{94,71},
        {142,77},{148,82},{132,110},{101,83},
        {112,76},{103,75},{154,120},{139,77},
        {151,102},{136,84},{130,95},{112,78},
        {151,101},{80,88},{111,83},{93,91},
        {137,86},{144,92},{128,86},{126,78},
        {140,93},{122,95},{133,90},{105,109},
        {145,97},{140,92},{105,135},{101,96}
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
        int accent=ACCENT[theme][logical];
        switch(Math.floorMod(slot,5)){
            case 0:return primary;
            case 1:return secondary;
            case 2:return accent;
            case 3:return secondary;
            default:return primary;
        }
    }
    /**
     * Shared-area furniture palette: reception/checkout, school commons,
     * stock handling and residential seating remain architecture-specific.
     */
    public static int shared(int theme,int station,int variation){
        if(theme<0||theme>=8)return 14;
        return SHARED[theme][Math.floorMod(station+variation,4)];
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
