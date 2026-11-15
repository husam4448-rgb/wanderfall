package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;

/** Original compact pixel-art HEX NUT currency icons, not coins or gems.
 * Three materials share one exact geometry: iron, silver, and gold.
 */
final class NutIconsV143 {
    private NutIconsV143(){}
    private static Paint fill(int color){
        Paint p=new Paint();p.setColor(color);
        p.setAntiAlias(false);p.setFilterBitmap(false);return p;
    }
    private static Path hex(int left,int top,int right,int bottom){
        Path p=new Path();
        int cut=(right-left)/4;
        p.moveTo(left+cut,top);p.lineTo(right-cut,top);
        p.lineTo(right,(top+bottom)/2f);
        p.lineTo(right-cut,bottom);p.lineTo(left+cut,bottom);
        p.lineTo(left,(top+bottom)/2f);p.close();return p;
    }
    static Drawable drawable(Context context,int denomination,int dp){
        if(denomination<0||denomination>2)return null;
        final int[] main={0xff788992,0xffc6d0df,0xffdfb34a},
            shine={0xffb4c2c7,0xfff1f5fa,0xffffe493},
            shade={0xff425560,0xff7d93ae,0xff936426};
        Bitmap bmp=Bitmap.createBitmap(40,40,Bitmap.Config.ARGB_8888);
        Canvas c=new Canvas(bmp);
        c.drawPath(hex(3,5,37,34),fill(0xff0f1c21));
        c.drawPath(hex(6,7,34,30),fill(shade[denomination]));
        c.drawPath(hex(7,6,33,27),fill(main[denomination]));
        c.drawPath(hex(9,8,31,13),fill(shine[denomination]));
        // Drilled through-hole with dark interior and a metallic rim.
        c.drawCircle(20,18,8,fill(0xff14262e));
        c.drawCircle(20,17,5,fill(0xff37444b));
        c.drawRect(17,12,22,13,fill(0xff111b21));
        c.drawRect(9,28,31,31,fill(shade[denomination]));
        BitmapDrawable d=new BitmapDrawable(context.getResources(),bmp);
        d.setFilterBitmap(false);
        int px=Math.max(20,Math.round(dp*context.getResources().
            getDisplayMetrics().density));
        d.setBounds(0,0,px,px);return d;
    }
}
