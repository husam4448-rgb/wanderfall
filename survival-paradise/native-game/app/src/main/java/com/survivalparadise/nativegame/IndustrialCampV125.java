package com.survivalparadise.nativegame;

/**
 * An open industrial gathering apron for workers/neutral roles. Stops the
 * original camp coordinates from putting NPC bodies into factory facade art.
 * No changes to V122 character sprites or the NPC AI state machine.
 */
public final class IndustrialCampV125 {
    private IndustrialCampV125(){}
    private static final float[][] START={
        {425f,930f},{520f,900f},{870f,925f},{875f,1080f},{465f,1150f}
    };
    public static final float[][] FIRES={{455f,1040f}};
    private static final int NPC_RADIUS=31;
    public static boolean clear(float x,float y,int seed){
        if(IndustrialOpenWorldV124.blocked(x,y,NPC_RADIUS,seed))return false;
        // The sprite extends upwards beyond the feet collision disk.
        if(IndustrialOpenWorldV124.blocked(x,y-62f,25f,seed))return false;
        // Stay outside the loading lane even if it has no physics collision.
        IndustrialOpenWorldV124.Plot home=IndustrialOpenWorldV124.firstStart(seed);
        if(y>home.doorY&&y<home.y+1220&&
           Math.abs(x-home.doorX)<145f)return false;
        // Do not overlap four physical salvaging racks or crates.
        IndustrialWorldV123.District d=IndustrialWorldV123.district(0,0,seed);
        for(int i=0;i<IndustrialWorldV123.MATERIALS.length;i++){
            float dx=x-d.materialX(i),dy=y-d.materialY(i);
            if(dx*dx+dy*dy<82f*82f)return false;
        }
        return true;
    }
    public static float[] home(int id,int seed){
        if(id<0||id>=START.length)throw new IllegalArgumentException("role");
        float x=START[id][0],y=START[id][1];
        if(clear(x,y,seed))return new float[]{x,y};
        // Deterministic non-random fallback for future changed lot footprints.
        for(int radius=35;radius<=350;radius+=35){
            for(int angle=0;angle<16;angle++){
                double a=angle*Math.PI/8.0;
                float px=x+(float)Math.cos(a)*radius;
                float py=y+(float)Math.sin(a)*radius;
                if(clear(px,py,seed))return new float[]{px,py};
            }
        }
        throw new IllegalStateException("No collision-free industrial spawn");
    }
    public static boolean patrolAllowed(float x,float y,int seed){
        return clear(x,y,seed);
    }
}
