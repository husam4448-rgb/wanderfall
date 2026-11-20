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
 * Real authored V166 furniture artwork: 96 themed equipment identities with
 * TWO separately painted top-down / profile sprites each.
 *
 * Renders the immutable, offline authored WebP alpha atlas. The old 128px
 * Canvas geometric placeholder renderer is removed, not layered beneath it.
 * Placement and collisions are entirely owned by NeighborhoodLayoutV163.
 * No per-frame bitmap allocations or runtime procedural object painting.
 */
public final class InteriorDirectionalFurnitureV166 {
    private InteriorDirectionalFurnitureV166(){}
    public static final int FIRST=InteriorFurnitureCatalogV166.FIRST;
    public static final int COUNT=InteriorFurnitureCatalogV166.COUNT;
    private static final int CELL=128,COLS=16,ROWS=12;
    private static final String FILE="sp_v166_directional_furniture.webp.b64";
    private static Bitmap atlas;
    private static boolean attempted;
    private static final Rect SOURCE=new Rect();
    private static final RectF DEST=new RectF();
    private static final Paint FILTER=new Paint(Paint.FILTER_BITMAP_FLAG|
        Paint.DITHER_FLAG);

    public static boolean valid(int sprite){
        return InteriorFurnitureCatalogV166.valid(sprite);
    }
    public static int kind(int sprite){
        return InteriorFurnitureCatalogV166.kind(sprite);
    }
    public static synchronized void load(AssetManager assets){
        if(attempted||assets==null)return;
        attempted=true;
        try(InputStream stream=assets.open(FILE)){
            ByteArrayOutputStream encoded=new ByteArrayOutputStream(180000);
            byte[] buf=new byte[8192];int count;
            while((count=stream.read(buf))!=-1)encoded.write(buf,0,count);
            byte[] raw=Base64.decode(encoded.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options options=new BitmapFactory.Options();
            options.inScaled=false;options.inPreferredConfig=Bitmap.Config.ARGB_8888;
            Bitmap result=BitmapFactory.decodeByteArray(raw,0,raw.length,options);
            if(result==null||result.getWidth()!=COLS*CELL||
               result.getHeight()!=ROWS*CELL){
                if(result!=null)result.recycle();
                throw new IllegalArgumentException(
                    "Invalid V166 authored directional art atlas dimensions");
            }
            atlas=result;
            android.util.Log.i("SP-V166",
                "Directional furniture ready: 96 fully authored object variants / 192 face views");
        }catch(Exception err){
            android.util.Log.e("SP-V166",
                "Missing source-authored directional furniture. Not silently using geometric placeholders.",err);
        }
    }
    public static boolean ready(){
        return atlas!=null&&!atlas.isRecycled();
    }
    public static boolean drawAt(Canvas canvas,int sprite,
                                 float x,float y,float width,float height,int facing){
        if(!valid(sprite)||width<=0||height<=0||!ready())return false;
        // Each side-facing pixel is authored independently rather than a
        // rotated south-facing square. 270 is a horizontal mirror ONLY.
        int side=(facing==90||facing==270)?1:0;
        int index=(sprite-FIRST)*2+side;
        int sx=(index%COLS)*CELL,sy=(index/COLS)*CELL;
        SOURCE.set(sx,sy,sx+CELL,sy+CELL);
        DEST.set(x,y,x+width,y+height);
        if(facing==270){
            canvas.save();
            canvas.scale(-1f,1f,x+width*.5f,y+height*.5f);
            canvas.drawBitmap(atlas,SOURCE,DEST,FILTER);
            canvas.restore();
        }else{
            canvas.drawBitmap(atlas,SOURCE,DEST,FILTER);
        }
        return true;
    }
    public static synchronized void release(){
        if(atlas!=null&&!atlas.isRecycled())atlas.recycle();
        atlas=null;attempted=false;
    }
}
