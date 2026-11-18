package com.survivalparadise.nativegame;

import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.BitmapShader;
import android.graphics.Canvas;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
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
    private static Bitmap leftStrip,rightStrip;
    private static final Rect SRC=new Rect();
    private static final RectF DST=new RectF();
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
            // Pre-rotate once. The previous canvas rotation + mirrored shader
            // matrix could generate giant diagonal wedges around the vertical
            // road. Draw vertical strips in untransformed WORLD coordinates.
            Matrix left=new Matrix(),right=new Matrix();
            left.setRotate(-90f);right.setRotate(90f);
            leftStrip=Bitmap.createBitmap(strip,0,0,strip.getWidth(),
                strip.getHeight(),left,true);
            rightStrip=Bitmap.createBitmap(strip,0,0,strip.getWidth(),
                strip.getHeight(),right,true);
            if(leftStrip.getWidth()!=128||leftStrip.getHeight()!=1024||
               rightStrip.getWidth()!=128||rightStrip.getHeight()!=1024)
                throw new IllegalArgumentException("Bad vertical road shoulder dimensions");
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

    /**
     * Tile a vertical shoulder by its absolute world-Y source offset.
     * It NEVER rotates the world Canvas, and cannot paint outside a
     * precise 128-world-unit road-edge band. Both materials and transitions
     * are identical regardless of which chunk/camera draws them.
     */
    private static void verticalBand(Canvas c,float edge,float first,float last,
                                     Bitmap art){
        if(art==null||art.isRecycled()||last<=first)return;
        final float tile=1024f;
        float y=first;
        while(y<last-.01f){
            float origin=(float)Math.floor(y/tile)*tile;
            float end=Math.min(last,origin+tile);
            // Prevent precision stalls when coordinates are very large.
            if(end<=y+.001f)break;
            int top=Math.max(0,Math.min(1023,(int)Math.floor(y-origin)));
            int bottom=Math.max(top+1,Math.min(1024,(int)Math.ceil(end-origin)));
            SRC.set(0,top,128,bottom);
            DST.set(edge-64f,y,edge+64f,end);
            c.drawBitmap(art,SRC,DST,P);
            y=end;
        }
    }
    /** Only existing road segments, excluding the real four-way junction. */
    public static void vertical(Canvas c,float left,float right,
                                float top,float bottom){
        if(!ready()||right<=left||bottom<=top)return;
        verticalBand(c,left,top,bottom,leftStrip);
        verticalBand(c,right,top,bottom,rightStrip);
    }

    public static synchronized void release(){
        shader=null;
        if(leftStrip!=null&&!leftStrip.isRecycled())leftStrip.recycle();
        if(rightStrip!=null&&!rightStrip.isRecycled())rightStrip.recycle();
        leftStrip=null;rightStrip=null;
        if(strip!=null&&!strip.isRecycled())strip.recycle();
        strip=null;
        attempted=false;
    }
}
