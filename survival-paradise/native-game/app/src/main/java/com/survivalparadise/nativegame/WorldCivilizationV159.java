package com.survivalparadise.nativegame;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Locale;
import java.util.zip.CRC32;

/**
 * Seed-specific, immutable and save-persisted civilization layout. Never
 * relocates existing V88 landmarks, V124 facilities or V154 building tiles.
 * This first generator version lays out real enclosed neighborhood parcels,
 * gates connected to authored streets, surface materials, and perimeter
 * geometry. Unbounded natural terrain remains chunk-streamed, not eagerly
 * allocated. Earlier V158 saves without this record retain their old layout.
 */
public final class WorldCivilizationV159 {
    private WorldCivilizationV159(){}
    public static final int VERSION=159;
    public static final int CITY=0, VILLAGE=1, OUTPOST=2;
    public static final int MIN_TX=-5,MAX_TX=8,MIN_TY=-5,MAX_TY=5;
    public static final float INSET_X=88f,INSET_TOP=90f,INSET_BOTTOM=64f;
    public static final float FENCE_RADIUS=10f;
    public interface Progress { void step(int percent,String stage); }
    public static final class Segment {
        public final float x1,y1,x2,y2;
        public final int material,variation;
        Segment(float x1,float y1,float x2,float y2,int material,int variation){
            this.x1=x1;this.y1=y1;this.x2=x2;this.y2=y2;
            this.material=material;this.variation=variation;
        }
        public boolean vertical(){return x1==x2;}
        public boolean blocked(float x,float y,float radius){
            float r=FENCE_RADIUS+Math.max(0f,radius);
            if(vertical())return Math.abs(x-x1)<=r&&
                y>=Math.min(y1,y2)-r&&y<=Math.max(y1,y2)+r;
            return Math.abs(y-y1)<=r&&x>=Math.min(x1,x2)-r&&
                x<=Math.max(x1,x2)+r;
        }
    }
    public static final class Parcel {
        public final int tx,ty,kind,variation,buildings;
        public final float left,top,right,bottom;
        public final Segment[] fences;
        private Parcel(int tx,int ty,int kind,int variation,int buildings){
            this.tx=tx;this.ty=ty;this.kind=kind;this.variation=variation;
            this.buildings=buildings;
            left=tx*(float)NeighborhoodV154.TILE_W+INSET_X;
            right=(tx+1f)*NeighborhoodV154.TILE_W-INSET_X;
            top=ty*(float)NeighborhoodV154.TILE_H+INSET_TOP;
            bottom=(ty+1f)*NeighborhoodV154.TILE_H-INSET_BOTTOM;
            fences=buildFences(this);
        }
        public boolean inside(float x,float y,float margin){
            return x>=left-margin&&x<=right+margin&&
                y>=top-margin&&y<=bottom+margin;
        }
        public boolean onScreen(float x,float y,float width,float height){
            return left<x+width+120f&&right>x-120f&&
                   top<y+height+120f&&bottom>y-120f;
        }
    }
    public static final class Plan {
        public final int seed;
        public final Parcel[] parcels;
        private final HashMap<Long,Parcel> byTile;
        private Plan(int seed,ArrayList<Parcel> list){
            this.seed=seed;
            parcels=list.toArray(new Parcel[0]);
            byTile=new HashMap<>(parcels.length*2+1);
            for(Parcel p:parcels)byTile.put(key(p.tx,p.ty),p);
        }
        public Parcel atTile(int tx,int ty){return byTile.get(key(tx,ty));}
        public Parcel at(float x,float y){
            return atTile(NeighborhoodV154.tileX(x),
                          NeighborhoodV154.tileY(y));
        }
        /** Actual developed lawn, yard and road surface, not the wilderness. */
        public boolean developed(float x,float y){
            Parcel p=at(x,y);
            return p!=null&&p.inside(x,y,0f);
        }
        /** Front and side fences have exact, shared rendering/collision bounds. */
        public boolean blocked(float x,float y,float radius){
            if(!Float.isFinite(x)||!Float.isFinite(y))return false;
            int tx=NeighborhoodV154.tileX(x),ty=NeighborhoodV154.tileY(y);
            for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){
                Parcel p=atTile(tx+dx,ty+dy);
                if(p==null||!p.inside(x,y,Math.max(20f,radius)+25f))continue;
                for(Segment f:p.fences)if(f.blocked(x,y,radius))return true;
            }
            return false;
        }
        public String encode(){
            StringBuilder b=new StringBuilder(32+parcels.length*17);
            b.append(VERSION).append('|').append(seed).append('|')
                .append(parcels.length).append('|');
            for(int i=0;i<parcels.length;i++){
                Parcel p=parcels[i];
                if(i>0)b.append(';');
                b.append(p.tx).append(',').append(p.ty).append(',')
                    .append(p.kind).append(',').append(p.variation)
                    .append(',').append(p.buildings);
            }
            String raw=b.toString();
            CRC32 crc=new CRC32();
            crc.update(raw.getBytes(StandardCharsets.UTF_8));
            return raw+'|'+Long.toHexString(crc.getValue());
        }
    }
    private static long key(int x,int y){
        return (((long)x)<<32)^(y&0xffffffffL);
    }
    private static int hash(int seed,int x,int y,int salt){
        return IndustrialWorldV123.hash(x*3+salt,y*5-salt,seed^0x159B4A);
    }
    private static int buildings(int tx,int ty){
        int result=0;
        for(int i=0;i<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;i++)
            if(NeighborhoodV154.get(tx,ty,i)!=null)result++;
        return result;
    }
    /**
     * Main highway (y=1036) and old vertical route (x=1605) pass through
     * perimeter gates, as do authored city collector streets.
     */
    private static float[] openings(Parcel p,boolean vertical){
        float sx=p.tx*(float)NeighborhoodV154.TILE_W;
        float sy=p.ty*(float)NeighborhoodV154.TILE_H;
        float[] gates=vertical?
            new float[]{sy+2190f,sy+4250f,
                1036f>=p.top&&1036f<=p.bottom?1036f:Float.NaN}:
            new float[]{sx+1750f,sx+3550f,
                1605f>=p.left&&1605f<=p.right?1605f:Float.NaN};
        Arrays.sort(gates);
        return gates;
    }
    private static void segment(ArrayList<Segment> out,float start,float end,
                                float fixed,boolean vertical,
                                int material,int variation){
        if(end-start<32f)return;
        out.add(vertical?
            new Segment(fixed,start,fixed,end,material,variation):
            new Segment(start,fixed,end,fixed,material,variation));
    }
    private static void edge(ArrayList<Segment> out,float start,float end,
                             float fixed,boolean vertical,float[] gates,
                             int material,int variation){
        float cursor=start;
        // Gate centers are authored in ascending order for both directions.
        for(float center:gates){
            if(!Float.isFinite(center)||center<start-200f||center>end+200f)
                continue;
            float width=vertical?166f:177f;
            float from=Math.max(start,center-width);
            float to=Math.min(end,center+width);
            if(from>cursor)segment(out,cursor,from,fixed,vertical,material,variation);
            cursor=Math.max(cursor,to);
        }
        segment(out,cursor,end,fixed,vertical,material,variation);
    }
    private static Segment[] buildFences(Parcel p){
        ArrayList<Segment> output=new ArrayList<>(22);
        float[] horizontal=openings(p,false),vertical=openings(p,true);
        // Gate slots at (1750,3550) follow actual north/south streets.
        edge(output,p.left,p.right,p.top,false,horizontal,p.kind,p.variation);
        edge(output,p.left,p.right,p.bottom,false,horizontal,p.kind,p.variation);
        // The longitudinal road and the original east/west highway remain open.
        edge(output,p.top,p.bottom,p.left,true,vertical,p.kind,p.variation);
        edge(output,p.top,p.bottom,p.right,true,vertical,p.kind,p.variation);
        return output.toArray(new Segment[0]);
    }
    /**
     * Phase-by-phase planning runs off the Android UI thread. World placement
     * validations use existing V154 collision clearance and named-site IDs.
     * Only the compact blueprint is persisted; terrain chunks remain streamed.
     */
    public static Plan generate(int seed,Progress onProgress){
        if(onProgress!=null)onProgress.step(0,"SURVEYING EXISTING ROADS");
        // Pre-validate established sectors without changing any save keys.
        for(int sy=IndustrialBiomeBridgeV128.INDUSTRIAL_MIN_SY;
                sy<IndustrialBiomeBridgeV128.INDUSTRIAL_MAX_SY;sy++){
            for(int sx=IndustrialBiomeBridgeV128.INDUSTRIAL_MIN_SX;
                    sx<IndustrialBiomeBridgeV128.INDUSTRIAL_MAX_SX;sx++){
                IndustrialOpenWorldV124.Plot site=IndustrialOpenWorldV124.plot(sx,sy,seed);
                if(site.enterable()&&(site.doorX!=site.x+700f||
                   site.doorY!=site.y+810f))
                    throw new IllegalStateException("Industrial entrance drift");
            }
        }
        if(onProgress!=null)onProgress.step(22,"VALIDATING INDUSTRIAL COMPOUNDS");
        ArrayList<Parcel> layout=new ArrayList<>();
        int rows=MAX_TY-MIN_TY+1;
        for(int ty=MIN_TY;ty<=MAX_TY;ty++){
            for(int tx=MIN_TX;tx<=MAX_TX;tx++){
                // A seed chooses which 2x2 macro-districts become towns.
                // This varies the actual building map, not merely paint.
                // Natural tracts remain between connected built-up clusters.
                if(tx==0&&ty==0)continue;
                int cluster=hash(seed,Math.floorDiv(tx,2),
                                 Math.floorDiv(ty,2),73);
                if(Math.floorMod(cluster,100)>=76)continue;
                int count=buildings(tx,ty);
                if(count<1)continue;
                // Coherent style across a 2-by-2 district, not random styles
                // assigned separately to each building or fenced segment.
                int macro=hash(seed,Math.floorDiv(tx,2),Math.floorDiv(ty,2),5);
                int type=Math.floorMod(macro,10)<5?CITY:
                    Math.floorMod(macro,10)<8?VILLAGE:OUTPOST;
                int variation=Math.floorMod(hash(seed,tx,ty,23),6);
                layout.add(new Parcel(tx,ty,type,variation,count));
            }
            if(onProgress!=null)
                onProgress.step(22+(int)(52f*(ty-MIN_TY+1)/rows),
                    "LAYING OUT FENCED CITY AND VILLAGE PLOTS");
        }
        if(layout.isEmpty())throw new IllegalStateException("Empty world blueprint");
        Plan plan=new Plan(seed,layout);
        if(onProgress!=null)onProgress.step(84,"VERIFYING ROAD GATES AND FENCES");
        // Every highway crossing must remain traversable, even if a fence
        // happens to intersect the original world road at the parcel edge.
        for(Parcel p:plan.parcels){
            for(float x:openings(p,false))
                if(Float.isFinite(x)&&x>p.left+200f&&x<p.right-200f)
                    if(plan.blocked(x,p.top,20f)||plan.blocked(x,p.bottom,20f))
                        throw new IllegalStateException("Blocked north/south street");
            for(float y:openings(p,true))
                if(Float.isFinite(y)&&y>p.top+200f&&y<p.bottom-200f)
                    if(plan.blocked(p.left,y,20f)||plan.blocked(p.right,y,20f))
                        throw new IllegalStateException("Blocked arterial street");
        }
        if(onProgress!=null)onProgress.step(100,"WORLD BLUEPRINT VERIFIED");
        return plan;
    }
    /** Corrupt or foreign-version records never silently overwrite a save. */
    public static Plan decode(String encoded,int expectedSeed){
        if(encoded==null||encoded.isEmpty()||encoded.length()>32000)return null;
        try{
            int split=encoded.lastIndexOf('|');
            if(split<=0)return null;
            String body=encoded.substring(0,split);
            CRC32 check=new CRC32();
            check.update(body.getBytes(StandardCharsets.UTF_8));
            if(!Long.toHexString(check.getValue()).equals(encoded.substring(split+1)))
                return null;
            String[] fields=body.split("\\|",-1);
            if(fields.length!=4||Integer.parseInt(fields[0])!=VERSION||
               Integer.parseInt(fields[1])!=expectedSeed)return null;
            int count=Integer.parseInt(fields[2]);
            if(count<1||count>(MAX_TX-MIN_TX+1)*(MAX_TY-MIN_TY+1))return null;
            String[] rows=fields[3].split(";",-1);
            if(rows.length!=count)return null;
            ArrayList<Parcel> parcels=new ArrayList<>(count);
            HashMap<Long,Boolean> duplicates=new HashMap<>();
            for(String row:rows){
                String[] q=row.split(",",-1);
                if(q.length!=5)return null;
                int tx=Integer.parseInt(q[0]),ty=Integer.parseInt(q[1]),
                    type=Integer.parseInt(q[2]),variation=Integer.parseInt(q[3]),
                    buildings=Integer.parseInt(q[4]);
                if(tx<MIN_TX||tx>MAX_TX||ty<MIN_TY||ty>MAX_TY||
                   type<CITY||type>OUTPOST||variation<0||variation>=6||
                   buildings!=buildings(tx,ty)||buildings<1||
                   duplicates.put(key(tx,ty),true)!=null)return null;
                parcels.add(new Parcel(tx,ty,type,variation,buildings));
            }
            return new Plan(expectedSeed,parcels);
        }catch(RuntimeException invalid){return null;}
    }
}
