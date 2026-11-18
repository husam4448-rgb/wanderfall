package com.survivalparadise.nativegame;

/**
 * Pure visual selection. Never consumes the world RNG, changes a building ID,
 * changes a parcel, or adjusts collision. Index contract matches the V166
 * production atlas: row 0/1 = eight kinds variant A, row 2/3 variant B.
 */
public final class BuildingArtSelectionV166 {
    private BuildingArtSelectionV166(){}
    public static final int TYPES=8, VARIANTS=2, SPRITES=TYPES*VARIANTS;
    public static final int CELL=320, COLUMNS=4, ROWS=4;
    public static int choose(int kind,int existingVariation,
                             int seed,int tx,int ty,int slot){
        if(kind<0||kind>=TYPES)return -1;
        int h=WorldChunkModel.hash(tx*67+slot*37+kind*113,
                                   ty*139+seed*3);
        int v=Math.floorMod(existingVariation^h,VARIANTS);
        return v*TYPES+kind;
    }
    public static boolean valid(int i){return i>=0&&i<SPRITES;}
}
