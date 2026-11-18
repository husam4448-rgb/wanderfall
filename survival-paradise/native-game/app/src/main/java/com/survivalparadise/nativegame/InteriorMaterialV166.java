package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/** Production indoor floors no longer use V165 outdoor pavement or soil. */
public final class InteriorMaterialV166 {
    private InteriorMaterialV166(){}
    public static void floor(Canvas c,Paint p,NeighborhoodInteriorV161 room){
        if(InteriorFloorArtV166.ready()){
            InteriorFloorArtV166.neighborhood(c,room);
            return;
        }
        // Emergency rendering only if the required authored floor atlas fails.
        p.setStyle(Paint.Style.FILL);
        p.setColor(0xff554e45);
        c.drawRect(23f,23f,1577f,1095f,p);
    }
}
