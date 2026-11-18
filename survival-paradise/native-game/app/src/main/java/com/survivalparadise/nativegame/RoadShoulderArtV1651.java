package com.survivalparadise.nativegame;

import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.BitmapShader;
import android.graphics.Canvas;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Shader;
import android.util.Base64;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;

/**
 * V165.1 original gravel/dirt/grass transition artwork.
 * Alpha band follows EXISTING road edges only. No false geometry, lanes,
 * obstacles or world-seed changes. A 1024-world-unit repeat is world anchored.
 */
public final class RoadShoulderArtV1651 {
    private RoadShoulderArtV1651(){}
    private static Bitmap strip;
    private static BitmapShader shader;
    private static final Matrix MATRIX=new Matrix();
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG |
                                           Paint.FILTER_BITMAP_FLAG |
                                           Paint.DITHER_FLAG);
    private static boolean attempted;

    public static synchronized void load(AssetManager assets){
        if(attempted||assets==null)return;
        attempted=true;
        try(InputStream in=assets.open("sp_v1651_road_shoulder.webp.b64")){
            ByteArrayOutputStream bytes=new ByteArrayOutputStream(8192);
            byte[] buffer=new byte[4096];int n;
            while((n=in.read(buffer))!=-1)bytes.write(buffer,0,n);
            byte[] raw=Base64.decode(bytes.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options opts=new BitmapFactory.Options();
            opts.inScaled=false;
            strip=BitmapFactory.decodeByteArray(raw,0,raw.length,opts);
            if(strip==null||strip.getWidth()!=1024||strip.getHeight()!=128)
                throw new IllegalArgumentException("Invalid road edge art");
            shader=new BitmapShader(strip,Shader.TileMode.REPEAT,Shader.TileMode.CLAMP);
            android.util.Log.i("SP-V1651","Road shoulder ready: 1024x128 RGBA strip");
        }catch(Exception e){
            android.util.Log.w("SP-V1651","Road shoulder art missing; base roads remain",e);
            release();
        }
    }
    public static boolean ready(){return shader!=null;}

    /** Band's local Y increases from dirt-side to asphalt-side. */
    private static void band(Canvas c,float start,float end,float edge,
                             float worldAnchor,boolean reverse){
        if(shader==null||end<=start)return;
        MATRIX.reset();
        if(reverse){
            // Left road edge uses a mirrored local X axis, but samples the
            // SAME world-Y coordinate as right edge and adjacent sectors.
            MATRIX.setScale(-1f,1f);
            MATRIX.postTranslate(worldAnchor,edge-64f);
        }else MATRIX.setTranslate(worldAnchor,edge-64f);
        shader.setLocalMatrix(MATRIX);
        P.setShader(shader);P.setAlpha(255);
        c.drawRect(start,edge-64f,end,edge+64f,P);
        P.setShader(null);
    }

    /** Draw one uninterrupted horizontal road SECTION, not across junctions. */
    public static void horizontal(Canvas c,float start,float end,
                                  float top,float bottom){
        if(shader==null||end<=start||bottom<=top)return;
        band(c,start,end,top,0f,false);
        c.save();
        c.translate(0f,2f*bottom);
        c.scale(1f,-1f);
        band(c,start,end,bottom,0f,false);
        c.restore();
    }

    /** Draw one uninterrupted vertical road SECTION, not across junctions. */
    public static void vertical(Canvas c,float left,float right,
                                float top,float bottom){
        if(shader==null||right<=left||bottom<=top)return;
        float len=bottom-top;
        c.save();
        c.translate(left,top);c.rotate(-90f);
        band(c,-len,0f,0f,top,true);
        c.restore();
        c.save();
        c.translate(right,bottom);c.rotate(90f);
        band(c,-len,0f,0f,-bottom,false);
        c.restore();
    }

    public static synchronized void release(){
        shader=null;
        if(strip!=null&&!strip.isRecycled())strip.recycle();
        strip=null;
        attempted=false;
    }
}
