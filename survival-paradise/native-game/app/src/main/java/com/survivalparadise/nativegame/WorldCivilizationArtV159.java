package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/**
 * Civilization is drawn INSIDE authentic plotted lots and their fences.
 * Natural vegetation remains outside. The same fence segments are used for
 * physics, avoiding ghost walls. This is additional art, not a replacement
 * for the approved industrial WebPs or the immutable character sprites.
 */
public final class WorldCivilizationArtV159 {
    private WorldCivilizationArtV159(){}
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG);
    private static final int[] FENCE={
        0xff879c91,0xff957654,0xff9e9d8a
    };
    private static int mix(int color,int shade){
        int r=Math.min(255,Math.max(0,((color>>16)&255)+shade));
        int g=Math.min(255,Math.max(0,((color>>8)&255)+shade));
        int b=Math.min(255,Math.max(0,(color&255)+shade));
        return 0xff000000|(r<<16)|(g<<8)|b;
    }
    private static void paint(Canvas c,float x,float y,float w,float h,int color){
        if(w<=0||h<=0)return;
        P.setStyle(Paint.Style.FILL);P.setColor(color);P.setShader(null);
        c.drawRect(x,y,x+w,y+h,P);
    }
    /** Planned parcel geography is immutable; authored materials paint it. */
    public static void ground(Canvas c,WorldCivilizationV159.Plan plan,
                              float camX,float camY,float viewW,float viewH){
        ground(c,plan,camX,camY,viewW,viewH,1f);
    }
    public static void ground(Canvas c,WorldCivilizationV159.Plan plan,
                              float camX,float camY,float viewW,float viewH,float zoom){
        SettlementGroundArtV166.draw(c,plan,camX,camY,viewW,viewH);
    }
    private static void drawFence(Canvas c,WorldCivilizationV159.Segment s,
                                  float camX,float camY,float width,float height){
        if(Math.max(s.x1,s.x2)<camX-35||Math.min(s.x1,s.x2)>camX+width+35||
           Math.max(s.y1,s.y2)<camY-35||Math.min(s.y1,s.y2)>camY+height+35)
            return;
        boolean wood=s.material==WorldCivilizationV159.VILLAGE;
        boolean vertical=s.vertical();
        float len=vertical?Math.abs(s.y2-s.y1):Math.abs(s.x2-s.x1);
        float dx=vertical?0f:1f,dy=vertical?1f:0f;
        float a=vertical?Math.min(s.y1,s.y2):Math.min(s.x1,s.x2);
        float fixed=vertical?s.x1:s.y1;
        float x=vertical?fixed:a,y=vertical?a:fixed;
        int metal=FENCE[s.material];
        P.setStyle(Paint.Style.STROKE);
        P.setStrokeCap(Paint.Cap.SQUARE);
        P.setStrokeWidth(18);
        P.setColor(0xa61a2728);
        c.drawLine(x+4,y+5,x+dx*len+4,y+dy*len+5,P);
        P.setStrokeWidth(wood?12f:7f);
        P.setColor(mix(metal,-38));
        c.drawLine(x,y,x+dx*len,y+dy*len,P);
        P.setStrokeWidth(wood?5f:3.5f);
        P.setColor(metal);
        c.drawLine(x+(vertical?-7f:0),y+(vertical?0:-6f),
            x+dx*len+(vertical?-7f:0),
            y+dy*len+(vertical?0:-6f),P);
        c.drawLine(x+(vertical?7f:0),y+(vertical?0:6f),
            x+dx*len+(vertical?7f:0),
            y+dy*len+(vertical?0:6f),P);
        P.setStyle(Paint.Style.FILL);
        float step=wood?104f:122f;
        int num=Math.max(1,(int)Math.ceil(len/step));
        for(int i=0;i<=num;i++){
            float t=i/(float)num*len;
            float px=x+dx*t,py=y+dy*t;
            if(px<camX-38||px>camX+width+38||
               py<camY-38||py>camY+height+38)continue;
            paint(c,px-(wood?10:7),py-(wood?10:7),
                wood?20:14,wood?20:14,0xff22302f);
            paint(c,px-(wood?7:4),py-(wood?7:4),
                wood?14:8,wood?14:8,metal);
            if(!wood){
                paint(c,px-2f,py-2f,4f,4f,0xffd1b88a);
                float nx=vertical?12f:0f,ny=vertical?0f:12f;
                // Rivets and cross-braces only on long industrial/urban
                // segments, never over the road gate gaps.
                if(i<num){
                    P.setStrokeWidth(1.8f);P.setColor(0xbcd1c4a6);
                    P.setStyle(Paint.Style.STROKE);
                    float end=Math.min(len,t+70f);
                    c.drawLine(px+nx,py+ny,
                        x+dx*end-nx,y+dy*end-ny,P);
                    P.setStyle(Paint.Style.FILL);
                }
            }
        }
    }
    /** Always render exterior fences AFTER environment/building sprites but
     * BEFORE characters. Gates are genuinely open on both sides of the road.
     */
    public static void fences(Canvas c,WorldCivilizationV159.Plan plan,
                              float camX,float camY,float viewW,float viewH){
        if(plan==null)return;
        c.save();c.clipRect(camX-35,camY-35,camX+viewW+35,camY+viewH+35);
        for(WorldCivilizationV159.Parcel p:plan.parcels){
            if(!p.onScreen(camX,camY,viewW,viewH))continue;
            for(WorldCivilizationV159.Segment segment:p.fences)
                drawFence(c,segment,camX,camY,viewW,viewH);
        }
        c.restore();
    }
    public static void industrialFence(Canvas c,int seed,
                                       float camX,float camY,float width,float height){
        if(camX+width<IndustrialBiomeBridgeV128.WEST-340f||
           camX>IndustrialBiomeBridgeV128.EAST+340f||
           camY+height<IndustrialBiomeBridgeV128.NORTH-340f||
           camY>IndustrialBiomeBridgeV128.SOUTH+340f)return;
        c.save();c.clipRect(camX-35,camY-35,camX+width+35,camY+height+35);
        for(WorldCivilizationV159.Segment f:IndustrialPerimeterV159.segments(seed))
            drawFence(c,f,camX,camY,width,height);
        c.restore();
    }
}
