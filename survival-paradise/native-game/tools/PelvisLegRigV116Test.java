package com.survivalparadise.nativegame;

/** Headless geometry invariant tests for all original animation poses. */
public final class PelvisLegRigV116Test {
    private static void check(boolean value,String message) {
        if(!value)throw new AssertionError(message);
    }
    public static void main(String[] args) {
        check(PelvisLegRigV116.inwardPixels(100)==0,"neutral foot position");
        check(PelvisLegRigV116.inwardPixels(75)==25,"75% inward motion");
        check(PelvisLegRigV116.inwardPixels(55)==45,"55% inward motion");
        check(PelvisLegRigV116.inwardPixels(-1)==45,"minimum clamp");
        check(PelvisLegRigV116.inwardPixels(200)==0,"maximum clamp");
        for(int frame=0;frame<5;frame++){
            int[] counts=new int[4];
            for(int y=180;y<260;y++)for(int x=0;x<200;x++) {
                int part=PelvisLegRigV116.part(frame,x,y);
                check(part>=0&&part<=3,"exact unique pixel-layer attribution");
                counts[part]++;
            }
            if(frame==2) {
                check(counts[PelvisLegRigV116.OVERLAP_FOOT]==1200,
                    "intermediate step retains its original centered 60x20 block");
                check(counts[PelvisLegRigV116.LEFT_FOOT]==0&&
                      counts[PelvisLegRigV116.RIGHT_FOOT]==0,
                    "no splitting overlapping feet");
            } else {
                check(counts[PelvisLegRigV116.LEFT_FOOT]>0&&
                      counts[PelvisLegRigV116.RIGHT_FOOT]>0,
                    "each planted foot is a separately rigid source mask");
            }
            for(int percent=55;percent<=100;percent+=5){
                int shift=PelvisLegRigV116.inwardPixels(percent);
                // Translation moves two feet toward center. Width/height
                // and every ARGB pixel remain identical.
                for(int y=180;y<260;y++)for(int x=0;x<200;x++){
                    int part=PelvisLegRigV116.part(frame,x,y);
                    int translated=part==PelvisLegRigV116.LEFT_FOOT?
                        x+shift:part==PelvisLegRigV116.RIGHT_FOOT?
                        x-shift:x;
                    check(translated>=0&&translated<200,
                        "no feet leave the canonical sprite bounds");
                    if(part==PelvisLegRigV116.LEFT_FOOT)
                        check(translated>=x,"left foot never shifts outward");
                    if(part==PelvisLegRigV116.RIGHT_FOOT)
                        check(translated<=x,"right foot never shifts outward");
                    if(part==PelvisLegRigV116.OVERLAP_FOOT)
                        check(translated==x,"centered stride remains unchanged");
                }
            }
        }
        System.out.println("V116 five-pose rigid-foot translation and pelvis geometry: PASS");
    }
}
