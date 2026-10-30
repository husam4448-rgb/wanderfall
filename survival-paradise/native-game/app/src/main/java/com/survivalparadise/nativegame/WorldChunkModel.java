package com.survivalparadise.nativegame;

/**
 * Deterministic, allocation-free terrain data shared by Android rendering and JVM tests.
 * Signed chunk/tile coordinates preserve the same world across unload/revisit.
 */
public final class WorldChunkModel {
    private WorldChunkModel(){}
    public static final int TILE=72;
    public static final int TILES_PER_CHUNK=16;
    public static final int CHUNK_SIZE=TILE*TILES_PER_CHUNK;
    public static final int RASTER_SCALE=3;
    public static final int RASTER_SIZE=CHUNK_SIZE/RASTER_SCALE;
    public static final int MAX_RESIDENT=36;
    public static final long WORLD_SEED=14901L;

    public static int chunkIndex(float worldCoord){
        return (int)Math.floor((double)worldCoord/CHUNK_SIZE);
    }
    public static int tileIndex(float worldCoord){
        return (int)Math.floor((double)worldCoord/TILE);
    }
    public static long chunkKey(int cx,int cy){
        return ((long)cx<<32)|(cy&0xffffffffL);
    }
    public static int hash(int a,int b){
        int k=a*73856093^b*19349663; // preserve V53 terrain exactly
        k^=k>>>13;k*=0x5bd1e995;
        return k^(k>>>15);
    }
    public static int groundColor(int gx,int gy,int campX,int campY){
        int patch=hash(Math.floorDiv(gx,5),Math.floorDiv(gy,5));
        int biome=Math.floorMod(patch,4);
        int tint=biome==0?0xff375347:biome==1?0xff414d39:
                 biome==2?0xff40544b:0xff4b503d;
        float dx=gx*(float)TILE-campX,dy=gy*(float)TILE-campY;
        if(dx*dx+dy*dy<320f*320f)tint=0xff53624c;
        return tint;
    }
    public static int tileDetail(int gx,int gy){
        return hash(gx,gy);
    }
    public static boolean intersects(int cx,int cy,float x,float y,float width,float height){
        long x0=(long)cx*CHUNK_SIZE,y0=(long)cy*CHUNK_SIZE;
        return x0<x+width&&x0+CHUNK_SIZE>x&&y0<y+height&&y0+CHUNK_SIZE>y;
    }
}
