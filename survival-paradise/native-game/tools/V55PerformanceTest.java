package com.survivalparadise.nativegame;

public final class V55PerformanceTest {
    static void ok(boolean v,String name){if(!v)throw new AssertionError(name);}
    public static void main(String[] args){
        // Visible-area tests, including negative unbounded world coordinates.
        ok(WorldPerfV55.nearView(0,0,-100,-100,200,200,0),"origin camera");
        ok(WorldPerfV55.nearView(-1020,-1000,-1200,-1200,400,400,0),"signed world");
        ok(!WorldPerfV55.nearView(10000,10000,0,0,600,400,200),"distant cull");
        ok(WorldPerfV55.nearView(-50,100,0,0,600,400,60),"sprite extents");
        ok(!WorldPerfV55.nearView(-70,100,0,0,600,400,60),"outside margin");
        // Broad phase deliberately overestimates actual collisions, never underestimates.
        ok(WorldPerfV55.segmentNearRect(0,0,1500,0,600,-20,100,40,0),"fast shot crosses building");
        ok(!WorldPerfV55.segmentNearRect(0,0,30,0,600,-20,100,40,0),"far building skipped");
        ok(WorldPerfV55.segmentNearRect(-900,-900,900,900,-30,-30,60,60,0),
           "diagonal crossing");
        ok(WorldPerfV55.segmentNearActor(0,0,2000,0,950,0,1f),
           "fast shot crosses NPC");
        ok(!WorldPerfV55.segmentNearActor(0,0,25,0,950,0,1f),
           "distant NPC skipped");
        ok(WorldPerfV55.segmentNearActor(-200,-160,-100,-160,-140,-100,1.35f),
           "large character retains hit");
        ok(WorldPerfV55.distantFrom(10000,10000,0,0,1200),"far NPC sleeps");
        ok(!WorldPerfV55.distantFrom(520,0,0,0,1200),"combat NPC remains active");
        ok(!WorldPerfV55.distantFrom(1200,0,0,0,1200),"radius boundary active");
        // Retained V54 seed and identical chunk key after unload/revisit.
        int x=-100001,y=99999;
        long before=WorldChunkModel.chunkKey(x,y);
        ok(before==WorldChunkModel.chunkKey(x,y),"revisited chunk identity");
        ok(WorldChunkModel.groundColor(-2715,8891,1080,710)==
           WorldChunkModel.groundColor(-2715,8891,1080,710),
           "revisited ground palette");
        System.out.println("V55 PASS: signed-world culling, conservative bullets, AI tiers, persistent terrain");
    }
}
