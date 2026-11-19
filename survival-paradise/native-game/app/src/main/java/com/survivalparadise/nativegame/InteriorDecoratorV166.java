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
    // Small, non-solid floor evidence follows the building's function:
    // classrooms have paper and pencils; workshops have cables and bolts;
    // homes have textiles and mats. Every style is purely visual.
    private static final int[][] THEMES={
        {0,1,4,5,2,1,4}, // apartments
        {1,3,5,2,1,0,3}, // offices
        {2,5,1,3,2,6,5}, // market
        {0,4,1,5,0,2,4}, // hotel
        {1,5,1,2,5,0,1}, // school
        {3,5,6,2,3,5,2}, // factory
        {6,3,5,2,6,3,5}, // warehouse
        {0,4,1,5,2,4,0}  // residences
    };
    private static int style(int theme,int hash){
        int[] palette=THEMES[Math.floorMod(theme,THEMES.length)];
        return palette[Math.floorMod(hash,palette.length)];
    }
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
            float area=z[2]*z[3];
            int target=area>175000*S*S?11:area>90000*S*S?8:6;
            int filled=0;
            // Room anchors take priority; a deterministic lattice probes
            // remaining niches without creating any collidable entities.
            for(int candidate=0;candidate<ANCHORS.length+81&&filled<target;candidate++){
                int n=hash(worldSeed^theme*911,room,candidate);
                int ax,ay;
                if(candidate<ANCHORS.length){
                    int[] anchor=ANCHORS[
                        (candidate+Math.floorMod(n>>>12,7))%ANCHORS.length];
                    ax=anchor[0];ay=anchor[1];
                }else{
                    int index=Math.floorMod(
                        (candidate-ANCHORS.length)*47+
                        Math.floorMod(worldSeed^room*127,81),81);
                    ax=65+(index%9)*108;
                    ay=65+(index/9)*108;
                }
                int type=style(theme,n>>>5);
                float w=(type==0?78:type==1?35:type==2?48:
                    type==3?54:type==4?42:type==5?31:60)*S;
                float h=(type==0?49:type==1?31:type==2?25:
                    type==3?23:type==4?42:type==5?35:29)*S;
                float dx=maxx-xmin-w-72*S,dy=maxy-ymin-h-72*S;
                if(dx<=0||dy<=0)continue;
                float x=xmin+36*S+ax*dx/1000f;
                float y=ymin+36*S+ay*dy/1000f;
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
                result.add(new float[]{type,x,y,w,h});
                filled++;
            }
        }
        // Previously completely bare circulation spaces get sparse signs
        // of past use: receipts, broken hardware, marks and scattered paper.
        // These are flat decals, never loot, never physical obstructions.
        int commons=0;
        for(int candidate=0;candidate<90&&commons<9;candidate++){
            int pos=Math.floorMod(
                candidate*47+Math.floorMod(worldSeed^theme*53,90),90);
            int n=hash(worldSeed^theme*1237,81,candidate);
            int type=style(theme,n>>>5);
            if(type==0||type==4)type=theme==5||theme==6?5:1;
            float w=(type==1?35:type==2?48:type==3?54:
                type==5?31:60)*S;
            float h=(type==1?31:type==2?25:type==3?23:
                type==5?35:29)*S;
            float x=(85+(pos%10)*145)*S,
                y=(85+(pos/10)*110)*S;
            float cx=x+w*.5f,cy=y+h*.5f;
            if(x<935*S&&x+w>650*S&&y+h>835*S)continue;
            boolean occupied=false;
            for(float[] room:rooms)
                if(overlap(x,y,w,h,room[0],room[1],
                           room[2],room[3],18*S)){occupied=true;break;}
            if(occupied)continue;
            for(float[] q:furniture)
                if(overlap(x,y,w,h,q[1],q[2],q[3],q[4],10*S)){
                    occupied=true;break;
                }
            if(occupied)continue;
            for(float[] cache:caches)
                if(Math.abs(cx-cache[0])<66*S&&
                   Math.abs(cy-cache[1])<64*S){occupied=true;break;}
            if(occupied)continue;
            for(float[] door:doors)
                if(Math.hypot(cx-door[0],cy-door[1])<144*S){
                    occupied=true;break;
                }
            if(occupied)continue;
            for(float[] q:result)
                if(overlap(x,y,w,h,q[1],q[2],q[3],q[4],16*S)){
                    occupied=true;break;
                }
            if(occupied)continue;
            result.add(new float[]{type,x,y,w,h});
            commons++;
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
