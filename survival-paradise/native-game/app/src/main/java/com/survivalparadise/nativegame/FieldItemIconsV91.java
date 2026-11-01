package com.survivalparadise.nativegame;

import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;

/** Distinct game-palette pixel silhouettes for the ten V91 salvage types. */
public final class FieldItemIconsV91 {
    private FieldItemIconsV91(){}
    private static void px(Canvas c,Paint p,int color,int x,int y,int w,int h){
        p.setColor(color);c.drawRect(x*3,y*3,(x+w)*3,(y+h)*3,p);
    }
    public static Drawable drawable(Resources res,int kind,int sizeDp){
        Bitmap icon=Bitmap.createBitmap(36,36,Bitmap.Config.ARGB_8888);
        Canvas c=new Canvas(icon);Paint p=new Paint(0);
        final int ink=0xff14221e,metal=0xff80928a,highlight=0xffceb78c,
            green=0xff6d936c,brown=0xff8c7258;
        switch(kind){
            case 0: // cloth folded
                px(c,p,ink,2,2,8,8);px(c,p,brown,3,3,6,6);px(c,p,highlight,4,4,3,1);break;
            case 1: // battery terminals
                px(c,p,ink,3,2,6,9);px(c,p,metal,4,3,4,7);
                px(c,p,highlight,5,1,2,2);px(c,p,green,5,5,2,3);break;
            case 2: // wires and copper
                px(c,p,ink,2,2,8,8);px(c,p,green,3,4,6,2);
                px(c,p,highlight,4,2,2,7);px(c,p,brown,7,3,1,6);break;
            case 3: // antiseptic container
                px(c,p,ink,3,3,6,8);px(c,p,metal,4,4,4,6);
                px(c,p,highlight,5,1,2,3);px(c,p,green,5,6,2,1);break;
            case 4: // fuel can
                px(c,p,ink,2,3,8,8);px(c,p,brown,3,4,6,6);
                px(c,p,highlight,4,2,4,2);px(c,p,ink,5,5,2,3);break;
            case 5: // filter cartridge
                px(c,p,ink,3,2,6,9);px(c,p,metal,4,3,4,7);
                px(c,p,green,4,4,4,2);px(c,p,highlight,4,8,4,1);break;
            case 6: // seed packet
                px(c,p,ink,2,2,8,9);px(c,p,brown,3,3,6,7);
                px(c,p,green,5,5,2,3);px(c,p,highlight,6,4,1,2);break;
            case 7: // toolkit
                px(c,p,ink,1,4,10,7);px(c,p,brown,2,5,8,5);
                px(c,p,metal,4,2,4,3);px(c,p,highlight,5,7,2,2);break;
            case 8: // coiled rope
                px(c,p,ink,2,2,8,8);px(c,p,highlight,3,3,6,6);
                px(c,p,brown,4,4,4,4);px(c,p,ink,5,5,2,2);break;
            default: // spare parts cog
                px(c,p,ink,2,2,8,8);px(c,p,metal,3,3,6,6);
                px(c,p,highlight,1,5,10,2);px(c,p,ink,5,4,2,4);break;
        }
        BitmapDrawable result=new BitmapDrawable(res,icon);
        result.setFilterBitmap(false);
        int px=Math.max(24,Math.round(sizeDp*res.getDisplayMetrics().density));
        result.setBounds(0,0,px,px);
        return result;
    }
}