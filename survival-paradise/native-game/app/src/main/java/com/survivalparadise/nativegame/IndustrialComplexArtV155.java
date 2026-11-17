package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Typeface;

/**
 * V155 architectural extensions are behind the four approved, front-facing
 * factory facade WebPs. Never paint new "roof grids" over their original
 * pixel artwork: that destroys their perspective, rusty panels and shading.
 * Both attached opaque wings share exact IndustrialComplexV155 collision.
 */
public final class IndustrialComplexArtV155 {
    private IndustrialComplexArtV155(){}
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG);
    private static final int DARK=0xff1a292d;
    private static final int[] ROOFS={
        0xff66747b,0xff627b79,0xff766c60,0xff616e74,
        0xff68766d,0xff6e625b,0xff5f7076,0xff786c5e
    };
    private static final int[] ACCENTS={
        0xffb59d74,0xff94b7ac,0xffc68a52,0xffa8abb0,
        0xffa5c3a8,0xffae996b,0xffadb1a5,0xffbfa77b
    };
    private static void rect(Canvas c,float x,float y,float w,float h,int color){
        if(w<=0f||h<=0f)return;
        P.setStyle(Paint.Style.FILL);P.setColor(color);
        c.drawRect(x,y,x+w,y+h,P);
    }
    private static void wing(Canvas c,IndustrialComplexV155.Wing part,
                             int kind,int variation){
        float x=part.x,y=part.y,w=part.w,h=part.h;
        int roof=ROOFS[kind],accent=ACCENTS[kind];
        // Opaque masonry matches the physical annex with no hitbox margins.
        rect(c,x,y,w,h,DARK);
        rect(c,x+9f,y+8f,w-18f,h-17f,roof);
        rect(c,x+18f,y+18f,w-36f,12f,accent);
        rect(c,x+18f,y+h-40f,w-36f,11f,0xff263b42);
        switch(kind){
            case 0: // steel mill: continuous rolling lines
                for(int j=0;j<5;j++)
                    rect(c,x+27,y+47+j*23,w-54,9,
                        j%2==0?accent:0xff3e545a);
                break;
            case 1: // assembly factory: separate ventilated bays
                for(int j=0;j<4;j++){
                    float xx=x+27+j*(w-54f)/4f;
                    rect(c,xx,y+51,28,h-109f,0xff293b41);
                    rect(c,xx+5,y+63,18,23,accent);
                }
                break;
            case 2: // foundry: thick exhaust banks
                for(int j=0;j<4;j++){
                    float xx=x+31+j*(w-62f)/4f;
                    rect(c,xx,y+48,30,52,0xff303c3f);
                    rect(c,xx+5,y+54,20,14,accent);
                    rect(c,xx+4,y+104,22,18,0xff8d5944);
                }
                break;
            case 3: // logistics warehouse: loading sections
                for(int j=0;j<4;j++)
                    rect(c,x+28+j*(w-56f)/4f,y+51,
                        Math.max(23f,(w-80f)/4f),h-112f,
                        j%2==0?0xff384c51:0xff82918b);
                break;
            case 4: // electric plant: rooftop transformer enclosures
                for(int j=0;j<3;j++){
                    float xx=x+33+j*(w-66f)/3f;
                    rect(c,xx,y+58,45,51,0xff273f42);
                    rect(c,xx+7,y+67,31,10,accent);
                }
                break;
            case 5: // scrap recycler: corrugated patchwork
                for(int j=0;j<5;j++)
                    rect(c,x+22+j*(w-44f)/5f,y+52,22,h-115f,
                        j%2==0?0xff88745a:0xff354a50);
                break;
            case 6: // machine works: pipe/service grid
                for(int j=0;j<5;j++){
                    float yy=y+43+j*(h-91f)/5f;
                    rect(c,x+29,yy,w-58,10,0xff324b52);
                    rect(c,x+41+j*17f,yy+3,27,6,accent);
                }
                break;
            default: // raw material depot: long reinforced roof hatches
                for(int j=0;j<4;j++){
                    float xx=x+26+j*(w-52f)/4f;
                    rect(c,xx,y+49,39,h-112f,0xff40565a);
                    rect(c,xx+7,y+62,25,h-138f,accent);
                }
        }
        for(int j=0;j<3;j++){
            float xx=x+29+j*(w-58f)/3f;
            rect(c,xx,y+h-25,22,10,j==variation%3?accent:DARK);
        }
    }
    /** Extensions first. Original facility sprites draw over them untouched. */
    public static void behindFacade(Canvas c,IndustrialOpenWorldV124.Plot site){
        if(!site.enterable())return;
        int kind=site.kind;
        int variant=Math.floorMod(IndustrialWorldV123.hash(
            site.sx,site.sy,site.seed^0x155),6);
        wing(c,IndustrialComplexV155.left(site),kind,variant);
        wing(c,IndustrialComplexV155.right(site),kind,(variant+2)%6);
    }
    /** Ground-only entry stencil, below the painted original source facade. */
    public static void overFacade(Canvas c,IndustrialOpenWorldV124.Plot site){
        if(!site.enterable())return;
        float door=site.doorX;
        float y=site.y+817f; // below the 804-unit-high facade bitmap
        int accent=ACCENTS[site.kind];
        rect(c,door-73,y+13,146,6,0xff28363a);
        rect(c,door-69,y+14,138,3,accent);
        // Marked walkable yard landing: does not put a fake door on the art.
        P.setColor(0xffd8c6a0);
        P.setTextSize(13f);
        P.setTypeface(Typeface.create("monospace",Typeface.BOLD));
        c.drawText("ENTER",door-20,y+5,P);
    }
}
