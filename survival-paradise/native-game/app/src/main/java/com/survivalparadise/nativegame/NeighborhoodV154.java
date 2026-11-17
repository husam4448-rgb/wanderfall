package com.survivalparadise.nativegame;

/**
 * V154 inhabited-world streets, not endless identical isolated rooms.
 * Deterministic six-lot districts. Each developed lot is a real 1100-1450
 * world-unit-wide building with its own facade, roof, and physical footprint.
 * Static geometry uses no saved identifiers: V153 site IDs, old save records,
 * camp, industrial plots, roads, and character art are never modified.
 */
public final class NeighborhoodV154 {
    private NeighborhoodV154(){}
    // Prevent allocating dozens of building/site-bound objects on every
    // NPC movement/collision tick. The bounded cache is derived entirely
    // from static world coordinates and is safe to rebuild at any time.
    private static final java.util.LinkedHashMap<Long,Building[]> CACHE=
        new java.util.LinkedHashMap<Long,Building[]>(128,.75f,true){
            @Override protected boolean removeEldestEntry(
                java.util.Map.Entry<Long,Building[]> e){return size()>144;}
        };
    public static final int TILE_W=5400, TILE_H=4400;
    public static final int COLS=3, ROWS=2;
    public static final int TYPES=8;
    public static final int APARTMENTS=0, OFFICES=1, MARKET=2, HOTEL=3,
        SCHOOL=4, FACTORY=5, WAREHOUSE=6, RESIDENCES=7;
    public static final String[] LABELS={
        "APARTMENTS","OFFICE BLOCK","SUPERMARKET","HOTEL","SCHOOL",
        "INDUSTRIAL HALL","DISTRIBUTION DEPOT","ROW HOUSES"
    };
    public static final class Building {
        public final int tileX,tileY,slot,kind,variation;
        public final float left,top,width,height,doorX,doorY;
        private Building(int tx,int ty,int slot,int kind,int variation,
                         float left,float top,float width,float height,float doorX,float doorY){
            this.tileX=tx;this.tileY=ty;this.slot=slot;this.kind=kind;
            this.variation=variation;this.left=left;this.top=top;
            this.width=width;this.height=height;
            this.doorX=doorX;this.doorY=doorY;
        }
        public float right(){return left+width;}
        /** Bottom of visible solid facade, not its walkable exterior steps. */
        public float bottom(){return top+height;}
        public boolean overlaps(float l,float t,float r,float b,float margin){
            return left<r+margin&&right()>l-margin&&
                   top<b+margin&&bottom()>t-margin;
        }
        public boolean blocked(float x,float y,float radius){
            return x+radius>left&&x-radius<right()&&
                y+radius>top&&y-radius<bottom();
        }
        public boolean onScreen(float x,float y,float w,float h){
            return overlaps(x,y,x+w,y+h,70f);
        }
    }
    public interface Visitor { void visit(Building building); }
    public static int tileX(float x){return (int)Math.floor((double)x/TILE_W);}
    public static int tileY(float y){return (int)Math.floor((double)y/TILE_H);}
    private static int hash(int x,int y,int salt){
        int n=x*0x45d9f3b^y*0x119de1f3^salt*0x27d4eb2d^0x154B317;
        n^=n>>>16;n*=0x7feb352d;n^=n>>>15;n*=0x846ca68b;
        return n^(n>>>16);
    }
    public static boolean district(int tx,int ty){
        // Compact groups are frequent; some parcels remain green/open,
        // instead of repeating an unnatural chessboard of identical blocks.
        return Math.floorMod(hash(tx,ty,17),100)<88;
    }
    public static Building candidate(int tx,int ty,int slot){
        if(slot<0||slot>=COLS*ROWS||!district(tx,ty))return null;
        int column=slot%COLS,row=slot/COLS;
        int n=hash(tx,ty,slot+100),v=hash(tx,ty,slot+401);
        // Mixed density creates incomplete streets, but most districts feel
        // populated. Landmark and highway exclusions are checked separately.
        if(Math.floorMod(n,100)<13)return null;
        int kind=Math.floorMod(n>>>3,TYPES);
        int variation=Math.floorMod(v>>>9,12);
        float w=1100f+Math.floorMod(v>>>3,8)*45f;
        float h=1000f+Math.floorMod(n>>>12,8)*45f;
        float x=tx*(float)TILE_W+850f+column*1800f+
            (Math.floorMod(v>>>18,5)-2)*12f;
        float doorY=ty*(float)TILE_H+(row==0?1640f:3860f)+
            (Math.floorMod(n>>>20,5)-2)*13f;
        return new Building(tx,ty,slot,kind,variation,
            x-w*.5f,doorY-h-28f,w,h,x,doorY);
    }
    private static boolean intersects(float l,float t,float r,float b,
                                      float ll,float tt,float rr,float bb,float m){
        return l<rr+m&&r>ll-m&&t<bb+m&&b>tt-m;
    }
    public static boolean safe(Building b){
        if(b==null)return false;
        float l=b.left,t=b.top,r=b.right(),bt=b.bottom()+150f;
        // Historic through-highways and their shoulders must remain open.
        if(intersects(l,t,r,bt,-1000000f,855f,1000000f,1220f,75f)||
           intersects(l,t,r,bt,1420f,-1000000f,1800f,1000000f,75f)||
           intersects(l,t,r,bt,535f,175f,1630f,1245f,155f))
            return false;
        // Do not paint through the stitched east industrial sector boundary.
        if(intersects(l,t,r,bt,5450f,-6900f,1000000f,9400f,0f))
            return false;
        for(ExpeditionSitesV88.Site s:ExpeditionSitesV88.SITES){
            float[] foot=ExteriorFootprintV130.bounds(s);
            if(intersects(l,t,r,bt,foot[0],foot[1],foot[2],foot[3],185f))
                return false;
        }
        return true;
    }
    private static long key(int tx,int ty){
        return (((long)tx)<<32)^(ty&0xffffffffL);
    }
    private static synchronized Building[] cell(int tx,int ty){
        long key=key(tx,ty);
        Building[] cached=CACHE.get(key);
        if(cached!=null)return cached;
        Building[] result=new Building[COLS*ROWS];
        for(int slot=0;slot<result.length;slot++){
            Building b=candidate(tx,ty,slot);
            if(safe(b))result[slot]=b;
        }
        CACHE.put(key,result);
        return result;
    }
    /**
     * V160 seeded districts retain all old plot/camp/road exclusions and
     * building-count save identities, but each surviving building can receive
     * a distinct type, size, and position. V159 saved towns use cell() above
     * and are never shifted.
     */
    private static int seededCacheSeed=Integer.MIN_VALUE;
    private static final java.util.LinkedHashMap<Long,Building[]> SEEDED_CACHE=
        new java.util.LinkedHashMap<Long,Building[]>(128,.75f,true){
            @Override protected boolean removeEldestEntry(
                java.util.Map.Entry<Long,Building[]> e){return size()>144;}
        };
    private static synchronized Building[] seededCell(int tx,int ty,
                                                      WorldCivilizationV159.Plan plan){
        if(plan==null||!plan.variedBuildingsV160)return cell(tx,ty);
        if(seededCacheSeed!=plan.seed){
            SEEDED_CACHE.clear();
            seededCacheSeed=plan.seed;
        }
        long key=key(tx,ty);
        Building[] cached=SEEDED_CACHE.get(key);
        if(cached!=null)return cached;
        Building[] originals=cell(tx,ty);
        Building[] updated=new Building[originals.length];
        WorldCivilizationV159.Parcel parcel=plan.atTile(tx,ty);
        for(int slot=0;slot<originals.length;slot++){
            Building old=originals[slot];
            if(old==null)continue;
            int h=IndustrialWorldV123.hash(tx*53+slot*11,
                ty*59-slot*7,plan.seed^0x160B17);
            int type=Math.floorMod(old.kind+Math.floorMod(h>>>15,TYPES),TYPES);
            int variation=Math.floorMod(old.variation+
                Math.floorMod(h>>>19,12),12);
            float cx=old.left+old.width*.5f+
                Math.floorMod(h,281)-140f;
            float top=old.top+Math.floorMod(h>>>8,171)-85f;
            float width=old.width*(.91f+Math.floorMod(h>>>22,9)*.017f);
            float height=old.height*(.90f+Math.floorMod(h>>>25,9)*.020f);
            Building proposed=new Building(tx,ty,slot,type,variation,
                cx-width*.5f,top,width,height,cx,top+height+28f);
            // Never cross real plot fences, established sites or highways.
            // Preserve a known-safe original footprint when a randomized
            // position is geometrically unsuitable.
            if(parcel!=null&&
               parcel.inside(proposed.left,proposed.top,35f)&&
               parcel.inside(proposed.right(),proposed.bottom()+60f,35f)&&
               safe(proposed))
                updated[slot]=proposed;
            else
                updated[slot]=new Building(tx,ty,slot,type,variation,
                    old.left,old.top,old.width,old.height,old.doorX,old.doorY);
        }
        SEEDED_CACHE.put(key,updated);
        return updated;
    }
    private static Building[] cell(int tx,int ty,WorldCivilizationV159.Plan plan){
        return plan!=null&&plan.variedBuildingsV160?
            seededCell(tx,ty,plan):cell(tx,ty);
    }
    public static Building get(int tx,int ty,int slot){
        return slot<0||slot>=COLS*ROWS?null:cell(tx,ty)[slot];
    }
    public static Building get(int tx,int ty,int slot,
                               WorldCivilizationV159.Plan plan){
        return slot<0||slot>=COLS*ROWS?null:cell(tx,ty,plan)[slot];
    }
    /** Broadphase limits all rendering to viewport tiles, not the whole world. */
    public static void visible(float x,float y,float width,float height,Visitor draw){
        visible(x,y,width,height,null,draw);
    }
    public static void visible(float x,float y,float width,float height,
                               WorldCivilizationV159.Plan plan,Visitor draw){
        int x0=tileX(x-170f),x1=tileX(x+width+170f);
        int y0=tileY(y-170f),y1=tileY(y+height+170f);
        for(int ty=y0;ty<=y1;ty++)for(int tx=x0;tx<=x1;tx++){
            if(plan!=null&&plan.atTile(tx,ty)==null)continue;
            Building[] buildings=cell(tx,ty,plan);
            for(int slot=0;slot<COLS*ROWS;slot++){
                Building b=buildings[slot];
                if(b!=null&&b.onScreen(x,y,width,height))draw.visit(b);
            }
        }
    }
    public static boolean blocked(float x,float y,float radius){
        return blocked(x,y,radius,null);
    }
    public static boolean blocked(float x,float y,float radius,
                                  WorldCivilizationV159.Plan plan){
        if(!Float.isFinite(x)||!Float.isFinite(y))return false;
        int tx=tileX(x),ty=tileY(y);
        for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){
            if(plan!=null&&plan.atTile(tx+dx,ty+dy)==null)continue;
            Building[] buildings=cell(tx+dx,ty+dy,plan);
            for(int slot=0;slot<COLS*ROWS;slot++){
                Building b=buildings[slot];
                if(b!=null&&b.blocked(x,y,radius))return true;
            }
        }
        return false;
    }
    /**
     * Old V153 saves may load with the player inside a newly populated city
     * block. Relocate to the nearest actual outside wall, not a new spawn,
     * without changing coordinates or the save schema of other actors.
     */
    public static float[] clearSavedPosition(float x,float y){
        return clearSavedPosition(x,y,null);
    }
    public static float[] clearSavedPosition(float x,float y,
                                              WorldCivilizationV159.Plan plan){
        if(!blocked(x,y,24f,plan))return new float[]{x,y};
        float best=Float.POSITIVE_INFINITY,px=x,py=y;
        int tx=tileX(x),ty=tileY(y);
        for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){
            if(plan!=null&&plan.atTile(tx+dx,ty+dy)==null)continue;
            for(Building b:cell(tx+dx,ty+dy,plan)){
                if(b==null||!b.blocked(x,y,24f))continue;
                float[][] possibilities={
                    {b.left-82f,y},{b.right()+82f,y},
                    {x,b.top-82f},{x,b.bottom()+82f}
                };
                for(float[] point:possibilities){
                    float xx=point[0],yy=point[1];
                    if(blocked(xx,yy,24f,plan))continue;
                    float d=(xx-x)*(xx-x)+(yy-y)*(yy-y);
                    if(d<best){best=d;px=xx;py=yy;}
                }
            }
        }
        return new float[]{px,py};
    }
    /** Dynamic broadphase, accurate for all projectile and NPC ray paths. */
    public static float firstImpact(float x0,float y0,float x1,float y1){
        return firstImpact(x0,y0,x1,y1,null);
    }
    public static float firstImpact(float x0,float y0,float x1,float y1,
                                    WorldCivilizationV159.Plan plan){
        float hit=Float.POSITIVE_INFINITY;
        int tx0=tileX(Math.min(x0,x1)-2),tx1=tileX(Math.max(x0,x1)+2);
        int ty0=tileY(Math.min(y0,y1)-2),ty1=tileY(Math.max(y0,y1)+2);
        // A pathological ray must not scan infinitely many procedural lots.
        if(tx1-tx0>16||ty1-ty0>16)return hit;
        for(int ty=ty0;ty<=ty1;ty++)for(int tx=tx0;tx<=tx1;tx++){
            if(plan!=null&&plan.atTile(tx,ty)==null)continue;
            Building[] buildings=cell(tx,ty,plan);
            for(int slot=0;slot<COLS*ROWS;slot++){
                Building b=buildings[slot];
                if(b==null||!b.overlaps(Math.min(x0,x1),Math.min(y0,y1),
                    Math.max(x0,x1),Math.max(y0,y1),3f))continue;
                float t=Ballistics.segmentBox(x0,y0,x1,y1,
                    b.left,b.top,b.right(),b.bottom());
                if(t<hit)hit=t;
            }
        }
        return hit;
    }
}
