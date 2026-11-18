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
 * V165.2 original world-ground pigment brushes: dirt, grass and dry soil.
 * Replaces the visible fourteen-sided monochrome V157 polygons, retaining
 * exact V157 world locations, biome categories, seed and patch rotations.
 * No tile geometry, saved world state or spawn/harvest system is touched.
 */
public final class NaturalBrushArtV1652 {
    private static final Paint P=new Paint(Paint.ANTI_ALIAS_FLAG |
        Paint.FILTER_BITMAP_FLAG | Paint.DITHER_FLAG);
    private static final Rect SRC=new Rect();
    private static final RectF DST=new RectF();
    private static Bitmap atlas;
    private static boolean attempted;
    private NaturalBrushArtV1652(){}

    public static synchronized void load(AssetManager assets){
        if(assets==null||attempted)return;
        attempted=true;
        try(InputStream in=assets.open("sp_v1652_biome_blends.webp.b64")){
            ByteArrayOutputStream stream=new ByteArrayOutputStream(8192);
            byte[] buf=new byte[4096];int n;
            while((n=in.read(buf))!=-1)stream.write(buf,0,n);
            byte[] data=Base64.decode(stream.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options o=new BitmapFactory.Options();
            o.inScaled=false;
            atlas=BitmapFactory.decodeByteArray(data,0,data.length,o);
            if(atlas==null||atlas.getWidth()!=768||atlas.getHeight()!=256)
                throw new IllegalArgumentException("Invalid organic biome brush atlas");
            // The original three-pigment atlas still carried substantial
            // alpha on some source CELL boundaries. A 30%-opaque cropped
            // rectangle rotated 40 degrees becomes the conspicuous straight
            // diagonal terrain bands seen in real emulator screenshots.
            // Feather EACH tile to zero once at load, never per frame.
            final int w=atlas.getWidth(),h=atlas.getHeight();
            int[] pixels=new int[w*h];
            atlas.getPixels(pixels,0,w,0,0,w,h);
            for(int y=0;y<h;y++){

                for(int x=0;x<w;x++){
                    int lx=x%256;

                    // Radial feather eliminates the rotated square's long,
                    // straight diagonal edges (the 38px strip was insufficient).
                    float ux=(lx-127.5f)/127.5f;
                    float uy=(y-127.5f)/127.5f;
                    float radius=(float)Math.sqrt(ux*ux+uy*uy);
                    float edge=Math.max(0f,Math.min(1f,(1.03f-radius)/.43f));
                    float feather=edge*edge*(3f-2f*edge);
                    int i=y*w+x;
                    int a=(pixels[i]>>>24);
                    pixels[i]=((Math.round(a*feather)&255)<<24)|
                        (pixels[i]&0x00ffffff);
                }
            }
            Bitmap masked=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);
            masked.setPixels(pixels,0,w,0,0,w,h);
            atlas.recycle();
            atlas=masked;
            android.util.Log.i("SP-V1652","Biome perimeter alpha feather: 38 pixels, three cells");
            android.util.Log.i("SP-V1652",
                "Natural biome brushes ready: 3 transparent authored pigments");
        }catch(Exception e){
            android.util.Log.e("SP-V1652","Missing natural brushes",e);
            release();
        }
    }
    public static boolean ready(){return atlas!=null&&!atlas.isRecycled();}
    public static boolean patch(Canvas c,NaturalGroundV157.Patch b,
                                int biome,boolean distant){
        if(!ready()||b==null)return false;
        int kind=b.kind;
        if(kind==NaturalGroundV157.GRASS&&
            (biome==BiomeWorldV74.DESERT||biome==BiomeWorldV74.HIGHLANDS))
            kind=NaturalGroundV157.DRY;
        if(kind==NaturalGroundV157.DIRT&&biome==BiomeWorldV74.WETLAND)
            kind=NaturalGroundV157.GRASS;
        SRC.set(kind*256,0,kind*256+256,256);
        // Alpha fades organically to zero at the edges, unlike a polygon
        // clipped to an arbitrary edge with uniform fill.
        DST.set(b.x-b.rx*1.15f,b.y-b.ry*1.15f,
                b.x+b.rx*1.15f,b.y+b.ry*1.15f);
        P.setAlpha(distant?214:255);
        c.save();
        c.rotate(b.rotation+(b.variation%3-1)*9f,b.x,b.y);
        c.drawBitmap(atlas,SRC,DST,P);
        c.restore();
        P.setAlpha(255);
        return true;
    }

    // Preallocated tint filters preserve the authored pigment detail while
    // differentiating industrial gravel, village earth and city concrete.
    private static final android.graphics.LightingColorFilter[] SETTLEMENT_TINT={
        new android.graphics.LightingColorFilter(0xffa6abb1,0x00070909),
        new android.graphics.LightingColorFilter(0xffd6ae86,0x00070503),
        new android.graphics.LightingColorFilter(0xffb5b3a5,0x00090604)
    };

    public static boolean stampSettlement(Canvas c,int kind,float x,float y,
                                          float width,float height,int variation,
                                          int alpha,int regionKind){
        if(regionKind<0||regionKind>=SETTLEMENT_TINT.length)return false;
        P.setColorFilter(SETTLEMENT_TINT[regionKind]);
        try{
            return stamp(c,kind,x,y,width,height,variation,alpha);
        }finally{
            P.setColorFilter(null);
        }
    }

    /** Paint author-sourced transparent ground in a physical world footprint. */
    public static boolean stamp(Canvas c,int kind,float x,float y,
                                float width,float height,int variation,int alpha){
        if(!ready()||kind<0||kind>2||width<=0||height<=0)return false;
        SRC.set(kind*256,0,(kind+1)*256,256);
        DST.set(x-width*.5f,y-height*.5f,x+width*.5f,y+height*.5f);
        P.setAlpha(Math.max(0,Math.min(255,alpha)));
        c.save();
        c.rotate(Math.floorMod(variation,150)-75f,x,y);
        c.drawBitmap(atlas,SRC,DST,P);
        c.restore();
        P.setAlpha(255);
        return true;
    }

    public static synchronized void release(){
        if(atlas!=null&&!atlas.isRecycled())atlas.recycle();
        atlas=null;attempted=false;
    }
}
