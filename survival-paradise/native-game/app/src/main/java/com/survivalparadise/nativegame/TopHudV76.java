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
    public static float x(int id,float width){
        float k=scale(width),left=width-8f-TOTAL*k;
        for(int n=0;n<id;n++)left+=(W[n]+GAP)*k;
        return left;
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
