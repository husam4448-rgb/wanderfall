package com.survivalparadise.nativegame;
/** Authored landmarks in original continuous world coords; no chunk generation side effects. */
public final class ExpeditionSitesV88 {
    private ExpeditionSitesV88(){}
    public static final int CABIN=0,CLINIC=1,GARAGE=2,RELAY=3,DEPOT=4,
        TOWER=5,FARM=6,CHECKPOINT=7,MOTEL=8,WORKSHOP=9;
    public static final class Site {
        public final int kind;public final float x,y;
        public final String name;
        public final boolean supplies;
        Site(int kind,float x,float y,String name,boolean supplies){
            this.kind=kind;this.x=x;this.y=y;this.name=name;this.supplies=supplies;
        }
    }
    public static final Site[] SITES={
      new Site(CABIN,480,605,"RANGER CABIN",true),
      new Site(CLINIC,2080,680,"FIELD CLINIC",true),
      new Site(GARAGE,2580,1410,"RUSTED GARAGE",true),
      new Site(RELAY,2890,390,"SIGNAL RELAY",true),
      new Site(DEPOT,760,1530,"SUPPLY DEPOT",true),
      new Site(TOWER,-220,380,"LOOKOUT TOWER",true),
      new Site(FARM,1240,1900,"ABANDONED FARM",true),
      new Site(CHECKPOINT,3520,830,"ROAD CHECKPOINT",true),
      new Site(MOTEL,2170,-410,"DESERT MOTEL",true),
      new Site(WORKSHOP,-850,1470,"FIELD WORKSHOP",true),
      new Site(CABIN,-1570,510,"FORESTER HUT",true),
      new Site(DEPOT,4240,1420,"FREIGHT STOREHOUSE",true),
      new Site(CHECKPOINT,-1880,-730,"BORDER OUTPOST",true),
      new Site(FARM,3270,2720,"ORCHARD FARMSTEAD",true),
      new Site(MOTEL,4800,-920,"ROADSIDE INN",true),
      new Site(GARAGE,-2450,1880,"MOTOR POOL",true),
      new Site(WORKSHOP,3680,-1800,"METALWORKS",true),
      new Site(RELAY,-940,-1700,"RADIO SUBSTATION",true),
      new Site(TOWER,1630,3050,"FOREST WATCH POST",true),
      new Site(CABIN,-3300,480,"HUNTER'S SHELTER",true),
      new Site(DEPOT,5530,660,"MILITARY SUPPLIES",true),
      new Site(FARM,-1710,3230,"RIVERSIDE FARM",true),
      // Originally non-enterable fixed buildings; now independent full interiors.
      new Site(DEPOT,475,327,"ADMINISTRATION BLOCK",true),
      new Site(MOTEL,1810,393,"COMMUNITY STORE",true),
      new Site(WORKSHOP,2380,1240,"WAREHOUSE ANNEX",true),
      new Site(FARM,894,1770,"DERELICT BARN",true)
    };
    // V153: The original 26 centers were placed only a few hundred pixels
    // apart, which cannot contain 2720x1904 interiors at comparable scale.
    // Reserve full-size plots, using the original coordinates as preferred
    // bearings. Preserve original array order/site IDs, storage/actor keys,
    // supplied items and the player's existing saved world coordinates.
    static {
        Site[] requested=SITES.clone();
        Site[] allocated=new Site[SITES.length];
        // Give the unique clinic its own physical campus first.
        allocated[1]=allocate(requested[1],allocated);
        for(int i=0;i<requested.length;i++){
            if(i==1)continue;
            allocated[i]=allocate(requested[i],allocated);
        }
        System.arraycopy(allocated,0,SITES,0,SITES.length);
    }
    private static boolean intersects(float[] a,float l,float t,float r,
                                      float b,float gap){
        return a[0]<r+gap&&a[2]>l-gap&&
               a[1]<b+gap&&a[3]>t-gap;
    }
    private static boolean clearBuilding(Site candidate,Site[] allocated){
        float[] b=ExteriorFootprintV130.roofBounds(candidate);
        // Preserve the two old physical highways, camp and the stitched
        // industrial biome. No giant building may block a through-road.
        if(intersects(b,1430f,-1000000f,1790f,1000000f,60f)||
           intersects(b,-1000000f,863f,1000000f,1210f,60f)||
           intersects(b,640f,270f,1520f,1190f,130f)||
           intersects(b,5500f,-6400f,1000000f,9000f,0f))
            return false;
        for(Site s:allocated){
            if(s==null)continue;
            float[] other=ExteriorFootprintV130.roofBounds(s);
            if(intersects(b,other[0],other[1],other[2],other[3],
                ExteriorFootprintV130.ROAD_CLEARANCE))return false;
        }
        return true;
    }
    private static Site allocate(Site old,Site[] allocated){
        final int STEP=300;
        for(int ring=0;ring<=90;ring++){
            Site best=null;
            int score=Integer.MAX_VALUE,side=Integer.MAX_VALUE;
            // Scan the entire distance ring so results are deterministic
            // and retain the old landmark's relative direction when possible.
            for(int dy=-ring;dy<=ring;dy++)for(int dx=-ring;dx<=ring;dx++){
                if(Math.max(Math.abs(dx),Math.abs(dy))!=ring)continue;
                Site candidate=new Site(old.kind,old.x+dx*STEP,
                    old.y+dy*STEP,old.name,old.supplies);
                if(!clearBuilding(candidate,allocated))continue;
                int distance=dx*dx+dy*dy;
                int preference=Math.abs(dy)*2+Math.abs(dx);
                if(best==null||distance<score||
                   (distance==score&&preference<side)){
                    best=candidate;score=distance;side=preference;
                }
            }
            if(best!=null)return best;
        }
        throw new IllegalStateException("No safe full-size site plot for "+old.name);
    }
    public static Site nearest(float x,float y,float reach){
        Site best=null;float dmin=reach*reach;
        for(Site s:SITES){
            float dx=x-s.x,dy=y-s.y,d=dx*dx+dy*dy;
            if(d<dmin){dmin=d;best=s;}
        }
        return best;
    }
    public static int[] supplies(int index){
        if(index<0||index>=SITES.length)return new int[8];
        int[] inventory=new int[8];int kind=SITES[index].kind;
        inventory[0]=kind==GARAGE||kind==DEPOT||kind==WORKSHOP?6:2;
        inventory[1]=kind==CLINIC?3:kind==MOTEL?1:0;
        inventory[2]=kind==CHECKPOINT||kind==TOWER||kind==RELAY?4:1;
        inventory[3]=kind==FARM?5:kind==CABIN?2:1;
        inventory[4]=kind==MOTEL||kind==CABIN||kind==FARM?3:1;
        inventory[5]=kind==CABIN||kind==WORKSHOP?4:0;
        inventory[6]=kind==GARAGE||kind==DEPOT?3:0;
        inventory[7]=kind==FARM||kind==RELAY?2:0;
        return inventory;
    }
}
