package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/**
 * Camera-independent infinite industrial terrain: materials are continuous
 * across sector boundaries, and wear/traffic features are painted into their
 * parent surface rather than dropped as incompatible cutout decals.
 */
public final class IndustrialSceneV124 {
    private IndustrialSceneV124(){}
    private static void box(Canvas c,Paint p,float x,float y,float w,float h,int color){
        p.setStyle(Paint.Style.FILL);p.setColor(color);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private static void stroke(Canvas c,Paint p,float x,float y,float xx,float yy,int color,float width){
        p.setColor(color);p.setStrokeWidth(width);
        c.drawLine(x,y,xx,yy,p);
    }
    private static int hash(int sx,int sy,int seed,int slot){
        return IndustrialWorldV123.hash(sx*73+slot*17,sy*91-slot*11,seed^0x58F1E);
    }
    private static void concrete(Canvas c,Paint p,IndustrialOpenWorldV124.Plot plot){
        float x=plot.x,y=plot.y;
        int base=plot.type==IndustrialOpenWorldV124.VACANT?0xff514f48:
            plot.type==IndustrialOpenWorldV124.YARD?0xff56554d:0xff555650;
        box(c,p,x,y,1400,1400,base);
        if(plot.developed()){
            // Building yard and stock pads use one concrete material.
            box(c,p,x+95,y+105,1180,1115,0xff65655b);
            box(c,p,x+113,y+118,1144,1079,0xff67665c);
            box(c,p,x+118,y+175,1128,995,0xff69675d);
            // Material staining spreads organically from the working surfaces.
            box(c,p,x+150,y+850,1080,286,0x16412d24);
            box(c,p,x+140,y+1060,1020,91,0x16342b26);
            for(int i=0;i<10;i++){
                float yy=y+181+i*97f;
                stroke(c,p,x+127,yy,x+1220,yy,0x33473f37,2);
            }
            for(int i=0;i<12;i++){
                float xx=x+130+i*97f;
                stroke(c,p,xx,y+143,xx,y+1160,0x214a4840,2);
            }
            // A physical continuous driveway reaches the connected street.
            float cx=plot.doorX;
            box(c,p,cx-112,plot.doorY,224,486,0xff5a5950);
            box(c,p,cx-103,plot.doorY,206,487,0xff6c695d);
            for(int i=0;i<5;i++){
                stroke(c,p,cx-95,plot.doorY+85+i*82,cx+95,plot.doorY+85+i*82,
                    0x55413b32,3);
            }
            if(plot.gateSide==0){
                box(c,p,cx-106,y+1218,212,185,0xff5a5a53);
                stroke(c,p,cx-80,y+1280,cx+80,y+1280,0xffa58e5a,5);
            }else if(plot.gateSide==1){
                box(c,p,x,y+1260,745,136,0xff50514d);
                stroke(c,p,x+55,y+1328,x+650,y+1328,0xffb09a69,4);
            }else if(plot.gateSide==2){
                box(c,p,x+540,y+1260,860,136,0xff50514d);
                stroke(c,p,x+600,y+1328,x+1340,y+1328,0xffb09a69,4);
            }
            // The entry points remain clear: no machinery or debris on aprons.
            for(int i=0;i<3;i++){
                float py=plot.doorY+135+i*83;
                stroke(c,p,cx-24,py,cx,py-20,0xffb9a371,6);
                stroke(c,p,cx,py-20,cx+24,py,0xffb9a371,6);
            }
        }else{
            // Empty lots are a believable mix of earth/concrete, not a fake roof.
            box(c,p,x+100,y+125,1200,1020,0x20484338);
            box(c,p,x+182,y+211,1035,840,0x105f594c);
        }
        // Small-scale seed-stable scuffs, grit and cracks cover *all* lots.
        for(int i=0;i<128;i++){
            int h=hash(plot.sx,plot.sy,plot.seed,i);
            float xx=x+Math.floorMod(h,1380)+10, yy=y+Math.floorMod(h>>>9,1380)+10;
            int dot=Math.floorMod(h>>>22,4);
            int shade=(dot==0?0x17552e21:dot==1?0x23453731:
                dot==2?0x2053544c:0x26443c33);
            box(c,p,xx,yy,2+Math.floorMod(h>>>16,11),1+Math.floorMod(h>>>19,4),shade);
            if((h&63)==9){
                stroke(c,p,xx,yy,xx+23,yy+6,0x4a3c3934,2);
                stroke(c,p,xx+23,yy+6,xx+31,yy+16,0x333e3935,1.5f);
            }
        }
    }
    private static void road(Canvas c,Paint p,int sx,int sy,int seed){
        final float x=sx*(float)IndustrialOpenWorldV124.SIZE;
        final float y=sy*(float)IndustrialOpenWorldV124.SIZE;
        final int S=IndustrialOpenWorldV124.SIZE;
        boolean v=IndustrialOpenWorldV124.vertical(sx,sy,seed);
        boolean h=IndustrialOpenWorldV124.horizontal(sy,sx,seed);
        float vw=IndustrialOpenWorldV124.verticalWidth(sx);
        float hw=IndustrialOpenWorldV124.horizontalWidth(sy);
        if(v){
            box(c,p,x-vw*.5f-11,y, vw+22,S,0xff8a8270);
            box(c,p,x-vw*.5f-5,y,vw+10,S,0xff464846);
            box(c,p,x-vw*.5f,y,vw,S,0xff303638);
            // No black strip sticker edges: cracks are part of asphalt itself.
            stroke(c,p,x-vw*.5f+8,y,x-vw*.5f+8,y+S,0xff6a6554,3);
            stroke(c,p,x+vw*.5f-8,y,x+vw*.5f-8,y+S,0xff6a6554,3);
            for(int i=0;i<12;i++){
                if(h&&i<2)continue;
                float py=y+63+i*114;
                stroke(c,p,x,py,x,py+49,0xff9d8c58,5);
            }
        }
        if(h){
            box(c,p,x,y-hw*.5f-11,S,hw+22,0xff8a8270);
            box(c,p,x,y-hw*.5f-5,S,hw+10,0xff464846);
            box(c,p,x,y-hw*.5f,S,hw,0xff303638);
            stroke(c,p,x,y-hw*.5f+8,x+S,y-hw*.5f+8,0xff6a6554,3);
            stroke(c,p,x,y+hw*.5f-8,x+S,y+hw*.5f-8,0xff6a6554,3);
            for(int i=0;i<12;i++){
                if(v&&i<2)continue;
                float px=x+63+i*114;
                stroke(c,p,px,y,px+49,y,0xffa99866,5);
            }
        }
        if(v&&h){
            // Actual pavement-junction shading rather than isolated corner tile.
            float a=Math.max(vw,hw)*.5f+6;
            box(c,p,x-a,y-a,a*2,a*2,0xff34393a);
            for(int i=0;i<5;i++){
                float xx=x-vw*.5f+19+i*(vw-38)/5f;
                stroke(c,p,xx,y-hw*.5f-55,xx,y-hw*.5f-20,0xffa9a198,7);
            }
            box(c,p,x-32,y-30,64,60,0x16393734);
        }
        // Embedded asphalt pitting is bounded by active street footprints.
        for(int i=0;i<12;i++){
            int v0=hash(sx,sy,seed,i+200);
            float px=x+Math.floorMod(v0,1200)+60;
            float py=y+Math.floorMod(v0>>>10,1200)+60;
            if(!IndustrialOpenWorldV124.roadAt(px,py,seed))continue;
            box(c,p,px,py,7+Math.floorMod(v0>>>18,16),2,0x40332e2b);
        }
    }
    private static void pad(Canvas c,Paint p,float x,float y,float w,float h){
        box(c,p,x-8,y-8,w+16,h+16,0x443c372f);
        box(c,p,x,y,w,h,0xff666359);
        stroke(c,p,x,y,x+w,y,0xffab8f4e,4);
        stroke(c,p,x,y+h,x+w,y+h,0xffa18650,4);
        for(int i=0;i<5;i++){
            float xx=x+i*w/5;
            stroke(c,p,xx,y,xx+Math.min(30,w/8),y+14,0xffa18744,2);
        }
    }
    private static void yard(Canvas c,Paint p,IndustrialOpenWorldV124.Plot plot){
        if(!plot.developed())return;
        float x=plot.x,y=plot.y;
        // No pasted clutter ground sprites; native pads use the same substrate.
        if(plot.type==IndustrialOpenWorldV124.FACILITY){
            // Parking and machine pads have the same scale and positions as
            // the approved machinery source sprites (V126 shared art layout).
            pad(c,p,x+174,y+888,265,192);
            pad(c,p,x+998,y+836,214,189);
            if((plot.kind&1)==0)
                pad(c,p,x+866,y+1000,279,194);
            else pad(c,p,x+902,y+1000,306,204);
        }else{
            pad(c,p,x+214,y+689,260,194);
            pad(c,p,x+880,y+761,307,211);
            pad(c,p,x+200,y+902,258,221);
            pad(c,p,x+876,y+963,260,204);
        }
        // Chain-link fencing with a real 251-unit wide gap facing the road.
        box(c,p,x+110,y+1204,473,12,0xff4a4d48);
        box(c,p,x+830,y+1204,438,12,0xff4a4d48);
        for(int i=0;i<3;i++){
            float yy=y+1204;
            stroke(c,p,x+120+i*145,yy,x+140+i*145,yy+9,0xffa39775,2);
            stroke(c,p,x+840+i*132,yy,x+860+i*132,yy+9,0xffa39775,2);
        }
        box(c,p,x+98,y+130,12,1086,0xff545951);
        box(c,p,x+1265,y+130,12,1086,0xff545951);
        box(c,p,x+570,y+1190,14,36,0xffac8538);
        box(c,p,x+830,y+1190,14,36,0xffac8538);
    }
    /** World coordinates, called from GameView within its normal drawing stack. */
    public static void outdoors(Canvas c,Paint p,float camX,float camY,
                                float vw,float vh,int seed){
        int x0=IndustrialOpenWorldV124.sx(camX)-1;
        int x1=IndustrialOpenWorldV124.sx(camX+vw)+1;
        int y0=IndustrialOpenWorldV124.sy(camY)-1;
        int y1=IndustrialOpenWorldV124.sy(camY+vh)+1;
        for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++)
            concrete(c,p,IndustrialOpenWorldV124.plot(x,y,seed));
        for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++)
            road(c,p,x,y,seed);
        for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++)
            yard(c,p,IndustrialOpenWorldV124.plot(x,y,seed));
    }
}
