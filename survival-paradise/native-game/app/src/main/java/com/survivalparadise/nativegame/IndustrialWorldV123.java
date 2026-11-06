package com.survivalparadise.nativegame;

/**
 * Deterministic, viewport-independent layout for the isolated V123 industrial
 * exploration test. Pure Java: no Android or drawing dependencies.
 * Future biome stitching can select this layout using biome identity + seed.
 */
public final class IndustrialWorldV123 {
    private IndustrialWorldV123() {}
    public static final int SECTOR = 1400;
    public static final int MINOR_ROAD = 168;
    public static final int ARTERIAL_ROAD = 270;
    public static final int INTERIOR_WIDTH = 3300;
    public static final int INTERIOR_HEIGHT = 2200;
    public static final int INTERIOR_ENTRANCE_X = INTERIOR_WIDTH / 2;
    public static final int INTERIOR_ENTRANCE_Y = INTERIOR_HEIGHT - 155;
    public static final int INTERIOR_EXIT_Y = INTERIOR_HEIGHT - 120;
    public static final int INTERACT_RADIUS = 105;
    public static final String SEED_PREF = "industrial_seed_v123";
    public static final String[] FACILITIES = {
        "STEEL ROLLING MILL", "ASSEMBLY FACTORY", "CASTING FOUNDRY",
        "LOGISTICS WAREHOUSE", "ELECTRICAL PLANT", "SCRAP RECYCLING",
        "MACHINE WORKS", "RAW MATERIAL DEPOT"
    };
    public static final String[] MATERIALS = {
        "IRON RODS", "STEEL PLATES", "COPPER WIRE", "MACHINE PARTS"
    };

    /** Reproducible 32-bit hash, including negative sector indices. */
    public static int hash(int x, int y, int seed) {
        int n = x * 374761393 ^ y * 668265263 ^ seed * -2048144777;
        n = (n ^ (n >>> 13)) * 1274126177;
        return n ^ (n >>> 16);
    }
    public static int sector(float coordinate) {
        return (int) Math.floor((double) coordinate / SECTOR);
    }
    public static int roadWidth(int boundarySector) {
        return Math.floorMod(boundarySector, 4) == 0 ? ARTERIAL_ROAD : MINOR_ROAD;
    }
    public static boolean roadAt(float x, float y) {
        int sx = Math.round(x / SECTOR), sy = Math.round(y / SECTOR);
        float bx = sx * (float) SECTOR, by = sy * (float) SECTOR;
        return Math.abs(x - bx) <= roadWidth(sx) * .5f
            || Math.abs(y - by) <= roadWidth(sy) * .5f;
    }
    public static final class District {
        public final int sx,sy,seed,kind;
        public final float x,y,doorX,doorY,buildingX,buildingY;
        public final String name,id;
        private District(int sx,int sy,int seed) {
            this.sx=sx;this.sy=sy;this.seed=seed;
            x=sx*(float)SECTOR;y=sy*(float)SECTOR;
            kind=IndustrialOpenWorldV124.family(sx,sy,seed);
            name=FACILITIES[kind];id=sx+","+sy;
            buildingX=x+245f;buildingY=y+225f;
            doorX=x+700f;doorY=y+810f;
        }
        public float materialX(int i) {
            switch(i){case 0:return x+315;case 1:return x+290;
                case 2:return x+1110;case 3:return x+1140;
                default:throw new IllegalArgumentException("material index");}
        }
        public float materialY(int i) {
            switch(i){case 0:return y+950;case 1:return y+1110;
                case 2:return y+1035;case 3:return y+1150;
                default:throw new IllegalArgumentException("material index");}
        }
        public String lootKey(int slot,boolean interior) {
            return seed+":"+id+":"+(interior?"indoor":"yard")+":"+slot;
        }
        public int materialQuantity(int slot) {
            if(slot<0||slot>=MATERIALS.length)throw new IllegalArgumentException("slot");
            return 2+Math.floorMod(hash(sx+3+slot,sy+7-slot,seed),5);
        }
    }
    public static District district(int sx,int sy,int seed) {
        return new District(sx,sy,seed);
    }
    public static District at(float wx,float wy,int seed) {
        return district(sector(wx),sector(wy),seed);
    }
    public static District nearestEntrance(float wx,float wy,float reach,int seed) {
        District best=null;float max=reach*reach;
        int ix=sector(wx),iy=sector(wy);
        for(int sy=iy-1;sy<=iy+1;sy++)for(int sx=ix-1;sx<=ix+1;sx++){
            District d=district(sx,sy,seed);
            float dx=wx-d.doorX,dy=wy-d.doorY,ds=dx*dx+dy*dy;
            if(ds<=max){max=ds;best=d;}
        }
        return best;
    }
    /** Sparse serialization keys include seed so industrial worlds never share loot. */
    public static String saveNamespace(int seed) {
        return "sp_industrial_v123_"+seed;
    }
}
