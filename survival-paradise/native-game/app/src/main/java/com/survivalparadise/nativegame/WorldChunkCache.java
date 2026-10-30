package com.survivalparadise.nativegame;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * V54: renderer-agnostic deterministic terrain indices, software chunk
 * rasterization off the UI thread, bounded bitmap LRU on the UI thread.
 * No map-edge clamps and no new permanent objects per traveled kilometer.
 */
public final class WorldChunkCache {
    private static final int C=WorldChunkModel.CHUNK_SIZE;
    private static final int TILE=WorldChunkModel.TILE;
    private static final int N=WorldChunkModel.TILES_PER_CHUNK;
    private static final int STEP=WorldChunkModel.RASTER_SCALE;
    private static final int TILE_PX=TILE/STEP;
    private static final int MAX_PENDING=26;

    private final ExecutorService worker=Executors.newSingleThreadExecutor(r->{
        Thread thread=new Thread(r,"SP-V54-ChunkRenderer");
        thread.setDaemon(true);
        thread.setPriority(Thread.MIN_PRIORITY+1);
        return thread;
    });
    private final ConcurrentLinkedQueue<Chunk> completed=new ConcurrentLinkedQueue<>();
    private final HashSet<Long> pending=new HashSet<>();
    // All bitmap ownership / LRU operations occur on Android's UI thread.
    private final LinkedHashMap<Long,Chunk> resident=new LinkedHashMap<>(48,.75f,true);
    private final Paint bitmapPaint=new Paint();
    private final Paint terrainPaint=new Paint();
    private final RectF dst=new RectF();
    private final int campX,campY;
    private boolean closed=false;
    public int cacheHits,cacheMisses,generated;

