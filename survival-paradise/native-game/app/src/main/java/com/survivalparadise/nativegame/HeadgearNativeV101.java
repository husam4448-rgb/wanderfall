package com.survivalparadise.nativegame;

import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.Base64;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;

/**
 * V101 native-pixel fitting prototype. Adapts the FOUR selected V100 headgear
 * designs to the approved V31 head's 9px sprite grid ONCE at startup.
 * The cache includes only headgear pixels; original body / face and animations
 * remain unchanged. The game already mirrors its actor canvas for left-facing.
 */
public final class HeadgearNativeV101 {
    private static final String SOURCE="approved_headgear_v100.png.b64";
    private final Bitmap[] fitted=new Bitmap[4];
    private final RectF dest=new RectF();

    public HeadgearNativeV101(AssetManager assets){
        Bitmap original;
        try(InputStream in=assets.open(SOURCE);
            ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] buffer=new byte[4096];int n;
            while((n=in.read(buffer))!=-1){
                if(out.size()+n>20000)throw new IOException("Headgear source too large");
                out.write(buffer,0,n);
            }
            byte[] bytes=Base64.decode(out.toByteArray(),Base64.DEFAULT);
            original=BitmapFactory.decodeByteArray(bytes,0,bytes.length);
            if(original==null||original.getWidth()!=256||original.getHeight()!=64)
                throw new IOException("Unexpected approved headgear atlas dimensions");
        }catch(Exception ex){
            throw new IllegalStateException("Approved V100 headgear assets missing",ex);
        }
        for(int k=0;k<4;k++)fitted[k]=makeFitted(original,k);
    }

    static Bitmap makeFitted(Bitmap src,int kind){
        final int index=Math.floorMod(kind,4);
        int minX=64,minY=64,maxX=-1,maxY=-1;
        for(int y=0;y<64;y++)for(int x=0;x<64;x++){
            if(Color.alpha(src.getPixel(index*64+x,y))<=75)continue;
            minX=Math.min(minX,x);minY=Math.min(minY,y);
            maxX=Math.max(maxX,x);maxY=Math.max(maxY,y);
        }
        if(minX>maxX)throw new IllegalStateException("Empty approved headgear "+kind);
        Bitmap crop=Bitmap.createBitmap(src,index*64+minX,minY,
                maxX-minX+1,maxY-minY+1);
        int cols=HeadgearFitV101.COLUMNS[index],rows=HeadgearFitV101.ROWS[index];
        Bitmap logical=Bitmap.createScaledBitmap(crop,cols,rows,false);
        Bitmap scaled=Bitmap.createScaledBitmap(logical,
                cols*HeadgearFitV101.PIXEL_STEP,
                rows*HeadgearFitV101.PIXEL_STEP,false);
        Bitmap result=Bitmap.createBitmap(HeadgearFitV101.FRAME_WIDTH,
                HeadgearFitV101.FRAME_HEIGHT,Bitmap.Config.ARGB_8888);
        Canvas c=new Canvas(result);
        Paint nearest=new Paint();
        nearest.setAntiAlias(false);nearest.setFilterBitmap(false);
        c.drawBitmap(scaled,HeadgearFitV101.X[index],HeadgearFitV101.Y[index],nearest);
        if(index==0){
            tintGlass(result,49,73,49,70,135,164,173,40);
            tintGlass(result,84,108,49,70,135,164,173,40);
            // Cover an exposed hair pixel above the right-hand goggle.
            for(int y=29;y<47;y++)for(int x=105;x<114;x++)
                result.setPixel(x,y,Color.argb(255,20,20,24));
        }else if(index==2){
            tintGlass(result,42,106,49,73,121,140,162,48);
        }else if(index==3){
            tintGlass(result,44,105,47,73,112,136,147,35);
        }
        return result;
    }
    private static void tintGlass(Bitmap image,int x0,int x1,int y0,int y1,
                                  int r,int g,int b,int alpha){
        int tint=Color.argb(alpha,r,g,b);
        for(int y=y0;y<y1;y++)for(int x=x0;x<x1;x++){
            if(Color.alpha(image.getPixel(x,y))>0)image.setPixel(x,y,tint);
        }
    }
    public void draw(Canvas canvas,int type,float characterScale,
                     float headSize,float headBob,Paint paint){
        float[] bound=HeadgearFitV101.bounds(characterScale,headSize,headBob);
        dest.set(bound[0],bound[1],bound[2],bound[3]);
        canvas.drawBitmap(fitted[Math.floorMod(type,4)],null,dest,paint);
    }
}
