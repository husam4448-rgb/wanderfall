package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** V109 approved source-only character compositor.
 *  Exact original idle body (static), four original walking poses, 200 heads,
 *  V5 general fitting + 51 individual overrides. No wearable layers.
 *  Weapon/hand rigs remain in the existing GameView and are NOT replaced.
 */
final class CharacterSkinsV109 {
    static final int COUNT=200, WIDTH=200, HEIGHT=260;
    static final String SOURCE_ASSET="sp_v109_characters.zip";
    static final class Fit {
        int headScale=120,horizontal=-21,vertical=-24,blend=22,breath=3,fps=2;
        Fit(){}
        Fit(Fit o){headScale=o.headScale;horizontal=o.horizontal;vertical=o.vertical;blend=o.blend;breath=o.breath;fps=o.fps;}
        void read(JSONObject j){
            if(j==null)return;
            headScale=range(j.optInt("headScale",headScale),75,160);
            horizontal=range(j.optInt("horizontal",horizontal),-60,60);
            vertical=range(j.optInt("vertical",vertical),-60,60);
            blend=range(j.optInt("blend",blend),0,40);
            breath=range(j.optInt("breath",breath),0,12);
            fps=range(j.optInt("fps",fps),1,12);
        }
    }
    static int range(int a,int min,int max){return Math.max(min,Math.min(max,a));}
    private final byte[][] headData=new byte[COUNT+1][];
    private final Fit[] fitting=new Fit[COUNT+1];
    private final Bitmap[] originals=new Bitmap[5]; // 0 idle, 1..4 walk
    private final LinkedHashMap<Integer,Bitmap> heads=new LinkedHashMap<Integer,Bitmap>(36,.75f,true){
        @Override protected boolean removeEldestEntry(Map.Entry<Integer,Bitmap> e){
            if(size()<=36)return false;
            // No explicit recycle: the frame may still hold a reference during draw.
            return true;
        }
    };
    private final LinkedHashMap<Integer,Bitmap> blended=new LinkedHashMap<Integer,Bitmap>(16,.75f,true){
        @Override protected boolean removeEldestEntry(Map.Entry<Integer,Bitmap> e){return size()>28;}
    };
    private final Rect spriteSource=new Rect(0,0,WIDTH,HEIGHT);
    // Original V109 20px cells: torso y160..179, full blue pelvis y180..219,
    // black pelvis underside + rigid foot blocks y220..239; feet reach y259.
    private final Rect torsoSource=new Rect(0,TorsoWidthV114.TORSO_TOP,WIDTH,
        TorsoWidthV114.LOWER_BODY_TOP);
    private final Rect pelvisRigSource=new Rect(0,0,WIDTH,
        HEIGHT-PelvisLegRigV116.PELVIS_TOP);
    private static final class FootLayers {
        final Bitmap pelvis,left,right,overlap;
        FootLayers(Bitmap pelvis,Bitmap left,Bitmap right,Bitmap overlap) {
            this.pelvis=pelvis;this.left=left;this.right=right;this.overlap=overlap;
        }
    }
    /** Render masks are derived from existing body bitmaps and never written to source. */
    private final LinkedHashMap<Integer,FootLayers> footCacheV116=
        new LinkedHashMap<Integer,FootLayers>(18,.75f,true){
            @Override protected boolean removeEldestEntry(Map.Entry<Integer,FootLayers> e){
                return size()>18;
            }
        };
    // Cached nontransparent bounds of each approved V5 head (nothing edited).
    private final int[][] headOpaqueV131=new int[COUNT+1][];
    private int[] headOpaqueBoundsV131(int id,Bitmap bitmap){
        int[] cached=headOpaqueV131[id];if(cached!=null)return cached;
        int width=bitmap.getWidth(),height=bitmap.getHeight();
        int[] colors=new int[width*height];
        bitmap.getPixels(colors,0,width,0,0,width,height);
        int minX=width,minY=height,maxX=0,maxY=0;
        for(int y=0;y<height;y++)for(int x=0;x<width;x++){
            if((colors[y*width+x]>>>24)<72)continue;
            minX=Math.min(minX,x);minY=Math.min(minY,y);
            maxX=Math.max(maxX,x+1);maxY=Math.max(maxY,y+1);
        }
        cached=minX>=maxX||minY>=maxY?
            new int[]{0,0,width,height}:new int[]{minX,minY,maxX,maxY};
        headOpaqueV131[id]=cached;return cached;
    }
    /** Exact V109/V5 head transform; local/world collision uses opaque alpha
     * bounds, independent of the obsolete V31 head rows in body-mask tests.
     */
    float[] headBoundsLocalV131(int id,float characterScale,
          int headOffsetX,int headOffsetY,int headSizePercent,
          int breathingAmplitude,float breathingTempo,
          float timeSec,boolean walking){
        id=range(id,1,COUNT);
        Bitmap h=head(id);if(h==null)return null;
        Fit fit=fitting[id];
        float unit=(160f/HEIGHT)*characterScale;
        float left=-100f*unit,top=-136f*characterScale;
        float headScale=Math.min(186f/h.getWidth(),192f/h.getHeight())*
            (fit.headScale/107f)*
            CharacterScopeV113.headSizeMultiplier(headSizePercent);
        int hw=Math.round(h.getWidth()*headScale),
            hh=Math.round(h.getHeight()*headScale);
        int hx=HeadFitOffsetsV112.x(hw,fit.horizontal,headOffsetX);
        float breathing=CharacterAnimationV110.breathOffset(walking,timeSec,
            fit.breath*(Math.max(0,Math.min(12,breathingAmplitude))/4f),
            breathingTempo);
        int hy=HeadFitOffsetsV112.y(hh,fit.vertical,breathing,headOffsetY);
        int[] bounds=headOpaqueBoundsV131(id,h);
        float x0=left+(hx+bounds[0]*hw/(float)h.getWidth())*unit;
        float y0=top+(hy+bounds[1]*hh/(float)h.getHeight())*unit;
        float x1=left+(hx+bounds[2]*hw/(float)h.getWidth())*unit;
        float y1=top+(hy+bounds[3]*hh/(float)h.getHeight())*unit;
        return new float[]{x0,y0,x1,y1};
    }
    private final Rect headSource=new Rect();
    private final RectF destination=new RectF();
    // Separate black-ink paint: never modify approved original PNG pixels,
    // V5 head colors or caller's reusable bitmap Paint.
    private final Paint upperOutlinePaintV120=new Paint(0);
    private JSONObject configuration;
    private boolean loaded=false;

