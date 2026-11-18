package com.survivalparadise.nativegame;

public final class V166InteriorArtTest {
    private static void check(boolean x,String m){if(!x)throw new AssertionError(m);}
    public static void main(String[] args){
        check(InteriorPropSelectionV166.SPRITES==16,"Atlas cells");
        check(InteriorPropSelectionV166.CELL==256,"Atlas dimensions");
        for(int theme=0;theme<NeighborhoodV154.TYPES;theme++){
            int seen=0;
            for(int i=0;i<60;i++){
                int kind=i%6;
                float width=68+i%55,height=57+i%39;
                int sprite=InteriorPropSelectionV166.choose(
                    theme,kind,i,width,height);
                check(InteriorPropSelectionV166.valid(sprite),"Index invalid");
                check(sprite/2==theme,"Wrong family");
                check(sprite==InteriorPropSelectionV166.choose(
                    theme,kind,i,width,height),"Index unstable");
                seen|=1<<(sprite%2);

            }
            check(seen==3,"Missing visual variant for family "+theme);
        }
        check(InteriorPropSelectionV166.choose(-1,0,0,90,75)==-1,
            "Invalid family");
        System.out.println("PASS V166: 16 themed indoor props, 8 distinct floors, stable choice");
    }
}
