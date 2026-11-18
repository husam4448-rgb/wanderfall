package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;

/**
 * V164 authored top-down camp art with actual readable structures: two
 * walk-through open tents, occupied trade/medical posts, guard barricade,
 * stocked lockable crate, tools, pallets, poles, rugs, paths, seam stitching.
 * There are NO tent collision rectangles or teleport portals.
 */
public final class CampArtV164 {
    private CampArtV164(){}
    private static void rect(Canvas c,Paint p,float x,float y,float w,float h,int color){
        if(w<=0||h<=0)return;
        p.setColor(color);p.setStyle(Paint.Style.FILL);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private static void line(Canvas c,Paint p,float x,float y,float xx,float yy,
                             float width,int color){
        p.setColor(color);p.setStyle(Paint.Style.STROKE);
        p.setStrokeCap(Paint.Cap.SQUARE);p.setStrokeWidth(width);
        c.drawLine(x,y,xx,yy,p);p.setStyle(Paint.Style.FILL);
    }
    private static void poly(Canvas c,Paint p,int color,float... points){
        Path path=new Path();
        path.moveTo(points[0],points[1]);
        for(int i=2;i<points.length;i+=2)path.lineTo(points[i],points[i+1]);
        path.close();p.setColor(color);p.setStyle(Paint.Style.FILL);
        c.drawPath(path,p);
    }
    private static void oval(Canvas c,Paint p,float x,float y,float w,float h,int color){
        p.setColor(color);p.setStyle(Paint.Style.FILL);
        c.drawOval(x,y,x+w,y+h,p);
    }
    private static void label(Canvas c,Paint p,String s,float x,float y,int color){
        p.setColor(0xff152725);p.setTextSize(16f);
        p.setTypeface(android.graphics.Typeface.create("monospace",
            android.graphics.Typeface.BOLD));
        c.drawText(s,x+1,y+2,p);
        p.setColor(color);c.drawText(s,x,y,p);
    }
    private static int hash(CampWorldV164.Site s,int k){
        return IndustrialWorldV123.hash(s.tx*17+k*29,
            s.ty*23+k*31,s.seed^s.variation*101);
    }
    public static void drawGround(Canvas c,Paint p,CampWorldV164.Site s,
                                  boolean reduced){
        float x=s.x,y=s.y;
        // Meadow/clearing is porous and organic; even a city camp is placed
        // on the green of an abandoned OPEN lot, not the rooftop of a house.
        oval(c,p,x-470,y-295,x+470,y+317,0x77718b63);
        oval(c,p,x-435,y-260,x+430,y+283,0x665d7452);
        oval(c,p,x-310,y-260,x+370,y+289,0x53686652);
        // V165 pigment art does not seal tent doorways or alter movement.
        Path clearing=new Path();
        clearing.addOval(x-390,y-258,x+395,y+275,Path.Direction.CW);
        SurfaceArtV165.path(c,clearing,SurfaceArtV165.SOIL,300f,81);
        // Cut-stone walking trail, wood chips, and scuffed foot tracks.
        poly(c,p,0x90715f4c,x-78,y+294,x-95,y+155,x-120,y+50,
            x-130,y-90,x-75,y-102,x+9,y+57,x+18,y+200,x+28,y+308);
        poly(c,p,0x8875684f,x-70,y+290,x-75,y+162,x-104,y+56,
            x-106,y-71,x-86,y-74,x-2,y+63,x+1,y+215,x+8,y+303);
        int details=reduced?30:86;
        for(int i=0;i<details;i++){
            int h=hash(s,i+7);
            float xx=x-450+Math.floorMod(h,900);
            float yy=y-280+Math.floorMod(h>>>10,560);
            if(Math.abs(xx-x)<60&&Math.abs(yy-y)<115)continue;
            if((h&3)==0){
                line(c,p,xx,yy,xx-5,yy-12,2f,0xff506c47);
                line(c,p,xx+1,yy,xx+6,yy-9,2f,0xff81965b);
                line(c,p,xx+2,yy-3,xx+2,yy-12,1.5f,0xffb2a76c);
            }else if((h&3)==1){
                oval(c,p,xx-5,yy-3,xx+9,yy+4,0x80685e4d);
                rect(c,p,xx-1,yy-3,7,3,0xff99947a);
            }else if((h&3)==2){
                line(c,p,xx-7,yy+2,xx+6,yy-2,2.5f,0x78644533);
            }else rect(c,p,xx,yy,3,2,0xff8b9b67);
        }
        // Ground contact details are permanently visible through tents.
        for(int a:new int[]{-210,200}){
            oval(c,p,x+a-130,y-255,x+a+130,y-58,0x66504438);
            rect(c,p,x+a-100,y-204,200,115,0xff6b5f49);
            for(int j=0;j<5;j++)
                line(c,p,x+a-95,y-196+j*26,x+a+93,y-196+j*26,
                    2,0xff8d7652);
        }
        // Fire ring is drawn underneath a depth-sorted, actual live campfire.
        float fx=s.fireX(),fy=s.fireY();
        oval(c,p,fx-72,fy-49,fx+72,fy+62,0x99504433);
        for(int i=0;i<11;i++){
            double angle=i*Math.PI*2/11;
            float px=fx+(float)Math.cos(angle)*62f;
            float py=fy+(float)Math.sin(angle)*44f;
            oval(c,p,px-12,py-6,px+14,py+10,
                i%3==0?0xffa99f83:0xff575952);
        }
    }
    private static void canvasTent(Canvas c,Paint p,float x,float y,
                                   int variant,boolean olive){
        if(CampSpriteArtV1651.drawTent(c,x,y,olive))return;
        int dark=0xff172b2a;
        int fabric=olive?0xff596e56:0xff8b8061;
        int sun=olive?0xff9aa47a:0xffc2af80;
        int shadow=olive?0xff3f5949:0xff6c6650;
        // A top-down rectangular tent whose middle is an OPEN floor, not a
        // filled solid box. There is a 118-unit front doorway.
        poly(c,p,dark,x-143,y-74,x-99,y-154,x+101,y-154,x+145,y-74,
            x+140,y+93,x-141,y+93);
        poly(c,p,fabric,x-136,y-70,x-95,y-147,x+95,y-147,x+138,y-70,
            x+133,y-27,x-133,y-27);
        poly(c,p,sun,x-90,y-143,x+92,y-143,x+130,y-75,x-130,y-75);
        // Ridge, ropes and stitched fabric: hand-placed silhouettes.
        line(c,p,x,y-145,x,y-51,4f,0xff314840);
        line(c,p,x-84,y-135,x-121,y-70,2,0xffb6ae8b);
        line(c,p,x+84,y-135,x+121,y-70,2,0xffb6ae8b);
        for(int i=0;i<11;i++){
            float xx=x-84+i*17;
            line(c,p,xx,y-133,xx+10,y-120,1.4f,0xffbcb69a);
        }
        // Left and right canvas flaps, with dark open doorway at center.
        poly(c,p,dark,x-134,y-31,x-121,y+89,x-55,y+88,x-48,y-31);
        poly(c,p,shadow,x-127,y-32,x-112,y+82,x-61,y+82,x-55,y-29);
        poly(c,p,dark,x+48,y-31,x+55,y+88,x+121,y+89,x+134,y-31);
        poly(c,p,shadow,x+55,y-29,x+61,y+82,x+112,y+82,x+127,y-32);
        rect(c,p,x-49,y-32,98,111,0x44212d29);
        // Actual bedding and supplies visible inside the open canopy.
        rect(c,p,x-35,y+12,31,49,0xff303d37);
        rect(c,p,x-31,y+16,23,40,0xffb5a785);
        rect(c,p,x-30,y+19,21,10,0xffded4b7);
        rect(c,p,x+12,y+29,28,26,0xff162927);
        rect(c,p,x+15,y+32,22,20,0xff766a4d);
        rect(c,p,x+18,y+38,16,6,0xffb59f70);
        // Wooden pegs and guy lines stay thin and have no blocking hitbox.
        for(int side:new int[]{-1,1}){
            float anchor=x+side*143f;
            line(c,p,anchor,y-37,x+side*164f,y+108,2f,0xffd0b88a);
            rect(c,p,x+side*163f-4,y+99,8,18,0xff3a392b);
            rect(c,p,x+side*163f-2,y+102,4,12,0xff988664);
        }
        // Vary the flap stitching/seam tape without altering collision.
        rect(c,p,x-132,y-24,10,7,0xffc4af7b);
        rect(c,p,x+122,y-24,10,7,0xffc4af7b);
        if((variant&1)==0){
            line(c,p,x-117,y+12,x-71,y+15,2f,0xffb7ae8a);
            line(c,p,x+74,y+17,x+120,y+14,2f,0xffb7ae8a);
        }
    }
    private static void storage(Canvas c,Paint p,float x,float y){
        // Tapered, shaded reinforced supply chest with actual lock and straps.
        oval(c,p,x-69,y-38,x+74,y+43,0x5b132223);
        rect(c,p,x-69,y-54,138,103,0xff1b2b2a);
        rect(c,p,x-62,y-49,124,91,0xff8e7049);
        rect(c,p,x-55,y-43,110,79,0xffa88857);
        rect(c,p,x-56,y-13,112,6,0xff544635);
        rect(c,p,x-13,y-44,25,82,0xff494b3d);
        rect(c,p,x-9,y-44,17,82,0xffc6b083);
        for(int sx:new int[]{-50,43})for(int sy:new int[]{-40,27})
            rect(c,p,x+sx,y+sy,6,5,0xffe6c78d);
        rect(c,p,x-12,y-3,25,17,0xff1a3031);
        rect(c,p,x-7,y+1,15,9,0xffdfbf77);
        rect(c,p,x-3,y+1,6,4,0xff243938);
        label(c,p,"SUPPLIES",x-46,y+64,0xffe5cf9b);
    }
    private static void tradeStand(Canvas c,Paint p,float x,float y){
        // Counter and open merchant stall: shelves stocked with real-looking
        // produce, jerrycans, rifles, med packets and assorted small goods.
        oval(c,p,x-111,y-86,x+115,y+95,0x74202a24);
        rect(c,p,x-109,y-103,219,39,0xff1b302d);
        poly(c,p,0xffa17955,x-110,y-87,x-80,y-140,x+75,y-140,x+111,y-87);
        poly(c,p,0xffc0ad77,x-94,y-97,x-77,y-135,x+72,y-135,x+94,y-97);
        for(int i=0;i<9;i++)
            line(c,p,x-70+i*17,y-128,x-58+i*17,y-108,2f,0xffdfc59c);
        for(int sx:new int[]{-100,97}){
            rect(c,p,x+sx-5,y-102,11,160,0xff203231);
            rect(c,p,x+sx-2,y-100,5,154,0xff927250);
        }
        rect(c,p,x-95,y-57,188,38,0xff374744);
        rect(c,p,x-89,y-54,178,31,0xff8f7855);
        for(int i=0;i<8;i++){
            float bx=x-79+i*21f;
            int color=i%3==0?0xffe4e3c7:i%3==1?0xff8baf84:0xffd6b16a;
            rect(c,p,bx,y-52,14,16,0xff253735);
            rect(c,p,bx+2,y-49,10,12,color);
        }
        rect(c,p,x-106,y+16,212,49,0xff253634);
        rect(c,p,x-101,y+17,202,40,0xff8e7651);
        rect(c,p,x-97,y+23,190,7,0xffc3a47a);
        rect(c,p,x-86,y+30,21,20,0xff4b625e);
        rect(c,p,x-82,y+33,12,11,0xff9dbfbc);
        rect(c,p,x+60,y+30,22,20,0xff23362f);
        rect(c,p,x+64,y+33,15,15,0xffd2c18e);
        label(c,p,"TRADE",x-28,y+78,0xffffdfaa);
    }
    private static void medicPost(Canvas c,Paint p,float x,float y){
        // Dedicated open treatment station and olive canvas shade; patient
        // cot stays accessible from front and sides.
        oval(c,p,x-96,y-90,x+99,y+91,0x6220312e);
        poly(c,p,0xff22332f,x-102,y-48,x-67,y-112,x+72,y-112,x+102,y-48);
        poly(c,p,0xff72806b,x-93,y-49,x-66,y-105,x+67,y-105,x+94,y-49);
        poly(c,p,0xff9caf89,x-72,y-93,x+72,y-93,x+87,y-58,x-87,y-58);
        for(int side:new int[]{-1,1})
            rect(c,p,x+side*90-4,y-51,9,115,0xff3a443a);
        rect(c,p,x-70,y-25,135,63,0xff253936);
        rect(c,p,x-61,y-22,118,58,0xffb5ae94);
        rect(c,p,x-57,y-18,38,19,0xffe5e4cc);
        rect(c,p,x-57,y+5,110,26,0xff637e74);
        rect(c,p,x+30,y-16,23,27,0xffece9df);
        rect(c,p,x+38,y-13,8,21,0xffbb594c);
        rect(c,p,x+31,y-7,21,8,0xffbb594c);
        // Medicine box and labelled medical shelf.
        rect(c,p,x+67,y+12,32,26,0xff1b2f30);
        rect(c,p,x+71,y+15,25,19,0xffdbddc5);
        rect(c,p,x+80,y+18,7,13,0xffc34b41);
        rect(c,p,x+76,y+22,15,6,0xffc34b41);
        label(c,p,"MEDIC",x-38,y+84,0xffe2e7bf);
    }
    private static void watchPost(Canvas c,Paint p,float x,float y){
        // A guard post with a two-sided sandbag breastwork and a weapon rack.
        oval(c,p,x-95,y-39,x+94,y+76,0x65202c24);
        for(int row=0;row<2;row++)for(int i=0;i<5;i++){
            float xx=x-94+i*39+(row%2)*11;
            rect(c,p,xx,y+42+row*22,35,21,0xff263632);
            rect(c,p,xx+3,y+44+row*22,29,17,
                (i+row)%2==0?0xff96815c:0xffb7a179);
            line(c,p,xx+6,y+49+row*22,xx+27,y+49+row*22,
                2f,0xffe3c493);
        }
        rect(c,p,x+60,y-81,8,118,0xff263a36);
        rect(c,p,x+65,y-78,4,113,0xffb69963);
        line(c,p,x+35,y-54,x+90,y-54,8f,0xff2a3334);
        line(c,p,x+37,y-56,x+87,y-56,3f,0xffa6aaa0);
        rect(c,p,x+62,y-66,12,18,0xff6b4937);
        label(c,p,"WATCH",x-41,y+97,0xfff0d39a);
    }
    private static void clutter(Canvas c,Paint p,float x,float y,int variant){
        // Nonblocking atmospheric props around the meadow perimeter.
        for(int i=0;i<4;i++){
            float bx=x-410+i*240f,by=y+234+(i%2)*18;
            rect(c,p,bx-13,by-4,62,24,0xff1e2c2a);
            rect(c,p,bx-9,by-12,54,29,0xff836247);
            rect(c,p,bx-6,by-8,49,7,0xffc09b61);
            for(int j=0;j<4;j++)
                line(c,p,bx+j*13-4,by+1,bx+j*13-4,by+16,2,0xff523f31);
        }
        // Water drums and solar charging board.
        for(int i=0;i<3;i++){
            float ax=x+286+i*31,ay=y-235+(i%2)*6;
            rect(c,p,ax-13,ay-13,26,47,0xff1d3436);
            rect(c,p,ax-10,ay-11,20,42,0xff58777a);
            rect(c,p,ax-10,ay-10,20,6,0xffa3b5a2);
            rect(c,p,ax-10,ay+19,20,5,0xff91a9a9);
            oval(c,p,ax-9,ay-15,ax+9,ay-7,0xffc0bb9c);
        }
        rect(c,p,x-420,y-260,132,74,0xff1c3235);
        rect(c,p,x-414,y-254,120,62,0xff537c83);
        for(int k=1;k<5;k++)line(c,p,x-414+k*24,y-253,
            x-414+k*24,y-192,2,0xffd5d9bb);
        for(int k=1;k<3;k++)line(c,p,x-413,y-254+k*21,
            x-294,y-254+k*21,2,0xffd5d9bb);
        if((variant&1)==0){
            for(int j=0;j<6;j++)
                rect(c,p,x-420+j*16,y-104,8,24,0xff715638);
        }
    }

    /** Visible camp structures have foreground lips ordered by world Y.
     * They do NOT introduce teleport doors, tent collision, or character art.
     * 0/1: tent side drapes, 2: trader counter, 3: medic cot, 4: guard bags.
     */
    public static float foregroundY(CampWorldV164.Site s,int kind){
        if(kind<2)return s.y+(s.starter?-185f:-153f)+100f;
        if(kind==2)return s.y+(s.starter?34f:125f)+67f;
        if(kind==3)return s.y+(s.starter?42f:119f)+40f;
        return s.y+(s.starter?5f:273f)+91f;
    }
    public static void foreground(Canvas c,Paint p,CampWorldV164.Site s,int kind){
        float x=s.x,y=s.y;
        if(kind<2){
            if(kind==0)CampSpriteArtV1651.drawFront(c,
                x+(s.starter?-300f:-205f),
                y+(s.starter?-185f:-153f),true);
            else CampSpriteArtV1651.drawFront(c,
                x+(s.starter?225f:186f),
                y+(s.starter?-185f:-153f),false);
            return;
        }
        float cx=x+(s.starter?-215f:-255f);
        float cy=y+(s.starter?34f:125f);
        if(kind==2){
            // The existing physical front counter occludes characters behind
            // it; sprites are never simply painted on top of all actors.
            rect(c,p,cx-107,cy+17,214,50,0xff253634);
            rect(c,p,cx-100,cy+20,200,40,0xff826c4e);
            rect(c,p,cx-96,cy+23,192,8,0xffc4a679);
            for(int i=0;i<9;i++){
                float xx=cx-90+i*23f;
                line(c,p,xx,cy+33,xx-2,cy+55,1.2f,
                    i%2==0?0xff665139:0xffa28a64);
            }
            rect(c,p,cx-85,cy+36,22,18,0xff344f4b);
            rect(c,p,cx-81,cy+39,13,10,0xff9ab5b0);
            rect(c,p,cx+61,cy+37,23,18,0xff343d33);
            rect(c,p,cx+64,cy+41,15,10,0xffc1b684);
            label(c,p,"TRADE",cx-28,cy+78,0xffffdfaa);
            return;
        }
        if(kind==3){
            cx=x+(s.starter?4f:155f);
            cy=y+(s.starter?42f:119f);
            rect(c,p,cx-70,cy-2,135,42,0xff263a35);
            rect(c,p,cx-61,cy+2,119,33,0xff9c9d86);
            rect(c,p,cx-57,cy+6,37,23,0xffdfdfca);
            rect(c,p,cx+31,cy+6,22,24,0xffe9e9d4);
            rect(c,p,cx+37,cy+9,9,19,0xffb74b46);
            rect(c,p,cx+33,cy+14,18,8,0xffb74b46);
            return;
        }
        cx=x+(s.starter?222f:55f);
        cy=y+(s.starter?5f:273f);
        for(int row=0;row<2;row++)for(int i=0;i<5;i++){
            float xx=cx-94+i*39+(row&1)*11;
            rect(c,p,xx,cy+42+row*22,35,21,0xff263632);
            rect(c,p,xx+3,cy+44+row*22,29,17,
                (i+row)%2==0?0xff96815c:0xffb7a179);
        }
    }

    public static void drawStructures(Canvas c,Paint p,CampWorldV164.Site s){
        float x=s.x,y=s.y;
        if(s.starter){
            // Never paint across the historical y=925 highway beside the
            // original player spawn; the larger countryside layouts use
            // the uncompressed full-sized version instead.
            c.save();
            c.clipRect(x-470,y-350,x+470,y+210);
            canvasTent(c,p,x-300,y-185,s.variation,true);
            canvasTent(c,p,x+225,y-185,s.variation+3,false);
            tradeStand(c,p,x-215,y+34);
            medicPost(c,p,x+4,y+42);
            watchPost(c,p,x+222,y+5);
            storage(c,p,s.chestX(),s.chestY());
            // Solar panels and supplies occupy unused shaded corners.
            rect(c,p,x-420,y+99,107,69,0xff172c2d);
            rect(c,p,x-415,y+104,97,59,0xff5e8791);
            for(int i=1;i<4;i++)
                line(c,p,x-415+i*24,y+105,x-415+i*24,y+162,
                    2,0xffc3d6d5);
            for(int i=1;i<3;i++)
                line(c,p,x-414,y+104+i*20,x-318,y+104+i*20,
                    2,0xffc3d6d5);
            c.restore();
        }else{
            canvasTent(c,p,x-205,y-153,s.variation,true);
            canvasTent(c,p,x+186,y-153,s.variation+3,false);
            tradeStand(c,p,x-255,y+125);
            medicPost(c,p,x+155,y+119);
            watchPost(c,p,x+55,y+273);
            storage(c,p,s.chestX(),s.chestY());
            clutter(c,p,x,y,s.variation);
        }
    }
}
