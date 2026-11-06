package com.survivalparadise.nativegame;
/** Stable authored site IDs with V130 road-safe, camp-clear full-scale layouts. Existing site-indexed loot and interiors remain stable. */
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
      new Site(CABIN,-150,-250,"RANGER CABIN",true),
      new Site(CLINIC,2080,680,"FIELD CLINIC",true),
      new Site(GARAGE,2580,1550,"RUSTED GARAGE",true),
      new Site(RELAY,2890,390,"SIGNAL RELAY",true),
      new Site(DEPOT,350,2150,"SUPPLY DEPOT",true),
      new Site(TOWER,-220,380,"LOOKOUT TOWER",true),
      new Site(FARM,2050,2440,"ABANDONED FARM",true),
      new Site(CHECKPOINT,3520,830,"ROAD CHECKPOINT",true),
      new Site(MOTEL,2170,-410,"DESERT MOTEL",true),
      new Site(WORKSHOP,-850,1470,"FIELD WORKSHOP",true),
      new Site(CABIN,-1570,510,"FORESTER HUT",true),
      new Site(DEPOT,4240,1600,"FREIGHT STOREHOUSE",true),
      new Site(CHECKPOINT,-1880,-730,"BORDER OUTPOST",true),
      new Site(FARM,3270,2720,"ORCHARD FARMSTEAD",true),
      new Site(MOTEL,4800,-920,"ROADSIDE INN",true),
      new Site(GARAGE,-2450,1880,"MOTOR POOL",true),
      new Site(WORKSHOP,3680,-1800,"METALWORKS",true),
      new Site(RELAY,-940,-1700,"RADIO SUBSTATION",true),
      new Site(TOWER,1980,3350,"FOREST WATCH POST",true),
      new Site(CABIN,-3300,480,"HUNTER'S SHELTER",true),
      new Site(DEPOT,5190,280,"MILITARY SUPPLIES",true),
      new Site(FARM,-1710,3230,"RIVERSIDE FARM",true),
      // Originally non-enterable fixed buildings; now independent full interiors.
      new Site(DEPOT,500,-450,"ADMINISTRATION BLOCK",true),
      new Site(MOTEL,1110,-700,"COMMUNITY STORE",true),
      new Site(WORKSHOP,3000,1950,"WAREHOUSE ANNEX",true),
      new Site(FARM,650,3000,"DERELICT BARN",true)
    };
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
