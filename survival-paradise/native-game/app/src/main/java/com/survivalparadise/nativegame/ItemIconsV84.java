package com.survivalparadise.nativegame;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.content.res.Resources;

/** Original compact pixel item silhouettes generated once; no render-time allocation. */
public final class ItemIconsV84 {
    public static final int SCRAP=0,MED=1,AMMO=2,FOOD=3,WATER=4,WOOD=5,
        STONE=6,FIBER=7,BARRICADE=8,LAMP=9,PISTOL=10,RIFLE=11,TORCH=12,
        WATER_COLLECTOR=13,FIELD_SHELTER=14;
    private final Bitmap[] art=new Bitmap[15];
    private final Paint paint=new Paint();
    private final RectF dst=new RectF();
    private final android.graphics.Rect src=new android.graphics.Rect(0,0,32,32);

    public ItemIconsV84(){
        paint.setAntiAlias(false);paint.setFilterBitmap(false);
        for(int i=0;i<art.length;i++){
            art[i]=Bitmap.createBitmap(32,32,Bitmap.Config.ARGB_8888);
            Canvas c=new Canvas(art[i]);
            render(c,i);
        }
    }
    void r(Canvas c,int x,int y,int w,int h,int col){
        paint.setColor(col);paint.setStyle(Paint.Style.FILL);
        c.drawRect(x,y,x+w,y+h,paint);
    }
    void render(Canvas c,int t){
        final int dk=0xff142122,metal=0xff748586,shine=0xffb4c6be,
            brown=0xff795638,gold=0xffc3a06a,green=0xff74916d;
        switch(t){
            case SCRAP:
                r(c,4,19,25,9,dk);r(c,7,15,11,8,0xff9b6945);
                r(c,17,11,12,13,metal);r(c,18,14,9,3,shine);
                r(c,5,22,7,4,0xffb08b54);break;
            case MED:
                r(c,4,8,24,20,dk);r(c,6,10,20,16,0xffdad9c0);
                r(c,14,11,5,14,0xffb5514a);r(c,10,16,13,5,0xffb5514a);break;
            case AMMO:
                for(int i=0;i<3;i++){r(c,5+i*8,9,6,19,dk);r(c,6+i*8,10,4,15,gold);
                    r(c,6+i*8,7,4,4,shine);}break;
            case FOOD:
                r(c,7,8,19,21,dk);r(c,9,10,15,17,0xffa77a4a);
                r(c,11,7,11,4,gold);r(c,12,16,9,7,green);break;
            case WATER:
                r(c,13,5,7,6,0xff8da3a7);r(c,10,10,13,19,dk);
                r(c,12,12,9,15,0xff639bb8);r(c,13,14,3,10,0xffc3dcda);break;
            case WOOD:
                r(c,3,20,26,8,dk);r(c,5,19,23,6,brown);
                r(c,5,14,23,6,dk);r(c,7,14,19,4,0xffa17c54);
                r(c,9,16,5,2,gold);break;
            case STONE:
                r(c,4,15,24,13,dk);r(c,7,12,19,13,0xff647478);
                r(c,10,10,11,6,shine);r(c,9,22,8,3,0xff334649);break;
            case FIBER:
                r(c,14,16,4,13,dk);
                for(int i=0;i<4;i++){r(c,8+i*4,10-i%2*3,4,13,green);}
                r(c,12,20,10,4,0xffa0b76b);break;
            case BARRICADE:
                r(c,3,7,26,21,dk);
                for(int y=9;y<26;y+=7)r(c,5,y,22,5,y==9?brown:0xff9d7951);
                r(c,9,5,4,25,0xff3a3930);r(c,23,5,4,25,0xff3a3930);break;
            case LAMP:
                r(c,14,11,6,19,dk);r(c,16,12,3,17,brown);
                r(c,7,7,20,10,dk);r(c,9,9,16,6,gold);
                r(c,13,10,8,4,0xffffe4a1);break;
            case PISTOL:
                r(c,3,10,25,9,dk);r(c,5,12,20,4,metal);
                r(c,12,18,8,11,dk);r(c,14,19,5,9,brown);break;
            case RIFLE:
                r(c,2,13,28,7,dk);r(c,3,14,23,4,metal);
                r(c,8,20,7,9,brown);r(c,20,19,6,5,dk);break;
            case TORCH:
                r(c,5,13,23,9,dk);r(c,7,15,15,5,metal);
                r(c,23,11,5,13,gold);r(c,25,13,4,8,shine);break;
            case WATER_COLLECTOR:
                r(c,4,9,24,21,dk);r(c,6,11,20,18,0xff4e7181);
                r(c,3,7,27,6,0xff273b3c);r(c,6,6,21,4,shine);
                r(c,11,13,10,8,0xff8cb8c2);r(c,23,18,4,11,brown);break;
            case FIELD_SHELTER:
                r(c,3,22,27,7,dk);r(c,6,13,21,11,green);
                r(c,10,8,14,7,0xff99a879);r(c,12,16,10,12,dk);
                r(c,15,18,5,10,brown);r(c,3,24,27,3,gold);break;
            default:break;
        }
    }
    public Bitmap bitmap(int type){return art[Math.max(0,Math.min(type,art.length-1))];}
    public Drawable drawable(Resources resources,int type,int dp){
        BitmapDrawable d=new BitmapDrawable(resources,bitmap(type));
        d.setFilterBitmap(false);
        float den=resources.getDisplayMetrics().density;
        d.setBounds(0,0,Math.round(dp*den),Math.round(dp*den));
        return d;
    }
    public void draw(Canvas c,int type,float x,float y,float size){
        dst.set(x,y,x+size,y+size);
        paint.setAlpha(255);paint.setFilterBitmap(false);
        c.drawBitmap(bitmap(type),src,dst,paint);
    }
    public static int hotbarType(int item){
        if(item==1)return MED;
        if(item==2)return AMMO;
        if(item==3)return PISTOL;
        if(item==4||item==5)return RIFLE;
        if(item==6)return FOOD;
        if(item==7)return WATER;
        if(item==8)return TORCH;
        if(item==9)return BARRICADE;
        if(item==10)return LAMP;
        if(item==11)return WATER_COLLECTOR;
        if(item==12)return FIELD_SHELTER;
        return SCRAP;
    }
    public void release(){for(Bitmap b:art)if(b!=null&&!b.isRecycled())b.recycle();}
}
