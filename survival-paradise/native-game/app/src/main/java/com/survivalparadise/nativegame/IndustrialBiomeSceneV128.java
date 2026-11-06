package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.Shader;

/**
 * V128 joined-world draw pass. Rendered after the original V54 ground/biome
 * vegetation and before world actors, loot/constructed objects and the HUD.
 * Industrial geometry remains in its original seed-coordinate space.
 */
public final class IndustrialBiomeSceneV128 {
    private IndustrialBiomeSceneV128(){}
    private static final int WEST=IndustrialBiomeBridgeV128.WEST;
    private static final int EAST=IndustrialBiomeBridgeV128.EAST;
    private static final int NORTH=IndustrialBiomeBridgeV128.NORTH;
    private static final int SOUTH=IndustrialBiomeBridgeV128.SOUTH;
    private static final int ACCESS=IndustrialBiomeBridgeV128.ACCESS_ROAD_BEGIN_X;
    private static final int ROAD_Y=IndustrialBiomeBridgeV128.ROAD_CENTER_Y;

    private static int shade(int a,int b,float t){
        t=Math.max(0,Math.min(1,t));
        int ar=(a>>>16)&255,ag=(a>>>8)&255,ab=a&255;
        int br=(b>>>16)&255,bg=(b>>>8)&255,bb=b&255;
        return 0xff000000| (Math.round(ar+(br-ar)*t)<<16)
           |(Math.round(ag+(bg-ag)*t)<<8)|Math.round(ab+(bb-ab)*t);
    }
    private static boolean onScreen(float x,float y,float w,float h,
                                    float camX,float camY,float vw,float vh){
        return x+w>=camX&&x<=camX+vw&&y+h>=camY&&y<=camY+vh;
    }
    private static Path areaPath(int seed){
        Path p=new Path();
        p.moveTo(IndustrialBiomeBridgeV128.westEdge(NORTH,seed),
                 IndustrialBiomeBridgeV128.northEdge(WEST,seed));
        // The exact same smooth edge functions drive drawing and collision.
        for(int x=WEST;x<=EAST;x+=230)
            p.lineTo(x,IndustrialBiomeBridgeV128.northEdge(x,seed));
        p.lineTo(EAST,IndustrialBiomeBridgeV128.northEdge(EAST,seed));
        for(int y=NORTH;y<=SOUTH;y+=230)
            p.lineTo(IndustrialBiomeBridgeV128.eastEdge(y,seed),y);
        p.lineTo(IndustrialBiomeBridgeV128.eastEdge(SOUTH,seed),SOUTH);
        for(int x=EAST;x>=WEST;x-=230)
            p.lineTo(x,IndustrialBiomeBridgeV128.southEdge(x,seed));
        p.lineTo(WEST,IndustrialBiomeBridgeV128.southEdge(WEST,seed));
        for(int y=SOUTH;y>=NORTH;y-=230)
            p.lineTo(IndustrialBiomeBridgeV128.westEdge(y,seed),y);
        p.close();
        return p;
    }
    private static void approachRoad(Canvas c,Paint p,float camX,float camY,
                                     float vw,float vh,int seed){
        if(!onScreen(ACCESS-100,ROAD_Y-280,WEST-ACCESS+250,580,camX,camY,vw,vh))
            return;
        // Existing highway is 225 wide. Its shoulder widens smoothly to the
        // V124 270-wide arterial, with asphalt colour blending from old to new.
        Path surface=new Path();
        for(int i=0;i<=32;i++){
            float x=ACCESS+(WEST-ACCESS)*i/32f;
            float f=i/32f;
            float half=112.5f+22.5f*f;
            if(i==0)surface.moveTo(x,ROAD_Y-half);
            else surface.lineTo(x,ROAD_Y-half);
        }
        for(int i=32;i>=0;i--){
            float x=ACCESS+(WEST-ACCESS)*i/32f;
            float half=112.5f+22.5f*i/32f;
            surface.lineTo(x,ROAD_Y+half);
        }
        surface.close();
        p.setStyle(Paint.Style.FILL);
        p.setShader(new LinearGradient(ACCESS,ROAD_Y,WEST,ROAD_Y,
           new int[]{0xff565b50,0xff444b48,0xff303638},
           new float[]{0f,.56f,1f},Shader.TileMode.CLAMP));
        c.drawPath(surface,p);p.setShader(null);
        // The approach stripes follow the old road, then adopt the V124
        // narrower amber center dashes at the actual industrial intersection.
        for(int i=(int)Math.floor((camX-70-ACCESS)/110f);
            i<=Math.ceil((camX+vw+70-ACCESS)/110f);i++){
            float x=ACCESS+i*110f;
            if(x<ACCESS+35||x>WEST-48)continue;
            float t=(x-ACCESS)/(float)(WEST-ACCESS);
            p.setColor(0xffb5a16b);
            c.drawRect(x,ROAD_Y-3f,x+46f-7f*t,ROAD_Y+3f,p);
        }
        // Physical sign set in the shoulder, never in the usable traffic lane.
        if(onScreen(WEST-1020,ROAD_Y-255,390,120,camX,camY,vw,vh)){
            float x=WEST-900,y=ROAD_Y-212;
            p.setColor(0xff222d2d);
            c.drawRoundRect(x-42,y-19,x+263,y+26,5,5,p);
            p.setColor(0xffaa925d);p.setStrokeWidth(3f);
            c.drawLine(x-31,y-19,x-31,y+55,p);
            c.drawLine(x+249,y-19,x+249,y+55,p);
            p.setColor(0xffead3a5);p.setTextSize(23);
            p.setTypeface(android.graphics.Typeface.create("monospace",
                android.graphics.Typeface.BOLD));
            c.drawText("INDUSTRIAL  >",x-20,y+10,p);
        }
    }
    private static void groundRim(Canvas c,Paint p,
                                  float camX,float camY,float vw,float vh,int seed){
        // Procedural native sub-surface wear, not resized 'sticker' sprites.
        // Only near biome boundary, cheap to cull on normal factory gameplay.
        float startX=Math.max(WEST-500,camX-60),endX=Math.min(EAST+500,camX+vw+60);
        float startY=Math.max(NORTH-500,camY-60),endY=Math.min(SOUTH+500,camY+vh+60);
        if(startX>endX||startY>endY)return;
        int gx0=(int)Math.floor(startX/74),gx1=(int)Math.ceil(endX/74);
        int gy0=(int)Math.floor(startY/74),gy1=(int)Math.ceil(endY/74);
        for(int gy=gy0;gy<=gy1;gy++)for(int gx=gx0;gx<=gx1;gx++){
            float x=gx*74f,y=gy*74f;
            float strength=IndustrialBiomeBridgeV128.boundaryStrength(x,y,seed);
            if(strength<=.01f)continue;
            int n=IndustrialWorldV123.hash(gx,gy,seed^0x1A625);
            if(Math.floorMod(n,4)==0)continue;
            float a=(float)(Math.floorMod(n>>>7,13)+3)*strength;
            int opacity=Math.min(45,Math.max(0,Math.round(a*2.5f)));
            int color=(opacity<<24)|((n&1)==0?0x00605b4a:0x003b4542);
            p.setColor(color);
            float w=18+Math.floorMod(n>>>11,33);
            float h=9+Math.floorMod(n>>>17,21);
            c.drawOval(x,y,x+w,y+h,p);
            if((n&31)==11){
                p.setColor((Math.min(62,opacity+11)<<24)|0x002e3230);
                c.drawRect(x+3,y+3,x+24,y+5,p);
            }
        }
    }
    public static void draw(Canvas c,Paint p,IndustrialArtV123 art,
                            float camX,float camY,float vw,float vh,int seed){
        if(!onScreen(ACCESS,ROAD_Y-300,WEST-ACCESS+200,600,camX,camY,vw,vh)
            &&!onScreen(WEST-500,NORTH-500,EAST-WEST+1000,SOUTH-NORTH+1000,
                         camX,camY,vw,vh))return;
        approachRoad(c,p,camX,camY,vw,vh,seed);
        if(onScreen(WEST-150,NORTH-150,EAST-WEST+300,SOUTH-NORTH+300,
                    camX,camY,vw,vh)){
            c.save();
            c.clipPath(areaPath(seed));
            c.translate(IndustrialBiomeBridgeV128.ORIGIN_X,
                        IndustrialBiomeBridgeV128.ORIGIN_Y);
            IndustrialSceneV124.outdoors(c,p,
                 camX-IndustrialBiomeBridgeV128.ORIGIN_X,
                 camY-IndustrialBiomeBridgeV128.ORIGIN_Y,vw,vh,seed);
            art.outdoors(c,
                 camX-IndustrialBiomeBridgeV128.ORIGIN_X,
                 camY-IndustrialBiomeBridgeV128.ORIGIN_Y,vw,vh,seed);
            c.restore();
        }
        groundRim(c,p,camX,camY,vw,vh,seed);
    }
}
