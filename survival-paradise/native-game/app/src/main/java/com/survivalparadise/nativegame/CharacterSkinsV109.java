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
    private final Rect headSource=new Rect();
    private final RectF destination=new RectF();
    private JSONObject configuration;
    private boolean loaded=false;

    CharacterSkinsV109(Context context) throws IOException {
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
        originals[0]=idleSheet;
        for(int f=0;f<4;f++) originals[f+1]=Bitmap.createBitmap(walkSheet,f*WIDTH,0,WIDTH,HEIGHT);
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
    /** Draw at the existing GameView origin: character feet are planted at y+24s.
     * Uses nearest-neighbor source sampling, original silhouettes, unchanged feet.
     */
    void draw(Canvas c,int id,boolean walking,int walkingFrame,float timeSec,float s,Paint pixel) {
        id=range(id,1,COUNT);
        Fit fit=fitting[id];
        // Rendering scale uses 160/260 to match the old native 160px character rig.
        // The body has 200x260 canonical pixels; NO stretching between axes.
        float unit=(160f/HEIGHT)*s;
        float left=-100f*unit, top=-136f*s;
        Bitmap body=body(walking?1+Math.floorMod((int)Math.floor(timeSec*fit.fps),4):0,fit.blend);
        destination.set(left,top,left+WIDTH*unit,top+HEIGHT*unit);
        c.drawBitmap(body,spriteSource,destination,pixel);
        Bitmap h=head(id);if(h==null)return;
        float headScale=Math.min(186f/h.getWidth(),192f/h.getHeight())*(fit.headScale/107f);
        int hw=Math.round(h.getWidth()*headScale),hh=Math.round(h.getHeight()*headScale);
        int hx=Math.round((200f-hw)/2+fit.horizontal+10);
        float breathing=walking?0f:(float)Math.sin(timeSec*4f)*fit.breath;
        int hy=Math.round(200f-hh+fit.vertical-3+breathing);
        headSource.set(0,0,h.getWidth(),h.getHeight());
        destination.set(left+hx*unit,top+hy*unit,left+(hx+hw)*unit,top+(hy+hh)*unit);
        c.drawBitmap(h,headSource,destination,pixel);
    }
}