    CharacterSkinsV109(Context context) throws IOException {
        upperOutlinePaintV120.setColor(android.graphics.Color.BLACK);
        upperOutlinePaintV120.setAntiAlias(false);
        upperOutlinePaintV120.setFilterBitmap(false);
        byte[] idle=null,walk=null,fitFile=null;
        try(InputStream source=context.getAssets().open(SOURCE_ASSET);
            ZipInputStream archive=new ZipInputStream(source)) {
            ZipEntry entry;
            while((entry=archive.getNextEntry())!=null){
                if(entry.isDirectory())continue;
                String name=entry.getName();
                boolean needed=name.equals("body_idle.png")||name.equals("body_walk.png")||name.equals("v5_fittings.json")||
                    (name.startsWith("heads/")&&name.endsWith(".png"));
                if(!needed)continue;
                ByteArrayOutputStream buffer=new ByteArrayOutputStream();
                byte[] tmp=new byte[8192];int n;
                while((n=archive.read(tmp))!=-1)buffer.write(tmp,0,n);
                byte[] bytes=buffer.toByteArray();
                if(name.equals("body_idle.png"))idle=bytes;
                else if(name.equals("body_walk.png"))walk=bytes;
                else if(name.equals("v5_fittings.json"))fitFile=bytes;
                else {
                    try {int id=Integer.parseInt(name.substring(6,name.length()-4));
                        if(id>=1&&id<=COUNT)headData[id]=bytes;
                    }catch(NumberFormatException ignored){}
                }
            }
        }
        if(idle==null||walk==null||fitFile==null)throw new IOException("V109 assets incomplete");
        Bitmap idleSheet=BitmapFactory.decodeByteArray(idle,0,idle.length);
        Bitmap walkSheet=BitmapFactory.decodeByteArray(walk,0,walk.length);
        if(idleSheet==null||idleSheet.getWidth()!=WIDTH||idleSheet.getHeight()!=HEIGHT||
           walkSheet==null||walkSheet.getWidth()!=WIDTH*4||walkSheet.getHeight()!=HEIGHT)
            throw new IOException("V109 source dimensions incorrect");
        // V5 source-mask: original heads occupy y=0..159. Remove ONLY those
        // pixels, leaving all torso, pants and feet below y=160 bit-identical.
        // Independently verified on the four approved walk poses and idle #1.
        originals[0]=withoutOldHead(idleSheet);
        for(int f=0;f<4;f++) originals[f+1]=withoutOldHead(
            Bitmap.createBitmap(walkSheet,f*WIDTH,0,WIDTH,HEIGHT));
        for(int id=1;id<=COUNT;id++)if(headData[id]==null)throw new IOException("Missing approved head "+id);
        try {
            configuration=new JSONObject(new String(fitFile,java.nio.charset.StandardCharsets.UTF_8));
            if(configuration.optInt("totalCharacters")!=COUNT)throw new IOException("Invalid fitting count");
            JSONObject general=configuration.getJSONObject("generalFitting");
            JSONObject exceptions=configuration.getJSONObject("characterOverrides");
            Fit base=new Fit();base.read(general);
            for(int id=1;id<=COUNT;id++){
                fitting[id]=new Fit(base);
                fitting[id].read(exceptions.optJSONObject(Integer.toString(id)));
            }
        }catch(org.json.JSONException e){throw new IOException("Invalid V5 fitting JSON",e);}
        loaded=true;
    }
    private static Bitmap withoutOldHead(Bitmap image){
        int[] pixels=new int[WIDTH*HEIGHT];
        image.getPixels(pixels,0,WIDTH,0,0,WIDTH,HEIGHT);
        java.util.Arrays.fill(pixels,0,WIDTH*160,0);
        return Bitmap.createBitmap(pixels,WIDTH,HEIGHT,Bitmap.Config.ARGB_8888);
    }
    boolean ready(){return loaded;}
    Fit fit(int id){return fitting[range(id,1,COUNT)];}
    private Bitmap head(int id){
        synchronized(heads){
            Bitmap b=heads.get(id);
            if(b!=null)return b;
            byte[] d=headData[id];if(d==null)return null;
            b=BitmapFactory.decodeByteArray(d,0,d.length);
            if(b!=null)heads.put(id,b);
            return b;
        }
    }
    private Bitmap body(int frame,int blend){
        int index=range(frame,0,4),key=index*64+range(blend,0,40);
        if(blend<=0)return originals[index];
        Bitmap cached=blended.get(key);if(cached!=null)return cached;
        Bitmap source=originals[index];
        int[] rgba=new int[WIDTH*HEIGHT];source.getPixels(rgba,0,WIDTH,0,0,WIDTH,HEIGHT);
        for(int y=180;y<Math.min(220,180+blend);y++) for(int x=0;x<WIDTH;x++) {
            int offset=y*WIDTH+x;
            if(rgba[offset]==0xff004aa1)rgba[offset]=0xff820000;
        }
        Bitmap result=Bitmap.createBitmap(rgba,WIDTH,HEIGHT,Bitmap.Config.ARGB_8888);
        blended.put(key,result);
        return result;
    }
    /** Cache original pixel masks for the pelvis and each rigid foot in one pose.
     * Classifies every source pixel without any recoloring, scaling, or redrawing.
     * Four layers together have exactly the original source pixels; no omissions.
     */
    private FootLayers footLayers(Bitmap source,int frame,int blend) {
        int key=Math.max(0,Math.min(4,frame))*64+
            Math.max(0,Math.min(40,blend));
        FootLayers cached=footCacheV116.get(key);
        if(cached!=null)return cached;
        final int h=HEIGHT-PelvisLegRigV116.PELVIS_TOP;
        int[] rgba=new int[WIDTH*h];
        source.getPixels(rgba,0,WIDTH,0,PelvisLegRigV116.PELVIS_TOP,WIDTH,h);
        int[][] separated=new int[4][WIDTH*h];
        for(int row=0;row<h;row++)for(int x=0;x<WIDTH;x++){
            int index=row*WIDTH+x;
            int part=PelvisLegRigV116.part(frame,x,row+PelvisLegRigV116.PELVIS_TOP);
            separated[part][index]=rgba[index];
        }
        FootLayers layers=new FootLayers(
            Bitmap.createBitmap(separated[PelvisLegRigV116.PELVIS],WIDTH,h,Bitmap.Config.ARGB_8888),
            Bitmap.createBitmap(separated[PelvisLegRigV116.LEFT_FOOT],WIDTH,h,Bitmap.Config.ARGB_8888),
            Bitmap.createBitmap(separated[PelvisLegRigV116.RIGHT_FOOT],WIDTH,h,Bitmap.Config.ARGB_8888),
            Bitmap.createBitmap(separated[PelvisLegRigV116.OVERLAP_FOOT],WIDTH,h,Bitmap.Config.ARGB_8888));
        footCacheV116.put(key,layers);
        return layers;
    }

