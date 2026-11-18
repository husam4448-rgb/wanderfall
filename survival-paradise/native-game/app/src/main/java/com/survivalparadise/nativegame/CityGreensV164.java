package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;

/**
 * V164: genuinely unbuilt inner-city greens, not buildings with green roofs.
 * Park identity is seeded from existing vacant V160 plots; building identities
 * and collision polygons remain absolutely unchanged for old saved worlds.
 */
public final class CityGreensV164 {
    private CityGreensV164(){}
    private static void rect(Canvas c,Paint p,float x,float y,float w,float h,int color){
        p.setStyle(Paint.Style.FILL);p.setColor(color);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private static void oval(Canvas c,Paint p,float x,float y,float rx,float ry,int color){
        p.setStyle(Paint.Style.FILL);p.setColor(color);
        c.drawOval(x-rx,y-ry,x+rx,y+ry,p);
    }
    public static int vacantPlots(WorldCivilizationV159.Plan plan){
        if(plan==null)return 0;
        int count=0;
        for(WorldCivilizationV159.Parcel parcel:plan.parcels)
            for(int slot=0;slot<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;slot++)
                if(NeighborhoodV154.get(parcel.tx,parcel.ty,slot,plan)==null)
                    count++;
        return count;
    }
    public static void draw(Canvas c,Paint p,WorldCivilizationV159.Plan plan,
                            float camX,float camY,float w,float h,boolean lowDetail){
        if(plan==null)return;
        for(WorldCivilizationV159.Parcel parcel:plan.parcels){
            if(!parcel.onScreen(camX,camY,w,h))continue;
            for(int slot=0;slot<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;slot++){
                if(NeighborhoodV154.get(parcel.tx,parcel.ty,slot,plan)!=null)continue;
                int col=slot%NeighborhoodV154.COLS,row=slot/NeighborhoodV154.COLS;
                float x=parcel.tx*(float)NeighborhoodV154.TILE_W+850f+col*1800f;
                float y=parcel.ty*(float)NeighborhoodV154.TILE_H+
                    (row==0?1140f:3360f);
                if(x<camX-700||x>camX+w+700||y<camY-600||y>camY+h+600)
                    continue;
                int seed=IndustrialWorldV123.hash(parcel.tx*73+slot,
                    parcel.ty*101-slot,plan.seed^0x1647AA);
                // Constrain planting to one vacant lot. The surrounding roads,
                // building foundations and perimeter fence all stay unobstructed.
                oval(c,p,x,y,645f,475f,0xff586e55);
                oval(c,p,x-26,y-15,592f,427f,0xff6b815e);
                oval(c,p,x+41,y+40,510f,360f,0xff7b8965);
                // Painterly native grass/soil material within the EXISTING
                // vacant-lot boundary; park placement remains immutable.
                Path meadow=new Path();
                meadow.addOval(x-470,y-300,x+480,y+350,Path.Direction.CW);
                SurfaceArtV165.path(c,meadow,SurfaceArtV165.SOIL,300f,94);
                // Different parks have curved paths, athletic lawns,
                // vegetable plots and overgrown wasteland clearings.
                int type=Math.floorMod(seed,4);
                if(type==0){
                    oval(c,p,x-24,y+15,294,220,0xff998d70);
                    oval(c,p,x-24,y+15,274,200,0xff74885e);
                    rect(c,p,x-340,y-2,685,16,0xff8e825f);
                    for(int k=0;k<3;k++){
                        float bx=x-350+k*287;
                        rect(c,p,bx,y-100,95,14,0xff394c3f);
                        rect(c,p,bx+5,y-98,85,9,0xff967b56);
                        rect(c,p,bx+13,y-88,5,38,0xff514333);
                        rect(c,p,bx+72,y-88,5,38,0xff514333);
                    }
                }else if(type==1){
                    for(int n=0;n<5;n++){
                        float yy=y-320+n*134;
                        rect(c,p,x-430,yy,860,64,0xff5b614a);
                        for(int j=0;j<8;j++){
                            int v=IndustrialWorldV123.hash(j+n*7,seed,plan.seed);
                            float xx=x-395+j*104;
                            oval(c,p,xx,yy+37,18f+Math.floorMod(v,13),13,
                                j%2==0?0xff44694b:0xff7a9662);
                        }
                    }
                }else if(type==2){
                    // Wild open field, leaf litter, natural ditch, worn trail.
                    rect(c,p,x-55,y-453,84,902,0xff8e846a);
                    rect(c,p,x-40,y-447,53,893,0xffb5a37d);
                }else{
                    oval(c,p,x,y,490,344,0xff536a4e);
                    oval(c,p,x+31,y-29,426,284,0xff6c8556);
                    rect(c,p,x-38,y-368,70,738,0xff85785d);
                    rect(c,p,x-34,y-359,61,718,0xffa89b7c);
                }
                // Tuft, clover, saplings and small organic details, capped at
                // low zoom for performance.
                for(int k=0;k<(lowDetail?14:53);k++){
                    int n=IndustrialWorldV123.hash(seed+k*23,
                        slot*11+k*31,plan.seed);
                    float bx=x-530+Math.floorMod(n,1060);
                    float by=y-385+Math.floorMod(n>>>13,770);
                    if((n&7)==0){
                        oval(c,p,bx,by,14,8,0xff365b43);
                        oval(c,p,bx+12,by-8,10,7,0xff668b59);
                        rect(c,p,bx+5,by+1,5,9,0xff594f39);
                    }else if((n&3)==1){
                        rect(c,p,bx,by,3,13,0xff47683f);
                        rect(c,p,bx+5,by+2,2,9,0xffa3a76a);
                    }else rect(c,p,bx,by,3,2,0xffc5ba84);
                }
            }
        }
    }
}
