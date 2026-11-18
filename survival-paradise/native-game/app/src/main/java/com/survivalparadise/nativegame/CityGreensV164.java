package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/**
 * V166 vacant-lot greens use authored alpha material brushwork and foliage.
 * Plot geography, vacant identities, fence gaps, roads and collision are
 * derived exclusively from the existing V159/V164 world models.
 */
public final class CityGreensV164 {
    private CityGreensV164(){}
    public static int vacantPlots(WorldCivilizationV159.Plan plan){
        if(plan==null)return 0;
        int count=0;
        for(WorldCivilizationV159.Parcel parcel:plan.parcels)
            for(int slot=0;slot<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;slot++)
                if(NeighborhoodV154.get(parcel.tx,parcel.ty,slot,plan)==null)
                    count++;
        return count;
    }
    public static void draw(Canvas c,Paint p,WorldCivilizationV159.Plan plan,
                            float camX,float camY,float width,float height,
                            boolean lowDetail){
        if(plan==null)return;
        for(WorldCivilizationV159.Parcel parcel:plan.parcels){
            if(!parcel.onScreen(camX,camY,width,height))continue;
            for(int slot=0;slot<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;slot++){
                if(NeighborhoodV154.get(parcel.tx,parcel.ty,slot,plan)!=null)continue;
                int col=slot%NeighborhoodV154.COLS,row=slot/NeighborhoodV154.COLS;
                float x=parcel.tx*(float)NeighborhoodV154.TILE_W+850f+col*1800f;
                float y=parcel.ty*(float)NeighborhoodV154.TILE_H+
                    (row==0?1140f:3360f);
                if(x<camX-720||x>camX+width+720||
                   y<camY-620||y>camY+height+620)continue;
                int seed=IndustrialWorldV123.hash(parcel.tx*73+slot,
                    parcel.ty*101-slot,plan.seed^0x1647AA);
                int style=Math.floorMod(seed,4);
                // A site is an aggregate of small, naturally feathered
                // authored paint stamps, never a giant opaque rectangle,
                // three concentric ellipses or a ruler-straight fake path.
                for(int i=0;i<10;i++){
                    int h=IndustrialWorldV123.hash(seed+i*127,
                        slot*31-i*97,plan.seed);
                    float px=x-380f+Math.floorMod(h,761);
                    float py=y-245f+Math.floorMod(h>>>11,491);
                    float w=150f+Math.floorMod(h>>>20,145);
                    NaturalBrushArtV1652.stamp(c,NaturalGroundV157.GRASS,
                        px,py,w,w*.70f,h,lowDetail?148:200);
                }
                if(style!=0){
                    int strokes=style==1?5:style==2?3:4;
                    for(int i=0;i<strokes;i++){
                        int h=IndustrialWorldV123.hash(seed^i*79,
                            slot*37+i*43,plan.seed);
                        float px=x-280f+Math.floorMod(h,561);
                        float py=y-155f+Math.floorMod(h>>>13,311);
                        NaturalBrushArtV1652.stamp(c,
                            style==1?NaturalGroundV157.DIRT:NaturalGroundV157.DRY,
                            px,py,110f+Math.floorMod(h>>>20,85),
                            63f+Math.floorMod(h>>>24,55),h,lowDetail?115:153);
                    }
                }
                // Small decorative shrubs are visual ground cover, not solid
                // trees or invisible obstacles in walkable city green spaces.
                int n=lowDetail?10:34;
                for(int i=0;i<n;i++){
                    int h=IndustrialWorldV123.hash(seed+i*23,
                        slot*11+i*31,plan.seed);
                    float bx=x-500f+Math.floorMod(h,1001);
                    float by=y-325f+Math.floorMod(h>>>12,651);
                    float size=24f+Math.floorMod(h>>>23,18);
                    WorldArtV166.draw(c,WorldArtSelectionV166.BUSH,
                        bx,by,size,size*.69f,plan.seed,h);
                }
            }
        }
    }
}