    /** The original red upper torso had side-black x20..39 / x160..179
     * but no top black contour. Add an 8-source-pixel continuous cap between
     * those sides, entirely INSIDE the old torso row y160..179.
     * This is a draw-only outline, source bitmaps are immutable.
     */
    private void topBodyOutlineV120(Canvas c,float left,float top,float unit,
                                    int torsoPercent){
        float x0=left+BodyAlignmentV120.outlineLeft(torsoPercent)*unit;
        float x1=left+BodyAlignmentV120.outlineRight(torsoPercent)*unit;
        float y0=top+BodyAlignmentV120.TORSO_TOP*unit;
        float y1=y0+BodyAlignmentV120.TORSO_OUTLINE_HEIGHT*unit;
        c.drawRect(x0,y0,x1,y1,upperOutlinePaintV120);
    }

    /** V120 source-locked body fitting. Original boots translated as a rigid
     * pixel block. The forward boot RIGHT edge anchors to the last black
     * leading contour of the fitted torso/pelvis; rear boot joins the rear
     * hip bridge and never gets hauled to body center. Existing walk frame
     * footprints, square block dimensions and source RGBA remain untouched.
     */
    private void drawBody(Canvas canvas,Bitmap source,int frame,int blend,
                          float left,float top,float unit,
                          int torsoWidth,int pelvisWidth,Paint pixels) {
        if(torsoWidth>=TorsoWidthV114.MAX_PERCENT &&
           pelvisWidth>=PelvisWidthV115.MAX_PERCENT) {
            destination.set(left,top,left+WIDTH*unit,top+HEIGHT*unit);
            canvas.drawBitmap(source,spriteSource,destination,pixels);
            topBodyOutlineV120(canvas,left,top,unit,torsoWidth);
            return;
        }
        FootLayers layers=footLayers(source,frame,blend);
        float bandTop=top+PelvisLegRigV116.PELVIS_TOP*unit;
        float bandBottom=top+HEIGHT*unit;
        destination.set(PelvisWidthV115.left(left,unit,pelvisWidth),
            bandTop,PelvisWidthV115.right(left,unit,pelvisWidth),bandBottom);
        canvas.drawBitmap(layers.pelvis,pelvisRigSource,destination,pixels);
        // Source coordinates are local right-facing. The parent canvas flips
        // both boot layers intact for left-facing actors (no asymmetric art).
        final int rearInset=BodyAlignmentV120.rearBootShift(pelvisWidth);
        final int frontInset=BodyAlignmentV120.frontBootShift(
            torsoWidth,pelvisWidth);
        // If the torso remains wider than an independently narrowed pelvis,
        // close ONLY the short dark outline gap between the hip bridge and
        // the correctly placed forward foot. Never widen blue pelvis pixels.
        // The centered-overlap walking pose has no separate front foot.
        if(frame!=2&&BodyAlignmentV120.frontBlackConnectorGap(
                torsoWidth,pelvisWidth)>.01f){
            float from=left+BodyAlignmentV120.hipBridgeFront(pelvisWidth)*unit;
            float to=left+BodyAlignmentV120.frontFootStart(
                torsoWidth,pelvisWidth)*unit;
            float yy=top+220f*unit;
            canvas.drawRect(from,yy,to,
                yy+BodyAlignmentV120.TORSO_OUTLINE_HEIGHT*unit,
                upperOutlinePaintV120);
        }
        destination.set(left+rearInset*unit,bandTop,
            left+(WIDTH+rearInset)*unit,bandBottom);
        canvas.drawBitmap(layers.left,pelvisRigSource,destination,pixels);
        destination.set(left+frontInset*unit,bandTop,
            left+(WIDTH+frontInset)*unit,bandBottom);
        canvas.drawBitmap(layers.right,pelvisRigSource,destination,pixels);
        destination.set(left,bandTop,left+WIDTH*unit,bandBottom);
        canvas.drawBitmap(layers.overlap,pelvisRigSource,destination,pixels);

        // Retain the exact V114 upper torso width control and its source pixels.
        destination.set(
            TorsoWidthV114.left(left,unit,torsoWidth),
            top+TorsoWidthV114.TORSO_TOP*unit,
            TorsoWidthV114.right(left,unit,torsoWidth),
            top+TorsoWidthV114.LOWER_BODY_TOP*unit);
        canvas.drawBitmap(source,torsoSource,destination,pixels);
        topBodyOutlineV120(canvas,left,top,unit,torsoWidth);
    }

