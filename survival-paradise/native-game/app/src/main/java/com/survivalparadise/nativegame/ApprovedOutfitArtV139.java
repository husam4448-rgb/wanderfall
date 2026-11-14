package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import java.io.IOException;
import java.io.InputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Approved source-only torso and pants textures, 20 each.
 *
 * Samples pixels of the user's original PNGs into ONLY the pre-existing colored
 * regions of the immutable V137 universal body. Original black outlines,
 * dimensions, four walk poses, separate V133 boots and 200 V109 heads are never
 * modified. Rendered source pixels are cached by CharacterSkinsV109.
 * Unavailable archive: preserve the V137 legacy draw path (no crash/data loss).
 */
final class ApprovedOutfitArtV139 {
    static final int COUNT=20;
    static final String SOURCE_ASSET="sp_v139_outfits.zip";
    private final int[][] torsoColors=new int[COUNT][];
    private final int[][] pantsColors=new int[COUNT][];
    private final Bitmap[] torsoSprites=new Bitmap[COUNT];
    private final Bitmap[] pantsSprites=new Bitmap[COUNT];
    private final int[] torsoWidth=new int[COUNT],torsoHeight=new int[COUNT];
    private final int[] pantsWidth=new int[COUNT],pantsHeight=new int[COUNT];
    private final boolean available;

    ApprovedOutfitArtV139(Context ctx){
        boolean ok=false;
        try(InputStream file=ctx.getAssets().open(SOURCE_ASSET);
            ZipInputStream zip=new ZipInputStream(file)){
            ZipEntry entry;
            while((entry=zip.getNextEntry())!=null){
                String name=entry.getName();
                boolean torso=name.startsWith("torsos/");
                boolean pants=name.startsWith("pants/");
                if(!(torso||pants)||!name.endsWith(".png"))continue;
                int slash=name.indexOf('/')+1;
                if(name.length()<slash+2)continue;
                int id;
                try{id=Integer.parseInt(name.substring(slash,slash+2))-1;}
                catch(NumberFormatException ignored){continue;}
                if(id<0||id>=COUNT)continue;
                java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();
                byte[] chunk=new byte[8192];int n;
                while((n=zip.read(chunk))>0)bytes.write(chunk,0,n);
                byte[] data=bytes.toByteArray();
                Bitmap bitmap=BitmapFactory.decodeByteArray(data,0,data.length);
                if(bitmap==null)continue;
                int w=bitmap.getWidth(),h=bitmap.getHeight();
                int[] pixels=new int[w*h];
                bitmap.getPixels(pixels,0,w,0,0,w,h);
                if(torso){torsoColors[id]=pixels;torsoWidth[id]=w;torsoHeight[id]=h;torsoSprites[id]=bitmap;}
                else{pantsColors[id]=pixels;pantsWidth[id]=w;pantsHeight[id]=h;pantsSprites[id]=bitmap;}
                zip.closeEntry();
            }
            ok=true;
            for(int i=0;i<COUNT;i++)if(torsoColors[i]==null||pantsColors[i]==null)
                ok=false;
        }catch(IOException ignored){ok=false;}
        available=ok;
    }
    boolean ready(){return available;}

    /**
     * Exact original approved V132/V133 modular rig projection.
     * Five-frame fitting bundle uses a 300x355 canvas with fixed torso
     * x=86 y=116 width=120 and pants x=97 y=199 width=93*104%.
     * Existing BootArtV133 FIT was built from these SAME profiles with
     * x offset -50 / y offset -45. We translate outfit parts accordingly
     * without stretching any source art or painting into the old body masks.
     * Paint is the original nearest-neighbor renderer.
     */
    void drawApprovedRig(Canvas c,float left,float top,float unit,
             int torsoStyle,int pantsStyle,int torsoWidthPercent,
             int pelvisWidthPercent,android.graphics.Paint pixel){
        if(!available)return;
        int torso=Math.max(0,Math.min(19,torsoStyle));
        int pants=Math.max(0,Math.min(19,pantsStyle));
        // The user-approved simulator draws pants FIRST, then torso, then
        // the original head, then independently animated rear/front boots.
        drawRigSprite(c,pantsSprites[pants],47f,154f,93f*1.04f,
            pelvisWidthPercent,left,top,unit,pixel);
        drawRigSprite(c,torsoSprites[torso],36f,71f,120f,
            torsoWidthPercent,left,top,unit,pixel);
    }

    private static void drawRigSprite(Canvas c,Bitmap bitmap,
                float x,float y,float approvedWidth,int percent,
                float left,float top,float unit,android.graphics.Paint paint){
        if(bitmap==null)return;
        // User width sliders affect this part only; no foot pixels move.
        float widthScale=Math.max(.55f,Math.min(1f,percent/100f));
        float w=approvedWidth*widthScale;
        float center=x+approvedWidth*.5f;
        float drawX=center-w*.5f;
        float h=approvedWidth*bitmap.getHeight()/(float)bitmap.getWidth();
        android.graphics.RectF target=new android.graphics.RectF(
            left+drawX*unit,top+y*unit,left+(drawX+w)*unit,top+(y+h)*unit);
        c.drawBitmap(bitmap,null,target,paint);
    }

    /** Overwrite colored interiors only, respecting the exact original pixel mask. */
    void apply(int[] dressed,int[] original,int torso,int legs){
        if(!available||original.length!=BodyClothingV137.WIDTH*BodyClothingV137.HEIGHT)
            return;
        if(torso>=0&&torso<COUNT)
            texture(dressed,original,torsoColors[torso],torsoWidth[torso],
                torsoHeight[torso],160,200,true);
        if(legs>=0&&legs<COUNT)
            texture(dressed,original,pantsColors[legs],pantsWidth[legs],
                pantsHeight[legs],200,220,false);
    }

    private static void texture(int[] out,int[] src,int[] colors,int w,int h,
                                int top,int bottom,boolean torso) {
        if(colors==null||w<=0||h<=0)return;
        for(int y=top;y<bottom;y++)for(int x=0;x<BodyClothingV137.WIDTH;x++){
            int i=y*BodyClothingV137.WIDTH+x;
            int old=src[i];
            if(torso?(old!=BodyClothingV137.RED&&old!=BodyClothingV137.BLUE):
                old!=BodyClothingV137.BLUE)continue;
            // Image content is sampled without editing PNG source, with 200px
            // width / source height automatically respected for each style.
            float u=Math.max(0f,Math.min(.99999f,(x-40f)/120f));
            float v=Math.max(0f,Math.min(.99999f,(y-top)/(float)(bottom-top)));
            int px=Math.min(w-1,(int)(u*w)),py=Math.min(h-1,(int)(v*h));
            int sample=colors[py*w+px];
            if((sample>>>24)>=160)out[i]=sample;
        }
    }
}
