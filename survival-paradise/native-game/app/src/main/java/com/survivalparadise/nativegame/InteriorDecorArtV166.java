package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/** Small floor-level authored motifs; no apparent rigid obstructions. */
public final class InteriorDecorArtV166 {
    private InteriorDecorArtV166(){}
    private static void r(Canvas c,Paint p,float x,float y,float w,float h,int color){
        if(w<=0||h<=0)return;
        p.setColor(color);p.setStyle(Paint.Style.FILL);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private static int hash(int n){
        n^=n>>>16;n*=0x7feb352d;n^=n>>>15;
        return n^(n>>>16);
    }
    public static void draw(Canvas c,Paint p,float[] q,int theme,int key){
        if(q==null||q.length<5)return;
        float x=q[1],y=q[2],w=q[3],h=q[4];
        int style=(int)q[0];
        if(w<7||h<7)return;
        c.save();c.clipRect(x,y,x+w,y+h);
        int grain=hash(key^(int)x^(int)y);
        switch(style){
            case 0: // frayed wool rug or washable mat; lies flush with floor
                r(c,p,x+2,y+2,w-4,h-4,0x6c292e2c);
                r(c,p,x+6,y+5,w-12,h-10,
                    theme==3?0x998e6454:theme==4?0x99717b74:0x998c7765);
                r(c,p,x+9,y+8,w-18,h-16,0x77716f60);
                for(int i=8;i<w-8;i+=11){
                    r(c,p,x+i,y+5,3,4,0xffa2987c);
                    r(c,p,x+i,y+h-8,3,4,0xffad987c);
                }
                for(int i=4;i<h-4;i+=9){
                    r(c,p,x+6,y+i,2,3,0xffa28e72);
                    r(c,p,x+w-8,y+i,2,3,0xffa28e72);
                }
                break;
            case 1: // several scattered, separately oriented paper sheets
                for(int i=0;i<3;i++){
                    float xx=x+3+i*(w-11)/3f;
                    float yy=y+4+(i%2)*7;
                    r(c,p,xx+2,yy+2,Math.max(7,w*.22f),Math.max(10,h*.46f),
                        0x78303b35);
                    r(c,p,xx,yy,Math.max(7,w*.22f),Math.max(10,h*.46f),
                        i%2==0?0xffc7bea5:0xffa6b1a8);
                    for(int j=0;j<3;j++)
                        r(c,p,xx+3,yy+4+j*4,Math.max(3,w*.15f),1,0xff77756a);
                }
                break;
            case 2: // dry debris, shoe marks and dirt, not an unblended patch
                for(int i=0;i<19;i++){
                    int n=hash(grain+i*79);
                    float xx=x+Math.floorMod(n,(int)Math.max(1,w-4));
                    float yy=y+Math.floorMod(n>>>13,(int)Math.max(1,h-3));
                    r(c,p,xx,yy,2+((n>>>10)&3),1+((n>>>16)&1),
                        (n&1)==0?0x65574742:0x5745443c);
                }
                break;
            case 3: // short lengths of cable, fixtures, loose hardware
                for(int i=0;i<4;i++){
                    float yy=y+4+i*(h-8)/4f;
                    r(c,p,x+5+(i%2)*6,yy,w*.55f,2,0xff313d3a);
                    r(c,p,x+w*.48f,yy+2,5,4,0xff9e9271);
                    r(c,p,x+5,yy,5,3,0xffad8156);
                }
                break;
            case 4: // torn textile, tarp, or discarded fabric
                r(c,p,x+5,y+7,w-11,h-12,0x7e3b4341);
                r(c,p,x+2,y+4,w-13,h-13,theme==3?0xffab957a:0xff6d877c);
                r(c,p,x+6,y+7,w-23,h-21,0xff929d86);
                for(int i=0;i<6;i++)
                    r(c,p,x+8+i*5,y+h-11,2,5,0xffc3b9a2);
                break;
            case 5: // bolts, pencils, crayons, fasteners or small tools
                for(int i=0;i<5;i++){
                    int n=hash(grain+i*31);
                    float xx=x+3+i*(w-7)/5f;
                    float yy=y+4+Math.floorMod(n,Math.max(1,(int)h-11));
                    r(c,p,xx,yy,5,3,i%2==0?0xffa58e66:0xff56666a);
                    r(c,p,xx+2,yy+3,2,4,0xff373f40);
                }
                break;
            default: // cracked warning stencil, faded and broken
                for(int i=0;i<6;i++){
                    float xx=x+3+i*(w-6)/6f;
                    r(c,p,xx,y+4,Math.max(2,w/14f),h-8,
                        (i&1)==0?0x889e8554:0x76727a68);
                    r(c,p,xx+3,y+h-8,5,3,0x6d4d4939);
                }
                break;
        }
        c.restore();
    }
}
