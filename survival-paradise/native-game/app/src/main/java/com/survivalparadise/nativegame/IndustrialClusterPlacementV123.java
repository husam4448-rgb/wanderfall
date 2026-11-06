package com.survivalparadise.nativegame;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Seed-stable and geometry-aware industrial ground details. All categories
 * have authored eligibility; never scatter a road feature in unpaved terrain.
 * Rendering assets are separate from this pure geometry model.
 */
public final class IndustrialClusterPlacementV123 {
    private IndustrialClusterPlacementV123() {}
    public static final int CORNER=1, ROAD_MARK=2, ROAD_SURFACE=3,
        ROAD_EDGE=4, YARD=5, MAINTENANCE=6, STAIN=7, GATE_APRON=8;
    private static final int[] CORNERS={30,48};
    private static final int[] MARKS={47};
    private static final int[] TURNS={26};
    private static final int[] PEDESTRIANS={33};
    private static final int[] GATE_MARKS={31,38,40,41,45,50};
    private static final int[] SURFACES={12,14,23,28,32,34,37,42,44,49};
    private static final int[] EDGES={1,3,7,16,18,29,36,39,43,46,81,85,87,94,99};
    private static final int[] YARDS={6,8,10,13,15,19,20,22,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,70,72,73,74,75,82,90,96,100};
    private static final int[] SERVICE_ART={4,9,21,25,71,79,83,88,92,98};
    private static final int[] STAINS={2,5,17,24,76,77,78,84,86,89,91,93,95};

