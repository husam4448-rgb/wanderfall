package com.survivalparadise.nativegame;

/** V76 unified responsive geometry for eight compact HUD actions. */
public final class TopHudV76 {
    private TopHudV76(){}
    public static final int FORM=0,EDIT=1,DAY=2,CAMP=3,LAMP=4,BAG=5,PAUSE=6,SET=7,COUNT=8;
    public static final float Y=5f,HEIGHT=31f;
    private static final float[] W={56,58,58,62,64,49,62,54};
    private static final float TOTAL=498f,GAP=5f;
    public static float scale(float width){
        return Math.max(.55f,Math.min(1f,(width-250f)/TOTAL));
    }
    public static float buttonWidth(int id,float width){return W[id]*scale(width);}
    /** PAUSE is a physical top-center anchor; the other HUD controls
     * flow to its left and right without overlapping at mobile widths.
     */
    private static final int[] LEFT={CAMP,FORM,DAY,EDIT};
    private static final int[] RIGHT={LAMP,BAG,SET};
    public static float x(int id,float width){
        float k=scale(width);
        float center=width*.5f-W[PAUSE]*k*.5f;
        if(id==PAUSE)return center;
        float leftWidth=0;
        for(int q:LEFT)leftWidth+=(W[q]+GAP)*k;
        leftWidth-=GAP*k;
        float x=center-GAP*k-leftWidth;
        for(int q:LEFT){
            if(id==q)return x;
            x+=(W[q]+GAP)*k;
        }
        x=center+(W[PAUSE]+GAP)*k;
        for(int q:RIGHT){
            if(id==q)return x;
            x+=(W[q]+GAP)*k;
        }
        return x;
    }
    public static int hit(float x,float y,float width){
        if(y<Y||y>Y+HEIGHT)return -1;
        for(int i=0;i<COUNT;i++){
            float left=x(i,width);
            if(x>=left&&x<=left+buttonWidth(i,width))return i;
        }
        return -1;
    }
}
