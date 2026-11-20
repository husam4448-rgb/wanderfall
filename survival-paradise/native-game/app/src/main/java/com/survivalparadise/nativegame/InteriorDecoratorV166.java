package com.survivalparadise.nativegame;

import java.util.ArrayList;

/**
 * A maximum of one flat, usable textile per habitable room. Floor detail
 * never substitutes for actual furniture, blocks a portal, overlaps storage,
 * or creates repeated loose-paper / miniature debris scatters.
 */
public final class InteriorDecoratorV166 {
    private InteriorDecoratorV166(){}
    private static final float S=ClinicInteriorV89.EXPANSION_V90;
    public static float[][] plan(float[][] rooms,float[][] furniture,
                                 float[][] caches,float[][] doors,
                                 int worldSeed,int theme){
        ArrayList<float[]> placed=new ArrayList<>();
        // Hard, washable workshop and warehouse floors receive no fake rugs.
        if(theme==NeighborhoodV154.FACTORY||
           theme==NeighborhoodV154.WAREHOUSE)return new float[0][];
        for(int i=0;i<rooms.length;i++){
            float[] z=rooms[i];
            float w=Math.min(142*S,z[2]*.38f);
            float h=Math.min(92*S,z[3]*.33f);
            if(w<65*S||h<45*S)continue;
            float[][] positions={
                {.5f,.5f},{.28f,.46f},{.72f,.46f},
                {.5f,.7f},{.32f,.72f},{.68f,.72f}
            };
            for(float[] p:positions){
                float x=z[0]+z[2]*p[0]-w*.5f;
                float y=z[1]+z[3]*p[1]-h*.5f;
                if(x<z[0]+24*S||y<z[1]+24*S||
                   x+w>z[0]+z[2]-24*S||y+h>z[1]+z[3]-24*S)continue;
                boolean clear=true;
                for(float[] f:furniture){
                    if(x<f[1]+f[3]+4*S&&x+w>f[1]-4*S&&
                       y<f[2]+f[4]+4*S&&y+h>f[2]-4*S){
                        clear=false;break;
                    }
                }
                if(!clear)continue;
                for(float[] cache:caches){
                    if(x<cache[0]+54*S&&x+w>cache[0]-54*S&&
                       y<cache[1]+54*S&&y+h>cache[1]-54*S){
                        clear=false;break;
                    }
                }
                if(!clear)continue;
                for(float[] door:doors){
                    if(x<door[0]+88*S&&x+w>door[0]-88*S&&
                       y<door[1]+88*S&&y+h>door[1]-88*S){
                        clear=false;break;
                    }
                }
                if(clear){
                    placed.add(new float[]{0,x,y,w,h});
                    break;
                }
            }
        }
        return placed.toArray(new float[0][]);
    }
    public static float[][] legacy(int seed,int theme){
        // Pre-V163 legacy layouts never require cosmetic scatters.
        return new float[0][];
    }
}
