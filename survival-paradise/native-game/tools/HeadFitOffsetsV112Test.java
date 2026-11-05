package com.survivalparadise.nativegame;

/** Tests source-pixel position for all 200 selectable characters. */
public final class HeadFitOffsetsV112Test {
    static void check(boolean b,String msg){if(!b)throw new AssertionError(msg);}
    static void eq(int a,int b,String msg){
        check(a==b,msg+": expected "+b+", got "+a);
    }
    public static void main(String[] args){
        for(int character=1;character<=200;character++){
            // V5 poses differ by head size/individual fitting; no runtime file I/O.
            int width=80+(character%60),height=90+(character%68);
            int approvedX=-30+(character%31),approvedY=-32+(character%37);
            int originX=HeadFitOffsetsV112.x(width,approvedX,0);
            int originY=HeadFitOffsetsV112.y(height,approvedY,0f,0);
            eq(originX,Math.round((200f-width)*.5f+approvedX+10f),
                "V5 horizontal fit unchanged at neutral "+character);
            eq(originY,Math.round(200f-height+approvedY-3f),
                "V5 vertical fit unchanged at neutral "+character);
            for(int d=-24;d<=24;d++){
                eq(HeadFitOffsetsV112.x(width,approvedX,d),originX+d,
                    "horizontal slider acts on character "+character);
                eq(HeadFitOffsetsV112.y(height,approvedY,0f,d),originY+d,
                    "vertical slider acts on character "+character);
            }
            eq(HeadFitOffsetsV112.x(width,approvedX,50),originX+24,
                "horizontal offset clamped");
            eq(HeadFitOffsetsV112.y(height,approvedY,0f,-80),originY-24,
                "vertical offset clamped");
            // Breathing stays active; user offset is applied without changing it.
            eq(HeadFitOffsetsV112.y(height,approvedY,3f,7),
                originY+10,"head-only breathing retained "+character);
        }
        // Neck pivot is derived from the translated head rect and follows it.
        float left=10f,w=66f,bottom=89f,unit=.7f;
        check(HeadAimV111.neckX(left+12,w)==HeadAimV111.neckX(left,w)+12,
            "head/neck pivot translates with horizontal fitting");
        check(HeadAimV111.neckY(bottom+9,unit)==HeadAimV111.neckY(bottom,unit)+9,
            "head/neck pivot translates with vertical fitting");
        System.out.println("V112 all-character additive head fit slider tests: PASS");
    }
}
