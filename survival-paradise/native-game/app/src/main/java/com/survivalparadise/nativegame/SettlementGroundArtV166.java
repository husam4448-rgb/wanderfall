package com.survivalparadise.nativegame;

import android.graphics.Canvas;

/**
 * V166 production ground art for actual seeded settlement parcels.
 * Replaces V159 giant flat rounded rectangles, polygons and checkerboard
 * with overlapping, authored, alpha-feathered compacted-earth brushwork.
 * All parcel IDs, fence geometry, roads and saved seed maps are read-only.
 */
public final class SettlementGroundArtV166 {
    private SettlementGroundArtV166(){}
    private static final int STEP=SettlementGroundSelectionV166.STEP;
    public static void draw(Canvas c,WorldCivilizationV159.Plan plan,
                            float camX,float camY,float width,float height){
        if(plan==null||!NaturalBrushArtV1652.ready())return;
        for(WorldCivilizationV159.Parcel parcel:plan.parcels){
            if(!parcel.onScreen(camX,camY,width,height))continue;
            // World-aligned tile indices avoid camera-relative seams.
            float minX=Math.max(parcel.left-420f,camX-420f);
            float maxX=Math.min(parcel.right+420f,camX+width+420f);
            float minY=Math.max(parcel.top-420f,camY-420f);
            float maxY=Math.min(parcel.bottom+420f,camY+height+420f);
            if(minX>=maxX||minY>=maxY)continue;
            int gx0=(int)Math.floor(minX/STEP),gx1=(int)Math.ceil(maxX/STEP);
            int gy0=(int)Math.floor(minY/STEP),gy1=(int)Math.ceil(maxY/STEP);
            c.save();
            // Just a spatial mask; visible artwork has its OWN feather.
            c.clipRect(parcel.left,parcel.top,parcel.right,parcel.bottom);
            for(int gy=gy0;gy<=gy1;gy++)for(int gx=gx0;gx<=gx1;gx++){
                int h=SettlementGroundSelectionV166.anchorHash(gx,gy,
                    plan.seed,parcel.variation);
                float xx=(gx+.5f)*STEP+
                    Math.floorMod(h>>>7,101)-50f;
                float yy=(gy+.5f)*STEP+
                    Math.floorMod(h>>>15,101)-50f;
                if(xx<parcel.left-370||xx>parcel.right+370||
                   yy<parcel.top-370||yy>parcel.bottom+370)continue;
                int m=SettlementGroundSelectionV166.material(
                    parcel.kind,gx,gy,plan.seed,parcel.variation);
                float w=490f+Math.floorMod(h>>>17,190);
                float height0=440f+Math.floorMod(h>>>23,160);
                int alpha=parcel.kind==WorldCivilizationV159.CITY?194:
                    parcel.kind==WorldCivilizationV159.VILLAGE?182:201;
                if(m==SettlementGroundSelectionV166.GRASS){
                    NaturalBrushArtV1652.stamp(c,NaturalGroundV157.GRASS,
                        xx,yy,w*.77f,height0*.8f,h,126);
                }else{
                    int source=m==SettlementGroundSelectionV166.DRY?
                        NaturalGroundV157.DRY:NaturalGroundV157.DIRT;
                    NaturalBrushArtV1652.stampSettlement(c,source,
                        xx,yy,w,height0,h,alpha,parcel.kind);
                }
            }
            c.restore();
        }
    }
}
