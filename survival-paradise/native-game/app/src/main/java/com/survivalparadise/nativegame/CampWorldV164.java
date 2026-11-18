package com.survivalparadise.nativegame;

import java.util.ArrayList;

/**
 * V164 persistent-by-seed, build-free survivor settlements.
 * Camps are primarily in genuine wilderness tiles. The rare urban camp
 * can occupy only a fully unbuilt plot, surrounded by green space, not a
 * building lot. Never modifies the V160 city blueprint or existing site IDs.
 */
public final class CampWorldV164 {
    private CampWorldV164(){}
    public static final float RADIUS_X=480f,RADIUS_Y=345f;
    public static final int ROLES=5,TRADER=0,MEDIC=1,GUARD=2,
        MECHANIC=3,SURVIVOR=4;
    public static final class Site {
        public final String id;
        public final float x,y;
        public final int variation,seed,tx,ty,slot;
        public final boolean urban,starter;
        public Site(String id,float x,float y,int variant,int seed,
                    int tx,int ty,int slot,boolean urban,boolean starter){
            this.id=id;this.x=x;this.y=y;this.variation=variant;
            this.seed=seed;this.tx=tx;this.ty=ty;this.slot=slot;
            this.urban=urban;this.starter=starter;
        }
        /** Each role has a real station; no camp roles are assigned randomly. */
        public float npcX(int role){
            float[] dx={-248,157,66,-112,12};
            return x+dx[Math.max(0,Math.min(role,ROLES-1))];
        }
        public float npcY(int role){
            float[] dy={214,222,280,183,-38};
            return y+dy[Math.max(0,Math.min(role,ROLES-1))];
        }
        public float chestX(){return x+(starter?335f:342f);}
        public float chestY(){return y+(starter?155f:125f);}
        public float fireX(){return x+(starter?90f:20f);}
        public float fireY(){return y+(starter?95f:70f);}
        public String saveId(){return "c"+seed+"_"+tx+"_"+ty+"_"+slot;}
    }
    private static int hash(int x,int y,int seed){
        return IndustrialWorldV123.hash(x*113+9,y*79-17,seed^0x164CA7);
    }
    private static boolean detached(float x,float y,ArrayList<Site> sites){
        for(Site s:sites){
            float dx=x-s.x,dy=y-s.y;
            if(dx*dx+dy*dy<1880f*1880f)return false;
        }
        return true;
    }
    private static boolean intersectsRoad(float x,float y,float margin){
        return Math.abs(y-1036f)<margin+128f||
            Math.abs(x-1605f)<margin+129f;
    }
    private static boolean safe(float x,float y,int seed,
                                WorldCivilizationV159.Plan city,
                                ArrayList<Site> sites){
        if(!detached(x,y,sites)||intersectsRoad(x,y,560f)||
           IndustrialBiomeBridgeV128.bounds(x,y))return false;
        if(city!=null&&city.blocked(x,y,460f))return false;
        // Test the complete footprint and all real buildings, not just the
        // center; a tent must not protrude into streets or factory roofs.
        if(WorldBuildingV157.sceneryBlocked(x,y,410f,seed,city))return false;
        for(float dx:new float[]{-345f,345f})
            for(float dy:new float[]{-235f,235f})
                if(WorldBuildingV157.sceneryBlocked(x+dx,y+dy,95f,seed,city))
                    return false;
        // Industrial roads are world coordinates, including non-core stripes.
        if(IndustrialBiomeBridgeV128.bounds(x-RADIUS_X,y-RADIUS_Y)||
           IndustrialBiomeBridgeV128.bounds(x+RADIUS_X,y+RADIUS_Y))
            return false;
        return true;
    }
    public static Site[] generate(int seed,WorldCivilizationV159.Plan city){
        ArrayList<Site> sites=new ArrayList<>();
        // Keep the original starter NPC coordinates and trade identities.
        sites.add(new Site("original_camp",1080f,710f,
            0,seed,0,0,-1,false,true));
        if(city==null)return sites.toArray(new Site[0]);
        // Rural sites take priority, and are excluded from ALL developed
        // parcels, including industrial compounds and the original camp.
        for(int ty=WorldCivilizationV159.MIN_TY-1;
                ty<=WorldCivilizationV159.MAX_TY+1;ty++){
            for(int tx=WorldCivilizationV159.MIN_TX-1;
                    tx<=WorldCivilizationV159.MAX_TX+1;tx++){
                if(city.atTile(tx,ty)!=null)continue;
                int h=hash(tx,ty,seed);
                if(Math.floorMod(h,100)>=19)continue;
                float x=tx*(float)NeighborhoodV154.TILE_W+2490f+
                    Math.floorMod(h>>>8,801)-400f;
                float y=ty*(float)NeighborhoodV154.TILE_H+2140f+
                    Math.floorMod(h>>>17,581)-290f;
                if(!safe(x,y,seed,city,sites))continue;
                sites.add(new Site("wilderness_"+tx+"_"+ty,
                    x,y,Math.floorMod(h>>>22,8),seed,tx,ty,-1,false,false));
            }
        }
        // A small number of urban camps may occupy only physically vacant
        // housing blocks. Unbuilt public greens are painted separately.
        for(WorldCivilizationV159.Parcel parcel:city.parcels){
            int hash=hash(parcel.tx,parcel.ty,seed^0x471);
            if(Math.floorMod(hash,100)>=38)continue;
            for(int i=0;i<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;i++){
                int slot=Math.floorMod(i+hash,NeighborhoodV154.COLS*NeighborhoodV154.ROWS);
                if(NeighborhoodV154.get(parcel.tx,parcel.ty,slot,city)!=null)
                    continue; // never take an existing building lot
                int col=slot%NeighborhoodV154.COLS,row=slot/NeighborhoodV154.COLS;
                float x=parcel.tx*(float)NeighborhoodV154.TILE_W+850f+col*1800f;
                float y=parcel.ty*(float)NeighborhoodV154.TILE_H+
                    (row==0?1140f:3360f);
                if(!parcel.inside(x,y,550f)||
                   !safe(x,y,seed,city,sites))continue;
                sites.add(new Site("city_green_"+parcel.tx+"_"+parcel.ty+"_"+slot,
                    x,y,Math.floorMod(hash+slot*7,8),seed,
                    parcel.tx,parcel.ty,slot,true,false));
                break;
            }
        }
        return sites.toArray(new Site[0]);
    }
    public static Site nearbyChest(Site[] sites,float px,float py,float reach){
        if(sites==null)return null;
        float closest=reach*reach;
        Site found=null;
        for(Site site:sites){
            float dx=px-site.chestX(),dy=py-site.chestY(),dist=dx*dx+dy*dy;
            if(dist<closest){closest=dist;found=site;}
        }
        return found;
    }
    public static boolean visible(Site s,float camX,float camY,float w,float h){
        return s.x+RADIUS_X>=camX-90&&s.x-RADIUS_X<=camX+w+90&&
            s.y+RADIUS_Y>=camY-90&&s.y-RADIUS_Y<=camY+h+90;
    }
}
