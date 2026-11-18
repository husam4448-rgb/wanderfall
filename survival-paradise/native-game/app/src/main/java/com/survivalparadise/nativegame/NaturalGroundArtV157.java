package com.survivalparadise.nativegame;

import android.graphics.Canvas;

/**
 * Ground logic is the immutable V157/V160 patch model. The visual layer uses
 * alpha-authored material stamps, never polygon or rectangle placeholders.
 */
public final class NaturalGroundArtV157 {
    private NaturalGroundArtV157(){}
    public static void draw(Canvas c,float camX,float camY,
                            float viewW,float viewH){
        draw(c,camX,camY,viewW,viewH,null,false);
    }
    public static void draw(Canvas c,float camX,float camY,
                            float viewW,float viewH,
                            WorldGeographyV160 geography){
        draw(c,camX,camY,viewW,viewH,geography,false);
    }
    public static void draw(Canvas c,float camX,float camY,
                            float viewW,float viewH,
                            WorldGeographyV160 geography,boolean distant){
        int firstX=(int)Math.floor((camX-330f)/NaturalGroundV157.CELL);
        int lastX=(int)Math.floor((camX+viewW+330f)/NaturalGroundV157.CELL);
        int firstY=(int)Math.floor((camY-330f)/NaturalGroundV157.CELL);
        int lastY=(int)Math.floor((camY+viewH+330f)/NaturalGroundV157.CELL);
        for(int gy=firstY;gy<=lastY;gy++)
            for(int gx=firstX;gx<=lastX;gx++)
                for(int slot=0;slot<NaturalGroundV157.PER_CELL;slot++){
                    NaturalGroundV157.Patch b=geography==null?
                        NaturalGroundV157.patch(gx,gy,slot):
                        NaturalGroundV157.patchSeeded(gx,gy,slot,geography.seed);
                    if(b==null||b.x+b.rx*1.7f<camX||
                       b.x-b.rx*1.7f>camX+viewW||
                       b.y+b.rx*1.7f<camY||
                       b.y-b.rx*1.7f>camY+viewH)continue;
                    int biome=geography==null?
                        BiomeWorldV74.biome(b.x,b.y):
                        geography.biomeAt(b.x,b.y);
                    // Base V54/V160 terrain remains present if the painted
                    // library is missing. Never resurrect hard-edged V157
                    // polygons or monochrome ellipse fallback shapes.
                    NaturalBrushArtV1652.patch(c,b,biome,distant);
                }
    }
}
