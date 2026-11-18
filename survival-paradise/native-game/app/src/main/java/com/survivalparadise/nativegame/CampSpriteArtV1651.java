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
 * V165.1 inspected original authored olive/sand camp tents.
 * Only renders fabric, bedding and props; NEVER changes world model,
 * character heads, saves, or open tent traversal.
 */
public final class CampSpriteArtV1651 {
    private CampSpriteArtV1651(){}
    private static final int WIDTH=334, HEIGHT=263;
    private static final Bitmap[] TENTS=new Bitmap[2];
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG |
                                           Paint.FILTER_BITMAP_FLAG |
                                           Paint.DITHER_FLAG);
    private static final RectF DST=new RectF();
    private static final Rect SRC_LEFT=new Rect(0,120,104,263);
    private static final Rect SRC_RIGHT=new Rect(230,120,334,263);
    private static boolean attempted=false;

    public static synchronized void load(AssetManager assets){
        if(attempted||assets==null)return;
        attempted=true;
        try(InputStream in=assets.open("sp_v1651_camp_tents.webp.b64")){
            ByteArrayOutputStream bytes=new ByteArrayOutputStream(8192);
            byte[] tmp=new byte[4096];int n;
            while((n=in.read(tmp))!=-1)bytes.write(tmp,0,n);
            byte[] decoded=Base64.decode(bytes.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options opts=new BitmapFactory.Options();
            opts.inScaled=false;
            Bitmap atlas=BitmapFactory.decodeByteArray(decoded,0,decoded.length,opts);
            if(atlas==null||atlas.getWidth()!=WIDTH*2||atlas.getHeight()!=HEIGHT)
                throw new IllegalArgumentException("Bad authored camp tent atlas");
            for(int i=0;i<2;i++)
                TENTS[i]=Bitmap.createBitmap(atlas,i*WIDTH,0,WIDTH,HEIGHT);
            atlas.recycle();
        }catch(Exception e){
            android.util.Log.w("SP-V1651","Tent sprites failed; V164 drawings remain",e);
            release();
        }
    }
    public static boolean ready(){return TENTS[0]!=null&&TENTS[1]!=null;}

    public static boolean drawTent(Canvas c,float x,float y,boolean olive){
        Bitmap b=TENTS[olive?0:1];
        if(b==null||b.isRecycled())return false;
        DST.set(x-WIDTH*.5f,y-155f,x+WIDTH*.5f,y+108f);
        c.drawBitmap(b,null,DST,P);
        return true;
    }

    /**
     * Depth-sorted forward side flaps; intentionally do not paint across the
     * middle doorway. A character inside a tent passes behind the fabric,
     * while one in front renders over it.
     */
    public static void drawFront(Canvas c,float x,float y,boolean olive){
        Bitmap b=TENTS[olive?0:1];
        if(b==null||b.isRecycled())return;
        DST.set(x-167f,y-35f,x-63f,y+108f);
        c.drawBitmap(b,SRC_LEFT,DST,P);
        DST.set(x+63f,y-35f,x+167f,y+108f);
        c.drawBitmap(b,SRC_RIGHT,DST,P);
    }

    public static synchronized void release(){
        for(int i=0;i<TENTS.length;i++){
            if(TENTS[i]!=null&&!TENTS[i].isRecycled())TENTS[i].recycle();
            TENTS[i]=null;
        }
        attempted=false;
    }
}