    private static final class Chunk{
        final int cx,cy;
        final Bitmap bitmap;
        Chunk(int x,int y,Bitmap b){cx=x;cy=y;bitmap=b;}
        long key(){return WorldChunkModel.chunkKey(cx,cy);}
    }
    public WorldChunkCache(int campX,int campY){
        this.campX=campX;this.campY=campY;
        bitmapPaint.setAntiAlias(false);
        bitmapPaint.setFilterBitmap(false);
        terrainPaint.setAntiAlias(false);
    }
    private static void rect(Canvas c,Paint p,float x,float y,float w,float h,int color){
        p.setColor(color);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private static void tile(Canvas canvas,Paint p,int gx,int gy,int tx,int ty,
                             int pixelsPerTile,int scale,int campX,int campY){
        int color=WorldChunkModel.groundColor(gx,gy,campX,campY);
        int h=WorldChunkModel.tileDetail(gx,gy);
        float x=tx*(float)pixelsPerTile,y=ty*(float)pixelsPerTile;
        rect(canvas,p,x,y,pixelsPerTile,pixelsPerTile,color);
        float fx=(10+(h&17))/(float)scale;
        rect(canvas,p,x+fx,y+30f/scale,Math.max(1,4f/scale),Math.max(1,3f/scale),0xff60745c);
        if((h&15)==1){
            rect(canvas,p,x+33f/scale,y+52f/scale,Math.max(1,7f/scale),
                 Math.max(1,5f/scale),0xff647a61);
            rect(canvas,p,x+41f/scale,y+46f/scale,1,Math.max(1,6f/scale),0xff557156);
        }
    }
    private Chunk build(int cx,int cy){
        Bitmap bitmap=Bitmap.createBitmap(WorldChunkModel.RASTER_SIZE,
                WorldChunkModel.RASTER_SIZE,Bitmap.Config.RGB_565);
        Canvas c=new Canvas(bitmap);
        Paint p=new Paint();
        p.setAntiAlias(false);
        for(int y=0;y<N;y++)for(int x=0;x<N;x++)
            tile(c,p,cx*N+x,cy*N+y,x,y,TILE_PX,STEP,campX,campY);
        return new Chunk(cx,cy,bitmap);
    }
    private void queue(int cx,int cy){
        if(closed||pending.size()>=MAX_PENDING)return;
        long key=WorldChunkModel.chunkKey(cx,cy);
        if(resident.containsKey(key)||!pending.add(key))return;
        worker.execute(()->{
            Chunk chunk=null;
            try{if(!Thread.currentThread().isInterrupted())chunk=build(cx,cy);}
            catch(Throwable ignored){/* fallback remains safe while queued work fails */}
            if(chunk!=null)completed.offer(chunk);
            else completed.offer(new Chunk(cx,cy,null));
        });
    }
    private void acceptCompleted(){
        // Bound main-thread bitmap bookkeeping, never allocate bitmaps here.
        for(int i=0;i<MAX_PENDING;i++){
            Chunk chunk=completed.poll();
            if(chunk==null)break;
            pending.remove(chunk.key());
            if(closed){if(chunk.bitmap!=null)chunk.bitmap.recycle();continue;}
            if(chunk.bitmap==null)continue;
            Chunk older=resident.put(chunk.key(),chunk);
            if(older!=null&&older.bitmap!=null)older.bitmap.recycle();
            generated++;
        }
        while(resident.size()>WorldChunkModel.MAX_RESIDENT){
            Iterator<Map.Entry<Long,Chunk>> it=resident.entrySet().iterator();
            if(!it.hasNext())break;
            Chunk evicted=it.next().getValue();
            it.remove();
            evicted.bitmap.recycle();
        }
    }
    private void fallback(Canvas canvas,int cx,int cy){
        // Exact deterministic colors while a fresh texture renders in background.
        for(int y=0;y<N;y++)for(int x=0;x<N;x++){
            int gx=cx*N+x,gy=cy*N+y;
            tile(canvas,terrainPaint,gx,gy,cx*C+x*TILE,cy*C+y*TILE,
                 TILE,1,campX,campY);
        }
    }
    public void draw(Canvas canvas,float camX,float camY,float width,float height){
        if(closed)return;
        acceptCompleted();
        int x0=WorldChunkModel.chunkIndex(camX);
        int y0=WorldChunkModel.chunkIndex(camY);
        int x1=WorldChunkModel.chunkIndex(camX+width-0.001f);
        int y1=WorldChunkModel.chunkIndex(camY+height-0.001f);
        // Clip to the camera. Do not draw or rasterize outside of visible space.
        canvas.save();
        canvas.clipRect(camX-1,camY-1,camX+width+1,camY+height+1);
        for(int cy=y0;cy<=y1;cy++)for(int cx=x0;cx<=x1;cx++){
            Chunk current=resident.get(WorldChunkModel.chunkKey(cx,cy));
            if(current==null){
                cacheMisses++;
                queue(cx,cy);
                fallback(canvas,cx,cy);
            }else{
                cacheHits++;
                dst.set(cx*(float)C,cy*(float)C,(cx+1f)*C,(cy+1f)*C);
                canvas.drawBitmap(current.bitmap,null,dst,bitmapPaint);
            }
        }
        canvas.restore();
        // Ring prefetch: a walking player usually reaches fully prepared chunks.
        int centerX=WorldChunkModel.chunkIndex(camX+width*.5f);
        int centerY=WorldChunkModel.chunkIndex(camY+height*.5f);
        for(int radius=0;radius<=2;radius++){
            for(int dy=-radius;dy<=radius;dy++)for(int dx=-radius;dx<=radius;dx++){
                if(Math.max(Math.abs(dx),Math.abs(dy))!=radius)continue;
                queue(centerX+dx,centerY+dy);
            }
        }
    }
    public void release(){
        closed=true;
        worker.shutdownNow();
        for(Chunk ch:resident.values())if(ch.bitmap!=null)ch.bitmap.recycle();
        resident.clear();
        Chunk chunk;
        while((chunk=completed.poll())!=null)if(chunk.bitmap!=null)chunk.bitmap.recycle();
        pending.clear();
    }
}
