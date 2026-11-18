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
 * V165.1 isolated, original, character-free trade shack and field clinic.
 * This is presentation ONLY: NPC identities, trade ledger, healing, inventory,
 * caches, saved-world IDs and collision topology are untouched.
 */
public final class CampStationSpriteV1651 {
    private CampStationSpriteV1651(){}
    private static final Bitmap[] sprites=new Bitmap[2];
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG |
                                           Paint.FILTER_BITMAP_FLAG |
                                           Paint.DITHER_FLAG);
    private static final RectF dst=new RectF();
    private static final Rect counter=new Rect(0,143,250,195);
    private static final Rect medicLeft=new Rect(0,94,65,215);
    private static final Rect medicRight=new Rect(185,94,250,215);
    private static boolean attempted;

    public static synchronized void load(AssetManager assets){
        if(attempted||assets==null)return;
        attempted=true;
        try(InputStream in=assets.open("sp_v1651_stations.webp.b64")){
            ByteArrayOutputStream bytes=new ByteArrayOutputStream(8192);
            byte[] tmp=new byte[4096];int n;
            while((n=in.read(tmp))!=-1)bytes.write(tmp,0,n);
            byte[] decoded=Base64.decode(bytes.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options opts=new BitmapFactory.Options();
            opts.inScaled=false;
            Bitmap atlas=BitmapFactory.decodeByteArray(decoded,0,decoded.length,opts);
            if(atlas==null||atlas.getWidth()!=500||atlas.getHeight()!=215)
                throw new IllegalArgumentException("Bad V1651 camp station atlas");
            sprites[0]=Bitmap.createBitmap(atlas,0,0,250,215);
            sprites[1]=Bitmap.createBitmap(atlas,250,0,250,215);
            atlas.recycle();
            android.util.Log.i("SP-V1651","Trade and medic stations ready: 2 authored RGBA sprites");
        }catch(Exception e){
            android.util.Log.w("SP-V1651","Camp station artwork unavailable",e);
            release();
        }
    }

    public static boolean ready(){return sprites[0]!=null&&sprites[1]!=null;}
    public static boolean drawTrader(Canvas c,float x,float y){
        Bitmap b=sprites[0];if(b==null||b.isRecycled())return false;
        dst.set(x-125f,y-140f,x+125f,y+75f);
        c.drawBitmap(b,null,dst,P);
        return true;
    }
    public static boolean drawMedic(Canvas c,float x,float y){
        Bitmap b=sprites[1];if(b==null||b.isRecycled())return false;
        dst.set(x-125f,y-115f,x+125f,y+100f);
        c.drawBitmap(b,null,dst,P);
        return true;
    }
    /** Only the real front counter occludes actors behind it. */
    public static boolean drawTraderFront(Canvas c,float x,float y){
        Bitmap b=sprites[0];if(b==null||b.isRecycled())return false;
        dst.set(x-125f,y+3f,x+125f,y+55f);
        c.drawBitmap(b,counter,dst,P);
        return true;
    }
    /** Keep center medical doorway clear: depth overlay is side fabric ONLY. */
    public static boolean drawMedicFront(Canvas c,float x,float y){
        Bitmap b=sprites[1];if(b==null||b.isRecycled())return false;
        dst.set(x-125f,y-21f,x-60f,y+100f);
        c.drawBitmap(b,medicLeft,dst,P);
        dst.set(x+60f,y-21f,x+125f,y+100f);
        c.drawBitmap(b,medicRight,dst,P);
        return true;
    }
    public static synchronized void release(){
        for(int i=0;i<2;i++){
            if(sprites[i]!=null&&!sprites[i].isRecycled())sprites[i].recycle();
            sprites[i]=null;
        }
        attempted=false;
    }
}
