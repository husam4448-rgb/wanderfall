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
    /**
     * Each saved storage ID is a functional cabinet in its NAMED room.
     * Unlike the old index%4 building-wide list, these choices cannot
     * put bookcases in kitchens, grocery refrigeration in hotel linen
     * rooms, or office filing cabinets in a classroom.
     *
     * Rows: apartments, offices, market, hotel, school, factory,
     * warehouse, residences. Six rooms each, three curated fixtures:
     * two original per-room storage IDs and one optional original
     * extra storage (ID 12 in room 0 / ID 13 in room 5).
     * The existing 14 save indices and anchor locations never change.
     */
    private static final int[][][] ROOM_STORAGE_SLOTS={
        { // apartments: living, bedroom, kitchen, utility, bedroom, store
            {6,7,2},{2,7,6},{10,4,3},{2,7,6},{2,7,6},{6,2,7}
        },
        { // office: reception, workspace, meeting, records, server, supplies
            {8,3,7},{3,6,8},{3,6,8},{3,8,6},{5,8,3},{8,3,6}
        },
        { // market: fresh produce, groceries, coolers, checkout, stock, office
            {2,6,0},{2,6,0},{3,6,5},{4,2,6},{6,5,11},{11,6,5}
        },
        { // hotel: reception, guest suite, service, lounge, suite, laundry
            {9,6,3},{6,1,9},{9,7,6},{7,1,6},{6,1,9},{9,6,7}
        },
        { // school: classrooms, library, staff, laboratory, stores
            {2,8,2},{2,8,2},{2,8,2},{9,2,8},{7,8,11},{8,2,9}
        },
        { // factory: machinery, assembly, control, tools, parts, maintenance
            {2,3,9},{3,7,9},{6,9,3},{2,9,3},{3,7,9},{9,2,10}
        },
        { // warehouse: receiving, racks, dispatch, packing, spares, security
            {0,1,5},{0,1,5},{0,1,6},{0,5,1},{0,4,5},{7,5,6}
        },
        { // residences: living, bedroom, kitchen, dining, study, pantry
            {8,6,5},{5,6,5},{11,7,3},{6,5,4},{8,6,5},{11,7,3}
        }
    };
    static int cacheSprite(int theme,int variation,int index){
        int safeTheme=Math.floorMod(theme,ROOM_STORAGE_SLOTS.length);
        int room=index<12?index/2:index==12?0:5;
        room=InteriorRoomArchetypeV166.actualRoom(room,variation);
        int slot=ROOM_STORAGE_SLOTS[safeTheme][room]
            [index<12?index%2:2];
        return InteriorFurnitureCatalogV166.sprite(safeTheme,slot);
    }
    /**
     * Row shape: [global art sprite,x,y,width,height,facing].
     * Each cache remains centered on its previously saved V161 position.
     */
    public static float[][] build(int theme,float[][] rooms,float[][] centers){
        return build(theme,0,rooms,centers);
    }
    public static float[][] build(int theme,int variation,
                                  float[][] rooms,float[][] centers){
        float[][] result=new float[centers.length][];
        for(int index=0;index<centers.length;index++){
            float x=centers[index][0],y=centers[index][1];
            int sprite=cacheSprite(theme,variation,index);
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
