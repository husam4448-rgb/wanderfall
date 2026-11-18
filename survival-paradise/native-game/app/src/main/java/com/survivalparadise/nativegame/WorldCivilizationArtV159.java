package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;

/**
 * Civilization is drawn INSIDE authentic plotted lots and their fences.
 * Natural vegetation remains outside. The same fence segments are used for
 * physics, avoiding ghost walls. This is additional art, not a replacement
 * for the approved industrial WebPs or the immutable character sprites.
 */
public final class WorldCivilizationArtV159 {
    private WorldCivilizationArtV159(){}
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG);
    private static final Path SHAPE=new Path();
    private static final int[] BASE={
        0xff6f736c, // city: aged concrete
        0xff8a8068, // village: compacted earth
        0xff77766c  // outpost: industrial gravel
    };
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
    /** A region uses one material family, with natural, irregular weathering
     * instead of a visually flat 5km square or repeated tile checkerboard.
     */
    public static void ground(Canvas c,WorldCivilizationV159.Plan plan,
                              float camX,float camY,float viewW,float viewH){
        ground(c,plan,camX,camY,viewW,viewH,1f);
    }
    public static void ground(Canvas c,WorldCivilizationV159.Plan plan,
                              float camX,float camY,float viewW,float viewH,float zoom){
        if(plan==null)return;
        c.save();c.clipRect(camX-30,camY-30,camX+viewW+30,camY+viewH+30);
        for(WorldCivilizationV159.Parcel region:plan.parcels){
            if(!region.onScreen(camX,camY,viewW,viewH))continue;
            float x=region.left,y=region.top,w=region.right-x,h=region.bottom-y;
            // Slightly rounded, but planned fence corners remain square.
            // Industrial region is separately authored in V124/V128.
            P.setStyle(Paint.Style.FILL);
            // Preserve a faint trace of the procedural biome's color noise
            // underneath the developed surface. Fully opaque flat slabs
            // were visually artificial and destroyed terrain texture.
            int opacity=region.kind==WorldCivilizationV159.CITY?230:
                region.kind==WorldCivilizationV159.VILLAGE?205:224;
            P.setColor((opacity<<24)|(BASE[region.kind]&0xffffff));
            c.drawRoundRect(x,y,x+w,y+h,22f,22f,P);
            // Low-opacity hand-painted aggregate prevents homogeneous slabs;
            // park greenery and lane geometry are still drawn separately.
            SurfaceArtV165.rect(c,x+6f,y+6f,w-12f,h-12f,
                region.kind==WorldCivilizationV159.VILLAGE?
                    SurfaceArtV165.SOIL:SurfaceArtV165.CONCRETE,
                410f,region.kind==WorldCivilizationV159.VILLAGE?55:68);
            c.save();
            c.clipRect(x+2,y+2,x+w-2,y+h-2);
            for(int i=0;i<(zoom<.70f?11:44);i++){
                int rand=IndustrialWorldV123.hash(
                    region.tx*53+i*37,region.ty*71-i*29,
                    plan.seed^0x159A000+region.variation);
                float cx=x+68+Math.floorMod(rand,Math.max(1,(int)w-136));
                float cy=y+64+Math.floorMod(rand>>>9,Math.max(1,(int)h-128));
                float rx=25f+Math.floorMod(rand>>>17,165);
                float ry=12f+Math.floorMod(rand>>>23,93);
                P.setColor((region.kind==WorldCivilizationV159.VILLAGE?
                    0x2962473a:0x29343837));
                c.save();
                c.rotate(Math.floorMod(rand>>>13,160),cx,cy);
                SHAPE.reset();
                for(int v=0;v<10;v++){
                    double theta=v*Math.PI/5.0;
                    float jag=.74f+Math.floorMod(
                        IndustrialWorldV123.hash(v,i,rand),32)/100f;
                    float px=cx+(float)Math.cos(theta)*rx*jag;
                    float py=cy+(float)Math.sin(theta)*ry*jag;
                    if(v==0)SHAPE.moveTo(px,py);
                    else SHAPE.lineTo(px,py);
                }
                SHAPE.close();
                c.drawPath(SHAPE,P);
                c.restore();
            }
            // Fine stones and natural cracks instead of geometric floor grids.
            for(int i=0;i<(zoom<.70f?24:110);i++){
                int hsh=IndustrialWorldV123.hash(
                    region.tx*131+i*17,region.ty*119-i*23,plan.seed^0x15938);
                float px=x+28f+Math.floorMod(hsh,(int)Math.max(1,w-56));
                float py=y+22f+Math.floorMod(hsh>>>10,(int)Math.max(1,h-44));
                P.setColor(region.kind==WorldCivilizationV159.VILLAGE?
                    0x65644c36:0x45434b4a);
                float r=1.2f+Math.floorMod(hsh>>>22,4);
                c.drawOval(px-r,py-r*.5f,px+r*1.8f,py+r*.7f,P);
            }
            c.restore();
        }
        c.restore();
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
