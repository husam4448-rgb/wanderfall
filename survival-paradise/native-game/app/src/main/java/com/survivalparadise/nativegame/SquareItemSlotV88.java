package com.survivalparadise.nativegame;
import android.content.Context;
import android.widget.Button;
import android.view.View;
/** Maintains a truly square inventory cell independent of device/window width. */
public final class SquareItemSlotV88 extends Button {
    public SquareItemSlotV88(Context context){super(context);}
    @Override protected void onMeasure(int widthMeasureSpec,int heightMeasureSpec){
        super.onMeasure(widthMeasureSpec,heightMeasureSpec);
        int edge=getMeasuredWidth();
        if(edge>0)setMeasuredDimension(edge,edge);
    }
}
