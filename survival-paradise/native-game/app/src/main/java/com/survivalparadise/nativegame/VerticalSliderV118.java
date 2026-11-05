package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.view.MotionEvent;
import android.view.View;

/** Source-pixel-style vertical analogue for Y-axis controls. */
public final class VerticalSliderV118 extends View {
    public interface Listener { void changed(int next,boolean fromUser); }
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final int min,max;
    private int value;
    private final Listener listener;
    public VerticalSliderV118(Context context,int lo,int hi,int initial,Listener l){
        super(context);
        min=lo;max=Math.max(lo+1,hi);value=Math.max(min,Math.min(max,initial));
        listener=l;
        setMinimumHeight(Math.round(118f*getResources().getDisplayMetrics().density));
    }
    public int getValue(){return value;}
    public void setValue(int v,boolean user){
        int clamped=Math.max(min,Math.min(max,v));
        if(value!=clamped){value=clamped;invalidate();if(listener!=null)listener.changed(value,user);}
    }
    @Override protected void onMeasure(int widthSpec,int heightSpec) {
        int d=Math.round(getResources().getDisplayMetrics().density);
        setMeasuredDimension(resolveSize(44*d,widthSpec),resolveSize(118*d,heightSpec));
    }
    @Override protected void onDraw(Canvas c) {
        super.onDraw(c);
        float cx=getWidth()*.5f;
        float top=16f,bottom=getHeight()-16f;
        paint.setColor(0xff45645d);paint.setStrokeWidth(6f);
        c.drawLine(cx,top,cx,bottom,paint);
        float f=(value-min)/(float)(max-min);
        float yy=bottom-f*(bottom-top);
        paint.setColor(0xff9bc8b1);paint.setStrokeWidth(7f);
        c.drawLine(cx,yy,cx,bottom,paint);
        paint.setColor(0xffe4f0ed);c.drawCircle(cx,yy,10f,paint);
        paint.setColor(0xff193b3c);c.drawCircle(cx,yy,4f,paint);
    }
    @Override public boolean onTouchEvent(MotionEvent event){
        int a=event.getActionMasked();
        if(a==MotionEvent.ACTION_DOWN||a==MotionEvent.ACTION_MOVE){
            if(getParent()!=null)getParent().requestDisallowInterceptTouchEvent(true);
            float fraction=(getHeight()-16f-event.getY())/Math.max(1f,getHeight()-32f);
            setValue(min+Math.round(Math.max(0f,Math.min(1f,fraction))*(max-min)),true);
            return true;
        }
        if(a==MotionEvent.ACTION_UP||a==MotionEvent.ACTION_CANCEL)return true;
        return true;
    }
}
