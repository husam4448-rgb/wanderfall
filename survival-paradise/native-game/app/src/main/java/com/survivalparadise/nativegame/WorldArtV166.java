package com.survivalparadise.nativegame;

import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
import java.io.InputStream;

/**
 * V166 production sprite library: authored atlas / deterministic selector /
 * dimension-normalized world painter. The game model owns geography, object
 * identities, collision, interactions, trading and inventory independently.
 *
 * One bitmap and a reused source/destination rectangle per draw pass.
 * No per-frame asset decoding, RNG advancement or character transformations.
 */
public final class WorldArtV166 {
    private WorldArtV166(){}
    private static Bitmap atlas;
    private static boolean attempted;
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG |
        Paint.FILTER_BITMAP_FLAG | Paint.DITHER_FLAG);
    private static final Rect SRC=new Rect();
    private static final RectF DST=new RectF();

    public static synchronized void load(AssetManager assets){
        if(attempted||assets==null)return;
        attempted=true;
        try(InputStream in=assets.open("world_props_v166.png")){
            BitmapFactory.Options o=new BitmapFactory.Options();
            o.inScaled=false;
            atlas=BitmapFactory.decodeStream(in,null,o);
            if(atlas==null||atlas.getWidth()!=
                WorldArtSelectionV166.SPRITES*WorldArtSelectionV166.CELL||
                atlas.getHeight()!=WorldArtSelectionV166.CELL)
                throw new IllegalArgumentException("V166 atlas layout mismatch");
            android.util.Log.i("SP-V166","World sprite library ready: 23 original-art variations");
        }catch(Exception e){
            android.util.Log.e("SP-V166",
                "V166 world sprite atlas unavailable, see art QA requirements",e);
            release();
        }
    }
    public static boolean ready(){return atlas!=null&&!atlas.isRecycled();}
    /**
     * Draw anchored at the world-space foot/base, never at a screen position.
     * Returns false for missing art, so the caller can retain legacy gameplay
     * without manufacturing a replacement collision shape.
     */
    public static boolean draw(Canvas canvas,int family,float x,float y,
                               float width,float height,int seed,int identity){
        if(!ready()||width<=0f||height<=0f)return false;
        int i=WorldArtSelectionV166.choose(family,x,y,seed,identity);
        if(!WorldArtSelectionV166.valid(i))return false;
        int cell=WorldArtSelectionV166.CELL;
        SRC.set(i*cell,0,(i+1)*cell,cell);
        DST.set(x-width*.5f,y-height,x+width*.5f,y);
        canvas.drawBitmap(atlas,SRC,DST,P);
        return true;
    }
    public static synchronized void release(){
        if(atlas!=null&&!atlas.isRecycled())atlas.recycle();
        atlas=null;attempted=false;
    }
}
