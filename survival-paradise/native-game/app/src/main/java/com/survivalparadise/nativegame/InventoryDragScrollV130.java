package com.survivalparadise.nativegame;

import android.graphics.Rect;
import android.os.Handler;
import android.os.Looper;
import android.view.DragEvent;
import android.view.View;
import android.widget.ScrollView;

/** Smooth, continuous Android drag-autoscroll for the existing 40-slot bag. */
public final class InventoryDragScrollV130 {
    private final ScrollView pane;
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final int edge,step;
    private int direction=0;
    private boolean dragging=false;
    private final Runnable scrolling=new Runnable(){
        public void run(){
            if(!dragging||direction==0||!pane.isAttachedToWindow())return;
            if(pane.canScrollVertically(direction)){
                pane.scrollBy(0,direction*step);
                handler.postDelayed(this,45);
            }else direction=0;
        }
    };
    public InventoryDragScrollV130(ScrollView pane,float density){
        this.pane=pane;edge=Math.round(70f*density);
        step=Math.round(22f*density);
    }
    public void update(View target,DragEvent event){
        switch(event.getAction()){
            case DragEvent.ACTION_DRAG_STARTED:
                dragging=true;return;
            case DragEvent.ACTION_DRAG_LOCATION:
                int[] pos=new int[2];
                target.getLocationOnScreen(pos);
                int absY=pos[1]+Math.round(event.getY());
                Rect visible=new Rect();
                if(!pane.getGlobalVisibleRect(visible)){stop();return;}
                int next=absY<visible.top+edge?-1:
                    absY>visible.bottom-edge?1:0;
                if(next==direction)return;
                handler.removeCallbacks(scrolling);
                direction=next;
                if(direction!=0){
                    dragging=true;
                    handler.post(scrolling);
                }
                return;
            case DragEvent.ACTION_DROP:
            case DragEvent.ACTION_DRAG_ENDED:
                stop();return;
            default:return;
        }
    }
    public void stop(){
        dragging=false;direction=0;
        handler.removeCallbacks(scrolling);
    }
}
