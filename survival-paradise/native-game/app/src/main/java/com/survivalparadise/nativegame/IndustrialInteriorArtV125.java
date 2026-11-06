package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;

/** V125 art layer fitted to the real V123 indoor collision, rooms and loot. */
public final class IndustrialInteriorArtV125 {
    private IndustrialInteriorArtV125(){}
    private static final int INK=0xff20272a,STEEL=0xff3c4c4d,
        RUST=0xff845339,LINE=0xffb29457,LIGHT=0xffd4af6f;
    private static void rect(Canvas c,Paint p,float x,float y,float w,float h,int color){
        p.setColor(color);p.setStyle(Paint.Style.FILL);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private static void line(Canvas c,Paint p,float x,float y,float xx,float yy,
                             float width,int color){
        p.setColor(color);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(width);
        c.drawLine(x,y,xx,yy,p);p.setStyle(Paint.Style.FILL);
    }
    private static void circle(Canvas c,Paint p,float x,float y,float radius,int color){
        p.setColor(color);p.setStyle(Paint.Style.FILL);c.drawCircle(x,y,radius,p);
    }
    private static int hash(IndustrialInteriorV123 room,int i,int salt){
        return IndustrialWorldV123.hash(room.district.sx*53+i,
            room.district.sy*29-i,room.district.seed^salt);
    }
    /** Painted into the actual concrete/metal substrate, not overlay stickers. */
    public static void ground(Canvas c,Paint p,IndustrialInteriorV123 room){
        int kind=room.district.kind;
        int background=kind==2?0xff383d3c:kind==4?0xff454b49:
            kind==3?0xff4a4844:0xff444b4a;
        rect(c,p,0,0,2720,1904,0xff171e21);
        rect(c,p,35,35,2650,1825,background);
        // Structured concrete slabs with weathering integrated in the surface.
        for(int col=0;col<29;col++)for(int row=0;row<20;row++){
            float x=37+col*92f,y=37+row*92f;
            int h=hash(room,col*23+row,0x74D541);
            rect(c,p,x+2,y+2,88,88,(h&3)==0?0x11343b37:
                (h&3)==1?0x132e3031:0x0c89907c);
            rect(c,p,x,y,92,1,0x2e1d2828);
            rect(c,p,x,y,1,92,0x291d2828);
            if(Math.floorMod(h,7)==0){
                float xx=x+12+Math.floorMod(h>>>8,55);
                float yy=y+11+Math.floorMod(h>>>15,43);
                line(c,p,xx,yy,xx+13,yy+7,2,0x5a25282a);
                line(c,p,xx+13,yy+7,xx+20,yy+15,1.8f,0x4825282a);
            }
            if(Math.floorMod(h>>>5,9)==0){
                circle(c,p,x+Math.floorMod(h>>>12,70)+12,
                    y+Math.floorMod(h>>>19,70)+12,11,0x18202522);
                circle(c,p,x+Math.floorMod(h>>>12,70)+10,
                    y+Math.floorMod(h>>>19,70)+9,4,0x20302524);
            }
        }
        // Wide central forklift route and cross-hall are kept free of clutter.
        rect(c,p,1080,38,560,1821,0xff575c56);
        rect(c,p,536,818,1644,214,0xff555951);
        rect(c,p,1110,39,11,1821,0x443a3c32);
        rect(c,p,1598,39,11,1821,0x443a3c32);
        rect(c,p,538,836,1640,5,0xff99804e);
        rect(c,p,538,1004,1640,5,0xff99804e);
        for(int i=0;i<11;i++){
            float y=79+i*155f;
            rect(c,p,1352,y,12,67,0xffae9562);
        }
        for(int i=0;i<5;i++){
            float x=1120+i*107;
            rect(c,p,x,826,48,7,0xffb3a17a);
            rect(c,p,x,996,48,7,0xffa59470);
        }
        // Actual drain plates are in floor, recessed, not separate rubble blobs.
        for(int i=0;i<9;i++){
            float y=135+i*188;
            drawDrain(c,p,1145,y,42,25);
            drawDrain(c,p,1520,y,42,25);
        }
        // Fitted machine foundation paint follows the exact collision rectangles.
        for(int i=0;i<room.machines.length;i++){
            float[] q=room.machines[i];
            rect(c,p,q[0]-16,q[1]-16,q[2]+32,q[3]+32,0x3234201b);
            rect(c,p,q[0]-13,q[1]-13,q[2]+26,4,0xffa48845);
            rect(c,p,q[0]-13,q[1]+q[3]+9,q[2]+26,4,0xffa48845);
            for(int j=0;j<5;j++){
                float x=q[0]-11+j*Math.max(14,q[2]/5f);
                line(c,p,x,q[1]+q[3]+11,x+12,q[1]+q[3]+11,
                    2.5f,0xff403b2c);
            }
        }
        // Door mouths are left open: paint only their fitted side thresholds.
        for(float y:new float[]{318,814,1319}){
            for(float x:new float[]{515,2187}){
                rect(c,p,x-13,y,36,7,0xffb28b4b);
                rect(c,p,x-13,y+141,36,7,0xffb28b4b);
            }
        }
    }
    private static void drawDrain(Canvas c,Paint p,float x,float y,float w,float h){
        rect(c,p,x-2,y-2,w+4,h+4,0xff293235);
        rect(c,p,x,y,w,h,0xff846b51);
        rect(c,p,x+4,y+4,w-8,h-8,0xff1c2829);
        for(int i=0;i<5;i++)rect(c,p,x+7+i*6,y+3,3,h-6,0xff556366);
        circle(c,p,x+3,y+3,2,0xffa6a099);
        circle(c,p,x+w-3,y+h-3,2,0xffa6a099);
    }
    private static void rivet(Canvas c,Paint p,float x,float y){
        circle(c,p,x,y,3,0xff142427);circle(c,p,x-.6f,y-.8f,1.4f,0xffa0a6a0);
    }
    private static void crate(Canvas c,Paint p,float x,float y,float w,float h,boolean full){
        rect(c,p,x-5,y-4,w+10,h+9,0xff263133);
        rect(c,p,x,y,w,h,full?0xff92613e:0xff3a4645);
        rect(c,p,x+4,y+4,w-8,h-8,full?0xffa37b52:0xff515a56);
        rect(c,p,x+5,y+5,w-10,3,0xffc79f60);
        rect(c,p,x+5,y+h-9,w-10,3,0xff48372e);
        line(c,p,x+8,y+8,x+w-8,y+h-8,2.2f,0xff4d4030);
        line(c,p,x+w-8,y+8,x+8,y+h-8,2.2f,0xff4d4030);
        rivet(c,p,x+7,y+8);rivet(c,p,x+w-7,y+8);
        rivet(c,p,x+7,y+h-7);rivet(c,p,x+w-7,y+h-7);
    }
    private static void cabinet(Canvas c,Paint p,float x,float y,float w,float h,int k){
        rect(c,p,x-3,y-3,w+6,h+6,0xff19262b);
        rect(c,p,x,y,w,h,0xff526163);
        rect(c,p,x+6,y+8,w-12,h*.45f,k==4?0xff3b6669:0xff3a4242);
        rect(c,p,x+11,y+14,w-22,h*.17f,0xff1d3033);
        for(int i=0;i<4;i++){
            rect(c,p,x+11+i*(w-25)/4f,y+h*.62f,7,5,
                i==2?0xffc77438:0xffa2a65e);
        }
        rect(c,p,x+10,y+h-17,w-20,6,0xff82918a);
        rivet(c,p,x+5,y+5);rivet(c,p,x+w-5,y+h-5);
    }
    private static void pump(Canvas c,Paint p,float x,float y,float w,float h,int kind){
        rect(c,p,x-6,y-6,w+12,h+12,0xff1c292d);
        rect(c,p,x,y,w,h,0xff5f6665);
        rect(c,p,x+9,y+11,w-18,h-23,0xff2e3d3e);
        float cx=x+w*.42f,cy=y+h*.5f;
        float r=Math.min(w,h)*.26f;
        circle(c,p,cx,cy,r+9,0xff93623e);
        circle(c,p,cx,cy,r,0xff495a5b);
        circle(c,p,cx,cy,r*.64f,kind==2?0xffb15c28:0xff8f8f79);
        circle(c,p,cx,cy,r*.24f,0xff252d2e);
        for(int i=0;i<7;i++){
            float yy=y+17+i*7;
            rect(c,p,x+w*.71f,yy,w*.19f,3,0xff9eaa9e);
        }
        rect(c,p,x+w*.7f,y+h*.77f,w*.2f,9,0xffc3944a);
        rivet(c,p,x+7,y+8);rivet(c,p,x+w-7,y+h-8);
    }
    private static void rack(Canvas c,Paint p,float x,float y,float w,float h,int seed){
        rect(c,p,x-3,y-3,w+6,h+6,0xff243035);
        rect(c,p,x,y,w,h,0xff5d4c3c);
        for(int i=0;i<4;i++){
            float xx=x+12+i*(w-24)/4f;
            rect(c,p,xx,y+12,(w-38)/4f,h-25,
                (i+seed)%3==0?0xff68756c:0xff87654a);
            rect(c,p,xx+5,y+19,(w-55)/4f,h*.12f,0xffbca076);
        }
        rect(c,p,x+5,y+5,w-10,5,0xffb1884a);
        rect(c,p,x+5,y+h-10,w-10,5,0xffb1884a);
        for(int i=0;i<5;i++){
            float xx=x+6+i*(w-12)/4;
            rivet(c,p,xx,y+8);rivet(c,p,xx,y+h-8);
        }
    }
    /** Decoration is contained inside real machine collision hulls or on walls. */
    public static void details(Canvas c,Paint p,IndustrialInteriorV123 room){
        int kind=room.district.kind;
        // Machine consoles, motors, tools and storage follow the existing
        // exact same 16 machine rectangles and deterministic room identity.
        for(int i=0;i<room.machines.length;i++){
            float[] q=room.machines[i];
            float x=q[0]+15,y=q[1]+12,w=q[2]-30,h=q[3]-24;
            if(w<35||h<28)continue;
            int mode=Math.floorMod(kind+i,4);
            if(i<6){
                if(mode==0||mode==2)pump(c,p,x+12,y+10,w-24,h-23,kind);
                else cabinet(c,p,x+12,y+11,w-24,h-22,kind);
            }else if(i<14){
                if(mode==0||mode==1)rack(c,p,x+6,y+4,w-12,h-8,kind+i);
                else crate(c,p,x+9,y+8,w-18,h-16,true);
            }else crate(c,p,x+5,y+3,w-10,h-6,true);
        }
        // Linear overhead trunking sits on wall edges, never across passage.
        for(int wing=0;wing<2;wing++){
            float xx=wing==0?57:2625;
            rect(c,p,xx,75,21,1690,0xff352f2b);
            rect(c,p,xx+5,75,6,1690,0xff9b623d);
            rect(c,p,xx+14,75,4,1690,0xffa28b69);
            for(int y=120;y<1720;y+=211){
                rect(c,p,xx-3,y,29,13,0xff4b5754);
                rivet(c,p,xx+4,y+7);rivet(c,p,xx+21,y+7);
            }
        }
        // Utility lights bring contrast and depth without large yellow circles.
        for(int side=0;side<2;side++)for(int row=0;row<7;row++){
            float x=side==0?567:2147,y=160+row*240;
            rect(c,p,x-25,y-7,50,14,0xff1c2a2c);
            rect(c,p,x-18,y-4,36,7,0xffd0a564);
            rect(c,p,x-12,y-1,24,3,0xffffd09a);
        }
        // Detail all 14 searchable boxes at their real V123 storage positions.
        for(int i=0;i<room.storages.length;i++){
            ClinicInteriorV89.Storage s=room.storages[i];
            if(s==null)continue;
            boolean supplies=!s.empty();
            if(i%4==0)cabinet(c,p,s.x-32,s.y-25,64,47,kind);
            else crate(c,p,s.x-31,s.y-21,62,42,supplies);
            if(supplies){
                rect(c,p,s.x-19,s.y-5,38,4,0xffbc9b62);
                rect(c,p,s.x-5,s.y+5,10,5,0xffd7b374);
            }
        }
        // Staged hazard hatching exactly at real main door.
        for(int i=0;i<7;i++)
            line(c,p,1247+i*34,1870,1262+i*34,1858,4,0xffb49a57);
    }
}
