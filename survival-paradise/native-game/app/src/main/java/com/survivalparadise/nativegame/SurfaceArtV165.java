package com.survivalparadise.nativegame;

import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.BitmapShader;
import android.graphics.Canvas;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.Shader;
import android.util.Base64;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;

/**
 * V165 first authored surface pass. Four original top-down texture paintings
 * are encoded in a small WebP atlas; repeatable world-space shaders dress
 * EXISTING roads and terrain without changing geometry, hitboxes, world RNG,
 * object identities, saves, or the legacy character asset pipeline.
 */
public final class SurfaceArtV165 {
    private SurfaceArtV165(){}
    public static final int ASPHALT=0, AGED_PAVEMENT=1, CONCRETE=2, SOIL=3;
    private static final Bitmap[] tiles=new Bitmap[4];
    private static final BitmapShader[] shaders=new BitmapShader[4];
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG |
                                           Paint.FILTER_BITMAP_FLAG |
                                           Paint.DITHER_FLAG);
    private static final Matrix MAT=new Matrix();
    private static boolean attempted;
    public static synchronized void load(AssetManager assets){
        if(attempted)return;
        attempted=true;
        if(assets==null)return;
        try(InputStream in=assets.open("sp_v165_surface.webp.b64")){
            ByteArrayOutputStream bytes=new ByteArrayOutputStream(8192);
            byte[] buffer=new byte[4096];
            int n;
            while((n=in.read(buffer))!=-1)bytes.write(buffer,0,n);
            byte[] raw=Base64.decode(bytes.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options opts=new BitmapFactory.Options();
            opts.inScaled=false;
            Bitmap atlas=BitmapFactory.decodeByteArray(raw,0,raw.length,opts);
            if(atlas==null||atlas.getWidth()<64||atlas.getHeight()<64)
                throw new IllegalArgumentException("Bad V165 texture atlas");
            int w=atlas.getWidth()/2,h=atlas.getHeight()/2;
            for(int i=0;i<4;i++){
                tiles[i]=Bitmap.createBitmap(atlas,(i%2)*w,(i/2)*h,w,h);
                shaders[i]=new BitmapShader(tiles[i],Shader.TileMode.REPEAT,
                                            Shader.TileMode.REPEAT);
            }
            atlas.recycle();
        }catch(Exception e){
            android.util.Log.w("SP-V165","Surface atlas unavailable; retaining V164 colors",e);
            release();
        }
    }
    public static boolean ready(){return shaders[ASPHALT]!=null;}
    private static boolean bind(int material,float worldTile,int opacity){
        if(material<0||material>=shaders.length||shaders[material]==null)
            return false;
        MAT.reset();
        MAT.setScale(worldTile/tiles[material].getWidth(),
                     worldTile/tiles[material].getHeight());
        shaders[material].setLocalMatrix(MAT);
        P.setShader(shaders[material]);
        P.setStyle(Paint.Style.FILL);
        P.setAlpha(Math.max(0,Math.min(255,opacity)));
        return true;
    }
    private static void unbind(){
        P.setShader(null);
        P.setAlpha(255);
    }
    public static void rect(Canvas c,float x,float y,float width,float height,
                            int material,float worldTile,int opacity){
        if(width<=0||height<=0||!bind(material,worldTile,opacity))return;
        c.drawRect(x,y,x+width,y+height,P);
        unbind();
    }
    public static void path(Canvas c,Path shape,int material,float worldTile,
                            int opacity){
        if(shape==null||!bind(material,worldTile,opacity))return;
        c.drawPath(shape,P);
        unbind();
    }
    public static synchronized void release(){
        for(int i=0;i<tiles.length;i++){
            shaders[i]=null;
            if(tiles[i]!=null&&!tiles[i].isRecycled())tiles[i].recycle();
            tiles[i]=null;
        }
        attempted=false;
    }
}
