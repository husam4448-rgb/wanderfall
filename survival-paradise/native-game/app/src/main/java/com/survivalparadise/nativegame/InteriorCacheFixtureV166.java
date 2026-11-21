package com.survivalparadise.nativegame;

/**
 * Render 14 ORIGINAL saved, searchable loot caches as real, substantial
 * pieces of room-appropriate storage furniture. Indexed inventories, world
 * coordinates, item contents and save keys are unchanged.
 *
 * Deterministic art rectangles and physics share precisely the same geometry.
 * Flat crate icons are reserved for original legacy interiors, never V163.
 */
public final class InteriorCacheFixtureV166 {
    private InteriorCacheFixtureV166(){}
    private static final float S=ClinicInteriorV89.EXPANSION_V90;
    private static final int[][] STATION_SLOTS={
        {2,6,7,10}, // homes: cupboard, shelving, dresser, drawers
        {3,6,8,10}, // office: files, books, locker, dresser
        {0,2,3,6},  // market: merchandise, stock, cold unit, rack
        {6,7,9,8},  // hotel: wardrobe, bookcase, locker, housekeeping
        {2,8,9,11}, // school: bookshelf, cabinet, drawers, sink
        {2,7,9,8},  // factory: tools, supply pallets, lockers, trolley
        {0,1,4,5},  // warehouse: racks, freight, spare storage, lockers
        {5,8,6,11}  // residence: wardrobes, shelving, dresser, pantry
    };
    /**
     * Row shape: [global art sprite,x,y,width,height,facing].
     * Each cache remains centered on its previously saved V161 position.
     */
    public static float[][] build(int theme,float[][] rooms,float[][] centers){
        float[][] result=new float[centers.length][];
        int safeTheme=Math.floorMod(theme,STATION_SLOTS.length);
        for(int index=0;index<centers.length;index++){
            float x=centers[index][0],y=centers[index][1];
            int slot=STATION_SLOTS[safeTheme][index%4];
            int sprite=InteriorFurnitureCatalogV166.sprite(safeTheme,slot);
            int face=0;
            for(float[] z:rooms){
                if(x<z[0]||x>z[0]+z[2]||
                   y<z[1]||y>z[1]+z[3])continue;
                float left=x-z[0],right=z[0]+z[2]-x;
                float top=y-z[1],bottom=z[1]+z[3]-y;
                // Face into the chamber along the actual nearest wall.
                // Top remains a separate front-view pixel painting.
                if(left+24*S<top &&left<right&&left<bottom)
                    face=90;
                else if(right+24*S<top&&right<left&&right<bottom)
                    face=270;
                break;
            }
            // Searchable storage is actual full-sized room furniture, not
            // a miniature loot crate. Visuals and collision use one bbox.
            float w=(face==0?76f:66f)*S;
            float h=(face==0?66f:76f)*S;
            result[index]=new float[]{sprite,x-w*.5f,y-h*.5f,w,h,face};
        }
        return result;
    }
    public static boolean collides(float[] item,float x,float y,float r){
        float margin=2f*S;
        return x+r>item[1]+margin&&x-r<item[1]+item[3]-margin&&
               y+r>item[2]+margin&&y-r<item[2]+item[4]-margin;
    }
}
