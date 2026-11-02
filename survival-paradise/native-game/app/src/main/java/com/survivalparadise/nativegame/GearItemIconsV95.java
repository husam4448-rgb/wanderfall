package com.survivalparadise.nativegame;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;

/** Small, readable gear item icons based on original native pixel-art sources. */
public final class GearItemIconsV95 {
    private GearItemIconsV95(){}
    private static void rect(Canvas c,Paint p,int x,int y,int w,int h,int color){
        p.setColor(color);c.drawRect(x,y,x+w,y+h,p);
    }
    public static Drawable drawable(Context context,int kind,int dp){
        if(kind<0||kind>=GearLootV95.TYPES)return null;
        Bitmap src=null;
        String path=kind<3?"backpack.png":kind<6?"headgear.png":
            kind<9?"vest.png":null;
        if(path!=null){
            try(java.io.InputStream in=context.getAssets().open("pixel_gear_v95/"+path)){
                src=BitmapFactory.decodeStream(in);
            }catch(Exception ignored){}
        }
        if(src==null){
            src=Bitmap.createBitmap(20,20,Bitmap.Config.ARGB_8888);
            Canvas c=new Canvas(src);Paint p=new Paint(0);
            int dark=0xff142422,cloth=kind%3==0?0xff686d51:
                kind%3==1?0xff677a6d:0xff546068;
            if(kind<12){
                rect(c,p,3,3,6,13,dark);rect(c,p,11,3,6,13,dark);
                rect(c,p,4,4,4,11,cloth);rect(c,p,12,4,4,11,cloth);
                rect(c,p,3,13,6,4,0xff26382d);rect(c,p,11,13,6,4,0xff26382d);
            }else{
                rect(c,p,1,7,8,9,dark);rect(c,p,10,7,9,9,dark);
                rect(c,p,3,8,5,6,cloth);rect(c,p,12,8,5,6,cloth);
                rect(c,p,1,15,8,2,0xff9b9678);rect(c,p,10,15,9,2,0xff9b9678);
            }
        }
        int size=Math.max(16,Math.round(dp*context.getResources().getDisplayMetrics().density));
        BitmapDrawable out=new BitmapDrawable(context.getResources(),src);
        out.setFilterBitmap(false);out.setBounds(0,0,size,size);
        return out;
    }
}
