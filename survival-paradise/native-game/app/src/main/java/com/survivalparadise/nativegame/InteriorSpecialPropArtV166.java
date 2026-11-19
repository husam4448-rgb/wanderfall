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
 * Dedicated V166 4x4 hand-painted hotel, school, office, market, factory
 * and clinic art. This is rendering ONLY: existing V163/V89/V123 objects
 * keep their footprint, collision, seed identity, door access and save data.
 * Indices 16..31 are stable within the global V166 furniture vocabulary.
 */
public final class InteriorSpecialPropArtV166 {
    private InteriorSpecialPropArtV166(){}
    private static final int CELL=96,COUNT=16;
    private static Bitmap atlas;
    private static boolean attempted;
    private static final Paint P=new Paint(Paint.FILTER_BITMAP_FLAG | Paint.DITHER_FLAG);
    private static final Rect SRC=new Rect();
    private static final RectF DST=new RectF();
    // Tight alpha bounds measured from the actual original source cells,
    // preserving silhouette while avoiding invisible 96px padding.
    private static final int[][] BOUNDS={
        {3,12,93,83},{12,3,84,93},{3,8,93,88},{9,3,87,93},
        {3,11,93,84},{3,7,93,89},{3,13,93,82},{3,7,93,88},
        {3,13,93,83},{3,11,93,84},{3,11,93,85},{3,5,93,90},
        {3,7,93,88},{3,7,93,89},{5,3,90,93},{7,3,89,93}
    };
    public static synchronized void load(AssetManager assets){
        if(assets==null||attempted)return;
        attempted=true;
        try(InputStream in=assets.open("sp_v166_specialized_furniture.webp.b64")){
            ByteArrayOutputStream data=new ByteArrayOutputStream(64000);
            byte[] buffer=new byte[8192];int n;
            while((n=in.read(buffer))!=-1)data.write(buffer,0,n);
            byte[] raw=Base64.decode(data.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options o=new BitmapFactory.Options();
            o.inScaled=false;
            Bitmap result=BitmapFactory.decodeByteArray(raw,0,raw.length,o);
            if(result==null||result.getWidth()!=CELL*4||
                    result.getHeight()!=CELL*4)
                throw new IllegalArgumentException("Bad specialized furnishing atlas");
            atlas=result;
            android.util.Log.i("SP-V166","16 specialized furnished-room sprites ready");
        }catch(Exception err){
            android.util.Log.e("SP-V166","Specialized interior art failed",err);
            release();
        }
    }
    public static boolean ready(){
        return atlas!=null&&!atlas.isRecycled();
    }
    public static boolean drawAt(Canvas canvas,int sprite,float x,float y,
                                 float width,float height){
        if(!ready()||sprite<16||sprite>=16+COUNT||
                width<=0||height<=0)return false;
        int local=sprite-16, col=local%4,row=local/4;
        int[] bounds=BOUNDS[local];
        SRC.set(col*CELL+bounds[0],row*CELL+bounds[1],
                col*CELL+bounds[2],row*CELL+bounds[3]);
        DST.set(x,y,x+width,y+height);
        canvas.drawBitmap(atlas,SRC,DST,P);
        return true;
    }
    public static synchronized void release(){
        if(atlas!=null&&!atlas.isRecycled())atlas.recycle();
        atlas=null;attempted=false;
    }
}
