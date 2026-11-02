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
import java.io.IOException;

/**
 * V100 visual-only game integration of the FOUR newly approved user-supplied
 * headgear sprite images. 256x64 atlas = 4 independent 64x64 RGBA sprites:
 * gas mask / olive helmet / riot visor / hazmat hood.
 *
 * 75%-160% scaling and idle breathing share the V82 character head pivot.
 * GameView already mirrors its entire local canvas for left-facing actors.
 * The original V31 character atlas is not altered or recolored here.
 */
public final class HeadgearApprovedV100 {
    public static final String SOURCE="approved_headgear_v100.png.b64";
    private final Bitmap atlas;
    private final Rect from=new Rect();
    private final RectF to=new RectF();

    public HeadgearApprovedV100(AssetManager assets){
        try(InputStream in=assets.open(SOURCE);
            ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] part=new byte[4096];int n;
            while((n=in.read(part))!=-1){
                if(out.size()+n>20000)throw new IOException("Headgear asset exceeds limit");
                out.write(part,0,n);
            }
            byte[] data=Base64.decode(out.toByteArray(),Base64.DEFAULT);
            atlas=BitmapFactory.decodeByteArray(data,0,data.length);
            if(atlas==null||atlas.getWidth()!=256||atlas.getHeight()!=64)
                throw new IOException("Wrong headgear atlas dimensions");
        }catch(Exception ex){
            throw new IllegalStateException("Approved V100 headgear source unavailable",ex);
        }
    }

    public void draw(Canvas canvas,int type,float charScale,
                     float headMultiplier,float headBob,Paint pixel){
        int kind=Math.floorMod(type,4);
        from.set(kind*64,0,(kind+1)*64,64);
        float[] b=HeadgearFitV100.bounds(kind,charScale,headMultiplier,headBob);
        to.set(b[0],b[1],b[2],b[3]);
        canvas.drawBitmap(atlas,from,to,pixel);
    }
}
