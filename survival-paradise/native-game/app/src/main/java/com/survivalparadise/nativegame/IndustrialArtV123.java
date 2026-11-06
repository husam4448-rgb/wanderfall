package com.survivalparadise.nativegame;

import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import java.io.InputStream;

/** Approved 24-user-asset industrial artwork, normalized losslessly to light WebP. */
public final class IndustrialArtV123 {
    private static final String[] NAMES={
        "SP_Industrial_Scrap_Field_01",
        "SP_Industrial_Factory_Double_Bay_01",
        "SP_Industrial_Chainlink_Fence_Long_01",
        "SP_Industrial_Factory_Single_Bay_01",
        "SP_Industrial_Abandoned_Sedan_01",
        "SP_Industrial_Conveyor_Unit_01",
        "SP_Industrial_Damaged_Reinforced_Gate_01",
        "SP_Industrial_Corrugated_Fence_Rusted_01",
        "SP_Industrial_Electric_Transformer_01",
        "SP_Industrial_Forklift_01",
        "SP_Industrial_Abandoned_Utility_Truck_01",
        "SP_Industrial_Vertical_Pipe_Unit_01",
        "SP_Industrial_Belt_Drive_Machine_01",
        "SP_Industrial_Double_Pressure_Tanks_01",
        "SP_Industrial_Scrap_Fence_Cluttered_01",
        "SP_Industrial_Cracked_Concrete_01",
        "SP_Industrial_Patchwork_Fence_Front_01",
        "SP_Industrial_Patchwork_Fence_Angled_01",
        "SP_Industrial_Pipe_Manifold_01",
        "SP_Industrial_Electric_Transformer_02",
        "SP_Industrial_Twin_Tank_Silos_01",
        "SP_Industrial_Chainlink_Gate_01",
        "SP_Industrial_Metal_Shed_01",
        "SP_Industrial_Warehouse_Roller_Door_01"
    };
    private static final int SCRAP=0,DOUBLE=1,FENCE=2,SINGLE=3,CAR=4,
        CONVEYOR=5,REINFORCED=6,CORRUGATED=7,TRANSFORMER=8,FORKLIFT=9,
        TRUCK=10,VERTICAL=11,BELT=12,TANKS=13,SCRAPFENCE=14,
        CONCRETE=15,PATCHWORK=16,ANGLED=17,PIPE=18,TRANSFORMER2=19,
        SILOS=20,GATE=21,SHED=22,WAREHOUSE=23;
    private final Bitmap[] sprites=new Bitmap[NAMES.length];
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
    private final RectF dst=new RectF();
    public int loaded(){int n=0;for(Bitmap b:sprites)if(b!=null)n++;return n;}
    public void load(AssetManager manager){
        BitmapFactory.Options opts=new BitmapFactory.Options();
        opts.inScaled=false;
        for(int i=0;i<NAMES.length;i++){
            try(InputStream in=manager.open("industrial_v123/"+NAMES[i]+".webp")){
                Bitmap b=BitmapFactory.decodeStream(in,null,opts);
                if(b!=null&&b.getWidth()<=1024&&b.getHeight()<=1024)sprites[i]=b;
                else if(b!=null)b.recycle();
            }catch(Exception ex){
                android.util.Log.w("SP-V123","Missing industrial artwork "+NAMES[i],ex);
            }
        }
    }
    private void draw(Canvas c,int index,float x,float y,float w,float h){
        Bitmap b=sprites[index];if(b==null)return;
        dst.set(x,y,x+w,y+h);c.drawBitmap(b,null,dst,paint);
    }
    public void outdoors(Canvas c,float camX,float camY,float vw,float vh,int seed){
        int x0=IndustrialWorldV123.sector(camX)-1,x1=IndustrialWorldV123.sector(camX+vw)+1;
        int y0=IndustrialWorldV123.sector(camY)-1,y1=IndustrialWorldV123.sector(camY+vh)+1;
        for(int iy=y0;iy<=y1;iy++)for(int ix=x0;ix<=x1;ix++){
            IndustrialWorldV123.District d=IndustrialWorldV123.district(ix,iy,seed);
            float x=d.x,y=d.y;
            // This source facade overlays an actual solid collision footprint,
            // and its front threshold remains freely accessible.
            int facade=d.kind==3?WAREHOUSE:d.kind%3==0?DOUBLE:
                        d.kind%3==1?SINGLE:SHED;
            draw(c,CONCRETE,x+121,y+163,846,580);
            draw(c,facade,x+146,y+178,791,545);
            draw(c,SCRAP,x+117,y+974,195,155);
            draw(c,TRANSFORMER,x+955,y+822,167,165);
            draw(c,BELT,x+170,y+911,165,145);
            draw(c,TRUCK,x+960,y+1060,190,155);
            draw(c,FORKLIFT,x+745,y+969,135,125);
            draw(c,TANKS,x+990,y+349,166,186);
            draw(c,PIPE,x+1035,y+592,118,145);
            draw(c,FENCE,x+100,y+1140,362,104);
            draw(c,GATE,x+668,y+1140,170,104); // gate slid aside; path stays open
            draw(c,PATCHWORK,x+654,y+1140,377,104);
            draw(c,CAR,x+1030,y+1000,149,120);
            // Hazard-strip outlined click target survives the decorative facade.
            Paint p=new Paint();p.setColor(0xffbd9e62);
            c.drawRect(d.doorX-74,d.doorY+8,d.doorX+74,d.doorY+18,p);
            p.setColor(0xff273a3b);
            c.drawRect(d.doorX-65,d.doorY+17,d.doorX+65,d.doorY+29,p);
        }
    }
    public void indoors(Canvas c,IndustrialInteriorV123 room){
        float[][] m=IndustrialInteriorV123.MACHINES;
        int kind=room.district.kind;
        int[] art=kind==2?new int[]{SILOS,PIPE,CONVEYOR,TANKS,VERTICAL,TRANSFORMER2,
                    BELT,TRANSFORMER,CORRUGATED,SCRAPFENCE,PIPE,TANKS,SHED,CAR,REINFORCED,DOUBLE}:
                    kind==3?new int[]{WAREHOUSE,BELT,FORKLIFT,TRUCK,CONVEYOR,PIPE,
                    CORRUGATED,PATCHWORK,TRANSFORMER2,TANKS,SCRAP,SILOS,SHED,ANGLED,CAR,FENCE}:
                    new int[]{TRANSFORMER,BELT,TANKS,PIPE,CONVEYOR,TRANSFORMER2,
                    VERTICAL,SILOS,SCRAPFENCE,CORRUGATED,REINFORCED,FORKLIFT,
                    PATCHWORK,SHED,DOUBLE,CAR};
        for(int i=0;i<m.length;i++){
            float[] q=m[i];
            draw(c,art[i],q[0],q[1],q[2],q[3]);
        }
    }
    public void release(){
        for(int i=0;i<sprites.length;i++){
            if(sprites[i]!=null&&!sprites[i].isRecycled())sprites[i].recycle();
            sprites[i]=null;
        }
    }
}
