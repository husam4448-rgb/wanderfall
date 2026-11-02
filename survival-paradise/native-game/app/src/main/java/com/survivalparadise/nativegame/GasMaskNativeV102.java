package com.survivalparadise.nativegame;

import android.graphics.Bitmap;
import java.util.HashMap;
import java.util.IdentityHashMap;

/**
 * V102 integrated-head replacement, computed once per source player/NPC pose.
 * Returns the original full 260x160 character with ONLY the head's interior
 * recolored. Rendering uses the existing V82 scaled-head compositor and the
 * existing planted-idle/walk identity code. No separate headgear draw call.
 */
public final class GasMaskNativeV102 {
    private final IdentityHashMap<Bitmap,HashMap<Integer,Bitmap>> saved=
        new IdentityHashMap<>();
    public synchronized Bitmap headVariant(Bitmap source,int sx,int sy){
        if(source==null)return null;
        final int ix=sx/260,iy=sy/160;
        final int key=(iy<<8)|ix;
        HashMap<Integer,Bitmap> variations=saved.get(source);
        if(variations==null){
            variations=new HashMap<>();
            saved.put(source,variations);
        }
        Bitmap existing=variations.get(key);
        if(existing!=null)return existing;
        Bitmap out=Bitmap.createBitmap(source,sx,sy,260,160)
            .copy(Bitmap.Config.ARGB_8888,true);
        int[] pixels=new int[260*160];
        out.getPixels(pixels,0,260,0,0,260,160);
        for(int y=29;y<92;y++){
            for(int x=33;x<105;x++){
                int pos=y*260+x;
                pixels[pos]=GasMaskPaletteV102.recolor(x,y,pixels[pos]);
            }
        }
        out.setPixels(pixels,0,260,0,0,260,160);
        variations.put(key,out);
        return out;
    }
}
