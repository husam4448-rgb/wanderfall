package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;

/**
 * V165.1 aged road contours: a physically continuous asphalt body with
 * seed-stable organic edges, not a mono-color, hard-edged rectangle.
 * The path only affects drawing. Road hitboxes, spawn geometry and saves
 * remain exactly as before. Edge detail is world-anchored, never per frame.
 */
public final class RoadContourV1651 {
    private RoadContourV1651(){}
    private static final Path ROAD=new Path();
    private static float noise(float worldCoord,int seed,int salt){
        final float cell=156f;
        float scaled=worldCoord/cell;
        int i=(int)Math.floor(scaled);
        float t=scaled-i;
        t=t*t*(3f-2f*t);
        int a=WorldChunkModel.hash(i*13+salt,seed*17-salt);
        int b=WorldChunkModel.hash((i+1)*13+salt,seed*17-salt);
        float av=(Math.floorMod(a,65536)/32767.5f)-1f;
        float bv=(Math.floorMod(b,65536)/32767.5f)-1f;
        return av+(bv-av)*t;
    }
    private static float erosion(float coord,int seed,int salt){
        return 10f*noise(coord,seed,salt)+
               3.5f*noise(coord*2.15f,seed^0x71A5,salt+71);
    }
    public static void horizontal(Canvas c,Paint p,
                                  float start,float end,
                                  float top,float bottom,int seed){
        if(end<=start||bottom<=top)return;
        ROAD.reset();
        ROAD.moveTo(start,top+erosion(start,seed,15));
        float step=40f;
        int n=Math.max(1,(int)Math.ceil((end-start)/step));
        for(int i=1;i<=n;i++){
            float x=start+(end-start)*i/n;
            ROAD.lineTo(x,top+erosion(x,seed,15));
        }
        for(int i=n;i>=0;i--){
            float x=start+(end-start)*i/n;
            ROAD.lineTo(x,bottom+erosion(x,seed,99));
        }
        ROAD.close();
        p.setStyle(Paint.Style.FILL);p.setColor(0xff565b50);
        c.drawPath(ROAD,p);
        SurfaceArtV165.path(c,ROAD,SurfaceArtV165.AGED_PAVEMENT,330f,223);
    }
    public static void vertical(Canvas c,Paint p,
                                float left,float right,
                                float top,float bottom,int seed){
        if(right<=left||bottom<=top)return;
        ROAD.reset();
        ROAD.moveTo(left+erosion(top,seed,33),top);
        float step=40f;
        int n=Math.max(1,(int)Math.ceil((bottom-top)/step));
        for(int i=1;i<=n;i++){
            float y=top+(bottom-top)*i/n;
            ROAD.lineTo(left+erosion(y,seed,33),y);
        }
        for(int i=n;i>=0;i--){
            float y=top+(bottom-top)*i/n;
            ROAD.lineTo(right+erosion(y,seed,144),y);
        }
        ROAD.close();
        p.setStyle(Paint.Style.FILL);p.setColor(0xff565b50);
        c.drawPath(ROAD,p);
        SurfaceArtV165.path(c,ROAD,SurfaceArtV165.AGED_PAVEMENT,330f,223);
    }
}