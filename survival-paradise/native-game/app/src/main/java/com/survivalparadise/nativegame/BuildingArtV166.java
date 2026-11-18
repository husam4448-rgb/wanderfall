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
 * V166: complete authored building-exterior art, not textures on former
 * prototype geometric roofs. Two distinct assets for each of the eight
 * city categories. The unchanged V154 building rectangle is the exact
 * outside wall/collision envelope. All signs/facades are baked into art.
 */
public final class BuildingArtV166 {
    private BuildingArtV166(){}
    private static Bitmap atlas;
    private static boolean attempted;
    private static final Rect SRC=new Rect();
    private static final RectF DST=new RectF();
    private static final Paint P=new Paint(Paint.FILTER_BITMAP_FLAG |
                                           Paint.DITHER_FLAG);
    public static synchronized void load(AssetManager assets){
        if(attempted||assets==null)return;
        attempted=true;
        try(InputStream input=assets.open("sp_v166_neighborhood.webp.b64")){
            ByteArrayOutputStream out=new ByteArrayOutputStream(196608);
            byte[] buf=new byte[8192];
            int read;
            while((read=input.read(buf))!=-1)out.write(buf,0,read);
            byte[] image=Base64.decode(out.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options options=new BitmapFactory.Options();
            options.inScaled=false;
            atlas=BitmapFactory.decodeByteArray(image,0,image.length,options);
            int c=BuildingArtSelectionV166.CELL;
            if(atlas==null||atlas.getWidth()!=c*BuildingArtSelectionV166.COLUMNS||
               atlas.getHeight()!=c*BuildingArtSelectionV166.ROWS)
                throw new IllegalArgumentException("V166 exterior atlas layout invalid");
            android.util.Log.i("SP-V166","Building exteriors ready: 8 families, 16 original sprites");
        }catch(Exception e){
            android.util.Log.e("SP-V166","Missing required V166 production exteriors",e);
            release();
        }
    }
    public static boolean ready(){return atlas!=null&&!atlas.isRecycled();}
    public static boolean draw(Canvas c,NeighborhoodV154.Building b,int worldSeed){
        if(!ready()||b==null||b.width<=0||b.height<=0)return false;
        int index=BuildingArtSelectionV166.choose(b.kind,b.variation,
            worldSeed,b.tileX,b.tileY,b.slot);
        if(!BuildingArtSelectionV166.valid(index))return false;
        int cell=BuildingArtSelectionV166.CELL;
        int col=index%BuildingArtSelectionV166.COLUMNS;
        int row=index/BuildingArtSelectionV166.COLUMNS;
        SRC.set(col*cell,row*cell,(col+1)*cell,(row+1)*cell);
        // Roof and facade remain fully WITHIN the original V154 collision
        // footprint. No newly passable roof, blocked entrance or phantom wall.
        DST.set(b.left,b.top,b.right(),b.bottom());
        c.drawBitmap(atlas,SRC,DST,P);
        return true;
    }
    public static synchronized void release(){
        if(atlas!=null&&!atlas.isRecycled())atlas.recycle();
        atlas=null;attempted=false;
    }
}
