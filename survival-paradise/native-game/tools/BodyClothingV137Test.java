package com.survivalparadise.nativegame;

import java.util.Arrays;

/** Pure JVM test: equipment colors may not affect any black silhouette pixel. */
public final class BodyClothingV137Test {
    private static final int W=200,H=260,BLACK=0xff000000;
    private static void check(boolean ok,String reason){
        if(!ok)throw new AssertionError(reason);
    }
    private static int[] standard(){
        int[] a=new int[W*H];
        for(int y=160;y<180;y++){
            Arrays.fill(a,y*W+20,y*W+40,BLACK);
            Arrays.fill(a,y*W+40,y*W+160,BodyClothingV137.RED);
            Arrays.fill(a,y*W+160,y*W+180,BLACK);
        }
        for(int y=180;y<200;y++){
            Arrays.fill(a,y*W+20,y*W+40,BLACK);
            Arrays.fill(a,y*W+40,y*W+80,BodyClothingV137.BLUE);
            Arrays.fill(a,y*W+80,y*W+120,BodyClothingV137.RED);
            Arrays.fill(a,y*W+120,y*W+160,BodyClothingV137.BLUE);
            Arrays.fill(a,y*W+160,y*W+180,BLACK);
        }
        for(int y=200;y<220;y++){
            Arrays.fill(a,y*W+40,y*W+60,BLACK);
            Arrays.fill(a,y*W+60,y*W+140,BodyClothingV137.BLUE);
            Arrays.fill(a,y*W+140,y*W+160,BLACK);
        }
        for(int y=220;y<240;y++)Arrays.fill(a,y*W+60,y*W+120,BLACK);
        return a;
    }
    public static void main(String[] args){
        int[] original=standard();
        boolean[] originalBlack=new boolean[W*H];
        for(int i=0;i<original.length;i++)originalBlack[i]=original[i]==BLACK;
        int[] first=null;
        for(int torso=-1;torso<=2;torso++)
        for(int pants=-1;pants<=2;pants++){
            int[] rgba=original.clone();
            BodyClothingV137.apply(rgba,W,H,torso,pants);
            check(BodyClothingV137.styleKey(torso,pants)>=0,"style key");
            if(first==null)first=rgba.clone();
            // Every non-underside pixel of the original black outline is unchanged.
            for(int y=0;y<H;y++)for(int x=0;x<W;x++){
                int idx=y*W+x;
                if(y<220||y>=240||x<60||x>=140){
                    if(originalBlack[idx])check(rgba[idx]==BLACK,"black changed "+x+","+y);
                    if(original[idx]==0)check(rgba[idx]==0,"alpha changed "+x+","+y);
                }
                if(y<160||y>=240)check(rgba[idx]==original[idx],"outside body changed");
            }
            for(int y=220;y<240;y++)for(int x=60;x<140;x++){
                int expected=y<236?BLACK:0;
                check(rgba[y*W+x]==expected,"underside height/width");
            }
            check(rgba[165*W+110]==(torso<0?BodyClothingV137.RED:
                BodyClothingV137.TOP[torso])||torso==2,"torso visible");
            check(rgba[205*W+100]==(pants<0?BodyClothingV137.BLUE:
                BodyClothingV137.PANTS[pants])||pants==1,"pants visible");
            int[] same=original.clone();BodyClothingV137.apply(same,W,H,torso,pants);
            check(Arrays.equals(same,rgba),"unstable frame result");
            // Head pixels are y<160, and are immutable across equipment styles.
            for(int i=0;i<W*160;i++)
                check(original[i]==rgba[i],"head changed");
        }
        for(int torso=0;torso<3;torso++){
            int[] c=original.clone();BodyClothingV137.apply(c,W,H,torso,0);
            check(!Arrays.equals(c,first),"gear should change interior color");
        }
        System.out.println("PASS V137 16 equipment pairs, 200-head common silhouette, stable outline, 16px centered underside");
    }
}
