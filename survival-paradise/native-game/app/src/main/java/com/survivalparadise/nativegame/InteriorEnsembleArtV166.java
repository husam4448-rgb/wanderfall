package com.survivalparadise.nativegame;

import android.graphics.Canvas;

/**
 * Paint original hand-authored furniture as purposeful multi-object stations.
 * No new bitmap allocation, loot entities or changed collision/save schema.
 */
public final class InteriorEnsembleArtV166 {
    private InteriorEnsembleArtV166(){}
    public static boolean drawAt(Canvas canvas,int group,
                                 float x,float y,float w,float h){
        if(!InteriorScenePlanV166.valid(group)||w<=0||h<=0||
           !InteriorPropArtV166.ready()||
           !InteriorScenePropArtV166.ready()||
           !InteriorSpecialPropArtV166.ready())return false;
        for(int[] obj:InteriorScenePlanV166.parts(group)){
            float xx=x+w*obj[1]/1000f, yy=y+h*obj[2]/1000f;
            float ww=w*obj[3]/1000f, hh=h*obj[4]/1000f;
            if(!InteriorPropArtV166.drawAt(canvas,obj[0],xx,yy,ww,hh))
                return false;
        }
        return true;
    }
}
