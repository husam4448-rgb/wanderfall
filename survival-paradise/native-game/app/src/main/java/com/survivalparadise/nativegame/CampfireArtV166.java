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
 * V166 authored campfire atlas: four looping flame states and one extinguished
 * bed. World-coordinate draw/seeded phase only. Gameplay fire, light emission,
 * heat, NPC interactions, saved objects and Y-sorted actor ordering unchanged.
 */
public final class CampfireArtV166 {
    private CampfireArtV166(){}
    private static final int CELL=256,FRAMES=5;
    private static Bitmap art;
    private static boolean attempted;
    private static final Rect SRC=new Rect();
    private static final RectF DST=new RectF();
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG |
                                           Paint.FILTER_BITMAP_FLAG |
                                           Paint.DITHER_FLAG);

    public static synchronized void load(AssetManager a){
        if(a==null||attempted)return;
        attempted=true;
        try(InputStream in=a.open("sp_v166_campfire.webp.b64")){
            ByteArrayOutputStream bytes=new ByteArrayOutputStream(16384);
            byte[] chunk=new byte[8192];int n;
            while((n=in.read(chunk))!=-1)bytes.write(chunk,0,n);
            byte[] binary=Base64.decode(bytes.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options options=new BitmapFactory.Options();
            options.inScaled=false;
            art=BitmapFactory.decodeByteArray(binary,0,binary.length,options);
            if(art==null||art.getWidth()!=FRAMES*CELL||art.getHeight()!=CELL)
                throw new IllegalArgumentException("Invalid campfire atlas dimensions");
            android.util.Log.i("SP-V166","Campfire production sprites ready: 4 lit + 1 unlit");
        }catch(Exception ex){
            android.util.Log.e("SP-V166","Campfire production artwork unavailable",ex);
            release();
        }
    }
    public static boolean ready(){return art!=null&&!art.isRecycled();}
    /** Stable fire phase; never advances game/world RNG or saved identity. */
    public static boolean draw(Canvas canvas,float x,float y,
                               boolean burning,float worldSeconds){
        if(!ready())return false;
        int frame=burning?Math.floorMod(
            (int)Math.floor(worldSeconds*5.2f)+
                (WorldChunkModel.hash(Math.round(x),Math.round(y))&3),4):4;
        SRC.set(frame*CELL,0,(frame+1)*CELL,CELL);
        // Ground contact at y+20. Preserves old V50 fire's physical footprint,
        // transparent rocks, and room for the original living characters.
        DST.set(x-86f,y-118f,x+86f,y+21f);
        canvas.drawBitmap(art,SRC,DST,P);
        return true;
    }
    public static synchronized void release(){
        if(art!=null&&!art.isRecycled())art.recycle();
        art=null;attempted=false;
    }
}
