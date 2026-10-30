package com.survivalparadise.nativegame;

/** Offline JVM tests: stable seed, signed world, revisit, finite cache budget. */
public final class V54WorldChunkTest {
    private static void require(boolean ok,String message){
        if(!ok)throw new AssertionError(message);
    }
    private static int legacyHash(int a,int b){
        int k=a*73856093^b*19349663;
        k^=k>>>13;k*=0x5bd1e995;return k^(k>>>15);
    }
    public static void main(String[] args){
        require(WorldChunkModel.TILES_PER_CHUNK==16,"16x16 chunks");
        require(WorldChunkModel.MAX_RESIDENT<=36,"bounded resident chunks");
        require(WorldChunkModel.chunkIndex(0)==0,"origin");
        require(WorldChunkModel.chunkIndex(-.01f)==-1,"negative world coordinates");
        require(WorldChunkModel.chunkIndex(-WorldChunkModel.CHUNK_SIZE)==-1,"negative boundary");
        require(WorldChunkModel.chunkIndex(WorldChunkModel.CHUNK_SIZE)==1,"positive boundary");
        require(WorldChunkModel.chunkKey(-1,2)!=WorldChunkModel.chunkKey(2,-1),
                "signed chunk coordinate hashing");
        require(WorldChunkModel.chunkKey(-333,4000)==WorldChunkModel.chunkKey(-333,4000),
                "stable key for returning traveler");
        int verified=0;
        for(int cy=-120;cy<=120;cy+=13){
            for(int cx=-120;cx<=120;cx+=7){
                long key=WorldChunkModel.chunkKey(cx,cy);
                require(key==WorldChunkModel.chunkKey(cx,cy),"revisit key");
                for(int ty=0;ty<16;ty+=5)for(int tx=0;tx<16;tx+=5){
                    int gx=cx*16+tx,gy=cy*16+ty;
                    require(WorldChunkModel.tileDetail(gx,gy)==legacyHash(gx,gy),
                            "legacy V53 tile art preserved");
                    int expected=WorldChunkModel.groundColor(gx,gy,1080,710);
                    require(expected==WorldChunkModel.groundColor(gx,gy,1080,710),
                            "terrain changes on revisiting");
                    require((expected>>>24)==255,"opaque continuous terrain");
                    float edge=gx*72f;
                    int a=WorldChunkModel.groundColorAt(edge-.05f,gy*72f,1080,710);
                    int b=WorldChunkModel.groundColorAt(edge+.05f,gy*72f,1080,710);
                    int diff=Math.abs(((a>>>16)&255)-((b>>>16)&255))+
                             Math.abs(((a>>>8)&255)-((b>>>8)&255))+
                             Math.abs((a&255)-(b&255));
                    require(diff<=4,"hard visual tile seam");
                    verified++;
                }
            }
        }
        require(WorldChunkModel.intersects(-1,0,-120,20,400,400),
                "negative chunk enters camera");
        require(!WorldChunkModel.intersects(-20,20,-120,20,400,400),
                "offscreen chunks culled");
        System.out.println("V54 PASS: "+verified+" deterministic sample cells, signed chunks, continuous V57 organic biome field");
    }
}
