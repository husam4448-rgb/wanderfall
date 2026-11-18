package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;

/** World-space organic, cartoonish soil dressing, under structures and roads. */
public final class NaturalGroundArtV157 {
    private NaturalGroundArtV157(){}
    private static final int[] DIRT={0xff665441,0xff7c664b,0xff71583e,0xff866b4a};
    private static final int[] GRASS={0xff496d47,0xff5d7a4f,0xff3d674d,0xff637850};
    private static final int[] DRY={0xff9a845b,0xff8a7650,0xff817752,0xffa08b64};
    private static int color(int index,int variation){
        int[] a=index==NaturalGroundV157.DIRT?DIRT:
                index==NaturalGroundV157.GRASS?GRASS:DRY;
        return a[Math.floorMod(variation,a.length)];
    }
    private static int alpha(int color,int opacity){
        return (opacity<<24)|(color&0xffffff);
    }
    private static void patch(Canvas c,Paint paint,Path path,
                              NaturalGroundV157.Patch b,
                              WorldGeographyV160 geography,boolean distant){
        int biome=geography==null?BiomeWorldV74.biome(b.x,b.y):
            geography.biomeAt(b.x,b.y);
        // Desert and highland ground gets less saturated grass.
        int base=biome==BiomeWorldV74.DESERT&&b.kind==NaturalGroundV157.GRASS?
            0xffa49364:biome==BiomeWorldV74.HIGHLANDS&&
                b.kind==NaturalGroundV157.GRASS?
            0xff828777:biome==BiomeWorldV74.WETLAND&&
                b.kind==NaturalGroundV157.DIRT?
            0xff596c54:color(b.kind,b.variation);
        // V165.2 replaces flat triangulated islands with authored blended
        // pigment, preserving the original deterministic patch position.
        if(NaturalBrushArtV1652.patch(c,b,biome,distant))return;
        path.reset();
        c.save();c.rotate(b.rotation,b.x,b.y);
        final int sides=distant?8:14;
        for(int i=0;i<sides;i++){
            double angle=i*Math.PI*2/sides;
            float jag=NaturalGroundV157.wobble(b,i);
            float xx=b.x+(float)Math.cos(angle)*b.rx*jag;
            float yy=b.y+(float)Math.sin(angle)*b.ry*jag;
            if(i==0)path.moveTo(xx,yy);
            else path.lineTo(xx,yy);
        }
        path.close();
        paint.setColor(alpha(base,b.kind==NaturalGroundV157.DIRT?109:93));
        c.drawPath(path,paint);
        // V165 original textured pigment dresses the EXISTING organic shape.
        SurfaceArtV165.path(c,path,SurfaceArtV165.SOIL,330f,
            b.kind==NaturalGroundV157.GRASS?31:62);
        // Two local splashes of uneven color with no rectangular stroke,
        // without introducing texture outside the site's actual dirt island.
        paint.setColor(alpha(base,73));
        c.drawOval(b.x-b.rx*.36f,b.y-b.ry*.22f,
            b.x+b.rx*.43f,b.y+b.ry*.31f,paint);
        c.restore();
        // Individual broken grass / grit clusters, not a tiled pattern.
        int count=distant?2:b.kind==NaturalGroundV157.GRASS?15:9;
        for(int i=0;i<count;i++){
            int h=WorldChunkModel.hash(Math.round(b.x)+i*31,
                                       Math.round(b.y)+i*19+b.variation*41);
            float xx=b.x+(Math.floorMod(h,201)-100)*b.rx/145f;
            float yy=b.y+(Math.floorMod(h>>>11,201)-100)*b.ry/145f;
            if((xx-b.x)*(xx-b.x)/(b.rx*b.rx)+
               (yy-b.y)*(yy-b.y)/(b.ry*b.ry)>.76f)continue;
            int accent=b.kind==NaturalGroundV157.GRASS?
                0xff8ba477:0xffb3a47e;
            paint.setColor(alpha(accent,105));
            if(b.kind==NaturalGroundV157.GRASS){
                c.drawLine(xx,yy,xx-2f,yy-9f,paint);
                c.drawLine(xx,yy,xx+3f,yy-6f,paint);
            }else{
                c.drawOval(xx-4f,yy-2f,xx+7f,yy+2f,paint);
            }
        }
    }
    public static void draw(Canvas c,float camX,float camY,
                            float viewW,float viewH){
        draw(c,camX,camY,viewW,viewH,null);
    }
    public static void draw(Canvas c,float camX,float camY,
                            float viewW,float viewH,
                            WorldGeographyV160 geography){
        draw(c,camX,camY,viewW,viewH,geography,false);
    }
    public static void draw(Canvas c,float camX,float camY,
                            float viewW,float viewH,
                            WorldGeographyV160 geography,boolean distant){
        Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setStyle(Paint.Style.FILL);
        p.setStrokeWidth(1.8f);
        Path shape=new Path();
        int firstX=(int)Math.floor((camX-250f)/NaturalGroundV157.CELL);
        int lastX=(int)Math.floor((camX+viewW+250f)/NaturalGroundV157.CELL);
        int firstY=(int)Math.floor((camY-250f)/NaturalGroundV157.CELL);
        int lastY=(int)Math.floor((camY+viewH+250f)/NaturalGroundV157.CELL);
        for(int gy=firstY;gy<=lastY;gy++)
            for(int gx=firstX;gx<=lastX;gx++)
                for(int k=0;k<NaturalGroundV157.PER_CELL;k++){
                    NaturalGroundV157.Patch b=geography==null?
                        NaturalGroundV157.patch(gx,gy,k):
                        NaturalGroundV157.patchSeeded(gx,gy,k,geography.seed);
                    if(b.x+b.rx<camX||b.x-b.rx>camX+viewW||
                       b.y+b.ry<camY||b.y-b.ry>camY+viewH)continue;
                    patch(c,p,shape,b,geography,distant);
                }
    }
}
