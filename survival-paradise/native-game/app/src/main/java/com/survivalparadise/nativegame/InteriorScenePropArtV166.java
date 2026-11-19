package com.survivalparadise.nativegame;

import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
import android.util.Base64;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;

/**
 * Sixteen original, room-specific furnished set pieces. The image is an
 * offline Android asset; it is not fetched from any remote service at runtime.
 * Every solid object retains its existing V163 physics and interactions.
 */
public final class InteriorScenePropArtV166 {
    private InteriorScenePropArtV166(){}
    public static final int FIRST=32,COUNT=16,CELL=96;
    private static final int[][] BOUNDS={
        {6,17,90,89},{0,23,95,91},{4,15,91,90},{18,12,77,91},
        {4,13,92,93},{8,23,89,81},{7,10,87,91},{2,14,93,91},
        {4,19,92,87},{2,5,92,89},{2,12,90,88},{5,17,91,83},
        {4,10,93,89},{5,17,90,87},{4,13,96,88},{0,14,95,92}
    };
    private static Bitmap atlas;
    private static boolean attempted;
    private static final Paint P=new Paint(Paint.FILTER_BITMAP_FLAG|Paint.DITHER_FLAG);
    private static final Rect SRC=new Rect();
    private static final RectF DST=new RectF();
    public static synchronized void load(AssetManager assets){
        if(assets==null||attempted)return;
        attempted=true;
        try(InputStream in=assets.open("sp_v166_story_props.webp.b64")){
            ByteArrayOutputStream bytes=new ByteArrayOutputStream(100000);
            byte[] buf=new byte[8192];int n;
            while((n=in.read(buf))!=-1)bytes.write(buf,0,n);
            byte[] raw=Base64.decode(bytes.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options opts=new BitmapFactory.Options();
            opts.inScaled=false;
            Bitmap b=BitmapFactory.decodeByteArray(raw,0,raw.length,opts);
            if(b==null||b.getWidth()!=4*CELL||b.getHeight()!=4*CELL)
                throw new IllegalStateException("Invalid story-prop atlas");
            atlas=b;
            android.util.Log.i("SP-V166","16 scene-specific original props ready");
        }catch(Exception e){
            android.util.Log.e("SP-V166","Story-prop atlas unavailable",e);
            release();
        }
    }
    public static boolean ready(){return atlas!=null&&!atlas.isRecycled();}
    public static boolean drawAt(Canvas c,int sprite,float x,float y,float w,float h){
        if(!ready()||sprite<FIRST||sprite>=FIRST+COUNT||w<=0||h<=0)
            return false;
        int i=sprite-FIRST, col=i%4,row=i/4;
        int[] bounds=BOUNDS[i];
        SRC.set(col*CELL+bounds[0],row*CELL+bounds[1],
                col*CELL+bounds[2],row*CELL+bounds[3]);
        DST.set(x,y,x+w,y+h);
        c.drawBitmap(atlas,SRC,DST,P);
        return true;
    }
    public static synchronized void release(){
        if(atlas!=null&&!atlas.isRecycled())atlas.recycle();
        atlas=null;attempted=false;
    }
}
