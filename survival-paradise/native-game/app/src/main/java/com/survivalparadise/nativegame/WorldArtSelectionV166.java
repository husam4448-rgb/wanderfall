package com.survivalparadise.nativegame;

/**
 * Art-only lookup table. Every resource retains its V80 placement, ID,
 * harvest behavior, hitbox and persistence. No world PRNG is consumed.
 * The contiguous atlas families match build_v166_world_atlas.py exactly.
 */
public final class WorldArtSelectionV166 {
    private WorldArtSelectionV166(){}
    public static final int FOREST=0,AUTUMN=1,ACACIA=2,DEAD=3,
        ROCK=4,WOOD=5,SPARSE=6,BUSH=7;
    public static final int CELL=128,SPRITES=23;
    private static final int[] START={0,3,5,6,7,13,17,20};
    private static final int[] COUNT={3,2,1,1,6,4,3,3};
    public static int familyCount(){return COUNT.length;}
    public static int count(int family){
        return family<0||family>=COUNT.length?0:COUNT[family];
    }
    public static int choose(int family,float worldX,float worldY,
                             int worldSeed,int stableIdentity){
        if(count(family)==0)return -1;
        int h=WorldChunkModel.hash((int)Math.floor(worldX/29f)+family*971,
                                   (int)Math.floor(worldY/37f)-family*613);
        h^=WorldChunkModel.hash(worldSeed,family*139+stableIdentity);
        h^=h>>>16;
        return START[family]+Math.floorMod(h,COUNT[family]);
    }
    public static boolean valid(int sprite){return sprite>=0&&sprite<SPRITES;}
}
