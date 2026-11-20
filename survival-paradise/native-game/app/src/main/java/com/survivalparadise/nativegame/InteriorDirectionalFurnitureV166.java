package com.survivalparadise.nativegame;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.Rect;
import android.graphics.RectF;

/**
 * V166 directional furniture: 96 individually assigned functional objects,
 * each drawn in original forward AND side projection, not rotated bitmap art.
 * Drawing is rasterised once per requested variant; no allocations per frame.
 * All sprites remain inside their V163 collision rectangle.
 */
public final class InteriorDirectionalFurnitureV166 {
    private InteriorDirectionalFurnitureV166(){}
    public static final int FIRST=InteriorFurnitureCatalogV166.FIRST;
    public static final int COUNT=InteriorFurnitureCatalogV166.COUNT;
    private static final int[] BASE={
        0xff846b52,0xff6e7866,0xff797f77,0xff897661,
        0xff9c9079,0xff858675,0xff66746c,0xff5b6662
    };
    private static final int OUT=0xff1d2d31, EDGE=0xff2e4445,
        LIGHT=0xffd4c8aa, INK=0xff263b40, GLASS=0xff6e9a9a,
        STEEL=0xff697c7d, RUST=0xffa8774c, PAPER=0xffc9c6a8;
    private static final Bitmap[] CACHE=new Bitmap[COUNT*2];
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.DITHER_FLAG);
    private static final Paint BLIT=new Paint(Paint.FILTER_BITMAP_FLAG);
    private static final Rect SOURCE=new Rect(0,0,128,128);
    private static final RectF DEST=new RectF();

    public static boolean valid(int sprite){return InteriorFurnitureCatalogV166.valid(sprite);}
    public static int kind(int sprite){return InteriorFurnitureCatalogV166.kind(sprite);}
    private static void r(Canvas c,float x,float y,float w,float h,int color){
        if(w<=0||h<=0)return;
        P.setColor(color);P.setStyle(Paint.Style.FILL);
        c.drawRect(x,y,x+w,y+h,P);
    }
    private static void o(Canvas c,float x,float y,float w,float h,int color){
        P.setColor(color);P.setStyle(Paint.Style.FILL);
        c.drawOval(x,y,x+w,y+h,P);
    }
    private static void rr(Canvas c,float x,float y,float w,float h,float rad,int color){
        P.setColor(color);P.setStyle(Paint.Style.FILL);
        c.drawRoundRect(x,y,x+w,y+h,rad,rad,P);
    }
    private static void line(Canvas c,float x,float y,float xx,float yy,float thick,int color){
        P.setColor(color);P.setStrokeWidth(thick);P.setStrokeCap(Paint.Cap.ROUND);
        P.setStyle(Paint.Style.STROKE);c.drawLine(x,y,xx,yy,P);
        P.setStyle(Paint.Style.FILL);
    }
    private static void poly(Canvas c,int color,float... points){
        Path path=new Path();path.moveTo(points[0],points[1]);
        for(int i=2;i<points.length;i+=2)path.lineTo(points[i],points[i+1]);
        path.close();P.setColor(color);P.setStyle(Paint.Style.FILL);c.drawPath(path,P);
    }
    private static void casework(Canvas c,boolean side,int wood,int front,int high){
        // Original perspective: 3/4-view narrow gable on the side, broad
        // front with top-depth reveal on the south-facing variant.
        if(side){
            poly(c,OUT,27,17,103,23,104,116,26,111);
            poly(c,wood,32,19,76,24,91,109,32,106);
            poly(c,high,76,24,100,20,100,109,89,109);
            line(c,77,23,89,109,3,EDGE);
            r(c,38,41,34,48,front);
            r(c,42,45,26,38,high);
            r(c,68,58,4,13,LIGHT);
        }else{
            poly(c,OUT,9,24,113,24,119,111,7,111);
            poly(c,high,13,20,106,19,115,34,10,36);
            poly(c,wood,11,34,115,34,112,107,13,107);
            r(c,18,39,89,60,front);
            line(c,62,41,62,97,3,EDGE);
            r(c,54,64,3,13,LIGHT);r(c,67,64,3,13,LIGHT);
            line(c,15,101,110,101,4,INK);
        }
    }
    private static void shelved(Canvas c,boolean side,int wood,int high,int kind){
        casework(c,side,wood,INK,high);
        if(side){
            for(int n=0;n<3;n++){
                int y=40+n*20;
                r(c,39,y,36,4,LIGHT);
                for(int j=0;j<3;j++)r(c,41+j*10,y-10,7,10,
                    (j+n)%3==0?RUST:(j+n)%3==1?GLASS:0xffb1b49a);
            }
        }else{
            for(int n=0;n<3;n++){
                int y=43+n*19;
                r(c,18,y+13,89,5,OUT);
                for(int j=0;j<7;j++)
                    rr(c,21+j*12,y,9,13,2,
                        (j+n)%4==0?RUST:(j+n)%4==1?GLASS:
                        (j+n)%4==2?0xffaca66f:0xff768b72);
            }
        }
        if(kind==25){ // structural racking, obvious upright bracing
            line(c,15,24,16,109,5,RUST);line(c,110,24,109,109,5,RUST);
            line(c,17,25,109,106,3,INK);
        }
    }
    private static void table(Canvas c,boolean side,int wood,int high){
        o(c,8,102,114,17,0x66313833);
        if(side){
            poly(c,OUT,39,9,94,19,103,94,43,100);
            poly(c,high,43,13,88,19,93,89,47,94);
            r(c,41,94,9,20,INK);r(c,89,91,8,21,INK);
            line(c,46,52,92,47,3,LIGHT);
        }else{
            poly(c,OUT,15,19,112,19,117,94,11,94);
            poly(c,high,20,23,106,23,111,85,17,85);
            r(c,18,86,10,23,INK);r(c,101,86,10,23,INK);
            line(c,22,31,107,31,2,LIGHT);
        }
    }
    private static void topMachine(Canvas c,boolean side,int base,int high){
        casework(c,side,base,STEEL,high);
        rr(c,side?47:32,side?34:40,side?30:63,side?34:36,5,OUT);
        rr(c,side?51:36,side?38:44,side?22:55,side?25:28,3,GLASS);
        for(int k=0;k<4;k++)r(c,side?78:27+k*19,side?40+k*12:85,6,5,
            (k&1)==0?RUST:LIGHT);
    }
    private static void drawShape(Canvas c,int kind,boolean side,int theme){
        int wood=BASE[theme], high=(theme==5||theme==6)?0xffa1a59b:
            theme==3?0xffb5a187:0xffb59e7e;
        int textile=theme==3?0xff668b89:theme==7?0xff8b8b72:
            theme==0?0xff9a715e:0xff728f82;
        o(c,7,105,116,17,0x5523332e); // single grounded shadow
        switch(kind){
            case 0: // bed: headboard/pillows/stitched long quilt
                rr(c,side?34:13,side?6:15,side?62:103,side?116:95,5,OUT);
                rr(c,side?41:20,side?12:23,side?47:89,side?106:81,4,wood);
                if(side){
                    r(c,43,15,43,13,LIGHT);r(c,43,31,43,68,textile);
                    r(c,46,39,37,4,0xffb3b4a2);r(c,47,76,35,2,0xffc4ad8f);
                    r(c,41,100,46,8,INK);
                }else{
                    rr(c,25,27,34,24,3,LIGHT);rr(c,65,27,33,24,3,LIGHT);
                    r(c,24,56,78,43,textile);r(c,25,70,76,4,0xffbca98d);
                    r(c,28,95,70,6,0xffb4c0b2);
                }break;
            case 1: // couch, different top and lateral silhouette
                rr(c,side?45:11,side?9:27,side?69:106,side?108:82,9,OUT);
                rr(c,side?50:17,side?14:34,side?58:94,side?97:71,7,textile);
                if(side){
                    rr(c,53,20,19,91,5,high);
                    for(int n=0;n<3;n++)rr(c,75,19+n*29,27,25,5,
                        n==1?0xff829a8a:0xff97a698);
                    r(c,50,97,60,9,wood);
                }else{
                    rr(c,17,36,94,16,5,wood);
                    for(int n=0;n<3;n++)rr(c,20+n*30,56,27,36,5,
                        n==1?0xff839a87:0xff9fac91);
                    rr(c,11,49,12,50,3,high);rr(c,103,49,12,50,3,high);
                }break;
            case 2:case 10:case 11:case 30: // wardrobe / file cabinet / locker / dresser
                casework(c,side,wood,kind==11?STEEL:high,high);
                if(kind==10||kind==30){
                    for(int n=0;n<3;n++){
                        r(c,side?44:22,47+n*16,side?35:81,3,INK);
                        r(c,side?59:54,51+n*16,8,3,LIGHT);
                    }
                }else if(kind==11){
                    for(int n=0;n<5;n++)line(c,side?40:21,40+n*10,side?67:50,40+n*10,2,OUT);
                }
                break;
            case 3:case 4:case 14:case 31: // hob, sink, cooler, island
                casework(c,side,wood,high,0xffd1c2a4);
                if(kind==3){
                    if(side){
                        for(int i=0;i<3;i++)r(c,39,35+i*19,34,4,INK);
                        r(c,80,53,7,22,OUT);
                    }else{
                        for(int i=0;i<4;i++){
                            int xx=37+(i%2)*44,yy=47+(i/2)*27;
                            o(c,xx-10,yy-7,22,18,OUT);o(c,xx-6,yy-4,14,11,STEEL);
                        }
                    }
                }else if(kind==4||kind==31){
                    rr(c,side?43:24,43,side?36:76,32,7,STEEL);
                    rr(c,side?47:28,47,side?28:68,25,7,INK);
                    line(c,side?65:63,32,side?65:63,43,4,LIGHT);
                    line(c,side?65:63,31,side?77:78,32,4,STEEL);
                }else{
                    r(c,side?70:17,44,side?16:94,53,0xffc5d0c6);
                    r(c,side?75:23,55,side?6:78,4,INK);
                }
                break;
            case 5: // dining table, two plates, chair silhouettes
                table(c,side,wood,high);
                if(side){
                    o(c,53,38,24,14,PAPER);o(c,57,42,15,8,STEEL);
                    r(c,30,29,12,18,wood);r(c,30,77,12,18,wood);
                }else{
                    o(c,30,39,24,21,PAPER);o(c,75,39,24,21,PAPER);
                    o(c,36,45,11,11,STEEL);o(c,81,45,11,11,STEEL);
                }break;
            case 6:case 16:case 12: // desk, reception, checkout counter
                table(c,side,wood,high);
                if(kind==12){
                    rr(c,side?54:70,side?29:35,29,20,3,OUT);
                    r(c,side?58:74,side?34:39,21,12,GLASS);
                    r(c,side?52:46,side?67:69,38,8,STEEL);
                }else{
                    rr(c,side?54:31,side?24:31,side?28:49,side?23:28,3,OUT);
                    r(c,side?59:36,side?29:36,side?19:39,side?13:18,GLASS);
                    r(c,side?53:43,side?58:63,side?35:44,5,INK);
                    if(kind==16)r(c,side?45:18,81,side?37:88,7,WOOD_COLOR(theme));
                }break;
            case 7:case 17: // office chair / student writing seat
                rr(c,side?53:24,side?18:17,side?37:80,side?64:44,7,OUT);
                rr(c,side?58:30,side?23:22,side?29:68,side?50:33,6,textile);
                rr(c,side?48:35,side?72:72,side?45:57,24,6,wood);
                line(c,side?71:63,95,side?71:63,114,6,INK);
                line(c,side?49:35,113,side?97:92,113,5,INK);
                if(kind==17){
                    r(c,side?40:24,55,side?48:79,7,high);
                    r(c,side?73:89,56,4,28,INK);
                    r(c,side?43:35,56,18,6,PAPER);
                }break;
            case 8:case 13:case 25: // bookshelves, merchandise, industrial rack
                shelved(c,side,wood,high,kind);
                break;
            case 9:case 20:case 29:case 28: // security, analyzer, server, copier
                topMachine(c,side,wood,high);
                if(kind==29){
                    for(int n=0;n<4;n++){
                        r(c,side?39:26,38+n*17,side?40:78,12,OUT);
                        for(int j=0;j<3;j++)o(c,(side?45:31)+j*9,40+n*17,4,4,
                            j==1?0xffa7cb7d:RUST);
                    }
                }else if(kind==28){
                    r(c,side?48:33,79,side?36:61,10,PAPER);
                    r(c,side?48:33,93,side?36:61,4,OUT);
                }else if(kind==20){
                    o(c,side?54:50,82,22,17,INK);
                    o(c,side?59:55,85,12,11,RUST);
                }
                break;
            case 15: // luggage trolley
                line(c,39,12,39,102,6,RUST);line(c,39,12,88,12,6,RUST);
                r(c,side?51:24,47,side?37:82,46,OUT);
                r(c,side?56:30,51,side?27:70,36,wood);
                line(c,32,99,105,99,6,STEEL);
                o(c,38,105,15,15,OUT);o(c,89,105,15,15,OUT);
                break;
            case 18: // blackboard / mounted diagram, flat profile
                rr(c,side?56:8,side?15:25,side?42:109,side?94:67,4,wood);
                rr(c,side?61:14,side?20:30,side?31:97,side?82:56,3,OUT);
                for(int n=0;n<5;n++){
                    line(c,side?68:21,side?35+n*13:40+n*8,
                        side?86:99,side?33+n*13:39+n*8,2,0xffb8bdb2);
                }
                r(c,side?52:14,side?103:86,side?47:100,7,high);
                break;
            case 19: // laboratory bench with bottles & basin integrated
                table(c,side,STEEL,0xffadb7b0);
                for(int n=0;n<3;n++){
                    int x=side?53:28+n*29,y=side?27+n*23:36;
                    r(c,x,y,10,18,GLASS);
                    r(c,x+2,y-5,6,6,INK);
                    r(c,x+2,y+9,6,5,n==1?RUST:0xff9ac1ac);
                }
                r(c,side?78:45,76,30,6,INK);
                break;
            case 21: // examination couch
                rr(c,side?39:18,side?10:30,side?60:94,side?101:62,5,STEEL);
                rr(c,side?46:24,side?16:36,side?43:82,side?92:50,4,0xffb7cdc3);
                rr(c,side?47:26,side?17:39,side?41:29,side?24:43,4,LIGHT);
                line(c,side?43:25,98,side?43:25,114,6,INK);
                line(c,side?96:104,98,side?96:104,114,6,INK);
                break;
            case 22:case 23: // punch press, conveyor with roller beds
                if(kind==23){
                    rr(c,side?40:9,side?8:32,side?63:111,side?108:64,5,OUT);
                    rr(c,side?45:14,side?13:38,side?54:101,side?96:51,4,STEEL);
                    for(int n=0;n<6;n++){
                        int x=side?51:19+n*16,y=side?19+n*16:46;
                        r(c,x,y,side?40:9,side?8:33,0xffa3a99c);
                        line(c,x+2,y+4,x+(side?37:7),y+4,2,OUT);
                    }
                }else{
                    casework(c,side,STEEL,0xff485e60,0xff9aa49b);
                    rr(c,side?43:33,side?29:42,side?40:62,side?53:47,5,OUT);
                    r(c,side?48:38,side?34:47,side?30:52,side?43:37,RUST);
                    r(c,side?58:55,side?46:40,side?12:18,side?37:51,INK);
                }break;
            case 24: // tool cabinet with mounted wrenches
                casework(c,side,wood,RUST,0xffa1aaa4);
                for(int n=0;n<4;n++){
                    r(c,side?45:25,42+n*16,side?35:77,4,INK);
                    r(c,side?59:56,45+n*16,10,3,LIGHT);
                }break;
            case 26: // hand truck, angled frame and load
                line(c,side?42:25,20,side?78:93,91,7,STEEL);
                line(c,side?54:33,18,side?94:108,86,5,INK);
                poly(c,RUST,side?46:35,53,side?91:95,55,
                    side?102:100,92,side?53:39,91);
                line(c,24,101,104,101,7,STEEL);
                o(c,34,98,17,17,INK);o(c,89,98,17,17,INK);break;
            case 27: // stacked strapped freight at human scale
                rr(c,side?39:17,side?13:32,side?67:96,side?92:69,4,OUT);
                for(int n=0;n<3;n++){
                    int x=side?44:23,y=side?19+n*27:38+n*21;
                    rr(c,x,y,side?55:83,side?23:19,2,n==1?0xffa88b60:wood);
                    line(c,x+5,y+4,x+(side?50:77),y+(side?19:15),2,INK);
                }
                r(c,side?66:55,side?18:34,6,side?86:70,0xff4b6265);
                break;
            default: // safe recognizable storage fixture, not an empty block
                casework(c,side,wood,STEEL,high);
        }
        // Fine wear, attachment rivets and grounded feet on each separate
        // silhouette. The side is not a rotated copy of the front.
        if(kind!=0&&kind!=1&&kind!=18){
            r(c,side?39:16,102,7,8,OUT);
            r(c,side?91:104,102,7,8,OUT);
        }
    }
    private static int WOOD_COLOR(int theme){return BASE[theme];}
    private static Bitmap raster(int sprite,int direction){
        Bitmap bitmap=Bitmap.createBitmap(128,128,Bitmap.Config.ARGB_8888);
        Canvas canvas=new Canvas(bitmap);
        int theme=(sprite-FIRST)/InteriorFurnitureCatalogV166.PER_THEME;
        drawShape(canvas,kind(sprite),direction==1,theme);
        return bitmap;
    }
    public static boolean drawAt(Canvas c,int sprite,float x,float y,
                                 float w,float h,int facing){
        if(!valid(sprite)||w<=0||h<=0)return false;
        int side=(facing==90||facing==270)?1:0;
        int slot=(sprite-FIRST)*2+side;
        Bitmap image=CACHE[slot];
        if(image==null||image.isRecycled()){
            synchronized(CACHE){
                image=CACHE[slot];
                if(image==null||image.isRecycled())
                    CACHE[slot]=image=raster(sprite,side);
            }
        }
        c.save();
        if(facing==270){
            c.scale(-1f,1f,x+w*.5f,y+h*.5f);
        }
        DEST.set(x,y,x+w,y+h);
        c.drawBitmap(image,SOURCE,DEST,BLIT);
        c.restore();
        return true;
    }
    public static void release(){
        synchronized(CACHE){
            for(int i=0;i<CACHE.length;i++){
                if(CACHE[i]!=null&&!CACHE[i].isRecycled())CACHE[i].recycle();
                CACHE[i]=null;
            }
        }
    }
}