    public static final class Placement {
        public final float x,y,width;
        public final int sprite,zone,quarterTurns,sectorX,sectorY;
        public final float opacity;
        public final boolean solid;
        private Placement(int sx,int sy,float x,float y,float width,int sprite,
                          int zone,int turns,float opacity,boolean solid) {
            this.sectorX=sx;this.sectorY=sy;this.x=x;this.y=y;this.width=width;
            this.sprite=sprite;this.zone=zone;this.quarterTurns=Math.floorMod(turns,4);
            this.opacity=opacity;this.solid=solid;
        }
        public String id(){return sectorX+":"+sectorY+":"+zone+":"+sprite+":"+
                Math.round(x)+":"+Math.round(y);}
    }
    private static int pick(int[] choices,int sx,int sy,int seed,int slot) {
        return choices[Math.floorMod(IndustrialWorldV123.hash(sx*17+slot,
            sy*23-slot,seed ^ (slot*157)),choices.length)];
    }
    private static void add(List<Placement> out,int[] choices,int sx,int sy,int seed,
            int slot,int zone,float x,float y,float width,int turns,float opacity,
            boolean solid) {
        int sprite=pick(choices,sx,sy,seed,slot);
        out.add(new Placement(sx,sy,x,y,width,sprite,zone,turns,opacity,solid));
    }
    public static boolean onRoad(float x,float y) {
        return IndustrialWorldV123.roadAt(x,y);
    }
    private static boolean nearEntrance(float x,float y,IndustrialWorldV123.District d,
                                        float clearance) {
        if(y>d.doorY-85 && y<d.y+IndustrialWorldV123.SECTOR-75 &&
                Math.abs(x-d.doorX)<clearance+90)return true;
        float dx=x-d.doorX,dy=y-d.doorY;
        return dx*dx+dy*dy<(clearance+110)*(clearance+110);
    }
    /** Every sector's road junction belongs to that sector: no redraw jitter. */
    public static List<Placement> inSector(int sx,int sy,int seed) {
        ArrayList<Placement> out=new ArrayList<>();
        IndustrialWorldV123.District d=IndustrialWorldV123.district(sx,sy,seed);
        float ox=d.x,oy=d.y;
        float xHalf=IndustrialWorldV123.roadWidth(sx)*.5f;
        float yHalf=IndustrialWorldV123.roadWidth(sy)*.5f;
        // Snap curved curbs to actual intersection quadrants, never field terrain.
        for(int q=0;q<4;q++) {
            if(Math.floorMod(IndustrialWorldV123.hash(sx+q,sy-q,seed),3)!=0)continue;
            int dx=(q==0||q==3)?1:-1, dy=(q<2)?1:-1;
            float px=ox+dx*(xHalf+18),py=oy+dy*(yHalf+18);
            if(!buildingFootprint(px,py,49))
                add(out,CORNERS,sx,sy,seed,100+q,CORNER,px,py,88,q,.77f,false);
        }
        // Horizontal and vertical road details share the true road centerlines.
        add(out,MARKS,sx,sy,seed,201,ROAD_MARK,ox,oy+365,120,1,.74f,false);
        if(Math.floorMod(IndustrialWorldV123.hash(sx,sy,seed+17),3)==0)
            add(out,TURNS,sx,sy,seed,205,ROAD_MARK,ox+40,oy+30,108,0,.72f,false);
        if(Math.floorMod(IndustrialWorldV123.hash(sx,sy,seed+219),4)==0)
            add(out,PEDESTRIANS,sx,sy,seed,206,ROAD_MARK,ox+120,oy,92,0,.70f,false);
        add(out,MARKS,sx,sy,seed,202,ROAD_MARK,ox+655,oy,120,0,.75f,false);
        add(out,SURFACES,sx,sy,seed,203,ROAD_SURFACE,ox,oy+960,115,1,.72f,false);
        add(out,SURFACES,sx,sy,seed,204,ROAD_SURFACE,ox+1030,oy,115,0,.72f,false);
        // Gutter and cracked-pavement decals must touch a real asphalt boundary.
        add(out,EDGES,sx,sy,seed,301,ROAD_EDGE,ox+xHalf+34,oy+525,105,1,.80f,false);
        add(out,EDGES,sx,sy,seed,302,ROAD_EDGE,ox+860,oy+yHalf+34,105,0,.80f,false);
        // Threshold paint is only authored on an actual enterable factory portal.
        if(Math.floorMod(IndustrialWorldV123.hash(sx,sy,seed+322),2)==0)
            add(out,GATE_MARKS,sx,sy,seed,320,GATE_APRON,d.doorX,d.doorY+45,108,0,.65f,false);
        // Scrap belongs to fenced stockpiles, never the road or the access lane.
        float[][] pads={{235,790},{358,1114},{845,1110},{1170,735}};
        for(int i=0;i<pads.length;i++) {
            if(Math.floorMod(IndustrialWorldV123.hash(sx+i,sy,seed),2)!=0)continue;
            float px=ox+pads[i][0],py=oy+pads[i][1];
            if(!nearEntrance(px,py,d,145) && !onRoad(px,py)) {
                add(out,YARDS,sx,sy,seed,401+i,YARD,px,py,110,Math.floorMod(i,4),.86f,true);
            }
        }
        // Maintenance decals only near placed machinery pads.
        float[][] service={{352,879},{1152,797}};
        for(int i=0;i<service.length;i++) {
            if(Math.floorMod(IndustrialWorldV123.hash(sx,sy+i,seed),2)!=0)continue;
            float px=ox+service[i][0],py=oy+service[i][1];
            if(!nearEntrance(px,py,d,125))
                add(out,SERVICE_ART,sx,sy,seed,501+i,MAINTENANCE,px,py,115,i,.81f,false);
        }
        float[][] runoff={{193,1070},{1152,1010}};
        for(int i=0;i<runoff.length;i++) {
            if(Math.floorMod(IndustrialWorldV123.hash(sx+53,sy+i,seed),3)!=0)continue;
            float px=ox+runoff[i][0],py=oy+runoff[i][1];
            if(!nearEntrance(px,py,d,120))
                add(out,STAINS,sx,sy,seed,601+i,STAIN,px,py,145,i,.67f,false);
        }
        return Collections.unmodifiableList(out);
    }
    /** Existing V123 factory collision footprint; includes adjacent sectors. */
    private static boolean buildingFootprint(float x,float y,float radius){
        int sx=IndustrialWorldV123.sector(x),sy=IndustrialWorldV123.sector(y);
        for(int yy=sy-1;yy<=sy+1;yy++)for(int xx=sx-1;xx<=sx+1;xx++){
            float bx=xx*(float)IndustrialWorldV123.SECTOR;
            float by=yy*(float)IndustrialWorldV123.SECTOR;
            if(x+radius>bx+170&&x-radius<bx+911&&
               y+radius>by+205&&y-radius<by+706)return true;
        }
        return false;
    }
}
