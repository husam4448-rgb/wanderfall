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
    // Continuous smooth value noise, sampled in WORLD coordinates, never per
    // chunk; both sides of a chunk edge therefore resolve to identical colors.
    private static float noise(float x,float y,float scale,int salt){
        double fx=x/scale,fy=y/scale;
        int ix=(int)Math.floor(fx),iy=(int)Math.floor(fy);
        float tx=(float)(fx-ix),ty=(float)(fy-iy);
        tx=tx*tx*(3f-2f*tx);ty=ty*ty*(3f-2f*ty);
        float v00=(hash(ix+salt,iy-salt)&65535)/65535f;
        float v10=(hash(ix+1+salt,iy-salt)&65535)/65535f;
        float v01=(hash(ix+salt,iy+1-salt)&65535)/65535f;
        float v11=(hash(ix+1+salt,iy+1-salt)&65535)/65535f;
        return (v00+(v10-v00)*tx)*(1f-ty)+(v01+(v11-v01)*tx)*ty;
    }
    private static int pack(int r,int g,int b){
        return 0xff000000|(Math.max(0,Math.min(255,r))<<16)
            |(Math.max(0,Math.min(255,g))<<8)|Math.max(0,Math.min(255,b));
    }
    public static int groundColorAt(float wx,float wy,int campX,int campY){
        // Muted old-world woodland/soil palette: continuous across all chunks.
        float forest=noise(wx,wy,760f,17)*.62f+noise(wx,wy,280f,73)*.38f;
        float soil=noise(wx,wy,410f,113)*.64f+noise(wx,wy,110f,37)*.36f;
        float micro=noise(wx,wy,44f,201)*.5f+noise(wx,wy,18f,51)*.5f;
        float dirt=Math.max(0f,Math.min(1f,(soil-.43f)*2.8f));
        float grass=Math.max(0f,Math.min(1f,(forest-.22f)*1.8f));
        float fine=(micro-.5f)*27f;
        float rr=53f+grass*23f+dirt*21f+fine;
        float gg=66f+grass*33f-dirt*4f+fine*.82f;
        float bb=48f+grass*14f-dirt*7f+fine*.60f;
        float dx=wx-campX,dy=wy-campY;
        float camp=dx*dx+dy*dy;
        if(camp<310f*310f){
            float k=Math.max(0f,Math.min(1f,(310f-(float)Math.sqrt(camp))/170f));
            rr=rr*(1f-k)+84f*k;gg=gg*(1f-k)+95f*k;
            bb=bb*(1f-k)+70f*k;
        }
        return pack(Math.round(rr),Math.round(gg),Math.round(bb));
    }
    public static int groundColor(int gx,int gy,int campX,int campY){
        return groundColorAt((gx+.5f)*TILE,(gy+.5f)*TILE,campX,campY);
    }
    public static int tileDetail(int gx,int gy){
        return hash(gx,gy);
    }
    public static boolean intersects(int cx,int cy,float x,float y,float width,float height){
        long x0=(long)cx*CHUNK_SIZE,y0=(long)cy*CHUNK_SIZE;
        return x0<x+width&&x0+CHUNK_SIZE>x&&y0<y+height&&y0+CHUNK_SIZE>y;
    }
}
