package com.survivalparadise.nativegame;

import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.BitmapShader;
import android.graphics.Canvas;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Shader;
import android.util.Base64;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;

/**
 * Eight ORIGINAL top-down indoor floor materials. Stable repeat shaders
 * prevent the old outdoor gravel texture from appearing inside buildings.
 * All clipping follows the unchanged indoor layout geometry.
 */
public final class InteriorFloorArtV166 {
    private InteriorFloorArtV166(){}
    private static final int TILES=InteriorFloorSelectionV166.TILE_COUNT;
    private static final int CELL=InteriorFloorSelectionV166.TILE_SIZE;
    private static final Bitmap[] bitmaps=new Bitmap[TILES];
    private static final BitmapShader[] shaders=new BitmapShader[TILES];
    private static final Paint PAINT=new Paint(Paint.FILTER_BITMAP_FLAG |
                                              Paint.DITHER_FLAG);
    private static final Matrix MATRIX=new Matrix();
    private static boolean attempted;
    public static synchronized void load(AssetManager assets){
        if(assets==null||attempted)return;
        attempted=true;
        try(InputStream input=assets.open("sp_v166_indoor_floors.webp.b64")){
            ByteArrayOutputStream buffer=new ByteArrayOutputStream(220000);
            byte[] chunk=new byte[8192];int n;
            while((n=input.read(chunk))!=-1)buffer.write(chunk,0,n);
            byte[] decoded=Base64.decode(buffer.toByteArray(),Base64.DEFAULT);
            BitmapFactory.Options options=new BitmapFactory.Options();
            options.inScaled=false;
            Bitmap sheet=BitmapFactory.decodeByteArray(decoded,0,decoded.length,options);
            if(sheet==null||sheet.getWidth()!=4*CELL||sheet.getHeight()!=2*CELL)
                throw new IllegalArgumentException("Invalid indoor floor atlas");
            try{
                for(int i=0;i<TILES;i++){
                    bitmaps[i]=Bitmap.createBitmap(sheet,
                        (i%4)*CELL,(i/4)*CELL,CELL,CELL);
                    shaders[i]=new BitmapShader(bitmaps[i],
                        Shader.TileMode.REPEAT,Shader.TileMode.REPEAT);
                }
            }finally{sheet.recycle();}
            android.util.Log.i("SP-V166","Indoor floor materials ready: 8 authored surfaces");
        }catch(Exception e){
            android.util.Log.e("SP-V166","Unable to decode eight indoor floor materials",e);
            release();
        }
    }
    public static boolean ready(){
        for(BitmapShader shader:shaders)if(shader==null)return false;
        return true;
    }
    /** World-aligned original texture; phase is deterministic per saved room. */
    public static boolean fill(Canvas c,int material,
                               float x,float y,float w,float h,
                               int seed,float tileWorldSize){
        if(!ready()||material<0||material>=TILES||w<=0||h<=0)return false;
        MATRIX.reset();
        float scale=tileWorldSize/CELL;
        MATRIX.setScale(scale,scale);
        // Small deterministic offset avoids identical repeating scratches
        // between neighboring rooms; constant under camera movement.
        MATRIX.postTranslate(Math.floorMod(seed,103)-51f,
                             Math.floorMod(seed>>>11,101)-50f);
        shaders[material].setLocalMatrix(MATRIX);
        PAINT.setStyle(Paint.Style.FILL);
        PAINT.setShader(shaders[material]);
        c.drawRect(x,y,x+w,y+h,PAINT);
        PAINT.setShader(null);
        return true;
    }
    public static void neighborhood(Canvas c,NeighborhoodInteriorV161 room){
        if(room==null||!ready())return;
        int base=InteriorFloorSelectionV166.hallway(room.theme);
        int phase=InteriorFloorSelectionV166.phase(room.seed,room.variation);
        fill(c,base,23f,23f,1554f,1072f,phase,
            InteriorFloorSelectionV166.worldTileSize(base));
        final float scale=ClinicInteriorV89.EXPANSION_V90;
        String[] labels=room.roomNames();
        for(int i=0;i<room.layoutV163.rooms.length;i++){
            float[] b=room.layoutV163.rooms[i];
            float x=b[0]/scale,y=b[1]/scale,
                w=b[2]/scale,h=b[3]/scale;
            if(w<8||h<8)continue;
            int tile=InteriorFloorSelectionV166.room(room.theme,
                i<labels.length?labels[i]:"");
            int roomPhase=InteriorFloorSelectionV166.phase(
                phase^room.building.slot*19,i);
            c.save();
            c.clipRect(x+2f,y+2f,x+w-2f,y+h-2f);
            fill(c,tile,x+2f,y+2f,w-4f,h-4f,roomPhase,
                InteriorFloorSelectionV166.worldTileSize(tile));
            c.restore();
        }
    }
    public static void legacy(Canvas c,int siteKind,boolean clinic,int seed){
        if(!ready())return;
        int tile=InteriorFloorSelectionV166.legacy(siteKind,clinic);
        int phase=InteriorFloorSelectionV166.phase(seed,siteKind);
        fill(c,tile,23f,23f,1554f,1072f,phase,
            InteriorFloorSelectionV166.worldTileSize(tile));
        for(int i=0;i<6;i++){
            float x=23+(i%3)*526f,y=i<3?44f:642f;
            float w=i%3==2?502f:506f,h=i<3?442f:428f;
            int roomTile=clinic?(i%3==1?TERRAZZO():InteriorFloorSelectionV166.LINO):
                (siteKind==ExpeditionSitesV88.MOTEL&&i%3==0?
                    InteriorFloorSelectionV166.CARPET:tile);
            fill(c,roomTile,x+3,y+3,w-6,h-6,phase+i*71,
                InteriorFloorSelectionV166.worldTileSize(roomTile));
        }
    }
    // Helper isolates the clinic's hygienic slate from legacy site carpets.
    private static int TERRAZZO(){return InteriorFloorSelectionV166.TERRAZZO;}
    /** Freight and factory floors keep existing machine and route geometry. */
    public static boolean industrial(Canvas c,IndustrialInteriorV123 room){
        if(room==null||!ready())return false;
        int tile=room.district.kind==3?
            InteriorFloorSelectionV166.CONCRETE:InteriorFloorSelectionV166.EPOXY;
        int seed=InteriorFloorSelectionV166.phase(room.district.seed,
            room.district.sx*37+room.district.sy*71);
        return fill(c,tile,35f,35f,2650f,1825f,seed,
            InteriorFloorSelectionV166.worldTileSize(tile));
    }
    public static synchronized void release(){
        for(int i=0;i<TILES;i++){
            shaders[i]=null;
            if(bitmaps[i]!=null&&!bitmaps[i].isRecycled())
                bitmaps[i].recycle();
            bitmaps[i]=null;
        }
        attempted=false;
    }
}
