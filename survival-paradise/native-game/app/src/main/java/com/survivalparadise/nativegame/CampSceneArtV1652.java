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
 * V165.2: original artistically detailed RGBA game props and organic ground
 * blend. Rendering only: existing camp identities, loot, trader inventories,
 * world seeds, original character heads and no-headgear policy are preserved.
 * Each bitmap is decoded only once and may be rendered at any zoom.
 */
public final class CampSceneArtV1652 {
    public static final int CHEST=0,WATCH=1,SOLAR=2,DEBRIS=3;
    private static final int CELL_W=384,CELL_H=288;
    private static final Bitmap[] ART=new Bitmap[4];
    private static Bitmap GROUND;
    private static Bitmap STARTER_GROUND;
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG |
        Paint.FILTER_BITMAP_FLAG | Paint.DITHER_FLAG);
    private static final RectF DST=new RectF();
    private static final Rect WATCH_FRONT=new Rect(
        CELL_W,140,CELL_W*2,CELL_H);
    private static final Rect CHEST_FRONT=new Rect(
        0,150,CELL_W,CELL_H);
    private static boolean loaded;
    private CampSceneArtV1652(){}

    private static Bitmap fromBase64(AssetManager a,String path) throws Exception{
        try(InputStream in=a.open(path)){
            ByteArrayOutputStream bytes=new ByteArrayOutputStream(8192);
            byte[] b=new byte[8192];int n;
            while((n=in.read(b))!=-1)bytes.write(b,0,n);
            byte[] data=Base64.decode(bytes.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options o=new BitmapFactory.Options();
            o.inScaled=false;
            Bitmap result=BitmapFactory.decodeByteArray(data,0,data.length,o);
            if(result==null)throw new IllegalArgumentException(path);
            return result;
        }
    }
    public static synchronized void load(AssetManager assets){
        if(loaded||assets==null)return;
        loaded=true;
        try {
            Bitmap props=fromBase64(assets,"sp_v1652_props.webp.b64");
            if(props.getWidth()!=768||props.getHeight()!=576)
                throw new IllegalArgumentException("Bad V165.2 four-prop atlas");
            for(int i=0;i<4;i++){
                ART[i]=Bitmap.createBitmap(props,(i&1)*CELL_W,
                    (i/2)*CELL_H,CELL_W,CELL_H);
            }
            props.recycle();
            GROUND=fromBase64(assets,"sp_v1652_ground.webp.b64");
            if(GROUND.getWidth()!=640||GROUND.getHeight()!=434)
                throw new IllegalArgumentException("Bad V165.2 camp ground decal");
            // The starter camp touches the original highway. A hard clip
            // would slice visible dirt at y+207: fade to transparent instead.
            STARTER_GROUND=GROUND.copy(Bitmap.Config.ARGB_8888,true);
            final int gw=STARTER_GROUND.getWidth(),gh=STARTER_GROUND.getHeight();
            int[] argb=new int[gw*gh];
            STARTER_GROUND.getPixels(argb,0,gw,0,0,gw,gh);
            for(int iy=0;iy<gh;iy++){
                float worldY=(iy+.5f)*650f/gh-325f;
                float fade=Math.max(0f,Math.min(1f,(207f-worldY)/90f));
                if(fade>=1f)continue;
                for(int ix=0;ix<gw;ix++){
                    int at=iy*gw+ix,v=argb[at];
                    argb[at]=(Math.round((v>>>24)*fade)<<24)|(v&0xffffff);
                }
            }
            STARTER_GROUND.setPixels(argb,0,gw,0,0,gw,gh);
            android.util.Log.i("SP-V1652","Organic camp ground and four authored props ready");
        }catch(Exception e){
            android.util.Log.e("SP-V1652","Camp scene art did not load",e);
            release();
        }
    }
    public static boolean ready(){
        if(GROUND==null||GROUND.isRecycled()||
           STARTER_GROUND==null||STARTER_GROUND.isRecycled())return false;
        for(Bitmap b:ART)if(b==null||b.isRecycled())return false;
        return true;
    }
    public static boolean ground(Canvas c,CampWorldV164.Site site){
        if(GROUND==null||GROUND.isRecycled())return false;
        float x=site.x,y=site.y;
        // The painted alpha fades to 0 around the full footprint; it never
        // draws a rectangle or displaces any collision or terrain tile.
        DST.set(x-480f,y-325f,x+480f,y+325f);
        Bitmap floor=site.starter?STARTER_GROUND:GROUND;
        if(floor==null||floor.isRecycled())return false;
        c.drawBitmap(floor,null,DST,P);
        return true;
    }
    public static boolean prop(Canvas c,int kind,float x,float y,
                               float width,float height){
        if(kind<0||kind>=ART.length||ART[kind]==null||
           ART[kind].isRecycled()||width<=0||height<=0)return false;
        DST.set(x-width*.5f,y-height*.5f,x+width*.5f,y+height*.5f);
        c.drawBitmap(ART[kind],null,DST,P);
        return true;
    }
    public static boolean chest(Canvas c,float x,float y){
        return prop(c,CHEST,x,y,104f,73f);
    }
    public static boolean guard(Canvas c,float x,float y){
        return prop(c,WATCH,x,y,170f,96f);
    }
    public static boolean solar(Canvas c,float x,float y){
        return prop(c,SOLAR,x,y,84f,64f);
    }
    public static boolean debris(Canvas c,float x,float y,boolean wide){
        return prop(c,DEBRIS,x,y,wide?92f:76f,wide?68f:56f);
    }
    /** World-Y foreground occlusion of real sandbags; NEVER flat color boxes. */
    public static boolean guardFront(Canvas c,float x,float y){
        Bitmap b=ART[WATCH];
        if(b==null||b.isRecycled())return false;
        // Bottom band of 170x96 frame (local Y 140/288..288/288).
        DST.set(x-85f,y-1.3f,x+85f,y+48f);
        c.drawBitmap(b,new Rect(0,140,CELL_W,CELL_H),DST,P);
        return true;
    }
    public static boolean chestFront(Canvas c,float x,float y){
        Bitmap b=ART[CHEST];
        if(b==null||b.isRecycled())return false;
        DST.set(x-52f,y+1.5f,x+52f,y+36.5f);
        c.drawBitmap(b,CHEST_FRONT,DST,P);
        return true;
    }
    public static synchronized void release(){
        if(STARTER_GROUND!=null&&!STARTER_GROUND.isRecycled())
            STARTER_GROUND.recycle();
        STARTER_GROUND=null;
        if(GROUND!=null&&!GROUND.isRecycled())GROUND.recycle();
        GROUND=null;
        for(int i=0;i<ART.length;i++){
            if(ART[i]!=null&&!ART[i].isRecycled())ART[i].recycle();
            ART[i]=null;
        }
        loaded=false;
    }
}
