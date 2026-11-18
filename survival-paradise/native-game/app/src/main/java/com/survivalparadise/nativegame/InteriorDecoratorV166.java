package com.survivalparadise.nativegame;

import java.util.ArrayList;

/**
 * Deterministic walk-through ground detail. These are deliberately FLAT
 * dressings (rugs, documents, footprints, loose supplies, stains), not solid
 * furniture or loot and must not alter navigation or persistent inventories.
 */
public final class InteriorDecoratorV166 {
    private InteriorDecoratorV166(){}
    private static final float S=ClinicInteriorV89.EXPANSION_V90;
    private static final int[][] ANCHORS={
        {75,75},{915,85},{90,905},{905,895},{490,92},{510,875},
        {85,485},{905,495},{280,245},{745,765},{265,790},
        {725,260},{400,420},{600,590},{200,485},{810,565},
        {385,760},{590,260},{250,85},{755,90}
    };
    private static int hash(int seed,int a,int b){
        int n=seed^(a*0x9e3779b9)^(b*0x7f4a7c15);
        n^=n>>>16;n*=0x7feb352d;n^=n>>>15;n*=0x846ca68b;
        return n^(n>>>16);
    }
    private static boolean overlap(float x,float y,float w,float h,
                                   float xx,float yy,float ww,float hh,float gap){
        return x<xx+ww+gap&&x+w>xx-gap&&y<yy+hh+gap&&y+h>yy-gap;
    }
    /**
     * Room rectangles, solid furnishings, container centers and door points
     * are already expanded to world coordinates. No renderer random state.
     */
    public static float[][] plan(float[][] rooms,float[][] furniture,
                                 float[][] caches,float[][] doors,
                                 int worldSeed,int theme){
        ArrayList<float[]> result=new ArrayList<>();
        for(int room=0;room<rooms.length;room++){
            float[] z=rooms[room];
            float xmin=z[0],ymin=z[1],maxx=xmin+z[2],maxy=ymin+z[3];
            int target=(z[2]*z[3]>410000*S*S)?6:4;
            int filled=0;
            for(int candidate=0;candidate<ANCHORS.length&&filled<target;candidate++){
                int n=hash(worldSeed^theme*911,room,candidate);
                int[] anchor=ANCHORS[(candidate+Math.floorMod(n>>>12,7))%ANCHORS.length];
                int style=Math.floorMod(n>>>5,7);
                float w=(style==0?78:style==1?35:style==2?48:
                    style==3?54:style==4?42:style==5?31:60)*S;
                float h=(style==0?49:style==1?31:style==2?25:
                    style==3?23:style==4?42:style==5?35:29)*S;
                float dx=maxx-xmin-w-72*S,dy=maxy-ymin-h-72*S;
                if(dx<=0||dy<=0)continue;
                float x=xmin+36*S+anchor[0]*dx/1000f;
                float y=ymin+36*S+anchor[1]*dy/1000f;
                float cx=x+w*.5f,cy=y+h*.5f;
                boolean occupied=false;
                for(float[] q:furniture){
                    if(overlap(x,y,w,h,q[1],q[2],q[3],q[4],10*S)){
                        occupied=true;break;
                    }
                }
                if(occupied)continue;
                for(float[] cache:caches){
                    if(Math.abs(cx-cache[0])<70*S&&
                       Math.abs(cy-cache[1])<65*S){occupied=true;break;}
                }
                if(occupied)continue;
                for(float[] door:doors){
                    if(Math.hypot(cx-door[0],cy-door[1])<133*S){
                        occupied=true;break;
                    }
                }
                if(occupied)continue;
                for(float[] q:result){
                    if(overlap(x,y,w,h,q[1],q[2],q[3],q[4],12*S)){
                        occupied=true;break;
                    }
                }
                if(occupied)continue;
                result.add(new float[]{style,x,y,w,h});
                filled++;
            }
        }
        return result.toArray(new float[0][]);
    }
    /**
     * Legacy rooms have fixed floorplans; scatter only small floor marks
     * beside the known room edges. Reuses existing geometry, never loot.
     */
    public static float[][] legacy(int seed,int theme){
        ArrayList<float[]> detail=new ArrayList<>();
        for(int room=0;room<6;room++){
            float x=room%3==0?25f:room%3==1?555f:1075f;
            float y=room<3?46f:645f;
            for(int i=0;i<3;i++){
                int n=hash(seed^theme,room,i);
                float xx=x+(i==0?68:i==1?265:395)+Math.floorMod(n,21);
                float yy=y+(i==0?125:i==1?265:130)+Math.floorMod(n>>>11,19);
                float[] q=new float[]{(float)Math.floorMod(n>>>4,7),
                    xx*S,yy*S,36*S,24*S};
                detail.add(q);
            }
        }
        return detail.toArray(new float[0][]);
    }
}