    /** Draw at the existing GameView origin: character feet are planted at y+24s.
     * Uses nearest-neighbor source sampling, original silhouettes, unchanged feet.
     */
    void draw(Canvas c,int id,boolean walking,int walkingFrame,float timeSec,float s,Paint pixel,
              float walkingTempo,float breathingTempo,int fixedWalkFps,int breathingAmplitude,
              float headTiltDegrees,int headOffsetX,int headOffsetY,int headSizePercent,
              int torsoWidthPercent,int pelvisWidthPercent) {
        id=range(id,1,COUNT);
        Fit fit=fitting[id];
        // Rendering scale uses 160/260 to match the old native 160px character rig.
        // The body has 200x260 canonical pixels; NO stretching between axes.
        float unit=(160f/HEIGHT)*s;
        float left=-100f*unit, top=-136f*s;
        int bodyFrame=CharacterAnimationV110.bodyFrame(walking,timeSec,fit.fps,
            fixedWalkFps,walkingTempo);
        Bitmap body=body(bodyFrame,fit.blend);
        drawBody(c,body,bodyFrame,fit.blend,left,top,unit,
            torsoWidthPercent,pelvisWidthPercent,pixel);
        Bitmap h=head(id);if(h==null)return;
        float headScale=Math.min(186f/h.getWidth(),192f/h.getHeight())*(fit.headScale/107f)*
            CharacterScopeV113.headSizeMultiplier(headSizePercent);
        int hw=Math.round(h.getWidth()*headScale),hh=Math.round(h.getHeight()*headScale);
        // V112: sliders add source-pixel offsets AFTER exact V5 individual fitting.
        int hx=HeadFitOffsetsV112.x(hw,fit.horizontal,headOffsetX);
        float breathing=CharacterAnimationV110.breathOffset(walking,timeSec,
            fit.breath*(Math.max(0,Math.min(12,breathingAmplitude))/4f),breathingTempo);
        int hy=HeadFitOffsetsV112.y(hh,fit.vertical,breathing,headOffsetY);
        headSource.set(0,0,h.getWidth(),h.getHeight());
        destination.set(left+hx*unit,top+hy*unit,left+(hx+hw)*unit,top+(hy+hh)*unit);
        // Rotate only the approved head bitmap about the fitted lower-neck pivot.
        // Source pixels, silhouette geometry, body, feet and hands are unchanged.
        float pivotX=HeadAimV111.neckX(destination.left,destination.width());
        float pivotY=HeadAimV111.neckY(destination.bottom,unit);
        c.save();
        c.rotate(Math.max(-HeadAimV111.MAX_DEGREES,
            Math.min(HeadAimV111.MAX_DEGREES,headTiltDegrees)),pivotX,pivotY);
        c.drawBitmap(h,headSource,destination,pixel);
        c.restore();
    }
}