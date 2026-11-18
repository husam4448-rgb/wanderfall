package com.survivalparadise.nativegame;

/** Pure seeded, coherent material selection; never mutates world/parcel state. */
public final class SettlementGroundSelectionV166 {
    private SettlementGroundSelectionV166(){}
    public static final int GRASS=0,COMPACTED=1,DRY=2;
    public static final int STEP=360;
    public static int material(int kind,int gx,int gy,int worldSeed,int variation){
        // One 4x4 brush neighbourhood shares a landscape tendency:
        // no confetti-like independent per-pixel colors.
        int h=WorldChunkModel.hash(Math.floorDiv(gx,4)*137+worldSeed*3,
                                   Math.floorDiv(gy,4)*79+variation*67);
        int n=Math.floorMod(h,100);
        if(kind==0)return n<12?GRASS:n<91?COMPACTED:DRY;
        if(kind==1)return n<34?GRASS:n<90?DRY:COMPACTED;
        return n<14?GRASS:n<49?COMPACTED:DRY;
    }
    public static int anchorHash(int gx,int gy,int seed,int variation){
        return WorldChunkModel.hash(gx*109+seed,gy*193+variation*17);
    }
}
