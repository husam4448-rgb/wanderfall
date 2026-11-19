package com.survivalparadise.nativegame;

/**
 * Pure-data compositions of already authored original artwork.
 * Each signature furnishing combines several functional objects into one
 * physical grouping. Fractions are a 0..1000 local room-set coordinate.
 * The whole grouping has one collision footprint, never phantom blockers.
 */
public final class InteriorScenePlanV166 {
    private InteriorScenePlanV166(){}
    public static final int FIRST=48,COUNT=16;
    private static final int[][][] PARTS={
        {{33,0,0,600,560},{32,580,500,400,420},{34,0,560,480,430}}, // lived-in lounge
        {{0,0,0,560,950},{35,585,70,380,440},{34,580,515,410,460}}, // home bedroom
        {{15,0,0,650,440},{34,650,0,350,420},{47,350,470,600,520}}, // kitchen and dining
        {{15,0,0,650,590},{1,650,0,350,790}}, // washroom utility
        {{36,0,0,710,750},{25,640,340,350,540},{37,0,730,470,270}}, // office desks and paperwork
        {{36,0,0,490,610},{36,510,0,490,610},{37,250,650,480,340}}, // meeting worktables
        {{26,0,240,660,710},{38,650,0,350,530},{45,660,560,330,420}}, // checkout and stock
        {{39,0,0,650,630},{33,630,0,370,450},{32,580,560,390,420}}, // hotel lobby
        {{40,0,0,490,500},{40,510,0,490,500},{22,250,550,500,430}}, // classroom group
        {{41,0,0,590,590},{23,570,0,420,590},{8,290,610,460,380}}, // library and study
        {{42,0,0,690,610},{21,490,580,500,400},{9,0,600,390,380}}, // science lab
        {{28,0,0,660,590},{44,580,430,410,550},{45,0,640,470,350}}, // production bay
        {{45,0,0,520,550},{12,500,0,480,550},{13,230,550,550,440}}, // freight storage
        {{38,0,0,550,610},{1,560,0,430,590},{45,270,580,480,410}}, // pantry
        {{25,0,0,640,700},{3,650,0,340,690},{37,200,700,600,290}}, // records corner
        {{6,0,0,590,850},{35,620,80,350,440},{19,590,600,410,380}} // hotel guest suite
    };
    public static int[][] parts(int sprite){
        if(sprite<FIRST||sprite>=FIRST+COUNT)return new int[0][];
        return PARTS[sprite-FIRST];
    }
    public static boolean valid(int sprite){
        return sprite>=FIRST&&sprite<FIRST+COUNT;
    }
}
