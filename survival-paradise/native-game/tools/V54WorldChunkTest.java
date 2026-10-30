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
                    int patch=legacyHash(Math.floorDiv(gx,5),Math.floorDiv(gy,5));
                    int tint=Math.floorMod(patch,4);
                    int expected=tint==0?0xff375347:tint==1?0xff414d39:
                                 tint==2?0xff40544b:0xff4b503d;
                    float dx=gx*72f-1080,dy=gy*72f-710;
                    if(dx*dx+dy*dy<320f*320f)expected=0xff53624c;
                    require(WorldChunkModel.groundColor(gx,gy,1080,710)==expected,
                            "regression: terrain changes after regeneration");
                    verified++;
                }
            }
        }
        require(WorldChunkModel.intersects(-1,0,-120,20,400,400),
                "negative chunk enters camera");
        require(!WorldChunkModel.intersects(-20,20,-120,20,400,400),
                "offscreen chunks culled");
        System.out.println("V54 PASS: "+verified+" deterministic sample cells, signed chunks, original V53 biome palette");
    }
}
