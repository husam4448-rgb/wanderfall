package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;

/** V131: 15 distinct, crisp 48px authored silhouettes drawn from geometric
 * seams, stitching, hardware and soles. Never use one generic two-rectangle
 * icon for clothing. All artwork remains confined to the inventory icons.
 */
public final class GearItemIconsV95 {
    private GearItemIconsV95(){}
    private static final int INK=0xff172425,EDGE=0xff334746,THREAD=0xffd7c59b;
    private static Paint paint=new Paint(0);
    private static void rect(Canvas c,int x,int y,int w,int h,int color){
        paint.setStyle(Paint.Style.FILL);paint.setColor(color);
        c.drawRect(x,y,x+w,y+h,paint);
    }
    private static void poly(Canvas c,int color,float... coordinates){
        Path path=new Path();path.moveTo(coordinates[0],coordinates[1]);
        for(int i=2;i<coordinates.length;i+=2)
            path.lineTo(coordinates[i],coordinates[i+1]);
        path.close();paint.setColor(color);paint.setStyle(Paint.Style.FILL);
        c.drawPath(path,paint);
        paint.setColor(INK);paint.setStrokeWidth(2.8f);paint.setStrokeJoin(Paint.Join.ROUND);
        paint.setStyle(Paint.Style.STROKE);c.drawPath(path,paint);
        paint.setStyle(Paint.Style.FILL);
    }
    private static void seam(Canvas c,int x1,int y1,int x2,int y2,int color){
        paint.setColor(color);paint.setStrokeWidth(1.45f);
        c.drawLine(x1,y1,x2,y2,paint);
    }
    private static void drawPack(Canvas c,int variant,int primary,int accent){
        int h=variant==0?27:variant==1?34:36;
        int top=42-h;
        poly(c,primary,12,top+4,16,top,32,top,37,top+5,37,39,33,44,14,44,11,39);
        poly(c,INK,8,top+8,12,top+5,15,top+6,15,39,11,40,8,34);
        poly(c,INK,36,top+5,40,top+8,40,34,37,40,34,39,34,top+6);
        rect(c,15,top+6,18,variant==0?11:17,accent);
        rect(c,16,top+7,16,2,THREAD);
        rect(c,15,36,18,5,variant==2?0xff383e35:0xff514b36);
        rect(c,22,37,5,3,0xffdabf79);
        if(variant==2){
            rect(c,14,top+21,21,3,0xffba9e61);
            rect(c,17,top+24,15,8,0xff343f3b);
            rect(c,19,top+28,11,2,THREAD);
        }
        seam(c,13,top+7,13,37,EDGE);seam(c,35,top+7,35,37,EDGE);
    }
    private static void drawHead(Canvas c,int variant,int primary,int accent){
        if(variant==0){
            poly(c,primary,11,26,11,20,16,13,29,11,36,17,36,27,12,29);
            poly(c,accent,9,27,39,26,43,30,39,33,10,33,6,30);
            seam(c,14,21,33,21,THREAD);
        }else if(variant==1){
            poly(c,primary,13,25,16,13,22,9,28,9,34,16,35,27);
            poly(c,accent,5,27,43,27,45,31,3,31);
            rect(c,17,21,16,3,0xff5c6149);
            seam(c,15,25,34,25,THREAD);
        }else{
            poly(c,0xff51594e,12,28,12,18,19,10,31,10,37,20,35,33,31,37,16,37);
            rect(c,14,26,22,4,0xff8e8d66);
            rect(c,15,30,5,9,0xff303c39);
            rect(c,30,30,5,8,0xff303c39);
            seam(c,19,16,30,16,THREAD);
            rect(c,33,24,5,3,0xffd2b66e);
        }
    }
    private static void drawTorso(Canvas c,int variant,int primary,int accent){
        int end=variant==1?43:40;
        poly(c,primary,17,8,13,11,5,15,2,27,11,32,13,end,
            35,end,37,32,46,27,42,15,35,11,31,8,25,13,23,13);
        poly(c,accent,18,10,24,16,30,10,33,14,29,21,24,26,19,21,15,14);
        seam(c,24,26,24,end-2,THREAD);
        if(variant==0){
            rect(c,14,29,8,6,0xff344941);rect(c,27,29,8,6,0xff344941);
            seam(c,15,19,18,35,THREAD);
        }else if(variant==1){
            rect(c,11,35,8,5,0xff353e3a);rect(c,30,35,8,5,0xff353e3a);
            rect(c,20,37,8,3,0xffbd9e70);
        }else{
            poly(c,0xff343d3a,13,20,35,20,33,36,15,36);
            rect(c,17,22,14,11,0xff6a6e63);
            rect(c,18,24,12,3,0xffa5a384);
            rect(c,18,30,12,2,0xffab9967);
            rect(c,9,20,6,4,0xffba9a61);rect(c,35,20,6,4,0xffba9a61);
        }
        seam(c,16,12,9,29,0xffa9a887);seam(c,33,12,40,29,0xffa9a887);
    }
    private static void drawLegs(Canvas c,int variant,int primary,int accent){
        poly(c,primary,11,8,37,8,40,21,35,44,26,44,24,25,
            22,25,20,44,10,44,8,24);
        rect(c,13,10,22,3,0xffb1a77a);
        rect(c,22,10,4,4,INK);
        seam(c,24,14,24,27,INK);
        if(variant==0){
            rect(c,7,25,11,11,accent);rect(c,31,25,11,11,accent);
            rect(c,9,27,9,2,THREAD);rect(c,31,27,9,2,THREAD);
        }else if(variant==1){
            seam(c,11,23,20,23,THREAD);seam(c,28,23,38,23,THREAD);
            seam(c,13,34,20,34,accent);seam(c,29,34,36,34,accent);
        }else{
            rect(c,9,25,12,10,0xff4e5851);rect(c,28,25,12,10,0xff4e5851);
            rect(c,10,29,10,3,0xffbcaa78);rect(c,29,29,10,3,0xffbcaa78);
            rect(c,12,39,8,3,accent);rect(c,28,39,8,3,accent);
        }
    }
    private static void drawBoots(Canvas c,int variant,int primary,int accent){
        poly(c,primary,8,11,20,11,22,28,29,32,30,40,25,44,5,44,4,35,9,30);
        poly(c,primary,29,9,40,9,41,27,46,33,45,42,29,43,26,35,30,28);
        rect(c,5,39,24,5,INK);rect(c,29,38,17,6,INK);
        rect(c,6,40,22,2,0xffb79d66);rect(c,30,40,15,2,0xffb79d66);
        for(int y=18;y<=27;y+=4){
            seam(c,12,y,19,y,accent);seam(c,31,y,38,y,accent);
        }
        if(variant==0){
            rect(c,5,32,14,3,0xffa69b80);rect(c,29,30,10,3,0xffa69b80);
        }else if(variant==1){
            rect(c,15,13,6,4,0xffbd9f65);rect(c,35,12,6,4,0xffbd9f65);
        }else{
            rect(c,8,17,13,4,0xff3c4e49);rect(c,28,18,12,4,0xff3c4e49);
            seam(c,8,33,20,33,THREAD);seam(c,30,32,42,32,THREAD);
        }
    }
    private static Bitmap render(int kind,boolean silhouette){
        Bitmap bitmap=Bitmap.createBitmap(48,48,Bitmap.Config.ARGB_8888);
        Canvas canvas=new Canvas(bitmap);
        int variant=Math.floorMod(kind,3);
        int[] palette={0xff736448,0xff62756a,0xff49585b};
        int[] secondary={0xffa78c5e,0xffbac09b,0xff9c9169};
        int primary=silhouette?0xff66736d:palette[variant];
        int accent=silhouette?0xff66736d:secondary[variant];
        if(kind<3)drawPack(canvas,variant,primary,accent);
        else if(kind<6)drawHead(canvas,variant,primary,accent);
        else if(kind<9)drawTorso(canvas,variant,primary,accent);
        else if(kind<12)drawLegs(canvas,variant,primary,accent);
        else drawBoots(canvas,variant,primary,accent);
        return bitmap;
    }
    private static Drawable from(Context context,Bitmap bitmap,int dp){
        int pixels=Math.max(16,Math.round(dp*
            context.getResources().getDisplayMetrics().density));
        BitmapDrawable icon=new BitmapDrawable(context.getResources(),bitmap);
        icon.setFilterBitmap(false);icon.setBounds(0,0,pixels,pixels);
        return icon;
    }
    public static Drawable drawable(Context context,int kind,int dp){
        if(kind<0||kind>=GearLootV95.TYPES)return null;
        return from(context,render(kind,false),dp);
    }
    /** Unoccupied equipment socket placeholder, by actual body part. */
    public static Drawable silhouette(Context context,int equipmentSlot,int dp){
        int kind=equipmentSlot==5?0:equipmentSlot==0?3:
            equipmentSlot==2?6:equipmentSlot==3?9:
            equipmentSlot==4?12:-1;
        if(kind<0)return null;
        return from(context,render(kind,true),dp);
    }
}
