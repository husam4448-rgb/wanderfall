package com.survivalparadise.nativegame;

/**
 * An open industrial gathering apron for workers/neutral roles. Stops the
 * original camp coordinates from putting NPC bodies into factory facade art.
 * No changes to V122 character sprites or the NPC AI state machine.
 */
public final class IndustrialCampV125 {
    private IndustrialCampV125(){}
    private static final float[][] START={
        {470f,850f},{505f,935f},{890f,865f},{885f,952f},{485f,1135f}
    };
    public static final float[][] FIRES={{490f,1055f}};
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
    // A candidate needs actual clear geometry AND sufficient distance from
    // all previously chosen NPC homes, not merely an unoccupied wall cell.
    private static boolean separated(float x,float y,float[][] chosen,int count){
        for(int j=0;j<count;j++){
            float dx=x-chosen[j][0],dy=y-chosen[j][1];
            if(dx*dx+dy*dy<112f*112f)return false;
        }
        float dx=x-FIRES[0][0],dy=y-FIRES[0][1];
        return dx*dx+dy*dy>=98f*98f;
    }
    public static float[] home(int id,int seed){
        if(id<0||id>=START.length)throw new IllegalArgumentException("role");
        float[][] chosen=new float[id+1][];
        for(int npc=0;npc<=id;npc++){
            float x=START[npc][0],y=START[npc][1];
            if(clear(x,y,seed)&&separated(x,y,chosen,npc)){
                chosen[npc]=new float[]{x,y};
                continue;
            }
            // Stable, bounded placement search. Recompute roles in exact order
            // so the same seed never moves an NPC when offscreen chunks reload.
            boolean found=false;
            for(int radius=35;radius<=525&&!found;radius+=35){
                for(int angle=0;angle<24;angle++){
                    double a=angle*Math.PI/12.0;
                    float px=x+(float)Math.cos(a)*radius;
                    float py=y+(float)Math.sin(a)*radius;
                    if(clear(px,py,seed)&&separated(px,py,chosen,npc)){
                        chosen[npc]=new float[]{px,py};
                        found=true;break;
                    }
                }
            }
            if(!found)throw new IllegalStateException(
                "No separate, collision-free industrial NPC spawn");
        }
        return chosen[id];
    }
    public static boolean patrolAllowed(float x,float y,int seed){
        return clear(x,y,seed);
    }
}
