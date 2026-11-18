package com.survivalparadise.nativegame;

/** Pure JVM mapping test. No Android Canvas classes on javac classpath. */
public final class V166InteriorFloorSelectionTest {
    private static void check(boolean value,String msg){
        if(!value)throw new AssertionError(msg);
    }
    public static void main(String[] args){
        int[] expected={
            InteriorFloorSelectionV166.OAK,InteriorFloorSelectionV166.TERRAZZO,
            InteriorFloorSelectionV166.VINYL,InteriorFloorSelectionV166.OAK,
            InteriorFloorSelectionV166.LINO,InteriorFloorSelectionV166.EPOXY,
            InteriorFloorSelectionV166.CONCRETE,InteriorFloorSelectionV166.PARQUET
        };
        for(int theme=0;theme<NeighborhoodV154.TYPES;theme++){
            int base=InteriorFloorSelectionV166.hallway(theme);
            check(base==expected[theme],"Incorrect hallway floor "+theme);
            for(int i=0;i<8;i++){
                int phase=InteriorFloorSelectionV166.phase(theme*917,i);
                check(phase==InteriorFloorSelectionV166.phase(theme*917,i),
                    "Non-deterministic floor phase");
            }
        }
        check(InteriorFloorSelectionV166.room(NeighborhoodV154.HOTEL,
            "GUEST SUITE")==InteriorFloorSelectionV166.CARPET,"Hotel carpet");
        check(InteriorFloorSelectionV166.room(NeighborhoodV154.SCHOOL,
            "LABORATORY")==InteriorFloorSelectionV166.TERRAZZO,"School lab");
        check(InteriorFloorSelectionV166.room(NeighborhoodV154.RESIDENCES,
            "KITCHEN")==InteriorFloorSelectionV166.VINYL,"Kitchen vinyl");
        check(InteriorFloorSelectionV166.room(NeighborhoodV154.WAREHOUSE,
            "PALLET RACKS")==InteriorFloorSelectionV166.CONCRETE,"Freight");
        for(int i=0;i<8;i++){
            float s=InteriorFloorSelectionV166.worldTileSize(i);
            check(s>=165f&&s<=230f,"World scale outside character reference");
        }
        check(InteriorFloorSelectionV166.TILE_COUNT==8,"Atlas contract");
        System.out.println("PASS V166: 8 semantic indoor floor materials, room swaps stable");
    }
}
