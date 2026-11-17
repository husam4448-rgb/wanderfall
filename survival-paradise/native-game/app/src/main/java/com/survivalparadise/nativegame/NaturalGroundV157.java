package com.survivalparadise.nativegame;

/**
 * Stable non-grid organic soil/grass islands in world coordinates. Source
 * terrain seeds and the V54 saved map remain untouched. The same patch
 * appears in the same place on every visit regardless of viewport/chunk.
 */
public final class NaturalGroundV157 {
    private NaturalGroundV157(){}
    public static final int CELL=350;
    public static final int PER_CELL=3;
    public static final int DIRT=0,GRASS=1,DRY=2;
    public static final class Patch {
        public final float x,y,rx,ry,rotation;
        public final int kind,variation;
        private Patch(float x,float y,float rx,float ry,float rotation,int kind,int variation){
            this.x=x;this.y=y;this.rx=rx;this.ry=ry;this.rotation=rotation;
            this.kind=kind;this.variation=variation;
        }
    }
    private static int hash(int x,int y,int salt){
        int v=WorldChunkModel.hash(x*37+salt*17,y*41-salt*23)^0x157C01A;
        v^=v>>>16;v*=0x7feb352d;v^=v>>>15;
        return v;
    }
    public static Patch patch(int cx,int cy,int slot){
        if(slot<0||slot>=PER_CELL)return null;
        int v=hash(cx,cy,slot+1);
        int u=hash(cx,cy,slot+57);
        // Small edge-overlapping islands break up the old regular squares.
        // Some are bare grass and some are exposed dry earth.
        float x=cx*CELL+Math.floorMod(v,340)+5f;
        float y=cy*CELL+Math.floorMod(v>>>9,340)+5f;
        float rx=86f+Math.floorMod(u,100);
        float ry=57f+Math.floorMod(u>>>9,84);
        float angle=Math.floorMod(v>>>17,180);
        int kind=Math.floorMod(u>>>17,11)<5?DIRT:
                 Math.floorMod(u>>>17,11)<9?GRASS:DRY;
        return new Patch(x,y,rx,ry,angle,kind,Math.floorMod(v>>>22,12));
    }
    public static float wobble(Patch p,int index){
        int seed=hash(Math.round(p.x),Math.round(p.y),index+121);
        return .78f+Math.floorMod(seed,38)/100f;
    }
}
