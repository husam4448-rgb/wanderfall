package com.survivalparadise.nativegame;

import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
import android.util.Base64;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;

/**
 * Real authored V166 furniture artwork: 96 themed equipment identities with
 * TWO separately painted top-down / profile sprites each.
 *
 * Renders the immutable, offline authored WebP alpha atlas. The old 128px
 * Canvas geometric placeholder renderer is removed, not layered beneath it.
 * Placement and collisions are entirely owned by NeighborhoodLayoutV163.
 * No per-frame bitmap allocations or runtime procedural object painting.
 */
public final class InteriorDirectionalFurnitureV166 {
    private InteriorDirectionalFurnitureV166(){}
    public static final int FIRST=InteriorFurnitureCatalogV166.FIRST;
    public static final int COUNT=InteriorFurnitureCatalogV166.COUNT;
    private static final int CELL=128,COLS=16,ROWS=12;
    private static final String FILE="sp_v166_directional_furniture.webp.b64";
    private static Bitmap atlas;
    private static boolean attempted;
    private static final Rect SOURCE=new Rect();
    private static final RectF DEST=new RectF();
    private static final Paint FILTER=new Paint(Paint.FILTER_BITMAP_FLAG|
        Paint.DITHER_FLAG);

    public static boolean valid(int sprite){
        return InteriorFurnitureCatalogV166.valid(sprite);
    }
    public static int kind(int sprite){
        return InteriorFurnitureCatalogV166.kind(sprite);
    }
    public static synchronized void load(AssetManager assets){
        if(attempted||assets==null)return;
        attempted=true;
        try(InputStream stream=assets.open(FILE)){
            ByteArrayOutputStream encoded=new ByteArrayOutputStream(180000);
            byte[] buf=new byte[8192];int count;
            while((count=stream.read(buf))!=-1)encoded.write(buf,0,count);
            byte[] raw=Base64.decode(encoded.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options options=new BitmapFactory.Options();
            options.inScaled=false;options.inPreferredConfig=Bitmap.Config.ARGB_8888;
            Bitmap result=BitmapFactory.decodeByteArray(raw,0,raw.length,options);
            if(result==null||result.getWidth()!=COLS*CELL||
               result.getHeight()!=ROWS*CELL){
                if(result!=null)result.recycle();
                throw new IllegalArgumentException(
                    "Invalid V166 authored directional art atlas dimensions");
            }
            atlas=result;
            android.util.Log.i("SP-V166",
                "Directional furniture ready: 96 fully authored object variants / 192 face views");
        }catch(Exception err){
            android.util.Log.e("SP-V166",
                "Missing source-authored directional furniture. Not silently using geometric placeholders.",err);
        }
    }
    public static boolean ready(){
        return atlas!=null&&!atlas.isRecycled();
    }
    /**
     * Exact source-pixel reuse of the existing HAND-PAINTED 16+16+16
     * approved-quality atlases for appropriate forward-facing furniture.
     * No new generative placeholders, no screenshot replacement, no
     * angle-rotation of a frontal source to fake a side projection.
     *
     * The 96-role authored atlas remains the genuine side-facing fallback
     * and covers functional shapes for which no original illustration exists.
     */
    private static int paintedFront(int sprite){
        int kind=InteriorFurnitureCatalogV166.kind(sprite);
        int theme=(sprite-FIRST)/InteriorFurnitureCatalogV166.PER_THEME;
        int slot=(sprite-FIRST)%InteriorFurnitureCatalogV166.PER_THEME;
        switch(kind){
            case 0:return theme==3?6:0; // actual detailed textile bed
            case 1:return 33;           // worn upholstered couch
            case 2:return 1;            // substantial wood wardrobe
            case 3:return -1;           // cooker: avoid wrong sink substitution
            case 4:return 15;           // functional kitchen sink
            case 5:return slot%3==0?47:14; // dining room set/table
            case 6:return slot%2==0?2:36; // complete computer workstation
            case 7:return -1;           // dedicated seating, not fake furniture
            case 8: // A market shelf is groceries, a depot shelf is freight.
                if(theme==2)return 38;
                if(theme==6)return 45;
                return slot%3==0?41:slot%2==0?23:9; // domestic/library books
            case 9:return 10;           // security/industrial console
            case 10:return 3;           // original filing drawers
            case 11:return theme==5?13:1; // steel stock cabinet / locker
            case 12:return slot%2==0?26:5; // actual store checkout
            case 13:return slot%2==0?38:4; // stocked retail shelving
            case 14:return 27;          // cold-glass grocery cabinet
            case 15:return 17;          // luggage rack with suitcases
            case 16:return theme==3?16:24; // hotel/office reception
            case 17:return slot%2==0?20:40; // classroom desks and books
            case 18:return 43;          // teaching notices/diagram board
            case 19:return slot%2==0?21:42; // real laboratory equipment
            case 20:return 21;          // lab diagnostic apparatus
            case 21:return 30;          // clinical examination bed
            case 22:return slot%2==0?28:44; // heavy factory machinery
            case 23:return -1;          // genuine conveyor in directional atlas
            case 24:return slot%2==0?29:44; // tools + workbenches
            case 25:return slot%2==0?45:11; // substantial storage racks
            case 26:return -1;          // handtruck side/front pair only
            case 27:return slot%2==0?12:45; // pallet stacks and loading racks
            case 28:return -1;          // copier: no unrelated cabinet art
            case 29:return 10;          // security electronics rack
            case 30:return slot%2==0?35:1; // dresser or wardrobe
            case 31:return 15;          // kitchen/utility island
            default:return -1;
        }
    }
    public static boolean drawAt(Canvas canvas,int sprite,
                                 float x,float y,float width,float height,int facing){
        if(!valid(sprite)||width<=0||height<=0||!ready())return false;
        // Each side-facing pixel is authored independently rather than a
        // rotated south-facing square. 270 is a horizontal mirror ONLY.
        int side=(facing==90||facing==270)?1:0;
        if(side==0){
            int painted=paintedFront(sprite);
            if(painted>=0&&InteriorPropArtV166.drawAt(canvas,painted,
                        x,y,width,height))
                return true;
        }
        int index=(sprite-FIRST)*2+side;
        int sx=(index%COLS)*CELL,sy=(index/COLS)*CELL;
        SOURCE.set(sx,sy,sx+CELL,sy+CELL);
        DEST.set(x,y,x+width,y+height);
        if(facing==270){
            canvas.save();
            canvas.scale(-1f,1f,x+width*.5f,y+height*.5f);
            canvas.drawBitmap(atlas,SOURCE,DEST,FILTER);
            canvas.restore();
        }else{
            canvas.drawBitmap(atlas,SOURCE,DEST,FILTER);
        }
        return true;
    }
    public static synchronized void release(){
        if(atlas!=null&&!atlas.isRecycled())atlas.recycle();
        atlas=null;attempted=false;
    }
}
