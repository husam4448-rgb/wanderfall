package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
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
    // Additive legacy art. The 20 approved V139 sprites stay byte-identical.
    private final Bitmap[] legacyTorsosV144=new Bitmap[3];
    private final Bitmap[] legacyPantsV144=new Bitmap[3];
    private final boolean legacyReadyV144;
    // Recolor only the approved original silhouette alpha. No alternative
    // anatomy, altered heads, transparent/nude body or external placeholder.
    private Bitmap undershirtV141,boxersV141;
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
        legacyReadyV144=ok&&loadLegacyArtworkV144(ctx);
        if(ok){
            undershirtV141=underwearSpriteV141(torsoSprites[0],true);
            boxersV141=underwearSpriteV141(pantsSprites[0],false);
        }
    }
    /**
     * Load nine source-sized V144 legacy garments without touching V139 PNGs.
     * A missing or mismatched archive safely falls back to existing V142 art.
     * The user's individual designs preserve the existing canvas dimensions and anchors,
     * but their INTERNAL alpha and silhouettes may differ. Never overlay V139 alpha masks.
     */
    private boolean loadLegacyArtworkV144(Context ctx){
        final int[] basesTorso={9,16,6},basesPants={10,18,6};
        try(InputStream input=ctx.getAssets().open("sp_v145_legacy_equipment.zip");
                ZipInputStream zip=new ZipInputStream(input)){
            ZipEntry entry;
            while((entry=zip.getNextEntry())!=null){
                String file=entry.getName();
                boolean top=file.startsWith("torsos/");
                boolean leg=file.startsWith("pants/");
                if(!(top||leg)||!file.endsWith(".png"))continue;
                int i;
                try {
                    int from=top?7:6;
                    i=Integer.parseInt(file.substring(from,from+2))-20;
                }catch(RuntimeException ignored){continue;}
                if(i<0||i>=3)continue;
                java.io.ByteArrayOutputStream out=new java.io.ByteArrayOutputStream();
                byte[] chunk=new byte[8192];int n;
                while((n=zip.read(chunk))!=-1)out.write(chunk,0,n);
                byte[] data=out.toByteArray();
                Bitmap image=BitmapFactory.decodeByteArray(data,0,data.length);
                Bitmap approved=top?torsoSprites[basesTorso[i]]:pantsSprites[basesPants[i]];
                if(!validCanvasV145(image,approved))return false;
                if(top)legacyTorsosV144[i]=image;
                else legacyPantsV144[i]=image;
            }
        }catch(IOException ignored){return false;}
        for(int i=0;i<3;i++)
            if(legacyTorsosV144[i]==null||legacyPantsV144[i]==null)return false;
        return true;
    }
    /** Canvas bounds are fixed; outlines and internal pixel art are NOT repainted. */
    private static boolean validCanvasV145(Bitmap candidate, Bitmap approved){
        if(candidate==null||approved==null||
                candidate.getWidth()!=approved.getWidth()||
                candidate.getHeight()!=approved.getHeight())return false;
        int w=candidate.getWidth(),h=candidate.getHeight();
        int[] pixels=new int[w*h];
        candidate.getPixels(pixels,0,w,0,0,w,h);
        int visible=0;
        for(int p:pixels)if((p>>>24)>127)visible++;
        return visible>=w*h/6;
    }
    private Bitmap torsoSpriteV144(int style){
        if(style<0)return undershirtV141;
        if(style<COUNT)return torsoSprites[style];
        int id=style-20;
        if(id<0||id>2)return torsoSprites[0];
        return legacyReadyV144?legacyTorsosV144[id]:
            torsoSprites[LegacyOutfitVisualV142.torso(id,0)];
    }
    private Bitmap pantsSpriteV144(int style){
        if(style<0)return boxersV141;
        if(style<COUNT)return pantsSprites[style];
        int id=style-20;
        if(id<0||id>2)return pantsSprites[0];
        return legacyReadyV144?legacyPantsV144[id]:
            pantsSprites[LegacyOutfitVisualV142.pants(id,0)];
    }
    /** Fully covered undershirt and boxer shorts from original silhouette.
     * Every non-transparent exterior source pixel remains within its original
     * outline. Nearest-neighbor rendering preserves the game's pixel grid.
     */
    private static Bitmap underwearSpriteV141(Bitmap source,boolean top){
        int w=source.getWidth(),h=source.getHeight();
        int[] pixels=new int[w*h],out=new int[w*h];
        source.getPixels(pixels,0,w,0,0,w,h);
        for(int y=0;y<h;y++)for(int x=0;x<w;x++){
            int index=y*w+x;
            if((pixels[index]>>>24)<128)continue;
            boolean edge=false;
            for(int yy=-2;yy<=2&&!edge;yy++)for(int xx=-2;xx<=2;xx++){
                int nx=x+xx,ny=y+yy;
                if(nx<0||ny<0||nx>=w||ny>=h||
                   (pixels[ny*w+nx]>>>24)<128){edge=true;break;}
            }
            if(edge){out[index]=0xff171b1e;continue;}
            float distance=Math.abs(x-(w-1)*.5f)/Math.max(1f,w*.5f);
            int base=top?0xffc5c9bb:0xff536070;
            int dark=top?0xff89968c:0xff303c50;
            int light=top?0xffd6d6c7:0xff677689;
            int waistband=h/10;
            if(!top&&(y>=waistband-3&&y<=waistband+3))
                out[index]=0xffb9b7aa;
            else if(!top&&Math.abs(x-(w-1)/2)<=2&&y>h*.4f)
                out[index]=0xff323c4b;
            else if(top&&y>h*.87f)
                out[index]=0xff7a867d;
            else if(distance>.75f)
                out[index]=dark;
            else if(distance<.34f)
                out[index]=light;
            else
                out[index]=base;
        }
        return Bitmap.createBitmap(out,w,h,Bitmap.Config.ARGB_8888);
    }
    boolean ready(){return available;}
    /** Exact original PNG rendered to a small nearest-neighbor inventory icon. */
    android.graphics.drawable.Drawable inventoryIcon(Context ctx,int type,int dp){
        int slot=OutfitInventoryV140.slot(type);
        int id=OutfitInventoryV140.style(type);
        Bitmap original=slot==0?torsoSprites[id]:slot==1?pantsSprites[id]:null;
        return makeOriginalIcon(ctx,original,dp);
    }
    static android.graphics.drawable.Drawable makeOriginalIcon(Context ctx,
            Bitmap original,int dp){
        if(original==null)return null;
        Bitmap tile=Bitmap.createBitmap(56,56,Bitmap.Config.ARGB_8888);
        Canvas canvas=new Canvas(tile);
        android.graphics.Paint nearest=new android.graphics.Paint();
        nearest.setFilterBitmap(false);nearest.setAntiAlias(false);
        float scale=Math.min(51f/original.getWidth(),51f/original.getHeight());
        int w=Math.max(1,Math.round(original.getWidth()*scale));
        int h=Math.max(1,Math.round(original.getHeight()*scale));
        float x=(56f-w)/2f,y=(56f-h)/2f;
        canvas.drawBitmap(original,null,new android.graphics.RectF(x,y,x+w,y+h),nearest);
        android.graphics.drawable.BitmapDrawable icon=
            new android.graphics.drawable.BitmapDrawable(ctx.getResources(),tile);
        icon.setFilterBitmap(false);
        float density=ctx.getResources().getDisplayMetrics().density;
        int pixels=Math.max(12,Math.round(dp*density));
        icon.setBounds(0,0,pixels,pixels);
        return icon;
    }

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
        int torso=Math.max(-1,Math.min(22,torsoStyle));
        int pants=Math.max(-1,Math.min(22,pantsStyle));
        // The user-approved simulator draws pants FIRST, then torso, then
        // the original head, then independently animated rear/front boots.
        drawRigSprite(c,pantsSpriteV144(pants),
            47f,154f,93f*1.04f,
            pelvisWidthPercent,72,left,top,unit,pixel);
        drawRigSprite(c,torsoSpriteV144(torso),
            36f,71f,120f,
            torsoWidthPercent,71,left,top,unit,pixel);
    }

    private static void drawRigSprite(Canvas c,Bitmap bitmap,
                float x,float y,float approvedWidth,int percent,int defaultPercent,
                float left,float top,float unit,android.graphics.Paint paint){
        if(bitmap==null)return;
        // User width sliders affect this part only; no foot pixels move.
        float widthScale=Math.max(.65f,Math.min(1.42f,percent/(float)defaultPercent));
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
