package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Typeface;

/**
 * Architectural massing painted around the existing approved industrial
 * sprites, never replacing or resampling them. Roof structure, loading bays,
 * skylights and machinery differ by actual facility kind. Geometry outside
 * the original V126 silhouette is exactly IndustrialComplexV155.Wing.
 */
public final class IndustrialComplexArtV155 {
    private IndustrialComplexArtV155(){}
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG);
    private static final int DARK=0xff1e2c31, STEEL=0xff657576;
    private static void rect(Canvas c,float x,float y,float w,float h,int color){
        if(w<=0||h<=0)return;
        P.setStyle(Paint.Style.FILL);P.setColor(color);
        c.drawRect(x,y,x+w,y+h,P);
    }
    private static final int[] ROOFS={
        0xff768188,0xff637b7b,0xff786b61,0xff68777a,
        0xff68756d,0xff766f62,0xff657781,0xff807766
    };
    private static final int[] ACCENTS={
        0xffb59d74,0xff97b3a9,0xffc68a52,0xffa6afb3,
        0xffaec4ab,0xffb39b69,0xffa9afa7,0xffc6a579
    };
    private static void drawWing(Canvas c,IndustrialComplexV155.Wing wing,
                                 int color,int accent,int variant){
        float x=wing.x,y=wing.y,w=wing.w,h=wing.h;
        // Opaque painted hull exactly matches the separate wing collision.
        rect(c,x,y,w,h,DARK);
        rect(c,x+9,y+8,w-18,h-17,color);
        rect(c,x+18,y+19,w-36,12,accent);
        for(int i=0;i<4;i++){
            float yy=y+40+i*29;
            rect(c,x+29,yy,w-58,8,0xff334a4e);
            rect(c,x+34,yy+9,Math.max(32,w-68),5,0xffa9ac9c);
        }
        for(int i=0;i<3;i++){
            float xx=x+31+i*(w-62f)/3f;
            rect(c,xx,y+h-33,27,21,i==variant%3?accent:0xff47585b);
        }
    }
    public static void behindFacade(Canvas c,IndustrialOpenWorldV124.Plot site){
        if(!site.enterable())return;
        int kind=site.kind,variant=Math.floorMod(
            IndustrialWorldV123.hash(site.sx,site.sy,site.seed^0x155),6);
        int color=ROOFS[kind],accent=ACCENTS[kind];
        drawWing(c,IndustrialComplexV155.left(site),color,accent,variant);
        drawWing(c,IndustrialComplexV155.right(site),color,accent,variant+2);
    }
    public static void overFacade(Canvas c,IndustrialOpenWorldV124.Plot site){
        if(!site.enterable())return;
        float bx=site.buildingX,by=site.buildingY;
        float w=site.buildingW,h=site.buildingH;
        int k=site.kind;
        int accent=ACCENTS[k],roof=ROOFS[k];
        int variation=Math.floorMod(IndustrialWorldV123.hash(
            site.sx+13,site.sy-19,site.seed^0x155),5);
        // The approved V126 bitmap still supplies the entire main facade;
        // these confined roof fixtures make the structure read as a facility.
        rect(c,bx+80,by+70,w-160,12,0x77404c51);
        rect(c,bx+80,by+h-121,w-160,12,0x77404c51);
        switch(k){
            case 0: // Steel mill: long steel rolling and cooling bays
                for(int i=0;i<5;i++){
                    float yy=by+128+i*(h-268)/5f;
                    rect(c,bx+140,yy,w-280,22,0xff41595f);
                    rect(c,bx+162,yy+5,w-324,8,0xffa9b7ad);
                }
                break;
            case 1: // Assembly factory: conveyor branches / skylights
                for(int i=0;i<4;i++){
                    float xx=bx+155+i*(w-310)/4f;
                    rect(c,xx,by+116,66,h-242,0xff3e5a60);
                    for(int j=0;j<5;j++)
                        rect(c,xx+11,by+132+j*(h-280)/5f,45,13,
                            0xffa0aaa1);
                }
                break;
            case 2: // Foundry: thermal venting, roof stacks and crane gantry
                for(int i=0;i<7;i++){
                    float xx=bx+135+i*(w-270)/7f;
                    rect(c,xx,by+130,54,54,0xff2e3e41);
                    rect(c,xx+10,by+141,32,32,i%2==0?0xffac7149:accent);
                }
                rect(c,bx+120,by+h*.62f,w-240,18,0xff9b8d78);
                break;
            case 3: // Logistics warehouse: huge repeated loading halls
                for(int i=0;i<6;i++){
                    float xx=bx+108+i*(w-216)/6f;
                    rect(c,xx,by+120,(w-255)/6f,h-240,
                        i%2==0?0xff4c646a:0xff839596);
                    rect(c,xx+10,by+130,(w-283)/6f,16,accent);
                }
                break;
            case 4: // Electrical plant: transformer arrays / roof duct grid
                for(int i=0;i<4;i++)for(int j=0;j<3;j++){
                    float xx=bx+126+i*(w-250)/4f;
                    float yy=by+120+j*(h-260)/3f;
                    rect(c,xx,yy,90,65,0xff273d3e);
                    rect(c,xx+7,yy+8,76,13,accent);
                    rect(c,xx+18,yy+33,55,17,0xff718e85);
                }
                break;
            case 5: // Scrap recycling: separated processing roof bays
                for(int i=0;i<5;i++){
                    float xx=bx+135+i*(w-270)/5f;
                    rect(c,xx,by+150,(w-300)/5f,h-320,
                        i%2==0?0xff705f54:0xff4b5559);
                    rect(c,xx+13,by+180,(w-338)/5f,15,accent);
                }
                break;
            case 6: // Machine works: overhead ventilation / service grid
                for(int i=0;i<7;i++){
                    float yy=by+122+i*(h-240)/7f;
                    rect(c,bx+112,yy,w-224,18,0xff304c53);
                    for(int j=0;j<4;j++)
                        rect(c,bx+142+j*(w-284)/4f,yy+3,42,9,
                            0xffb7b1a3);
                }
                break;
            default: // Raw material depot: multiple roof hoppers
                for(int i=0;i<5;i++){
                    float xx=bx+127+i*(w-254)/5f;
                    rect(c,xx,by+130,(w-290)/5f,h-280,
                        0xff34494d);
                    rect(c,xx+11,by+142,(w-320)/5f,h-316,
                        i%2==0?0xffa99779:0xff779090);
                }
        }
        // Repeatable building-specific wear and lightning rods, not uniform
        // copy-pasted facade plates. Confined well within alpha-solid roof.
        for(int i=0;i<variation+2;i++){
            float xx=bx+114+i*(w-228)/(float)(variation+3);
            rect(c,xx,by+h-103,24,8,accent);
        }
        // Massive human-scaled south service front with a visible signed
        // entrance in the EXACT historic world-space interaction corridor.
        float door=site.doorX,front=site.y+782f;
        rect(c,door-108f,front-20f,216f,17f,0xff1b2a2c);
        rect(c,door-101f,front-16f,202f,9f,accent);
        rect(c,door-71f,front,142f,21f,0xff59615d);
        rect(c,door-66f,front+4f,132f,12f,0xffb4aa8e);
        P.setTypeface(Typeface.create("monospace",Typeface.BOLD));
        P.setTextSize(17f);
        P.setColor(0xffecdec2);
        c.drawText("ENTER",door-27,front-27,P);
    }
}
