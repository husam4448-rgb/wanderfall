package com.survivalparadise.nativegame;

import android.graphics.Bitmap;

/** Cached COLOR-ONLY substitution on original immutable V31/V56 torso pixels.
 * No jacket drawing, outlines, heads, hands, pants, geometry or frames replaced.
 */
public final class TorsoRecolorV98 {
    private final Bitmap[][] cache=new Bitmap[13][3];
    public Bitmap frame(Bitmap original,Bitmap approvedNpcPalette,int npcRole,int outfit){
        if(outfit<0||outfit>=3||original==null||approvedNpcPalette==null)return original;
        int row=npcRole<0?0:Math.min(12,npcRole+1);
        Bitmap existing=cache[row][outfit];if(existing!=null)return existing;
        int sx=npcRole<0?GameView.APPROVED_PLANTED_IDLE_FRAME*260:0;
        int sy=npcRole<0?0:Math.min(11,npcRole)*160;
        int[] pixels=new int[260*160];
        original.getPixels(pixels,0,260,sx,sy,260,160);
        int[] approved=new int[260*160];
        approvedNpcPalette.getPixels(approved,0,260,0,
                WearableFitV98.sourceRole(outfit)*160,260,160);
        for(int y=92;y<=109;y++)for(int x=43;x<=108;x++){
            int index=y*260+x;
            int current=pixels[index],reference=approved[index];
            if(!WearableFitV98.torsoPixel(x,y,current))continue;
            // Never copy transparent regions, outlines, or source face pixels.
            if(!WearableFitV98.torsoPixel(x,y,reference))continue;
            pixels[index]=(current&0xff000000)|(reference&0x00ffffff);
        }
        Bitmap updated=Bitmap.createBitmap(260,160,Bitmap.Config.ARGB_8888);
        updated.setPixels(pixels,0,260,0,0,260,160);
        cache[row][outfit]=updated;
        return updated;
    }
}
