package com.survivalparadise.nativegame;

/** Pure Java stable metadata; Android visual layer lives separately. */
public final class InteriorFurnitureCatalogV166 {
    private InteriorFurnitureCatalogV166(){}
    public static final int FIRST=64, PER_THEME=12, COUNT=96;
    // Kinds: bed, sofa, wardrobe, hob, sink, table, workdesk, chair,
    // shelf, terminal, files, locker, checkout, merchandise, cooler,
    // luggage, counter, schooldesk, board, labbench, analyzer, exam,
    // press, conveyor, tools, rack, dolly, freight, printer, server,
    // dresser, island.
    private static final int[][] KINDS={
        {1,0,2,3,4,5,8,30,6,7,31,10},       // apartments
        {6,9,7,10,28,29,8,16,11,5,30,2},   // offices / security
        {13,12,8,14,16,27,25,5,6,26,4,11},// shops / market
        {0,30,15,16,1,7,2,8,4,11,5,14},   // hotel
        {17,18,8,6,7,5,19,20,11,10,28,4}, // school / science
        {22,23,24,25,20,19,29,27,26,11,4,9}, // factory
        {25,27,26,23,24,11,28,29,6,8,22,14},// warehouse
        {1,0,3,4,5,2,30,31,8,6,7,14}      // residences
    };
    private static final int[] WIDTH={
        132,148,108,126,119,137,139,91,116,131,98,111,
        145,144,124,102,145,126,135,155,142,141,165,173,
        113,170,102,145,123,128,132,143
    };
    private static final int[] HEIGHT={
        111,99,101,97,83,106,95,81,94,94,91,103,
        97,100,102,87,106,92,77,105,106,107,129,103,
        94,114,94,108,99,112,98,111
    };

    public static boolean valid(int sprite){return sprite>=FIRST&&sprite<FIRST+COUNT;}
    public static int sprite(int theme,int slot){
        return FIRST+theme*PER_THEME+Math.floorMod(slot,PER_THEME);
    }
    public static int kind(int sprite){
        if(!valid(sprite))return -1;
        int local=sprite-FIRST;
        return KINDS[local/PER_THEME][local%PER_THEME];
    }
    public static float width(int sprite){return WIDTH[kind(sprite)];}
    public static float height(int sprite){return HEIGHT[kind(sprite)];}
}
