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
    /** V124: genuine industrial props on seeded parcels, not surface decals. */
    public void outdoors(Canvas c,float camX,float camY,float vw,float vh,int seed){
        int x0=IndustrialOpenWorldV124.sx(camX)-1;
        int x1=IndustrialOpenWorldV124.sx(camX+vw)+1;
        int y0=IndustrialOpenWorldV124.sy(camY)-1;
        int y1=IndustrialOpenWorldV124.sy(camY+vh)+1;
        for(int iy=y0;iy<=y1;iy++)for(int ix=x0;ix<=x1;ix++){
            IndustrialOpenWorldV124.Plot p=IndustrialOpenWorldV124.plot(ix,iy,seed);
            if(!p.developed())continue;
            float x=p.x,y=p.y;
            if(p.enterable()){
                int shape=IndustrialFacadeShapeV126.facade(p.kind);
                int facade=shape==0?DOUBLE:shape==1?SINGLE:
                           shape==2?SHED:WAREHOUSE;
                // The facade and its collision use one approved PNG silhouette
                // and precisely the same world-to-art transform.
                draw(c,facade,p.buildingX-12,p.buildingY-22,
                     p.buildingW+24,p.buildingH+46);
            }
            // Props: physical size and position are shared with collision.
            for(IndustrialPropLayoutV126.Prop prop:
                    IndustrialPropLayoutV126.forPlot(p))
                draw(c,prop.sprite,x+prop.x,y+prop.y,prop.w,prop.h);
            // Fence sprites only over real physical fence segments; central
            // yard gate is left empty and can be crossed by characters.
            draw(c,FENCE,x+112,y+1178,470,48);
            draw(c,PATCHWORK,x+832,y+1178,433,48);
        }
    }
    public void indoors(Canvas c,IndustrialInteriorV123 room){
        float[][] m=room.machines;
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
