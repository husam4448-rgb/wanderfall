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
 * V166 original furniture art, all 8 V154 neighborhood themes. Each asset
 * is a complete transparent object rather than paint over a rectangle.
 * Per-object location, width, height, collision and interactions remain V163.
 */
public final class InteriorPropArtV166 {
    private InteriorPropArtV166(){}
    private static Bitmap atlas;
    private static boolean attempted;
    private static final Rect SRC=new Rect();
    private static final RectF DST=new RectF();
    private static final Paint P=new Paint(Paint.FILTER_BITMAP_FLAG |
        Paint.DITHER_FLAG);
    // Tight source silhouettes inside 256x256 cells: reduces invisible
    // footprint margins and matches the existing collision rectangle.
    private static final int[][] BOUNDS={
        {33,16,222,241},{41,16,215,241},{16,31,240,225},{64,16,192,241},
        {30,15,226,241},{20,15,236,240},{32,15,224,241},{26,15,230,240},
        {30,15,225,240},{20,16,235,240},{26,15,230,240},{16,24,240,231},
        {16,31,240,225},{18,16,238,240},{16,23,240,233},{16,49,240,207}
    };
    public static synchronized void load(AssetManager assets){
        if(assets==null||attempted)return;
        attempted=true;
        try(InputStream in=assets.open("sp_v166_furniture.webp.b64")){
            ByteArrayOutputStream bytes=new ByteArrayOutputStream(262144);
            byte[] buf=new byte[8192];int n;
            while((n=in.read(buf))!=-1)bytes.write(buf,0,n);
            byte[] raw=Base64.decode(bytes.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options options=new BitmapFactory.Options();
            options.inScaled=false;
            atlas=BitmapFactory.decodeByteArray(raw,0,raw.length,options);
            int c=InteriorPropSelectionV166.CELL;
            if(atlas==null||atlas.getWidth()!=c*4||atlas.getHeight()!=c*4)
                throw new IllegalArgumentException("Invalid V166 furniture atlas");
            android.util.Log.i("SP-V166","Indoor furniture ready: 16 authored objects, 8 room families");
        }catch(Exception e){
            android.util.Log.e("SP-V166","Unable to decode furniture production atlas",e);
            release();
        }
    }
    public static boolean ready(){return atlas!=null&&!atlas.isRecycled();}
    /**
     * Painted inside the exact V163 solid furniture bbox. Every footprint is
     * already inside a seeded room and excluded from all doors/caches.
     */
    public static boolean draw(Canvas c,float[] q,int theme,int variation,int index){
        if(q==null||q.length<5)return false;
        int sprite=InteriorPropSelectionV166.choose(
            theme,(int)q[0],index,q[3],q[4]);
        int facing=q.length>5?(int)q[5]:0;
        if(facing==0)return drawAt(c,sprite,q[1],q[2],q[3],q[4]);
        float cx=q[1]+q[3]*.5f,cy=q[2]+q[4]*.5f;
        c.save();
        c.rotate(facing,cx,cy);
        boolean drawn;
        if(facing==90||facing==270)
            drawn=drawAt(c,sprite,cx-q[4]*.5f,cy-q[3]*.5f,q[4],q[3]);
        else drawn=drawAt(c,sprite,q[1],q[2],q[3],q[4]);
        c.restore();
        return drawn;
    }
    public static boolean drawAt(Canvas canvas,int sprite,float x,float y,
                                 float width,float height){
        if(!InteriorPropSelectionV166.valid(sprite)||
           width<=0||height<=0)return false;
        if(sprite>=48)
            return InteriorEnsembleArtV166.drawAt(
                canvas,sprite,x,y,width,height);
        if(sprite>=32)
            return InteriorScenePropArtV166.drawAt(
                canvas,sprite,x,y,width,height);
        if(sprite>=16)
            return InteriorSpecialPropArtV166.drawAt(
                canvas,sprite,x,y,width,height);
        if(!ready())return false;
        int cell=InteriorPropSelectionV166.CELL;
        int col=sprite%4,row=sprite/4;
        int[] b=BOUNDS[sprite];
        SRC.set(col*cell+b[0],row*cell+b[1],
                col*cell+b[2],row*cell+b[3]);
        // No source silhouette is permitted to overhang the original solid.
        DST.set(x,y,x+width,y+height);
        canvas.drawBitmap(atlas,SRC,DST,P);
        return true;
    }
    public static synchronized void release(){
        if(atlas!=null&&!atlas.isRecycled())atlas.recycle();
        atlas=null;attempted=false;
    }
}
