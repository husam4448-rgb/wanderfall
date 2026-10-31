package com.survivalparadise.nativegame;

public final class V65RadialAimTest {
    static void ok(boolean value,String message){if(!value)throw new AssertionError(message);}
    static void near(float actual,float expected,String description){
        ok(Math.abs(actual-expected)<.001f,description+" expected="+expected+" got="+actual);
    }
    public static void main(String[] args){
        int[] ranges={250,265,220,0,430,415,395,325,650,435,330,74};
        for(int i=0;i<ranges.length;i++){
            float close=RadialAimV65.rest(i);
            float far=RadialAimV65.maximum(i,ranges[i],750);
            ok(close>0&&far>=close,"valid rest and max for "+i);
            near(RadialAimV65.distance(far,i,far,false,0,2900,.02f),
                close,"immediate thumb release "+i);
            near(RadialAimV65.distance(far,i,far,false,0,2900,1),
                close,"no residual distance after release "+i);
            near(RadialAimV65.distance(close,i,far,true,1,6500,1),far,
                "stick reaches weapon range "+i);
        }
        ok(RadialAimV65.rest(8)>RadialAimV65.rest(0),"long rifle distinct rest");
        near(RadialAimV65.direction(-1f,1f),-1f,"instant reverse to left");
        near(RadialAimV65.direction(1f,1f),1f,"instant reverse to right");
        // A 180-degree swipe must NOT cross the survivor center or preserve
        // the previous direction. The signed direction changes in one sample.
        float distance=220f;
        float oldCursor=RadialAimV65.direction(1f,1f)*distance;
        float newCursor=RadialAimV65.direction(-1f,1f)*distance;
        ok(oldCursor>0&&newCursor<0&&Math.abs(newCursor)==distance,
           "instant opposite hemisphere at same radial distance");
        float d=RadialAimV65.distance(RadialAimV65.rest(0),0,250,true,1,2900,.040f);
        ok(d>RadialAimV65.rest(0),"rapid aim extension at default speed");
        near(RadialAimV65.distance(d,0,250,false,0,2900,.016f),
             RadialAimV65.rest(0),"range-indicator snap without animation");
        near(RadialAimV65.maximum(8,650,400),400f,"player-configured max");
        System.out.println("V65 PASS: per-weapon rest, instant reversal, release snap, ballistic cap");
    }
}
