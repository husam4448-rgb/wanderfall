package com.survivalparadise.nativegame;

/** Pure Java V144 regression: never change V92 item IDs, default visuals or head rendering. */
public final class V144LegacyVisualTest {
    public static void main(String[] args) {
        for (int i=0;i<3;i++) {
            eq(LegacyOutfitVisualV144.torso(i,-1),20+i,"torso");
            eq(LegacyOutfitVisualV144.pants(i,-1),20+i,"pants");
            eq(LegacyOutfitVisualV144.boots(i,-1),5+i,"boots");
            eq(LegacyOutfitVisualV144.headgear(i),-1,"headgear hidden");
        }
        for(int i: new int[]{-1,3,100}) {
            eq(LegacyOutfitVisualV144.torso(i,9),9,"top fallback");
            eq(LegacyOutfitVisualV144.pants(i,10),10,"pants fallback");
            eq(LegacyOutfitVisualV144.boots(i,3),3,"boot fallback");
        }
        System.out.println("PASS V144 legacy style slots; head visuals always disabled");
    }
    private static void eq(int got,int expected,String label){
        if(got!=expected)throw new AssertionError(label+": "+got+" != "+expected);
    }
}
